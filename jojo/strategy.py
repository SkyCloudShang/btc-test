import pandas as pd
import numpy as np, time
import requests,json, talib
from HuobiServices import  get_kline

short_win = 12    # 短期EMA平滑天数
long_win = 26    # 长期EMA平滑天数
macd_win = 9     # DEA线平滑天数


SIGNAL_SELL = 2   # 卖出信号
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
    if res:
        res = res.get('data')
        cur_price = res[0].get('close')
        print(res)
        print('price:{}'.format(cur_price))
        return res, cur_price
    else:
        return None


def get_cur_money():
    """
    获取当前账户可用余额
    :return:
    """
    pass


def get_cur_btc():
    """
    获取当前账户内的比特币数量
    :return:
    """


def handle_data():
    price_list, cur_price = get_history_data()
    if not price_list or not cur_price:
        print('当前无数据')
        return None
    p_list = []
    for i in price_list:
        p_list.append(i.get('close'))
    p_list = np.array(p_list)
    # talib计算MACD
    macd_tmp = talib.MACD(p_list, fastperiod=short_win, slowperiod=long_win, signalperiod=macd_win)
    macd_value = macd_tmp[2]
    # DIF = macd_tmp[0]
    # DEA = macd_tmp[1]
    # MACD = macd_tmp[2]
    # print(MACD[-1])

    # 判断MACD走向
    if macd_value[-1] > THRESHPLD_POS:
        if get_cur_money() >= cur_price*BUY_NUM:  # 默认每次买入0.003个
            return SIGNAL_BUY, cur_price
        else:
            print("余额不足")
            return SIGNAL_WAIT, 0
    elif macd_value[-1] < THRESHPLD_PPASS:
        sale_num = get_cur_btc()
        if sale_num > 0:   # 获取可卖出的比特币，默认每次全部卖出
            return SIGNAL_SELL, cur_price
        else:
            print("账户内无币")
            return SIGNAL_WAIT, 0
    else:
        return SIGNAL_WAIT, 0


def run():
    while True:
        signal, cur_price = handle_data()
        if not signal:  # 有动作
            make_deal(signal, cur_price)
        time.sleep(300)  # 每五分钟发送一次信号
    

def make_deal(signal, cur_price):
    """
    交易函数
    :param signal: 交易信号
    :param cur_price: 当前价格
    :return:
    """
    if signal == SIGNAL_BUY:
        make_buy(cur_price, BUY_NUM)
    else:
        make_sale(cur_price, get_cur_btc())


def make_buy(cur_price, buy_num):
    """
    买入函数
    :param cur_price: 当前价格
    :param buy_num: 买入的量
    :return:
    """
    pass


def make_sale(cur_price, sale_num):
    """
    卖出函数
    :param cur_price: 当前价格
    :param sale_num: 卖出的量
    :return:
    """
    pass

run()

