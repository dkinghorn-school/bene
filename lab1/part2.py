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



# def part1(config):
# # parameters

#     Sim.scheduler.reset()

#     # setup network
#     net = Network(config)

#     # setup routes
#     n1 = net.get_node('n1')
#     n2 = net.get_node('n2')
#     n3 = net.get_node('n3')
#     n1.add_forwarding_entry(address=n2.get_address('n1'), link=n1.links[0])
#     n1.add_forwarding_entry(address=n3.get_address('n2'), link=n1.links[0])
#     n2.add_forwarding_entry(address=n3.get_address('n2'), link=n2.links[1])
    
#     # setup app
#     d = DelayHandler()
#     net.nodes['n2'].add_protocol(protocol="delay", handler=d)
#     net.nodes['n3'].add_protocol(protocol='delay', handler=d)
#     # send one packet
#     p1 = Packet(destination_address=n2.get_address('n1'), ident=1, protocol='delay', length=1000)
#     Sim.scheduler.add(delay=0, event=p1, handler=n1.send_packet)
    
#     # run the simulation
#     Sim.scheduler.run()

def part1(config):
    Sim.scheduler.reset()

    # setup network
    net = Network(config)

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n3 = net.get_node('n3')
    n1.add_forwarding_entry(address=n2.get_address('n1'), link=n1.links[0])
    n1.add_forwarding_entry(address=n3.get_address('n2'), link=n1.links[0])
    n2.add_forwarding_entry(address=n3.get_address('n2'), link=n2.links[1])
    
    # setup app
    d = DelayHandler()
    net.nodes['n2'].add_protocol(protocol="delay", handler=d)
    net.nodes['n3'].add_protocol(protocol='delay', handler=d)
    # send one packet
    for i in range(0,1000):
        Sim.scheduler.add(delay=0, 
            event = Packet(destination_address=n3.get_address('n2'), ident=i, protocol='delay', length=1000),
            handler=n1.send_packet
        )
    # p1 = Packet(destination_address=n2.get_address('n1'), ident=1, protocol='delay', length=1000)
    # Sim.scheduler.add(delay=0, event=p1, handler=n1.send_packet)
    
    # run the simulation
    Sim.scheduler.run()

def part2(config):
    Sim.scheduler.reset()

    # setup network
    net = Network(config)

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n3 = net.get_node('n3')
    n1.add_forwarding_entry(address=n2.get_address('n1'), link=n1.links[0])
    n1.add_forwarding_entry(address=n3.get_address('n2'), link=n1.links[0])
    n2.add_forwarding_entry(address=n3.get_address('n2'), link=n2.links[1])
    
    # setup app
    d = DelayHandler()
    net.nodes['n2'].add_protocol(protocol="delay", handler=d)
    net.nodes['n3'].add_protocol(protocol='delay', handler=d)
    # send one packet
    for i in range(0,1000):
        Sim.scheduler.add(delay=i * 0.03125,
            event = Packet(destination_address=n3.get_address('n2'), ident=i, protocol='delay', length=1000),
            handler=n1.send_packet
        )
    # p1 = Packet(destination_address=n2.get_address('n1'), ident=1, protocol='delay', length=1000)
    # Sim.scheduler.add(delay=0, event=p1, handler=n1.send_packet)
    
    # run the simulation
    Sim.scheduler.run()

def main():
    # print("part 1 slow")
    # part1('../networks/lab1/3nodes-1.txt')
    # print("part 1 fast")
    # part1('../networks/lab1/3nodes-1b.txt')
    # print("part 2")
    part2('../networks/lab1/3nodes-2.txt')
if __name__ == '__main__':
    main()
