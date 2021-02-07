import math
import random

# GLOBAL VARIABLES
CACHE_SIZE = 2048
M_COEFF = CACHE_SIZE >> 5
MAX_PAGES_BCAST = 2*CACHE_SIZE + random.randint(1, 10)

GHOST_CACHE = [] # empty at first

ONCE_QUEUE = [] # once accessed queue, mru pages
MULTIPLE_QUEUE = [] # multiply accessed queue, mru pages

# Initial utility of both queues
M_QUEUE_UTIL = 0
O_QUEUE_UTIL = 0

INIT_DELAY = 8
NEXT_TRANSMIT = 4
NEXT_REQUEST = 10

def get_tail_size(o_queue, m_queue):
    return min(CACHE_SIZE/M_COEFF, len(o_queue), len(m_queue))

'''
    queue_flag = 0 for once_accessed, 1 for multiply_accessed
'''
def calculate_emergency(queue_flag, distance, size_o, size_m):
    if (distance == 0.0):
        approx_distance = 0.0001
        emerg_1 = math.log(CACHE_SIZE/approx_distance, M_COEFF)
    else:
        emerg_1 = math.log(CACHE_SIZE/distance, M_COEFF)
    if (~queue_flag):
        Q_param = size_m/size_o
    else:
        Q_param = size_o/size_m
    emerg_2 = math.log(Q_param, M_COEFF)

    return (emerg_1, emerg_2)
'''
    hit_flag: "hit" or "replace"
    queue_flag: same as calculate_total_emergency
'''
'''# NOTE: PROBABLY NOT RIGHT, WILL CHECK
'''
def calculate_utility(page_emergency, queue_flag, hit_flag='hit'):
    global O_QUEUE_UTIL
    global M_QUEUE_UTIL

    if (hit_flag == 'hit'):
        if (~queue_flag):
            O_QUEUE_UTIL += page_emergency
        else:
            M_QUEUE_UTIL += page_emergency
    else:
        old_m_queue_util = M_QUEUE_UTIL
        old_o_queue_util = O_QUEUE_UTIL
        M_QUEUE_UTIL = old_m_queue_util*CACHE_SIZE/(old_m_queue_util+old_o_queue_util)
        O_QUEUE_UTIL = old_o_queue_util*CACHE_SIZE/(old_m_queue_util+old_o_queue_util)

def distance2tail(queue, page):
    size = len(queue)
    if (size == 1):
        print("Distance from tail (for small queue) = {}".format(page.time_stamp-queue[-1].time_stamp))
        return (page.time_stamp-queue[-1].time_stamp)
    else:
        print("Distance from tail (for bigger queue with size {}) = {}".format(size, size*(page.time_stamp-queue[-1].time_stamp)/(queue[0].time_stamp - queue[-1].time_stamp)))
        return (size*(page.time_stamp-queue[-1].time_stamp)/(queue[0].time_stamp - queue[-1].time_stamp))

class Page(object):
    def __init__(self, id, time_stamp):
        self.time_stamp = time_stamp
        self.id = id
        self.accessed = 0
        self.isDated = False
    
    def __repr__(self):
        return "id: {}, time_stamp: {}".format(self.id, self.time_stamp)
    
    def __eq__(self, other):
        return self.id == other.id
