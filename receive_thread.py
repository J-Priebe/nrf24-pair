import time
from threading import Thread
from nrf24_transceiver import Transceiver

#callback when a message is received
class ReceiveThread(Thread):

	def __init__(self, condition, callback):
		super(ReceiveThread, self).__init__()
		self.transceiver = Transceiver(False)
		self.last_message = None

		self.condition = condition
		self.callback = callback
		self.running = True

	def run(self):
		while self.running:
			self.condition.acquire()
			msg = self.transceiver.receive()
			if msg and msg != self.last_message:
				self.last_message = msg
				self.callback and self.callback(msg)
				#time.sleep(0.000001)
			self.condition.notify()
			self.condition.wait(5)
		print('receive thread done')


