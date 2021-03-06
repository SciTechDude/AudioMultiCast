from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from ast import literal_eval
import pyaudio
import wave
import time
import pickle

# PyAudio configuration
SIZE_PACKAGE = 1024
CHUNK = 1024
CHANNELS = 1
RATE = 10240
INPUT = True
FORMAT = pyaudio.paInt16
AUDIO_FILE = "test.wav"
#AUDIO_FILE = "mozart.wav"
WF = wave.open(AUDIO_FILE, 'rb')
p = pyaudio.PyAudio()

print "format = {}".format(p.get_format_from_width(WF.getsampwidth()))
print "sampleWidth = {}".format(WF.getsampwidth())
print "channels = {}".format(WF.getnchannels())
print "rate = {}".format(WF.getframerate())

stream = p.open(format=p.get_format_from_width(WF.getsampwidth()),
                channels=WF.getnchannels(),
                rate=WF.getframerate(),
                output=True)

class MulticastPingClient(DatagramProtocol):

    def sendData(self):
        self.chunk_count = 0
        self.data = WF.readframes(CHUNK)
        self.payload = pickle.dumps([self.chunk_count, self.data])

        while self.data  != '':
            print "Sent chunk_count={} , type={}".format(self.chunk_count,type(self.data)) 
            self.transport.write(self.payload, ("228.0.0.5", 8005))

            #check if data was sent
            #

            self.chunk_count +=1
            self.data = WF.readframes(CHUNK)
            self.payload = pickle.dumps([self.chunk_count, self.data])

    def startProtocol(self):
        # Set the TTL=1 so multicast will NOT cross router hops:
        self.transport.setTTL(1)

        # Join the multicast address, so we can send data:
        self.transport.joinGroup("228.0.0.5")

        # Send to 228.0.0.5:8005 - all listeners on the multicast address
        # (including us) will receive this message.
        self.transport.write('Server: Ping', ("228.0.0.5", 8005))
        

    def datagramReceived(self, datagram, address):
        #print "Datagram %s received from %s" % (repr(datagram), repr(address))
        if datagram == 'Server: Ping':
            print "Joined multicast group sucessfully at 228.0.0.5 on port 8005"
            #send data
            self.sendData()
        

reactor.listenMulticast(8005, MulticastPingClient(), listenMultiple=True)
reactor.run()

