from __future__ import print_function

import sys

sys.path.append('..')

from src.sim import Sim
from src.packet import Packet

from networks.network import Network
import random

class DelayHandler(object):
    @staticmethod
    def receive_packet(packet):
        print(("time: ", Sim.scheduler.current_time(),
               "ident: ", packet.ident,
               "created: ", packet.created,
               "elapsedTime: ", Sim.scheduler.current_time() - packet.created,
               "transmission delay: ", packet.transmission_delay,
               "Prop delay: ", packet.propagation_delay,
               "queueing delay: ", packet.queueing_delay))

class ForwardHandler(object):
    @staticmethod
    def receive_packet(packet):
        d = DelayHandler()
        Sim.scheduler.add(delay=0, event=Packet, handler=d)


def part1_1():
    # parameters
    Sim.scheduler.reset()

    # setup network
    net = Network('../networks/lab1/2nodes-1.txt')

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n1.add_forwarding_entry(address=n2.get_address('n1'), link=n1.links[0])
    n2.add_forwarding_entry(address=n1.get_address('n2'), link=n2.links[0])

    # setup app
    d = DelayHandler()
    net.nodes['n2'].add_protocol(protocol="delay", handler=d)

    # send one packet
    p = Packet(destination_address=n2.get_address('n1'), ident=1, protocol='delay', length=1000)
    Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

    # run the simulation
    Sim.scheduler.run()
    
def part1_2():
    # parameters
    Sim.scheduler.reset()

    # setup network
    net = Network('../networks/lab1/2nodes-2.txt')

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n1.add_forwarding_entry(address=n2.get_address('n1'), link=n1.links[0])
    n2.add_forwarding_entry(address=n1.get_address('n2'), link=n2.links[0])

    # setup app
    d = DelayHandler()
    net.nodes['n2'].add_protocol(protocol="delay", handler=d)

    # send one packet
    p = Packet(destination_address=n2.get_address('n1'), ident=1, protocol='delay', length=1000)
    Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

    # run the simulation
    Sim.scheduler.run()

def part1_3():
    # parameters
    Sim.scheduler.reset()

    # setup network
    net = Network('../networks/lab1/2nodes-3.txt')

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n1.add_forwarding_entry(address=n2.get_address('n1'), link=n1.links[0])
    n2.add_forwarding_entry(address=n3.get_address('n2'), link=n2.links[0])

    # setup app
    d = DelayHandler()
    net.nodes['n2'].add_protocol(protocol="delay", handler=d)

    # send one packet
    p1 = Packet(destination_address=n2.get_address('n1'), ident=1, protocol='delay', length=1000)
    Sim.scheduler.add(delay=0, event=p1, handler=n1.send_packet)
    
    p2 = Packet(destination_address=n2.get_address('n1'), ident=2, protocol='delay', length=1000)
    Sim.scheduler.add(delay=0, event=p2, handler=n1.send_packet)
    
    p3 = Packet(destination_address=n2.get_address('n1'), ident=3, protocol='delay', length=1000)
    Sim.scheduler.add(delay=0, event=p3, handler=n1.send_packet)
    
    p4 = Packet(destination_address=n2.get_address('n1'), ident=4, protocol='delay', length=1000)
    Sim.scheduler.add(delay=2, event=p4, handler=n1.send_packet)

    # run the simulation
    Sim.scheduler.run()

def part2_1():
# parameters

    Sim.scheduler.reset()

    # setup network
    net = Network('../networks/lab1/3nodes-1.txt')

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n3 = net.get_node('n3')
    n1.add_forwarding_entry(address=n3.get_address('n1'), link=n1.links[0])
    n1.add_forwarding_entry(address=n3.get_address('n2'), link=n1.links[0])
    n2.add_forwarding_entry(address=n3.get_address('n2'), link=n2.links[0])

    # setup app
    d2 = ForwardHandler()
    net.nodes['n2'].add_protocol(protocol="delay", handler=d2)
    d3 = DelayHandler()
    net.nodes['n3'].add_protocol(protocol="delay", handler=d3)

    # send one packet
    p1 = Packet(destination_address=n3.get_address('n2'), ident=1, protocol='delay', length=1000)
    Sim.scheduler.add(delay=0, event=p1, handler=n1.send_packet)
    
    # p2 = Packet(destination_address=n2.get_address('n1'), ident=2, protocol='delay', length=1000)
    # Sim.scheduler.add(delay=0, event=p2, handler=n1.send_packet)
    
    # p3 = Packet(destination_address=n2.get_address('n1'), ident=3, protocol='delay', length=1000)
    # Sim.scheduler.add(delay=0, event=p3, handler=n1.send_packet)
    
    # p4 = Packet(destination_address=n2.get_address('n1'), ident=4, protocol='delay', length=1000)
    # Sim.scheduler.add(delay=2, event=p4, handler=n1.send_packet)

    # run the simulation
    Sim.scheduler.run()

class Generator(object):
    def __init__(self, node, destination, load, duration):
        self.node = node
        self.load = load
        self.destination = destination
        self.duration = duration
        self.start = 0
        self.ident = 1

    def handle(self, event):
        # quit if done
        now = Sim.scheduler.current_time()
        if (now - self.start) > self.duration:
            return

        # generate a packet
        self.ident += 1
        p = Packet(destination_address=self.destination, ident=self.ident, protocol='delay', length=1000)
        Sim.scheduler.add(delay=0, event=p, handler=self.node.send_packet)
        # schedule the next time we should generate a packet
        Sim.scheduler.add(delay=random.expovariate(self.load), event='generate', handler=self.handle)

def part3():
    Sim.scheduler.reset()
    net = Network('../networks/one-hop.txt')
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    
    n1.add_forwarding_entry(address=n2.get_address('n1'), link=n1.links[0])
    n2.add_forwarding_entry(address=n1.get_address('n2'), link=n2.links[0])

    d = DelayHandler()
    net.nodes['n2'].add_protocol(protocol="delay", handler=d)

    destination = n2.get_address('n1')
    max_rate = 1000000 // (1000 * 8)
    load = .5 * max_rate
    g = Generator(node=n1, destination=destination, load=load, duration=60)
    Sim.scheduler.add(delay=0, event='generate', handler=g.handle)

    Sim.scheduler.run()

def main():
    # print()
    # print( "part 1_1" )
    # print()
    # part1_1()
    # print()
    # print( "part 1_2" )
    # print()
    # part1_2()
    # print()
    # print( "part 1_3" )
    # print()
    # part1_3()
    # part2_1()
    part3()

    # parameters
    # Sim.scheduler.reset()

    # # setup network
    # net = Network('../networks/lab1/2nodes.txt')

    # # setup routes
    # n1 = net.get_node('n1')
    # n2 = net.get_node('n2')
    # n1.add_forwarding_entry(address=n2.get_address('n1'), link=n1.links[0])
    # n2.add_forwarding_entry(address=n1.get_address('n2'), link=n2.links[0])

    # # setup app
    # d = DelayHandler()
    # net.nodes['n2'].add_protocol(protocol="delay", handler=d)

    # # send one packet
    # p = Packet(destination_address=n2.get_address('n1'), ident=1, protocol='delay', length=1000)
    # Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

    # # take the link down
    # Sim.scheduler.add(delay=1, event=None, handler=n1.get_link('n2').down)

    # # send one packet (it won't go through)
    # p = Packet(destination_address=n2.get_address('n1'), ident=1, protocol='delay', length=1000)
    # Sim.scheduler.add(delay=1.1, event=p, handler=n1.send_packet)

    # # bring the link up
    # Sim.scheduler.add(delay=2, event=None, handler=n1.get_link('n2').up)

    # # send one packet (and now it goes through)
    # p = Packet(destination_address=n2.get_address('n1'), ident=1, protocol='delay', length=1000)
    # Sim.scheduler.add(delay=2.1, event=p, handler=n1.send_packet)

    # # run the simulation
    # Sim.scheduler.run()

if __name__ == '__main__':
    main()
