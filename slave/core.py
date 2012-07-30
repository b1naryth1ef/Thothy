import socket, json, zlib, random, redis, thread
import sys, os, time
from lib import Connection

red = redis.Redis(host="hydr0.com", password="")
conn = None
alive = True

#info
wid = 0
server = ""
channels = ""
nick = ""

def read(r, w): #IRC -> REDIS
	global conn
	while True:
		c = conn.read()
		print c
		red.publish(r, zlib.compress(json.dumps({'action':'irc', 'data':c})))

def write(r, w): #REDIS -> IRC
	global conn
	W = red.pubsub()
	W.subscribe(w)
	W.subscribe('global')
	for msg in W.listen():
		if msg['channel'] == 'global':
			msg['data'] = json.loads(msg['data'])
			if msg['data']['action'] == 'ECHO':
				d = {
					'wid':wid,
					'server':server,
					'channels':channels,
				}
				red.publish(msg['data']['resp'], json.dumps(d))
		print msg #Parse, (Q?) and send

def load():
	global conn, alive, wid, server, channels, nick
	temp = red.pubsub()
	rid = str(random.randint(1, 999))
	red.publish("manage", json.dumps({'action':'HI', 'respid':rid}))

	temp.subscribe(rid)
	for msg in temp.listen():
		msg['data'] = json.loads(msg['data'])
		print msg['data']
		conn = Connection(msg['data']['server'], msg['data']['nick']).connect(True, autojoin=msg['data']['channels'])
		break
	temp.unsubscribe(rid)

	wid = msg['data']['id']
	server = msg['data']['server']
	channels = msg['data']['channels']
	nick = msg['data']['nick']

	r = 'r-%s' % msg['data']['id']
	w = 'w-%s' % msg['data']['id']

	thread.start_new_thread(read, (r, w))
	thread.start_new_thread(write, (r, w))

	while conn.alive and alive:
		time.sleep(3)

load()