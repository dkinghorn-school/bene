from __future__ import print_function

import sys

sys.path.append('..')

from src.sim import Sim
from src.packet import Packet

from networks.network import Network
import random

# WHenever you get an ack call slide
# fixed window size
# 