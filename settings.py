#coding:utf-8
DBENGINE = 'mysql'  # ENGINE OPTIONS: mysql, sqlite3, postgresql
DBNAME = 'lianjia'
DBUSER = 'root'
DBPASSWORD = 'a123456'
DBHOST = '127.0.0.1'
DBPORT = 3306

LOG_PATH = '/data/logs/scrawl/'

PROXY_ON = False
PROXY_API= 'http://192.168.1.3:33006/get/?speed=1000'

CITY = 'wh'  # only one, shanghai=sh shenzhen=sh......
REGIONLIST = [u'dongxihu', 'jiangan']  # only pinyin support


CHANNEL_PARAM = {
    'lianjia' : {'CITY': 'wh', 'REGIONLIST' : [u'dongxihu', u'jiangan'] },
    'fang': {'CITY': 'wuhan', 'REGIONLIST' :[u'东西湖', u'江岸']  }
}
