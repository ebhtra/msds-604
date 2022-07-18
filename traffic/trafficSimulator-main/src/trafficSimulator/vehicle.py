import numpy as np

class Vehicle:
    def __init__(self, config={}):
        # Set default configuration
        self.set_default_config()

        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)

        # Calculate properties
        self.init_properties()

    def set_default_config(self):    
        self.l = 4    # length of Veh
        self.s0 = 4   # minimum desired distance between the Veh and the one in front of it
        self.T = 1    # reaction time of the Veh
        self.v_max = 15  # this driver's maximum velocity
        self.a_max = 4   # this driver's max acceleration
        self.b_max = 4   # amount of deceleration the driver will tolerate

        self.path = []
        self.current_road_index = 0
        self.direction = 'STRAIGHT'

        self.x = 0
        self.v = self.v_max
        self.a = 0
        self.go = False # needed to make final push thru intersection sometimes
        self.stopped = False  # toggles the "Intelligent Driver" acceleration mode.
        self.queued = False  # to only allow a Veh to be queued once
        self.clr = (0, 100, 50)  # default car color "FOREST"

    def init_properties(self):   # the physics behind this driver's motions
        self.sqrt_ab = 2*np.sqrt(self.a_max*self.b_max)
        self._v_max = self.v_max

    def update(self, lead, dt):
        if self.go: 
            self.unstop() # should already be unstopped, but just in case
        # Update position and velocity
        if self.v + self.a*dt < 0:
            self.x -= 1/2*self.v*self.v/self.a
            self.v = 0
        else:
            self.v += self.a*dt
            self.x += self.v*dt + self.a*dt*dt/2
        
        # Update acceleration
        alpha = 0
        if lead:
            delta_x = lead.x - self.x - lead.l
            delta_v = self.v - lead.v

            alpha = (self.s0 + max(0, self.T*self.v + delta_v*self.v/self.sqrt_ab)) / delta_x

        self.a = self.a_max * (1-(self.v/self.v_max)**4 - alpha**2)

        if self.stopped: 
            self.a = -self.b_max*self.v/self.v_max
   
    def push(self):   # only way to get some drivers through the intersection sometimes
        self.go = True
        self.v = self.v_max
        self.stopped = False
    
    def stop(self):
        self.stopped = True

    def unstop(self):
        self.stopped = False

    def slow(self, v):
        self.v_max = v

    def unslow(self):
        self.v_max = self._v_max
        

