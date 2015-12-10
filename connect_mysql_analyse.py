#encoding=utf-8
import MySQLdb
import numpy as np
import matplotlib.pyplot as plt
from decimal import *
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

Month = ["一月份", "二月份", "三月份", "四月份", "五月份",
            "六月份", "七月份", "八月份", "九月份", "十月份"]
#对应数据库的相应子段
Data_Month = ["January", "February", "March", "April", "May",
                "June", "July", "August", "September", "October"]
for i in range(len(Data_Month)):
    Data_Month[i] = "Data_" + Data_Month[i]

#一线二线城市列表
First_Tier_City = ["北京", "上海", "广州", "深圳"]
Second_Tier_City =["杭州", "南京", "武汉", "重庆", "成都", "天津",
		"青岛", "长沙", "苏州", "厦门", "郑州", "西安",
		"无锡", "哈尔滨", "佛山", "珠海", "东莞", "海口",
		"宁波", "合肥", "南昌", "大连", "昆明", "济南",
		"沈阳", "太原", "乌鲁木齐", "南宁", "福州", "长春","石家庄"]

#连接fangdaishuju数据库
conn = MySQLdb.connect(
    host = 'localhost',
    port = 3306,
    user = 'root',
    passwd = '6143',
    db = 'fangdaishuju',
    charset = 'utf8')
cur = conn.cursor()

#定义一个三维数据存放一到十月份一线城市的平均利率
average_rate_interest = np.zeros((len(Data_Month), len(First_Tier_City), 2))

#定义每月的9折以下、9折～基准、基准及以上和停贷的银行个数, 以此计算折扣占比分布
Discount = ["9折以下", "9折(含)到基准", "基准(含)及以上", "停贷"]
quantity_different_discount = np.zeros((len(Data_Month), len(First_Tier_City), len(Discount)))
percentage_different_discount = np.zeros((len(Data_Month), len(First_Tier_City), len(Discount))) 

#从数据库导出想要的数据,此处是按月分城市的一套与二套房贷利率折扣
for month in range(len(Data_Month)):
    for city in range(len(First_Tier_City)):
        cur.execute("""select 
            id, city, bank,
            rate_interest_first_set,
            rate_interest_second_set 
            from %s
            where city = '%s'
            """%(Data_Month[month], First_Tier_City[city]))
        #将提取的数据存放在rows二维数组中
        rows = cur.fetchall()

        #获取连接对象的描述信息
        #desc = cur.description 
        #打印表头字段名称
        #print "%s\t%s\t%s\t%s\t%s" %(desc[0][0], desc[1][0], 
                #desc[2][0], desc[3][0], desc[4][0])

        #初始化一套及二套利率的总和为0，计数器为0
        sum_rate_interest_first_set = 0
        sum_rate_interest_second_set = 0
        count = 0

        #计算并整理数据
        for row in range(len(rows)):
            #排除数据中存在“555”的情况并计算按月各城市利率总和
            if 0 < rows[row][3] < 2 and 0 < rows[row][4] < 2:
                sum_rate_interest_first_set += rows[row][3] 
                sum_rate_interest_second_set += rows[row][4]
                count += 1
            #将按月份按城市求出的平均利率(计算总和除以总数,
            #之后可能乘以当月基准利率计算出当月的实际利率信息)放入数组中
            #Decimal.(*).quantize(Decimal('0.01'), rounding=ROUND_DOWN)函数
            #是取数据精度为小数点后两位，然后转换成浮点数float
            average_rate_interest[month, city] = [
                float(Decimal(sum_rate_interest_first_set/count).quantize(Decimal('0.01'), rounding = ROUND_DOWN)),
		float(Decimal(sum_rate_interest_second_set/count).quantize(Decimal('0.01'), rounding = ROUND_DOWN))]
            
            #按月统计处于四等不同类中的银行个数, 准备计算房贷利率折扣占比分布
            if 0 < rows[row][3] < 0.9:
                quantity_different_discount[month, city, 0] += 1;
            elif 0.9 <= rows[row][3] < 1:
                quantity_different_discount[month, city, 1] += 1;
            elif 1 <= rows[row][3] < 2:
                quantity_different_discount[month, city, 2] += 1;
            else:
                quantity_different_discount[month, city, 3] += 1;
    
        #计算房贷利率折扣占比分布
        #利用Decimal函数限制精度时，数据的取舍不是四舍五入的，还得找个更好的方法
        for i in range(4):
            percentage_different_discount[month, city, 
                    i] = float(Decimal(quantity_different_discount[month, city, 
                            i]/len(rows)).quantize(Decimal('0.0001'), rounding = ROUND_DOWN))
                
#print quantity_different_discount
#print percentage_different_discount 

#print average_rate_interest

'''
#转化数据开始自定义做图
plt.rc('figure', figsize=(10, 8))
fig, axes = plt.subplots(2, 2) #, sharex = True, sharey = True)
for i in range(2):
    for j in range(2):
        #利用m的值选择当个的城市和数据
        if ( i == 0 and j == 0 ):
            m = 0
        elif ( i == 0 and j == 1 ):
            m = 1
        elif ( i == 1 and j == 0 ):
            m = 2
        else:
            m = 3
        #设置子图坐标
        axes[i, j].set_xlim(0, 9.3)
        axes[i, j].set_ylim(0.8, 1)
        #单独调整第三四张子图的纵坐标
        if (i == 1):
            axes[i, j].set_ylim(0.8, 1.05)
        axes[i, j].set_xlabel(First_Tier_City[m])
        axes[i, j].set_ylabel("利率折扣")
        axes[i, j].set_xticks(np.arange(0.5, 9.5, 0.9))
        axes[i, j].set_xticklabels(['一','二','三','四','五','六','七','八','九','十'])
        #画柱状图同时返回其描述信息
        rects = axes[i, j].bar(left =tuple(np.arange(0.5, 9.5, 0.9)),
                height = (tuple(average_rate_interest[:, m, 0])),
                        width = 0.8, align = "center", color = 'k')
        #得到当条柱状的描述信息，重新获取柱子的高度、宽度以及坐标等
        for rect in rects:
            height = rect.get_height()
            #在柱状图上的合适位置显示其高度
            axes[i, j].text(rect.get_x(),
                     1.005*height, '%s' % float(height))
#设置子图的间距和边距
plt.subplots_adjust(left = 0.1, bottom = 0.1, right = 0.9,
        top = 0.9, wspace = 0.2, hspace = 0.2)

plt.show()
'''

plt.rc('figure', figsize=(10, 8))
fig, axes = plt.subplots(2, 2) #, sharex = True, sharey = True)
for i in range(2):
    for j in range(2):
        #设置子图坐标
        axes[i, j].set_xlim(0, 11)
        axes[i, j].set_ylim(0, 100)
        if ( i == 0 and j == 0 ):
            k = 0
        elif ( i == 0 and j == 1 ):
            k = 1
        elif ( i == 1 and j == 0 ):
            k = 2
        else:
            k = 3
        axes[i, j].set_xlabel(Discount[k])
        axes[i, j].set_ylabel("利率折扣占比（％）")
        axes[i, j].set_xticks(np.arange(1, 11))
        axes[i, j].set_xticklabels(['一','二','三','四','五','六','七','八','九','   十月份'])
        for l in range(4): 
            axes[i, j].plot(range(1, 11), 100*percentage_different_discount[:, l, k], 
                    linestyle = '--', label = First_Tier_City[l], marker = 'o')
        axes[0, 0].set_title("各月利率折扣占比分布")
        axes[0, 0].legend(loc = 'upper left')
        
#设置子图的间距和边距
plt.subplots_adjust(left = 0.1, bottom = 0.1, right = 0.9,
        top = 0.9, wspace = 0.2, hspace = 0.2)

plt.show()

cur.close()
conn.commit()
conn.close()
