import HuobiServices as hb
import time
import requests
import demjson
import mysql_connect
import strategy
import logging


SIGNAL_SELL = -1   # 卖出信号
SIGNAL_BUY = 1  # 买进信号
SIGNAL_WAIT = 0   # 无动作,包余额不足的情况
ALLMONEY = 14.32664700  #100元对应的初始usdt


#存储先前购买价格；用来卖出时进行对比，盈利才卖！！！
pre_buy_price=[]



def getlast5close():
    history_close = []
    datas = hb.get_kline('btcusdt', '1min', size=5)
    if datas is not None:
        if 'data' in datas:
            last5info = datas['data']
            for info in last5info:
                history_close.append(info['close'])
    return history_close


def get_cur_price():
    while (1):
        try:
            time.sleep(5)
            r = requests.get('https://api.huobi.pro/market/detail/merged?symbol=btcusdt', timeout=8).text
            break
        except:
            time.sleep(5)
            continue

    n = demjson.decode(r)
    return n['tick']['close']


def get_cur_price_by_kline():
    res = hb.get_kline('btcusdt', '5min')
    if res:
        res = res.get('data')
        cur_price = res[0].get('close')
        # print(res)
        #print('price:{}'.format(cur_price))
        return cur_price
    else:
        return None


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


#判断价格是否在下降
def isdown(price1,price2):
    if(price1>price2):
        return True
    else:
        return False

#市价买，money(usdt)
def buy_bymarket(money,rate=1):
    status=hb.send_order(money*rate,symbol='btcusdt',_type='buy-market',source='api')
    return status

#市价卖,btcnum(btc数量)
def sell_bymarket(btcnum,rate=1):
    status=hb.send_order(btcnum*rate,symbol='btcusdt',_type='sell-market',source='api')
    return status


#买入，money:下单总金额（usdt）；price：下单的单价(usdt)
def buy_byprice(money,price,rate=1):
    num=money*rate/price
    hb.send_order(num,symbol='btcusdt',_type='buy-limit',price=price,source='api')


#卖出，btcnum:卖出的比特币数量;price:下单的单价(usdt)
def sell_byprice(btcnum,price,rate=1):
    hb.send_order(btcnum*rate,symbol='btcusdt',_type='sell-limit',price=price,source='api')


def make_decision_bylast5close(close_list):
    decision=0
    current_price=get_cur_price()
    pre0=close_list[0]
    pre1=close_list[1]
    pre2=close_list[2]
    pre3=close_list[3]
    pre4=close_list[4]
    if(isdown(pre1,pre0)):
        decision=decision-1
    else:
        decision=decision+1

    if (isdown(pre2, pre1)):
        decision = decision - 1
    else:
        decision = decision + 1

    if (isdown(pre3, pre2)):
        decision = decision - 1
    else:
        decision = decision + 1

    if (isdown(pre4, pre3)):
        decision = decision - 1
    else:
        decision = decision + 1

    print(decision)
    if(decision<-2 ):#and current_price<pre0):
        print("buy")
        return SIGNAL_BUY
        pass #买入
    elif(decision>2 ):#and current_price>pre0):
        print("sell")
        return SIGNAL_SELL
        pass #卖出
    else:
        print("wait")
        return SIGNAL_WAIT
        pass #等待


def make_decision_bylstm():
    res=mysql_connect.get_predict_close()
    print(res)
    cur_price=get_cur_price()
    if(res[0]/cur_price>=1.001):
        if(res[1]/cur_price>=1.001):
            if(res[2]/cur_price>1.001):
                print("lstm_buy")
                return SIGNAL_BUY
    elif(res[0]/cur_price<=0.999):
        if (res[1] / cur_price <= 0.999):
            if (res[2] / cur_price < 0.999):
                print("lstm_sell")
                return SIGNAL_SELL
    else:
        print("lstm_wait")
        return SIGNAL_WAIT



def make_decision_bymacd():
    res=strategy.handle_data()
    return res



if __name__ == '__main__':
    while(1):
    #根据历史5次价格决定买/卖
        last5close = []
        last5close = getlast5close()
        print(last5close)
        current_price = get_cur_price()
        print(current_price)

        #三种策略进行决策
        state1=make_decision_bylast5close(last5close)
        state2=make_decision_bylstm()
        state3=make_decision_bymacd()

        if(state1==SIGNAL_BUY and state2==SIGNAL_BUY and state3==SIGNAL_BUY):
            myusdt=get_cur_acount("usdt")
            rmyusdt=round(myusdt,8)
            print(rmyusdt)
            if(rmyusdt>0.25*ALLMONEY):
                ret=buy_bymarket(ALLMONEY,0.25)
                print(ret)
            elif(rmyusdt>0.00000001):
                ret=buy_bymarket(rmyusdt)
                print(ret)
            else:
                print("no money to buy!")
                continue
        elif(state1==SIGNAL_SELL and state2==SIGNAL_SELL and state3==SIGNAL_SELL):
            mybtcs=get_cur_acount("btc")
            rmybtcs=int(mybtcs*10000)/10000
            print(rmybtcs)
            if(rmybtcs>0.00001):
                ret=sell_bymarket(rmybtcs)
                print(ret)
            else:
                continue

    #测试买入
    # myusdt = get_cur_acount("usdt")
    # rmyusdt=round(myusdt,8)
    # state=buy_bymarket(rmyusdt)
    # print(state)

    #测试卖出
    # mybtcs = get_cur_acount("btc")
    # res=int(mybtcs*10000)/10000
    # print(res)


    #测试账户金额
    # myusdt = get_cur_acount("usdt")
    # print(myusdt)
    # mybtcs = get_cur_acount("btc")
    # print(mybtcs)

    #查看账户的id
    # ids=[]
    # for idinfo in idLists:
    #     ids.append(idinfo['id'])
    #     print(hb.get_balance(idinfo['id']))
    #print(ids)


    #测试根据id，查询成交明细
    # mybtcs = get_cur_acount("btc")
    # rmybtcs = int(mybtcs * 10000) / 10000
    # print(rmybtcs)
    # if (rmybtcs > 0.00001):
    #     ret = sell_bymarket(rmybtcs)
    #     print(ret)
    #     orderid=ret['data']
    #     print(orderid)
    #     orderinfo=hb.order_matchresults(orderid)
    #     print(orderinfo)
    #     orderprice=orderinfo["price"]
    #     print(orderprice)
