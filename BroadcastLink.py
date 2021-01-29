import simpy as sim
import numpy as np
import config

class BroadcastLink(object):
    
    def __init__(self, env, capacity=np.inf):
        self.env = env
        self.capacity = capacity
        self.pipes = [] # all broadcast links with clients

    def put(self, page):
        if not self.pipes:
            raise RuntimeError("No broadcast links!")
        events = [store.put(page) for store in self.pipes]
        return self.env.all_of(events)
    
    def get_output_conn(self):
        """Get a new output connection for this broadcast pipe.

        The return value is a :class:`~simpy.resources.store.Store`.

        """
        pipe = sim.Store(self.env, capacity=self.capacity)
        self.pipes.append(pipe)
        return pipe