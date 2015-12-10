#计算全国的首套与二套利率的分类占比
#首套利率的分类是: 0到9折,9折(含)到基准,基准(含)及以上,停贷
#二套利率的分类是: 基准以下,基准(含)到基准上浮10%,基准上浮10%(含)及以上,停贷
#-*- encoding:utf-8 -*-
import MySQLdb
import sys
import numpy as np
from pyExcelerator import *

#尝试连接数据库data_personal_house_mortgage_loans
try:
    conn = MySQLdb.connect(
            host = '10.0.8.233',
            port = 3306,
            user = 'alas',
            passwd = '6143',
            db = 'data_personal_house_mortgage_loans',
            charset = 'utf8')
except Exception, e:
    print e
    sys.exit()

cur = conn.cursor()

month = ['january', 'february', 'march', 'april', 'may',
        'june', 'july', 'august', 'september', 'october',
        'november']

#三维数组存放一套利率与二套利率的分类占比
data_average = np.zeros((11, 2, 4))

#循环查询11个月的数据
for i in range(len(month)):
    month[i] += '2015'
    mysql = """
            select 
            city, bank, 
            loan_rates_first_home,
            loan_rates_second_home
            from %s""" % month[i]
         
    try:
        cur.execute(mysql)
    except Exception, e:
        print e

    rows = cur.fetchall()#获取查询的数据
#将查询数据以(另外新建)数组data_from_mysql格式存放
    data_from_mysql = range(len(rows))
    for x in range(len(rows)):
        data_from_mysql[x] = list(rows[x])

#初始化一套利率的四种分类标准的计数器
#分别是0到9折,9折(含)到基准,基准(含)及以上,停贷
    number_zero_to_ten_percent_discount = 0
    number_ten_percent_discount_to_benchmark = 0
    number_above_benchmark = 0
    number_stop_handling_loans_first_home = 0
#初始化二套利率的四种分类标准的计数器
#分别是基准以下,基准(含)到基准上浮10%,基准上浮10%(含)及以上,停贷
    number_zero_to_benchmark = 0
    number_benchmark_to_go_up_ten_percent = 0
    number_above_go_up_ten_percent = 0
    number_stop_handling_loans_second_home = 0

#设置一套利率的分类标准
    for data in data_from_mysql:
        if '0' < data[2] < '0.9':
            number_zero_to_ten_percent_discount +=1
        elif '0.9' <= data[2] < '1':
            number_ten_percent_discount_to_benchmark += 1
        elif '1' <= data[2] < '2':
            number_above_benchmark += 1
        else:
            number_stop_handling_loans_first_home += 1

#计算一套利率的分类占比,以小数形式表示
    data_average[i, 0, 0] = np.around(
            1.0*number_zero_to_ten_percent_discount/len(rows), decimals = 4)
    data_average[i, 0, 1] = np.around(
            1.0*number_ten_percent_discount_to_benchmark/len(rows), decimals = 4)
    data_average[i, 0, 2] = np.around(
            1.0*number_above_benchmark/len(rows), decimals = 4)
    data_average[i, 0, 3] = np.around(
            1.0*number_stop_handling_loans_first_home/len(rows), decimals = 4)
        
#设置二套利率的分类标准 并完成计数
    for data in data_from_mysql:
        if '0' < data[3] < '1':
            number_zero_to_benchmark +=1
        elif '1' <= data[3] < '1.1':
            number_benchmark_to_go_up_ten_percent += 1
        elif '1.1' <= data[3] < '2':
            number_above_go_up_ten_percent += 1
        else:
            number_stop_handling_loans_second_home += 1

#计算二套利率的分类占比,以小数形式表示        
    data_average[i, 1, 0] = np.around(
            1.0*number_zero_to_benchmark/len(rows), decimals = 4)
    data_average[i, 1, 1] = np.around(
            1.0*number_benchmark_to_go_up_ten_percent/len(rows), decimals = 4)
    data_average[i, 1, 2] = np.around(
            1.0*number_above_go_up_ten_percent/len(rows), decimals = 4)
    data_average[i, 1, 3] = np.around(
            1.0*number_stop_handling_loans_second_home/len(rows), decimals = 4)

w = Workbook()#创建工作簿
ws = w.add_sheet('sheet1')#创建工作表存放首套利率的分类占比值
for i in range(len(month)):
    for j in range(4):
        ws.write(i, j, data_average[i, 0, j])
ws = w.add_sheet('sheet2')#创建工作表存放二套利率的分类占比值
for i in range(len(month)):
    for j in range(4):
        ws.write(i, j, data_average[i, 1, j])
#把数据导入下列EXCEL表格
w.save('data_average_loan_rates_first_and_second_home.xls')

cur.close()
conn.close()

