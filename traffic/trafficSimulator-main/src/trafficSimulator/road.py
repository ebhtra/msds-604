from scipy.spatial import distance
from collections import deque

class Road:
    def __init__(self, start, end):
        self.start = start
        self.end = end

        self.vehicles = deque()

        self.init_properties()

    def init_properties(self):
        self.length = distance.euclidean(self.start, self.end)
        self.angle_sin = (self.end[1]-self.start[1]) / self.length  # not for the 4-way stop sign simulation
        self.angle_cos = (self.end[0]-self.start[0]) / self.length
        self.has_traffic_signal = False

    def set_traffic_signal(self, signal, group):
        self.traffic_signal = signal
        self.traffic_signal_group = group
        self.has_traffic_signal = True

        
    #### Here's where the traffic signal can be changed:  ##################################    
        ### The update(self) func below this property uses it to know whether to release the first car on the road.
            ### This property, in turn, references the @current_cycle property of the TrafficSignal
    @property
    def traffic_signal_state(self):
        if self.has_traffic_signal:
            i = self.traffic_signal_group
            return self.traffic_signal.current_cycle[i]
        return True
        

    def update(self, dt):
        n = len(self.vehicles)

        if n > 0:
            # Update first vehicle
            self.vehicles[0].update(None, dt)
            # Update other vehicles
            for i in range(1, n):  # "Stage 2" vehicles, dependent on the car in front of them
                lead = self.vehicles[i-1]
                self.vehicles[i].update(lead, dt)

             # Check for traffic signal (doesn't apply to stop signs, which don't toggle cleanly enough to use signals)
            if self.traffic_signal_state:
                # If traffic signal is green or doesn't exist
                # Then let vehicles past
                self.vehicles[0].unstop()
                for vehicle in self.vehicles:
                    vehicle.unslow()
            else:
                # If traffic signal is red (this is the part the stop signs use)
                
                if self.vehicles[0].x >= self.length - self.traffic_signal.slow_distance:
                    # Slow vehicles in slowing zone
                    self.vehicles[0].slow(self.traffic_signal.slow_factor*self.vehicles[0]._v_max)
                if self.vehicles[0].x >= self.length - self.traffic_signal.stop_distance and\
                   self.vehicles[0].x <= self.length - self.traffic_signal.stop_distance / 5 and\
                   not self.vehicles[0].go:
                    # Stop vehicles in the stop zone
                    self.vehicles[0].stop()
                  
