#About
Thread-based classes for using two NRF24L01 transceiver chips (one for transmitting, one for receiving) on a single Raspberry Pi. Created for McMaster University/General Motors autonomous vehicle capstone project groups, for use in the common V2V communication protocol.


# Getting Started
These classes use two Python libraries for interfacing with the chips through the Raspberry Pi: [libnrf24](https://github.com/BLavery/lib_nrf24) and [spidev](https://github.com/Gadgetoid/py-spidev). Follow [this tutorial](http://invent.module143.com/daskal_tutorial/rpi-3-tutorial-13-wireless-pi-to-pi-python-communication-with-nrf24l01/) for step-by-step instructions on setting up the libraries.

# Pin Wiring
This pin configuration is for a Raspberry Pi 3. If you are using an Arduino, check out this [nrf24-pair example from the nrf24 library](https://github.com/BLavery/lib_nrf24/blob/master/example-nrf24-pair.py).

## Shared Pins
Five pins (MOSI, SCLK, MISO, VCC, GND) are shared by BOTH CHIPS. Connect them via a breadboard, according to the below diagram:

!(http://invent.module143.com/wp-content/uploads/2016/07/nrf24l01_module_pinout-1-768x357.jpg)

!(http://invent.module143.com/wp-content/uploads/2016/07/RFToPiConnections-1.png)

source: [tutorial](http://invent.module143.com/daskal_tutorial/rpi-3-tutorial-13-wireless-pi-to-pi-python-communication-with-nrf24l01/)

## Individual Pins

### Chip 1 (Same as diagram)
***CSN Pin:*** GPIO 08 / Pin 24
***CE Pin:*** GPIO 17 / Pin 11

### Chip 2
***CSN Pin:*** GPIO 07 / Pin 26
***CE Pin:*** GPIO 27 / Pin 13


**Note: the IRQ pin is not used.**


# Usage
After following the above setup, download/clone the repository onto your Pi. If you want to use the included test module, install `scipy` as well (`sudo apt-get install scipy`). Then simply run `python packet_test.py`.

### Tranceiver
Object for initializing radio and sending/receiving messages. initialized in transmit mode (default) or receive mode.

### TransmitThread and ReceiveThread
Thread classes for operating a radio in transmit or receive mode. Their callback function is called every time they send or receive a message. A  shared *condition* similar to a thread lock) ensures the transmit and receive threads run equally. See `packet_test.py` for an example of initializing the threads, thread condition, callbacks, etc.


# Results
So far this has been tested with two Raspberry Pis. Using a thread condition is the best method I've found in terms of total message volume and even "sharing", i.e., the same proportion of messages are received by each Pi. Here are the results for one and two Pis, respectively:

!(http://i.imgur.com/VYIKPau.png)

!(http://i.imgur.com/YDCK0LY.png)

The % of messages lost appears proportionate to the number of Pis, which makes sense. Because of the alternating threads, a Pi can receive at most as many messages as it sends. 

Let N be the total number of Pis. Let S be the number of messages sent from a single Pi. Assume S is roughly the same for each Pi. Then a single Pi can only receive S/N messages from any other Pi.

Thus, % of messages lost from each Pi = (1 - 1/N).

We could reduce message loss be increasing the proportion of messages received vs. sent, ie., by having the receive thread run more often. But this would be at the cost of sending less messages, giving the same number of messages received overall.

# Next Steps
We still need to test this with more Pis - ideally as many as the number of cars which will be on the track at once. Give this a shot and feel free to open an issue or contact us with any questions or improvements! 

