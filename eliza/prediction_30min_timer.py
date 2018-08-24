# -*- coding: utf-8 -*-

import HuobiServices as hb
from keras.models import Sequential
from keras.layers import Activation, Dense, Dropout, LSTM
import numpy as np
import pandas as pd
import threading
import time
import mysql.connector
import sys, os


def normalise_zero_base(df):
    """ Normalise dataframe column-wise to reflect changes with respect to first entry. """
    return df / df.iloc[0] - 1

def normalise_min_max(df):
    """ Normalise dataframe column-wise min/max. """
    return (df - df.min()) / (data.max() - df.min())
def train_test_split(df, test_size=0.1):
    split_row = len(df) - int(test_size * len(df))
    train_data = df.iloc[:split_row]
    test_data = df.iloc[split_row:]
    return train_data, test_data
    
def extract_window_data(df, window_len=10, zero_base=True):
    """ Convert dataframe to overlapping sequences/windows of len `window_data`.
    
        :param window_len: Size of window
        :param zero_base: If True, the data in each window is normalised to reflect changes
            with respect to the first entry in the window (which is then always 0)
    """
    window_data = []
    for idx in range(len(df) - window_len):
        tmp = df[idx: (idx + window_len)].copy()
        if zero_base:
            tmp = normalise_zero_base(tmp)
        window_data.append(tmp.values)
    return np.array(window_data)
    
def prepare_data(df, target_col, window_len=10, zero_base=True):  
    X_train = extract_window_data(df, window_len, zero_base)
    y_train = df[target_col][window_len:].values
    if zero_base:
        y_train = y_train / df[target_col][:-window_len].values - 1
    return X_train, y_train


def build_lstm_model(input_data, output_size, neurons=20, activ_func='linear',
                     dropout=0.25, loss='mae', optimizer='adam'):
    model = Sequential()
    model.add(LSTM(neurons, input_shape=(input_data.shape[1], input_data.shape[2])))
    model.add(Dropout(dropout))
    model.add(Dense(units=output_size))
    model.add(Activation(activ_func))
    model.compile(loss=loss, optimizer=optimizer)
    return model
    
def produce_model(timeInterval,column):
	
	np.random.seed(42)
	global data
	data = hb.get_kline('btcusdt', timeInterval, size=2000)
	data['data'].reverse()
	hist = pd.DataFrame(data['data'])
	hist = hist.set_index('id')
	hist.index = pd.to_datetime(hist.index, unit='s')
	hist_t = hist[:-1]
	target_col = column
	window_len = 7
	zero_base = True
	# model params
	lstm_neurons = 20
	epochs = 50
	batch_size = 8
	loss = 'mae'
	dropout = 0.5
	optimizer = 'adam'
	X_train, y_train = prepare_data(hist_t, target_col, window_len=window_len, zero_base=zero_base)
	global model_close
	global model_high
	global model_low
	if column == 'close':
		model_close = build_lstm_model(X_train, output_size=1, neurons=lstm_neurons, dropout=dropout, loss=loss,optimizer=optimizer)
		history = model_close.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1, shuffle=True)
	elif column == 'high':
		model_high = build_lstm_model(X_train, output_size=1, neurons=lstm_neurons, dropout=dropout, loss=loss,optimizer=optimizer)
		history = model_high.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1, shuffle=True)
	else:
		model_low = build_lstm_model(X_train, output_size=1, neurons=lstm_neurons, dropout=dropout, loss=loss,optimizer=optimizer)
		history = model_low.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1, shuffle=True)
	
 
def predict(timeInterval,model,column):
	np.random.seed(42)
	data = hb.get_kline('btcusdt', timeInterval, size=2000)
	cur_time = data['data'][0]['id'] 
	data['data'].reverse() 	 
	hist = pd.DataFrame(data['data'])
	hist = hist.set_index('id')
	hist.index = pd.to_datetime(hist.index, unit='s')
	hist_t = hist[:-1]
	target_col = column
	window_len = 7
	zero_base = True
	final = hist_t[-window_len:].copy()
	tmp = final
	if zero_base:
		tmp = normalise_zero_base(tmp)
	X_test = np.array(tmp.values)
	preds = model.predict(X_test.reshape(1,7,7)).squeeze()
	#print(preds)
	preds = final[target_col].values[0] * (preds + 1)
	#最后一个数据不完整，故前面已经去掉了，这里相当于预测最后一个数据。
	print(preds)
	print(final)
	global close_price
	global high_price
	global low_price
	global close_time
	
	if column == 'close':
		close_price = preds
		close_time =  timestamp_datetime(cur_time + 1800 ) 
		print(cur_time)
	elif column == 'high':
		high_price = preds
	else:
		low_price = preds		
	
	
	


 
 
def timestamp_datetime(value):
    format = '%Y-%m-%d %H:%M:%S'
	# value为传入的值为时间戳(整形)，如：1332888820
    value = time.localtime(value)
    dt = time.strftime(format, value)
    return dt	

def connect():
	user = 'root'
	pwd  = 'root'
	host = 'sz1.me'
	db   = 'zhongbenben'
	try:
		global cursor
		global cnx
		cnx = mysql.connector.connect(user=user, password=pwd, host=host, database=db)
		cursor = cnx.cursor(buffered=True)
	except mysql.connector.Error as err:
		print("connection failed")
		print("Error: {}".format(err.msg))
		sys.exit()	
     
def insert(time,high,low,close):
	#注意表名固定了
	insert_sql = 'insert into forecast_data_30mins (time,high,low,close) values (%s,%s,%s,%s)'
	select_sql = 'select * from forecast_data_30mins where time = %s'
	update_sql = 'update forecast_data_30mins set high = %s, low = %s, close = %s where time = %s'
	global cursor
	try:
		cursor.execute(select_sql,[time])
		if cursor.rowcount == 0 :
			cursor.execute(insert_sql,[time,high,low,close])
		else:
			
			cursor.execute(update_sql,[high,low,close,time])
		cnx.commit()
	except mysql.connector.Error as err:
		print("insert table forecast_data_30mins failed.")
		print("Error: {}".format(err.msg))
		sys.exit()
#要将此函数设置为定时执行   
def runPredict():
	begin = time.time()
	predict('30min',model_close,'close')
	predict('30min',model_high,'high')
	predict('30min',model_low,'low')
	insert(close_time,str(high_price),str(low_price),str(close_price))
	end = time.time() 
	global timer
	timer = threading.Timer(1800- end + begin, runPredict)
	timer.start()
	
user = 'root'
pwd  = 'root'
host = 'sz1.me'
db   = 'zhongbenben'
global cursor
global cnx
connect()

global model_close
global model_high
global model_low
global high_price
global low_price
global close_price
global close_time

global data
global timer

data = hb.get_kline('btcusdt', '30min', size=2000)
produce_model('30min','close')
produce_model('30min','high')
produce_model('30min','low')

runPredict()




	





