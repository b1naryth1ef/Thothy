import sys, os, time
import socket

class Connection():
	def __init__(self, host, nick, port=6667):
		self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._info = [host, port, nick]

		self.alive = False

	def connect(self, block, autojoin=[]):
		self.c.connect((self._info[0], self._info[1]))
		self.alive = True
		self.c.send('NICK %s\r\n' % self._info[2])
		self.c.send('USER %s 0 * :WittleBoteh Hipstah\r\n' % self._info[2])
		startPong = time.time()
		while time.time()-startPong < 10: #Wait only 10 seconds for a PING message
			x = self.read().strip()
			if 'PING' in x:
				self.write('PONG%s' % x.split('PING')[1])
				break
		if block:
			startWait = time.time()
			while time.time() - startWait < 30:
				x = self.read().strip()
				print x
				if 'End of /MOTD' in x:
					self.write('JOIN')
					for i in autojoin:
						self.write('JOIN #%s' % i)
					break
		return self

	def disconnect(self):
		self.c.close
		self.alive = False

	def read(self, bytes=4080): 
		if self.alive is True:
			data = self.c.recv(bytes)
			if data:
				return data
			else:
				self.disconnect()
		return None

	def write(self, content): 
		print content
		self.c.send('%s\r\n' % content)