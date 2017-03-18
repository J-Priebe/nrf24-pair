import time
from threading import Thread
from nrf24_transceiver import Transceiver

# callback when a message is transmitted
class TransmitThread(Thread):

	def __init__(self, message, condition, callback=None):
		super(TransmitThread, self).__init__()
		self.transceiver = Transceiver(True)
		self.condition = condition
		self.message = message
		self.callback = callback
		self.enabled = True
		self.running = True

	def get_message(self):
		return self.message

	def set_message(self, message):
		self.message = message

	def set_enabled(self, enabled):
		self.enabled = enabled

	def run(self):
		while self.running:
			self.condition.acquire()
			if self.enabled:
				self.transceiver.transmit( self.message )
				self.callback and self.callback(self.message)
			self.condition.notify()
			self.condition.wait(5)
		print('transmit thread done')
