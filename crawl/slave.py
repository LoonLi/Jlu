#coding='utf-8'
from spider import Spider
import redis  
import MySQLdb
import time
import traceback
import sys
sys.path.append("..")
import config
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
  
class RedisQueue(object):  
    """Simple Queue with Redis Backend"""  
    def __init__(self, name, namespace='queue', **redis_kwargs):  
        """The default connection parameters are: host='localhost', port=6379, db=0"""  
        self.__db = redis.Redis(**redis_kwargs)  
        self.key = '%s:%s' %(namespace, name)  
  
    def qsize(self):  
        """Return the approximate size of the queue."""  
        return self.__db.llen(self.key)  
  
    def empty(self):  
        """Return True if the queue is empty, False otherwise."""  
        return self.qsize() == 0  
  
    def put(self, item):  
        """Put item into the queue."""  
        self.__db.rpush(self.key, item)  
  
    def get(self, block=True, timeout=None):  
        """Remove and return an item from the queue.  
 
        If optional args block is true and timeout is None (the default), block 
        if necessary until an item is available."""  
        if block:  
            item = self.__db.blpop(self.key, timeout=timeout)  
        else:  
            item = self.__db.lpop(self.key)  
  
        if item:  
            item = item[1]  
        return item  
  
    def get_nowait(self):  
        """Equivalent to get(False)."""  
        return self.get(False)

def make_dic(urls,depth):#make a dic set
    urls_set = []
    for url in urls:
        dic = {}
        dic['url'] =url
        dic['depth'] = depth
        urls_set.append(dic) 
    return urls_set


host_ip = config.host_ip
host_port = config.host_port
host_pass = config.host_pass
html_db = config.html_db
srq_db = config.srq_db
nrq_db = config.nrq_db
bl_db = config.bl_db # blacklist
tag_db = config.tag_db
urltag_db = config.urltag_db
mysql_user = config.mysql_user
mysql_passwd = config.mysql_passwd
mysql_db = config.mysql_db

#start_urls = ['http://zsb.jlu.edu.cn/list/45.html']

srq = RedisQueue('test', host = host_ip, port=host_port, db=srq_db,password=host_pass) #solved queue
nrq = RedisQueue('test', host = host_ip, port=host_port, db=nrq_db,password=host_pass) #have not solved queue
trq = RedisQueue('test', host = host_ip, port=host_port, db=tag_db,password=host_pass)#set a tag to keep parallel
blacklist = redis.Redis(host=host_ip,port=host_port,db=bl_db,password=host_pass)#save the url costs too much time
rhtml = MySQLdb.connect(host_ip,mysql_user,mysql_passwd,mysql_db,charset='utf8')
rurltag = redis.Redis(host=host_ip,port=host_port,db=urltag_db,password=host_pass)

# urls_dics = make_dic(start_urls,0)
# for url in urls_dics:#put the urls to queue
#     srq.put(url)
error_count = 0
while(True):
    # if nrq.empty() and srq.empty():
    #     print "Complete!"
    #     break
    while(True):
        if srq.empty() != True:#get a url
            urls_dic=eval(srq.get())   # convert to a dic contain a url and a depth
            break
        time.sleep(0.1)
    start_time = time.time()#set a start time
    try:
        # print repr(urls_dic)
        s = Spider(urls_dic['url'])#parse a web
        # print urls_dic['url']
    except:
        print 'May be time out.'
        blacklist.set(urls_dic['url'],-1)
        continue
    tag = int(trq.get())#get tag
    trq.put(tag+1)
    urls = s.parse_url()#get all urls in the website return a set
    urls_dics = make_dic(urls,int(urls_dic['depth'])+1) #make a set(each element is a dic(url,depth))pass to nrq 
    for x in urls_dics:
        nrq.put(x)       #pass all dic(url,depth) to nrq
    try:
        s.parse_html(tag,rhtml,rurltag)#save html
    except:
        # error_count+=1
        # if error_count>5:
        #     print "May be connection is closed."
        #     sys.exit(0)
        print traceback.print_exc()
        continue
    if error_count>0:
        error_count=error_count-1
    end_time = time.time()
    print 'Parse time is:',end_time - start_time#the sum cost time
    if (end_time-start_time)>5:
        blacklist.set(urls_dic['url'],end_time-start_time)
        print 'This page has been saved in blacklist.'

