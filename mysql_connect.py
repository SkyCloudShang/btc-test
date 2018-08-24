#!/usr/bin/python3

import pymysql
db = pymysql.connect( "sz1.me" ,"root" ,"root" ,"zhongbenben"  ) 
sql = " select * from forecast_data_30mins order by time desc limit 1" 

cursor = db.cursor( ) 
# 执行SQL语句
cursor.execute( sql) 
# 获取所有记录列表
results = cursor.fetchall( ) 
for row in results:
    time  = row[ 0] 
    high = row[ 1] 
    low = row[ 2] 
    close = row[ 3]  
    # 打印结果
    print ( " time=%s,high=%s,low=%s,close=%s"  % ( str(time),str( high),str( low),str( close) ) ) 
		 
# 关闭数据库连接
db.close( ) 
