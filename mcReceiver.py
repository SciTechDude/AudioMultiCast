from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from ast import literal_eval
import pyaudio
import wave
import time

# PyAudio configuration
SIZE_PACKAGE = 1024
CHUNK = 1024
CHANNELS = 1
RATE = 10240
INPUT = True
FORMAT = pyaudio.paInt16
CHUNK_COUNT = 0
p = pyaudio.PyAudio()
stream = p.open(format=8,
                channels=2,
                rate=44100,
                output=True)


class MulticastPingPong(DatagramProtocol):

    def __init__(self):
       self.CHUNK_COUNT = 0

    def startProtocol(self):
        """
        Called after protocol has started listening.
        """
        # Set the TTL=1 so multicast will NOT cross router hops:
        self.transport.setTTL(1)
        # Join a specific multicast group:
        self.transport.joinGroup("228.0.0.5")

    def datagramReceived(self, datagram, address):
        #print "Datagram %s received from %s" % (repr(datagram), repr(address))
        if datagram == "Server: Ping":
            #self.transport.write("Server: Pong", address)
            print "Joined multicast group sucessfully at 228.0.0.5 "
        else:
            #print "data received {}".format(type(datagram))
            #print "Playing  chunk {}".format(self.CHUNK_COUNT)
            stream.write(datagram)
            self.CHUNK_COUNT += 1
            


# We use listenMultiple=True so that we can run MulticastServer.py and
# MulticastClient.py on same machine:
reactor.listenMulticast(8005, MulticastPingPong(),
                        listenMultiple=True)
reactor.run()
