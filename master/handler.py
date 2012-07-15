import redis, json
import sys, os, time
import random

import config

corechan = "manager"
red = redis.Redis(host="hydr0.com", password=config.redis_pass)
core = red.pubsub()

server = "irc.quakenet.org"
channels = ["plus3"]
workers = []
subs = []

def allocateWorker():
	x = 0
	while x in workers:
		x = random.randint(111111, 999999)
	workers.append(x)
	return x

def killWorker(wid):
	if wid not in workerids:
		workerids.append(wid)

core.subscribe(corechan)
while True:
	for msg in core.listen():
		print msg
		msg['data'] = json.loads(msg['data'])
		if msg['channel'] == corechan:
			if msg['data']['action'] == 'HI':
				bid = allocateWorker()
				red.publish(msg['data']['respid'], json.dumps({'action':'HI', 'nick':'Thothy-%s' % bid, 'id':bid, 'server':server, 'channels':channels}))
				core.subscribe("recv-"+str(bid))
				subs.append("recv-"+str(bid))
		elif msg['channel'] in subs:
			print msg['data']['content']

