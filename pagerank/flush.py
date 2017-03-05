import redis
import sys
sys.path.append("..")
import config

host_ip = config.host_ip
host_port = config.host_port
host_pass = config.host_pass
html_db = config.html_db
urltag_db = config.urltag_db
need_calc_db = config.need_calc_db
get_calc_db = config.get_calc_db
final_pagerank_db = config.final_pagerank_db
mysql_user = config.mysql_user
mysql_passwd = config.mysql_passwd
mysql_db = config.mysql_db

r = redis.Redis(host=host_ip,port=host_port,db=need_calc_db)
r.flushdb()

r = redis.Redis(host=host_ip,port=host_port,db=get_calc_db)
r.flushdb()

r = redis.Redis(host=host_ip,port=host_port,db=final_pagerank_db)
r.flushdb()