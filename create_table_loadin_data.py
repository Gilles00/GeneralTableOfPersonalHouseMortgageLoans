#coding:utf-8
import MySQLdb
import sys

#在本地数据库中建立10个月的数据表, 并设置字段
#设置默认字符为utf8
reload(sys)
sys.setdefaultencoding('utf-8')

#连接数据库
conn = MySQLdb.connect(
    host = 'localhost',
    port = 3306,
    user = 'root',
    passwd = '6143',
    db = 'fangdaishuju',
    charset = 'utf8'
    )
cur = conn.cursor()

#设置表名, 与数据库字段相对应
Data_Month = ['January', 'February', 'March', 'April', 'May',
                'June', 'July', 'August', 'September', 'October']
for i in range(len(Data_Month)):
    Data_Month[i] = "Data_" + Data_Month[i]
    print Data_Month[i],

#建一月与二月份的表(因为缺少首套首付与二套首付的值)
for i in range(2):
    cur.execute("""create table %s(
        id int not null auto_increment, 
        leader varchar(10) not null,
        time varchar(10),
        city varchar(10),
        bank varchar(10),
        rate_interest_first_set float,
        rate_interest_second_set float,
        tel_bank varchar(1000),
        quato varchar(5),
        time_grant float,
        age_second_hand_house int,
        month_on_month_ratio varchar(10),
        remarks varchar(1000),
        primary key(id))engine = innodb charset = utf8"""% Data_Month[i])
    cur.execute("""LOAD DATA LOCAL INFILE
        '/Users/Alas/Downloads/%s.txt'
        INTO TABLE %s CHARACTER SET utf8 FIELDS TERMINATED BY '\t'
        """% (Data_Month[i], Data_Month[i]))
     
#建三月到十月的表
for i in range(2, len(Data_Month)):
    cur.execute("""create table %s(
        id int not null auto_increment, 
        leader varchar(10) not null,
        time varchar(10),
        city varchar(10),
        bank varchar(10),
        down_payment_first_set float,
        rate_interest_first_set float,
        down_payment_second_set float,
        rate_interest_second_set float,
        tel_bank varchar(1000),
        quato varchar(5),
        time_grant float,
        age_second_hand_house int,
        month_on_month_ratio varchar(10),
        condition_discount varchar(500),
        remarks varchar(500), 
        primary key(id))engine = innodb charset = utf8"""% Data_Month[i])
    cur.execute("""LOAD DATA LOCAL INFILE
        '/Users/Alas/Downloads/%s.txt'
        INTO TABLE %s CHARACTER SET utf8 FIELDS TERMINATED BY '\t'
        """% (Data_Month[i], Data_Month[i]))

cur.close()
conn.commit()
conn.close()centey
