import redis, json, zlib, random, thread, threading
import sys, os, time


red = redis.Redis(host="hydr0.com", password="") #dirty dirty
core = red.pubsub()

server = "irc.freenode.net"
channels = ["plus3"]
workers = []

inc = 0 #We gain in ID numbers forever right now

def genWID():
	global inc
	inc += 1
	return inc

class Worker():
	def __init__(self, wid, server, channels=[]):
		self.id = wid
		self.nick = "Thothy-%s" % wid
		self.active = False

		self.server = server
		self.channels = channels

		self.sub = red.pubsub()
		self.sub.subscribe("r-%s" % str(self.id))

		self._ping = (0, False)

	def parse(self, msg):
		try: m = json.loads(zlib.decompress(msg['data']))
		except: "Failed to parse in W#%s" % self.id
		if m['action'] == "DIE":
			self.kill()
		elif m['action'] == 'IRC':
			print m['data']

	def thread(self):
		while self.active:
			for m in self.sub.listen():
				print "Worker #%s got a message: %s" % (self.id, m)
				self.parse(m) #@NOTE thread here?

	def start(self):
		self.active = True
		thread.start_new_thread(self.thread, ())

	def write(self): pass

	def kill(self):
		workers.pop(workers.index(self))
		self.active = False #kill the thread
		#del self #@NOTE dont worry about this now.

def boot():
	print 'Checking for active workers...'
	def _bthread():
		for msg in temp.listen():
			if msg['data'] != 0L: #unsub
				m = json.loads(msg['data'])
				w = Worker(**m)
				w.start()
				workers.append(w)
	temp = red.pubsub()
	rid = 'temp-'+str(random.randint(111, 999))
	temp.subscribe(rid)
	red.publish('global', json.dumps({'action':'ECHO', 'resp':rid, 'msg':'hai'}))
	i = threading.Thread(target=_bthread)
	i.start()
	time.sleep(5) #give everyone 5 secs to respond
	i._Thread__stop()
	print 'DONE! Found %s' % len(workers)

boot()
core.subscribe("manage")
while True: #Listen for new workers
	for msg in core.listen():
		print msg
		msg['data'] = json.loads(msg['data'])
		if msg['channel'] == "manage":
			if msg['data']['action'] == 'HI':
				w = Worker(genWID(), server=server, channels=channels)
				red.publish(msg['data']['respid'], json.dumps({'action':'HI', 'nick':'Thothy-%s' % w.id, 'id':w.id, 'server':w.server, 'channels':w.channels}))
				w.start()

