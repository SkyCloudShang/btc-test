import pandas as pd
import numpy as np, time
import requests,json, talib
import HuobiServices as hb
from HuobiServices import  get_kline

short_win = 12    # 短期EMA平滑天数
long_win = 26    # 长期EMA平滑天数
macd_win = 9     # DEA线平滑天数


SIGNAL_SELL = -1   # 卖出信号
SIGNAL_BUY = 1  # 买进信号
SIGNAL_WAIT = 0   # 无动作,包余额不足的情况
TIME_STAMP = 14280  # 24/5 小时，当MACD一直处于买入WAIT时间超过该时间
                    # 则随机买入和卖出，保证至少5次的成交量
THRESHPLD_POS = 1  # MACD值大于该阈值则可卖出
THRESHPLD_PPASS = -1.5  # MACD值小于该阈值则买入
BUY_NUM = 0.003    # 买入量,默认值
SALE_NUM = 0.003   # 卖出量，默认值


def get_history_data():
    """
    获取历史数据和和最新的价格
    :return:
    """
    res = get_kline('btcusdt', '5min')
    #print(res['status'])
    if res:
        res = res.get('data')
        #cur_price = res[0].get('close')
        #print(res)
        #print('price:{}'.format(cur_price))
        return res
    else:
        return None


def get_cur_btc():
    return get_cur_acount('btc')


#itype可以为'usdt','btc','all'分别输出对应的余额
def get_cur_acount(itype):
    acct_id = hb.get_accounts()
    #print(acct_id)
    idLists = acct_id['data']
    masterid = idLists[0]['id']
    master_balance = hb.get_balance(masterid)
    balancelists = master_balance['data']['list']
    res=[]
    for listnum in balancelists:
        if(itype=='usdt'):
            if (listnum['currency'] == 'usdt' ):
                return float(listnum['balance'])
        elif(itype=='btc'):
            if (listnum['currency'] == 'btc'):
                return float(listnum['balance'])
        else:
            if (listnum['currency'] == 'usdt' and listnum['type']=='trade'):
                res.append(listnum['balance'])
            if (listnum['currency'] == 'btc' and listnum['type']=='trade'):
                res.append(listnum['balance'])
    return res


def handle_data():
    price_list = get_history_data()
    if not price_list :
        print('当前无数据')
        return None
    p_list = []
    for i in price_list:
        p_list.append(i.get('close'))
    p_list = np.array(p_list)
    # talib计算MACD
    macd_tmp = talib.MACD(p_list, fastperiod=short_win, slowperiod=long_win, signalperiod=macd_win)
    macd_value = macd_tmp[2]

    # 判断MACD走向
    if macd_value[-1] > THRESHPLD_POS:
        print("macd_buy")
        return SIGNAL_BUY
    elif macd_value[-1] < THRESHPLD_PPASS:
        print("macd_sell")
        return SIGNAL_SELL
    else:
        print("macd_wait")
        return SIGNAL_WAIT


def run():
    while True:
        signal, cur_price = handle_data()
        if(signal==SIGNAL_BUY):
            print("macdbuy")
        elif(signal==SIGNAL_SELL):
            print("macdsell")
        else:
            print("macdwait")
        # if not signal:  # 有动作
        #     make_deal(signal, cur_price)
        #time.sleep(30)  # 每五分钟发送一次信号

#run()
