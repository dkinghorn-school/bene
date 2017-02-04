from __future__ import print_function

import sys

sys.path.append('..')

from src.sim import Sim
from src.packet import Packet

from networks.network import Network
import random

queueLengths = []
class DelayHandler(object):
    @staticmethod
    def receive_packet(packet):
        global queueLengths 
        queueLengths = queueLengths + [packet.queueing_delay]
        # print(("time: ", Sim.scheduler.current_time(),
        #        "ident: ", packet.ident,
        #        "created: ", packet.created,
        #        "elapsedTime: ", Sim.scheduler.current_time() - packet.created,
        #        "transmission delay: ", packet.transmission_delay,
        #        "Prop delay: ", packet.propagation_delay,
        #        "queueing delay: ", packet.queueing_delay))


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

def part3(load):
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
    load = load * max_rate
    g = Generator(node=n1, destination=destination, load=load, duration=60)
    Sim.scheduler.add(delay=0, event='generate', handler=g.handle)

    Sim.scheduler.run()

def getAverageQueue():
    global queueLengths
    length = len(queueLengths)
    total = 0
    for l in queueLengths:
        total = total + l

    average = total/length
    queueLengths = []
    return average

def save(fileName, value):
    with open(fileName, 'w') as f:
        f.write(value)

def findForLoad(load):
    part3(load)
    average = getAverageQueue()
    save('./queue/{}.txt'.format(str(load)), '{} {}'.format(str(load),str(average)))
def main():
    # part3(.5)
    # average = getAverageQueue()
    # save('./queue/05', '.5 ' + str(average))

    # part3(.5)
    # average = getAverageQueue()
    # save('./queue/05', '.5 ' + str(average))
    findForLoad(.5)
    for i in range(1,10):
        findForLoad(i/10.0)

    findForLoad(.95)
    findForLoad(.98)

if __name__ == '__main__':
    main()
