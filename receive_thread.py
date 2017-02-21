import time
from threading import Thread
from nrf24_transceiver import Transceiver

#callback when a message is received
class ReceiveThread(Thread):

	def __init__(self, condition, callback):
		super(ReceiveThread, self).__init__()
		
		self.transceiver = Transceiver(False)
		self.condition = condition
		self.callback = callback
		self.running = True

	def run(self):
		print('Receive thread: started')

		while self.running:
            self.condition.acquire()

			msg = self.transceiver.receive()
			if msg:
				self.callback and self.callback(msg)
			
			self.condition.notify()
			self.condition.wait()
		
		print('Receive thread: done')


