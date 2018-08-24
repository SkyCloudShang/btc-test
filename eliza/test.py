
import mysql.connector
import sys, os
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
     
def insert(tablename,time,high,low,close):
	#这里把表写死了
	insert_sql = 'insert into forecast_data_15mins (time,high,low,close) values (%s,%s,%s,%s)'
	select_sql = 'select * from forecast_data_15mins where time = %s'
	update_sql = 'update forecast_data_15mins set high = %s, low = %s, close = %s where time = %s'
	global cursor
	try:
		cursor.execute(select_sql,[time])
		if cursor.rowcount == 0 :
			cursor.execute(insert_sql,[time,high,low,close])
		else:
			print('updating')
			cursor.execute(update_sql,[high,low,close,time])
		cnx.commit()
	except mysql.connector.Error as err:
		print("insert table forecast_data_15mins failed.")
		print("Error: {}".format(err.msg))
		sys.exit()
    
global cursor
global cnx
connect()

global high_price
global low_price
global close_price
global close_time
high_price = 6944.039257501718
low_price_price = 6944.039257501718
close_price = 6944.039257501718

insert('forecast_data_15mins','2018-08-07 15:15:00',str(high_price),'6934.660344059461','6944.672053420404')
cursor.close()
cnx.close()

