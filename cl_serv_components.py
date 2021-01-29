import simpy 
import numpy as np
import BroadcastLink
import config as cf
import random

def client_agent(id, env, in_conn):
    random.seed(51)
    requests = []
    requested_page_id = random.randint(1, cf.MAX_PAGES_BCAST)
    requests.append(requested_page_id)
    print("First request: {}".format(requested_page_id))
    idx = 0
    while True:
        page = yield in_conn.get()
        # Block A is accessed
        if (page.id == requested_page_id):
            # print("Found same request! Got page_id = {}".format(page.id))
            requested_page_id = random.randint(1, cf.MAX_PAGES_BCAST)
            requests.append(requested_page_id)
            print("{} -> New request id : {}".format(id, requested_page_id))
        else:
            # capturing the missed pages
            if (idx == cf.CACHE_SIZE-1):
                idx = 0
            else:
                cf.GHOST_CACHE.insert(idx, page)
                idx += 1
        if (page in cf.ONCE_QUEUE):
            
            page_idx = cf.ONCE_QUEUE.index(page)
            dist = cf.distance2tail(cf.ONCE_QUEUE, page)
            
            if (dist < cf.get_tail_size(cf.ONCE_QUEUE, cf.MULTIPLE_QUEUE)):
                emergs = cf.calculate_emergency(0, dist, len(cf.ONCE_QUEUE), len(cf.MULTIPLE_QUEUE))
                if (emergs[0] >= 1):
                    cf.O_QUEUE_UTIL += emergs[0]
                if (emergs[1] >= 1):
                    cf.O_QUEUE_UTIL += emergs[1]
            
            # NOTE: we let stamp_m be stamp of head ot m_queue
            if (cf.ONCE_QUEUE[page_idx].accessed == 2):
                cf.ONCE_QUEUE[page_idx].time_stamp = cf.MULTIPLE_QUEUE[0].time_stamp
                cf.ONCE_QUEUE[page_idx].accessed = -1
                page_copy = cf.ONCE_QUEUE[page_idx]
                del cf.ONCE_QUEUE[page_idx]
                cf.MULTIPLE_QUEUE.insert(0, page_copy)
                if (len(cf.MULTIPLE_QUEUE) > cf.CACHE_SIZE):
                    del cf.MULTIPLE_QUEUE[-1]
            
            else:
                cf.ONCE_QUEUE[page_idx].accessed = 2
                cf.ONCE_QUEUE[page_idx].time_stamp = page.time_stamp
                cf.ONCE_QUEUE.insert(0, cf.ONCE_QUEUE.pop(page_idx))
        
        elif(page in cf.MULTIPLE_QUEUE):
            
            page_idx = cf.MULTIPLE_QUEUE.index(page)
            dist = cf.distance2tail(cf.MULTIPLE_QUEUE, page)

            if (dist < cf.get_tail_size(cf.ONCE_QUEUE, cf.MULTIPLE_QUEUE)):
                emergs = cf.calculate_emergency(1, dist, len(cf.ONCE_QUEUE), len(cf.MULTIPLE_QUEUE))
                if (emergs[0] >= 1):
                    cf.M_QUEUE_UTIL += emergs[0]
                if (emergs[1] >= 1):
                    cf.M_QUEUE_UTIL += emergs[1]
            
            cf.MULTIPLE_QUEUE[page_idx].time_stamp = page.time_stamp
            cf.MULTIPLE_QUEUE.insert(0, cf.MULTIPLE_QUEUE.pop(page_idx))
        
        else:
            if (len(cf.ONCE_QUEUE) >= cf.CACHE_SIZE or len(cf.MULTIPLE_QUEUE) >= cf.CACHE_SIZE):
                Replace()   # subroutine
            if (page in cf.GHOST_CACHE):
                page_idx = cf.GHOST_CACHE.index(page)
                cf.GHOST_CACHE[page_idx].time_stamp = cf.MULTIPLE_QUEUE[0].time_stamp
                cf.MULTIPLE_QUEUE.insert(0, cf.GHOST_CACHE.pop(page_idx))
            else:
                page_idx = cf.GHOST_CACHE.index(page)
                cf.GHOST_CACHE[page_idx].time_stamp = cf.ONCE_QUEUE[0].time_stamp
                cf.ONCE_QUEUE.insert(0, cf.GHOST_CACHE.pop(page_idx))

def server_agent(id, env, out_conn):
    while True:
        yield env.timeout(cf.INIT_DELAY)
        
        for page_id in range(1, cf.MAX_PAGES_BCAST+1):
            yield env.timeout(cf.NEXT_TRANSMIT)
            page = cf.Page(env.now, page_id)
            out_conn.put(page)
            print('{} -> Next transmitted page id: {}'.format(id, page.id))

def Replace():
    pass