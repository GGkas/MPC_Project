import simpy 
import numpy as np
import BroadcastLink
import config as cf
import random
import time

def client_agent(id, env, in_conn):
    random.seed(51)
    requests = []
    requested_page = cf.Page(random.randint(1, cf.MAX_PAGES_BCAST), env.now)
    requests.append(requested_page)
    print("First request: {}".format(requested_page))

    while True:
        page = yield in_conn.get()
        # Block A is accessed
        if (page.id == requested_page.id):
            # print("Found same request! Got page_id = {}".format(page.id))
            if (requested_page in cf.ONCE_QUEUE):
            
                page_idx = cf.ONCE_QUEUE.index(requested_page)
                page_copy = cf.ONCE_QUEUE[page_idx]
                dist = cf.distance2tail(cf.ONCE_QUEUE, page_copy)
                print("Distance of page ({}) from tail is {}".format(page_copy, dist))
                print("Tail size is {}".format(cf.get_tail_size(cf.ONCE_QUEUE, cf.MULTIPLE_QUEUE)))
                if (dist < cf.get_tail_size(cf.ONCE_QUEUE, cf.MULTIPLE_QUEUE)):
                    #NEVER ENTERS HERE
                    emergs = cf.calculate_emergency(0, dist, len(cf.ONCE_QUEUE), len(cf.MULTIPLE_QUEUE))
                    print("Emergency_1 and Emergency_2 values for item in O_Q are [{},{}]".format(emergs[0], emergs[1]))
                    if (emergs[0] >= 1):
                        cf.O_QUEUE_UTIL += emergs[0]
                    if (emergs[1] >= 1):
                        cf.O_QUEUE_UTIL += emergs[1]
                
                # NOTE: we let stamp_m be stamp of head ot m_queue
                if (cf.ONCE_QUEUE[page_idx].accessed == 2):
                    cf.ONCE_QUEUE[page_idx].time_stamp = env.now
                    cf.ONCE_QUEUE[page_idx].accessed = -1
                    page_copy = cf.ONCE_QUEUE[page_idx]
                    del cf.ONCE_QUEUE[page_idx]
                    cf.MULTIPLE_QUEUE.insert(0, page_copy)
                    if (len(cf.MULTIPLE_QUEUE) > cf.CACHE_SIZE):
                        del cf.MULTIPLE_QUEUE[-1]
                
                else:
                    cf.ONCE_QUEUE[page_idx].accessed = 2
                    cf.ONCE_QUEUE[page_idx].time_stamp = env.now
                    cf.ONCE_QUEUE.insert(0, cf.ONCE_QUEUE.pop(page_idx))
            
            elif(requested_page in cf.MULTIPLE_QUEUE):
                
                page_idx = cf.MULTIPLE_QUEUE.index(requested_page)
                page_copy = cf.MULTIPLE_QUEUE[page_idx]
                dist = cf.distance2tail(cf.MULTIPLE_QUEUE, page_copy)

                # print("Tail size is {}".format(cf.get_tail_size(cf.ONCE_QUEUE, cf.MULTIPLE_QUEUE)))
                # print('\n\n')
                # print([i for i in requests if requests.count(i) < 2])
                # print('\n\n')
                # print(cf.ONCE_QUEUE)
                if (dist < cf.get_tail_size(cf.ONCE_QUEUE, cf.MULTIPLE_QUEUE)):
                    # NEVER ENTERS HERE
                    emergs = cf.calculate_emergency(1, dist, len(cf.ONCE_QUEUE), len(cf.MULTIPLE_QUEUE))
                    print("Emergency_1 and Emergency_2 values for item in M_Q are [{},{}]".format(emergs[0], emergs[1]))
                    if (emergs[0] >= 1):
                        cf.M_QUEUE_UTIL += emergs[0]
                    if (emergs[1] >= 1):
                        cf.M_QUEUE_UTIL += emergs[1]
                
                cf.MULTIPLE_QUEUE[page_idx].time_stamp = env.now
                cf.MULTIPLE_QUEUE.insert(0, cf.MULTIPLE_QUEUE.pop(page_idx))
            
            else:
                if (len(cf.ONCE_QUEUE) >= cf.CACHE_SIZE or len(cf.MULTIPLE_QUEUE) >= cf.CACHE_SIZE):
                    Replace(env)   # subroutine
                if (requested_page in cf.GHOST_CACHE):
                    page_idx = cf.GHOST_CACHE.index(requested_page)
                    # print(cf.MULTIPLE_QUEUE)
                    if (len(cf.MULTIPLE_QUEUE) == 0):
                        cf.GHOST_CACHE[page_idx].time_stamp == page.time_stamp
                    else:
                        cf.GHOST_CACHE[page_idx].time_stamp = env.now
                    cf.MULTIPLE_QUEUE.insert(0, cf.GHOST_CACHE.pop(page_idx))
                    # print("Popped a page!")
                # To play little ball, we prefer ghost cache to be smaller than CACHE_SIZE
                elif (requested_page not in cf.GHOST_CACHE and len(cf.GHOST_CACHE) == cf.CACHE_SIZE/4):
                    # print("Ghost cache full!!!")
                    requested_page.accessed += 1
                    cf.ONCE_QUEUE.insert(0, requested_page)
                elif (requested_page not in cf.GHOST_CACHE and len(cf.GHOST_CACHE) < cf.CACHE_SIZE/4):
                    cf.GHOST_CACHE.append(page)
                    # print(cf.ONCE_QUEUE)
                    
            requested_page = cf.Page(random.randint(1, cf.MAX_PAGES_BCAST), env.now)
            requests.append(requested_page)
            print("\n----------- PRINTING ONCE QUEUE -----------\n")
            print(cf.ONCE_QUEUE)
            print("\n----------- PRINTING MULTIPLE QUEUE -----------\n")
            print(cf.MULTIPLE_QUEUE)
            print("{} -> New request id : {}".format(id, requested_page.id))
def server_agent(id, env, out_conn):
    while True:
        yield env.timeout(cf.INIT_DELAY)
        
        for page_id in range(1, cf.MAX_PAGES_BCAST+1):
            # time.sleep(0.5)
            yield env.timeout(cf.NEXT_TRANSMIT)
            page = cf.Page(page_id, env.now)
            out_conn.put(page)
            # print('{} -> Next transmitted page id: {}'.format(id, page.id))

def Replace(env):
    print("ENTERED REPLACE SUBROUTINE")
    cf.M_QUEUE_UTIL = cf.M_QUEUE_UTIL*cf.CACHE_SIZE/(cf.M_QUEUE_UTIL + cf.O_QUEUE_UTIL)
    cf.O_QUEUE_UTIL = cf.O_QUEUE_UTIL*cf.CACHE_SIZE/(cf.M_QUEUE_UTIL + cf.O_QUEUE_UTIL)

    if (len(cf.ONCE_QUEUE) >= int(cf.O_QUEUE_UTIL) or len(cf.MULTIPLE_QUEUE) <= int(cf.M_QUEUE_UTIL)):
        while(True):
            if (cf.ONCE_QUEUE[-1].accessed == 1 or cf.ONCE_QUEUE[-1].isDated):
                cf.ONCE_QUEUE.pop()
                break
            else:
                cf.ONCE_QUEUE[-1].isDated = True
                cf.ONCE_QUEUE[-1].time_stamp = env.now
                cf.ONCE_QUEUE.insert(0, cf.ONCE_QUEUE.pop())
    else:
        cf.MULTIPLE_QUEUE.pop()