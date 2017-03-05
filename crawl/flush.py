import redis
import sys
sys.path.append("..")
import config

host_ip = config.host_ip
host_port = config.host_port
host_pass = config.host_pass
html_db = config.html_db
srq_db = config.srq_db
nrq_db = config.nrq_db
bl_db = config.bl_db # blacklist
tag_db = config.tag_db
urltag_db = config.urltag_db

r = redis.Redis(host=host_ip,port=host_port,db=html_db,password=host_pass)
r.flushdb()

r = redis.Redis(host=host_ip,port=host_port,db=srq_db,password=host_pass)
r.flushdb()

r = redis.Redis(host=host_ip,port=host_port,db=nrq_db,password=host_pass)
r.flushdb()

r = redis.Redis(host=host_ip,port=host_port,db=tag_db,password=host_pass)
r.flushdb()

r = redis.Redis(host=host_ip,port=host_port,db=urltag_db,password=host_pass)
r.flushdb()

print "finished."