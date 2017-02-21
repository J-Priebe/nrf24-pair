# hardware module

import sys
sys.path.insert(0, "../lib/")


import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev

class Transceiver:

	# create a receiver for transmiting or receiving
	# each transceiver should do only ONE of the two
	def __init__(self, transmit_mode=True):

		# boilerplate to initialize radio


		if transmit_mode:
			CS_PIN = 0
			DATA_PIN = 17
		else:
			CS_PIN = 1
			DATA_PIN = 27

		GPIO.setmode(GPIO.BCM)
		#GPIO.setwarnings(False)

		# NRF24L01 has 6 pipes
		# all of our vehices read and write to only one pipe
		pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

		self.radio = NRF24(GPIO, spidev.SpiDev())
		self.radio.begin(CS_PIN, DATA_PIN)
		time.sleep(1)
		#self.radio.setRetries(15,15)
		self.radio.setPayloadSize(32)

		# We can use any channel, but all cars must use the same one
		self.radio.setChannel(0x60) 

		self.radio.setDataRate(NRF24.BR_2MBPS)
		self.radio.setPALevel(NRF24.PA_MIN)

		# disable automatic acknowledgment
		self.radio.setAutoAck(False) 

		# allow variable message size
		# may consider using static payload size once message protocol is established
		self.radio.enableDynamicPayloads()

		# read and write on same pipe for everyone
		if transmit_mode:
			self.radio.openWritingPipe(pipes[1])
		else:
			self.radio.openReadingPipe(1, pipes[1])
			self.radio.startListening()


	# send message in form of character array
	def transmit(self, message):

		char_arr = list(message)
		self.radio.write(char_arr)


	def receive(self):

    		if self.radio.available(0):
    			receivedMessage = []
    			self.radio.read(receivedMessage, self.radio.getDynamicPayloadSize())
    			return receivedMessage
		return False

