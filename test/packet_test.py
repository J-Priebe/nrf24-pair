from threading import Condition
import sys
sys.path.insert(0, "../")
from receive_thread import *
from transmit_thread import *


import time
import os,binascii 
import numpy as np, scipy.stats as st

packet_data = {}
total_invalid_packets = 0

device_id = binascii.b2a_hex(os.urandom(3))

n = 100000

transmit_message = str(str(device_id) + ":" + str(n))



def _validate_message(message):
	return isinstance(message, list) and len(message) == 13 and chr(message[6]) == ':'

def _decode_message(msg):
	string = ''.join(chr(e) for e in msg)
	return string

def _record_packet(msg, arrival_time):

	global packet_data
	global total_invalid_packets

	if _validate_message(msg):
		decoded_message = _decode_message(msg)
		sender = decoded_message[0:6]
		msg_id = decoded_message[7:]
		# record arrival time of each packet
		packet_data.setdefault(sender, []).append([msg_id, arrival_time])

	else:
		# print invalid messages
		invalid_msg = _decode_message(msg)
		print('invalid message recieved: ' + invalid_msg)
		total_invalid_packets += 1


def _report():
	global packet_data
	global total_invalid_packets

	print 'generating report...'

	# remove junk from previous broadcasts on same channel	
        for k, v in packet_data.items():
		if len(v) < 3 :
			print('junk key ' + str(k) + ' deleted')
			del packet_data[k]

	# report on packets from each individual sender
	for key in packet_data:
		print('key' + str(key))
		# number of messages from sender
		discard = int( len(packet_data[key])/10 )
		packet_data[key] = packet_data[key][discard:-discard]
		n = len(packet_data[key])
		# find receival period since pi's are not synchronized
		# discard the first and last 10% of packets
		first_arrival_time = float(packet_data[key][0][1])
		last_arrival_time = float(packet_data[key][-1][1])
		receive_time = last_arrival_time - first_arrival_time

		# track interarrival times
		interarrival_times = []

		# number of lost packets
		lost = 0
		for i in range (1, n):

			# interarrival time
			prev_arrival_time = float(packet_data[key][i-1][1])
			arrival_time = float(packet_data[key][i][1])
			interarrival_times.append(arrival_time - prev_arrival_time)

			# count non sequential packets to find how many were lost in between
			prev_packet_id = int(packet_data[key][i-1][0])
			packet_id = int(packet_data[key][i][0])
			lost = lost + (packet_id - prev_packet_id - 1)

		print ('getting stats for key' + str(key))
		# statistics on interarrival distribution
		average_interarrival_time = np.mean(interarrival_times)
		max_interarrival_time = max(interarrival_times)
		max_index = interarrival_times.index(max_interarrival_time)
		min_interarrival_time = min(interarrival_times)
		interarrival_variance = np.var(interarrival_times)
		ci = st.t.interval(0.9999, len(interarrival_times)-1, loc=np.mean(interarrival_times), scale=st.sem(interarrival_times))

		# print('first 5 interarrivals: ')
		# r = min(len(interarrival_times), 5)
		# for j in range(0, r):
		# 	print(interarrival_times[j])

		        # total packets received from all senders
        	total_packets_received = sum(len(packet_data[key]) for key in packet_data)

        	print(str(total_packets_received) + " total valid packets received")
        	print(str(total_invalid_packets) + " total invalid packets received")

        	print('')

		print('\n------------- Sender: ' + str(key) + ' -------------')
		print(str(n) + " messages analyzed")
		percent = str(float(n) / float(total_packets_received) * 100.0)
		print(percent + "% of packets")
		print('estimated packets lost: ' + str( str(lost) + ' ( ' + str( float(lost)/(lost + n) * 100 ) + '%)' ))
		print('')
		print('total receive time: ' + str(receive_time))
		print('')
		print('average interarrival time: ') + str(average_interarrival_time)
		print('max: ' + str(max_interarrival_time))
		print('packet index of max: ' + str(max_index))
		print('min: ' + str(min_interarrival_time))
		print('interarrival variance: ' + str(interarrival_variance))

		print('\n99.99% confidence interval: ' + str(ci))
		print('------------------------------------------\n')
	print 'report done'
# thread callbacks
def on_message_received(msg):
	arrive_time = time.time()
	_record_packet(msg, arrive_time)

def on_message_sent(msg):
	global n, device_id
	global transmitter
	n +=1
	new_msg = str(str(device_id) + ":" + str(n))
	#print new_msg
	transmitter.set_message(new_msg)

condition = Condition()
receiver = ReceiveThread(condition, on_message_received)
transmitter = TransmitThread(transmit_message, condition, on_message_sent)

if __name__ == "__main__":

	print('')
	time.sleep(1)
	print('Device ID: '+ device_id)

	if transmitter.transceiver.radio.get_status() == 0:
		print 'Error initializing transmitter. Check your hardware.'
		sys.exit(0)
	else:
		print 'Transmitter OK'
	if receiver.transceiver.radio.get_status() == 0:
                print 'Error initializing receiver. Check your hardware.'
                sys.exit(0)
	else:
		print 'Receiver OK'	
	
	time.sleep(1)
	print('broadcast/receive started...')

	t = time.time()
	end = t + 5

	transmitter.start()
	receiver.start()

	# continuously broadcast and receive for 20 seconds
	while(t < end):
		t = time.time()
		time.sleep(2)
		print ('working')
	# report on packets collected
	transmitter.running = False
	receiver.running = False
	#transmitter.join()
	#receiver.join()

	_report()


