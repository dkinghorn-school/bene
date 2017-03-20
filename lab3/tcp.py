
import sys

sys.path.append('../src')

from src.buffer import SendBuffer, ReceiveBuffer
from src.connection import Connection
from src.sim import Sim
from src.tcppacket import TCPPacket


class TCP(Connection):
    """ A TCP connection between two hosts."""

    def __init__(self, transport, source_address, source_port,
                 destination_address, destination_port, app=None,
                 window=1000, fastRetransmit=True, initial_threshold=100000,drop=[]):
        Connection.__init__(self, transport, source_address, source_port,
                            destination_address, destination_port, app)

        # -- Sender functionality
        self.threshold = initial_threshold
        # maximum segment size, in bytes
        self.mss = 1000
        # send window; represents the total number of bytes that may
        # be outstanding at one time
        self.window = self.mss
        self.increment = 0
        # send buffer
        self.send_buffer = SendBuffer()
        # plot sequence numbers
        self.plot_sequence_header()
        self.plot_congestion_header()
        # packets to drop
        self.drop = drop
        self.dropped = []
        # largest sequence number that has been ACKed so far; represents
        # the next sequence number the client expects to receive
        self.sequence = 0
        # retransmission timer
        self.timer = None
        # timeout duration in seconds
        self.timeout = 1

        # -- Receiver functionality
        self.fastRetransmit = fastRetransmit
        self.sameAcks = 0
        # receive buffer
        self.receive_buffer = ReceiveBuffer()
        # ack number to send; represents the largest in-order sequence
        # number not yet received
        self.ack = 0

    def trace(self, message):
        """ Print debugging messages. """
        Sim.trace("TCP", message)

    def plot_sequence_header(self):
        if self.node.hostname =='n1':
            Sim.plot('sequence.csv','Time,Sequence Number,Event\n')

    def plot_sequence(self,sequence,event):
        if self.node.hostname =='n1':
            Sim.plot('sequence.csv','%s,%s,%s\n' % (Sim.scheduler.current_time(),sequence,event))
            self.plot_congestion()

    def plot_congestion_header(self):
        if self.node.hostname =='n1':
            Sim.plot('cwnd.csv','Time,Congestion Window,\n')

    def plot_congestion(self):
            if self.node.hostname =='n1':
                Sim.plot('cwnd.csv','%s,%s\n' % (Sim.scheduler.current_time(),self.window))

    def receive_packet(self, packet):
        """ Receive a packet from the network layer. """
        if packet.ack_number > 0:
            # handle ACK
            self.handle_ack(packet)
        if packet.length > 0:
            # handle data
            self.handle_data(packet)

    ''' Sender '''
# make sure timer hasn't been added already
    def send(self, data):
        """ Send data on the connection. Called by the application. This
            code currently sends all data immediately. """
        self.send_buffer.put(data)
        self.sendFullWindow()
        self.maybe_start_timer()

    def send_packet(self, data, sequence):
        packet = TCPPacket(source_address=self.source_address,
                           source_port=self.source_port,
                           destination_address=self.destination_address,
                           destination_port=self.destination_port,
                           body=data,
                           sequence=sequence, ack_number=self.ack)
        if sequence in self.drop and not sequence in self.dropped:
            self.dropped.append(sequence)
            self.plot_sequence(sequence,'drop')
            self.trace("%s (%d) dropping TCP segment to %d for %d" % (
                self.node.hostname, self.source_address, self.destination_address, packet.sequence))
            return

        # send the packet
        self.plot_sequence(sequence,'send')
        self.trace("%s (%d) sending TCP segment to %d for %d" % (
            self.node.hostname, self.source_address, self.destination_address, packet.sequence))
        self.transport.send_packet(packet)

# TODO: might have broken this by commenting it out.
        # # set a timer
        # if not self.timer:
        #     self.timer = Sim.scheduler.add(delay=self.timeout, event='retransmit', handler=self.retransmit)
    def increase_window(self, bytes_acked):
        if self.window < self.threshold:
            self.increment = self.increment + bytes_acked
            
        else:
            self.increment = self.increment + self.mss * bytes_acked / self.window
        self.set_window_from_cwnd()

    def handle_ack(self, packet):
        """ Handle an incoming ACK. """
        self.trace("%s (%d) received TCP ACK from %d for %d current seq %d currentWindow %d currentInc %d" % (
            self.node.hostname, packet.destination_address, packet.source_address, packet.ack_number, self.sequence, self.window, self.increment))
        self.plot_sequence(packet.ack_number - 1000,'ack')
        if packet.ack_number > self.sequence:
            self.increase_window(packet.ack_number - self.sequence)
            self.sequence = packet.ack_number
            self.cancel_timer()
            self.send_buffer.slide(self.sequence)
            self.maybe_start_timer()
            self.sendFullWindow()
            self.sameAcks = 1
        elif self.fastRetransmit and packet.ack_number == self.sequence:
            self.sameAcks += 1
            print("same acks", self.sameAcks)
            if self.sameAcks == 4:
                self.plot_sequence(self.sequence,'fast retransmit')
                self.trace('retransmitting')
                self.cancel_timer()
                self.resetWindow()

    def set_window_from_cwnd(self):
        if self.increment >= self.mss:
            self.increment = self.increment - self.mss
            self.window = self.window + self.mss

    def lower_threshold(self):
        self.threshold = max(self.mss, self.window / 2)
        self.increment = 0
        self.window = self.mss

    def resetWindow(self):
        """ resets the window and sends all data available in the window """
        self.lower_threshold()
        (data, sequence) = self.send_buffer.resend(self.mss)
        if len(data) > 0:
            self.maybe_start_timer()
            self.send_packet(data, sequence)

    def sendFullWindow(self):
        """ sends all data left in the window """
        while self.send_buffer.outstanding() < self.window:
            (data, seq) = self.send_buffer.get(self.mss)
            if len(data) == 0:
                return
            self.send_packet(data, seq)

# modify this code
    def retransmit(self, event):
        """ Retransmit data. """
        self.trace("%s (%d) retransmission timer fired" % (self.node.hostname, self.source_address))
        self.timer = None
        self.resetWindow()

# should work
    def cancel_timer(self):
        """ Cancel the timer. """
        # self.trace('canceling timer')
        if not self.timer:
            return
        Sim.scheduler.cancel(self.timer)
        self.timer = None

    def maybe_start_timer(self):
        """ Starts timer if it doesn't exist """
        # self.trace('maybe starting timer')
        if not self.timer and self.send_buffer.dataRemaining():
            # self.trace('starting timer')
            self.timer = Sim.scheduler.add(delay=self.timeout, event='retransmit', handler=self.retransmit)
        else:
            self.trace('timer not started')
    ''' Receiver '''
# get this to work correctly
    def handle_data(self, packet):
        """ Handle incoming data. This code currently gives all data to
            the application, regardless of whether it is in order, and sends
            an ACK."""
        self.trace("%s (%d) received TCP segment from %d for %d" % (
            self.node.hostname, packet.destination_address, packet.source_address, packet.sequence))
        self.receive_buffer.put(packet.body, packet.sequence)
        (data, seq) = self.receive_buffer.get()
        if len(data) > 0:
            self.app.receive_data(data)
            self.ack += len(data)
        self.send_ack()

# should work
    def send_ack(self):
        """ Send an ack. """
        packet = TCPPacket(source_address=self.source_address,
                           source_port=self.source_port,
                           destination_address=self.destination_address,
                           destination_port=self.destination_port,
                           sequence=self.sequence, ack_number=self.ack)
        # send the packet
        self.transport.send_packet(packet)
        self.trace("%s (%d) sending TCP ACK to %d for %d" % (
            self.node.hostname, self.source_address, self.destination_address, packet.ack_number))
        
