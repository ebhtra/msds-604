class TrafficSignal:
    def __init__(self, roads, config={}):
        # Initialize roads
        self.roads = roads   # [[0],[1],[2],[3]]
        # Set default configuration
        self.set_default_config()
        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)
        # Calculate properties
        self.init_properties()

    def set_default_config(self):
        self.cycle = [(False, False, False, False),   # Leaving this in to help understand stoplight cycle logic
                      (False, False, False, False),
                      (False, False, False, False),   # This is [[False]*4]*5
                      (False, False, False, False),
                      (False, False, False, False)] # added this cycle to shut down all if needed by index
        
        self.slow_distance = 22  # slow down starting this far from intersection
        self.slow_factor = 0.4  # higher values make the slow zone faster
        self.stop_distance = 7

        self.current_cycle_index = 4 # default to all "stop", and it doesn't matter for stop signs
        self.last_t = 0  
        
        self.signal_history = []  # debugging log

    def init_properties(self):
        for i in range(len(self.roads)):  # [[0],[1],[2],[3]]  len==4, list of lists
            for r in self.roads[i]:
                r.set_traffic_signal(self, i)  # road_0.set_tr_sig(thisTrSig, 0),  road_1.set_tr_sig(thisTrSig, 1), etc
                      
    
    ### Below is where the Road instance finds out if it has the green light. I'm preempting it for stop sign logic.
 
    @property
    def current_cycle(self):
        return self.cycle[self.current_cycle_index] 
    
    
    def update(self, sim):
        
        if sim.q:
            
            if sim.intersection_clear and all([veh[3].stopped for veh in sim.q]):
                sim.q[0][3].push()
                
            elif sim.roads[sim.q[0][2]].length - sim.q[0][3].x < .2 :
                nextcar = sim.q.pop(0) # (t_enter, t_needed, rd #, Veh, dir) tuple from sim Q
                sim.blocked_till = sim.t + nextcar[1]
                #logging (rd #, t_enter, t_needed, t_now, dir)
                sim.popped.append((nextcar[2], nextcar[0], nextcar[1], sim.t, nextcar[4]))  
        


    '''  [original logic, based on alternating stoplights------updates self.current_cycle_index based on time in sim]
    
    def update(self, sim):
        cycle_length = 20   
        k = (sim.t // cycle_length) % 2
        self.current_cycle_index = int(k)
    '''