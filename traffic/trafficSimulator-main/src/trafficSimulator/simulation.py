import simpy as sp
from collections import deque
from .road import Road
from copy import deepcopy
from .vehicle_generator import VehicleGenerator
from .traffic_signal import TrafficSignal

class Simulation:
    
    FOREST = (0, 100, 50)  # default car color
    QUEUED_COLOR = (200, 250, 50)  # queued car color
    
    def __init__(self, config={}):
        # Set default configuration
        self.set_default_config()
        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)

    def set_default_config(self):
        self.t = 0.0            # Time keeping
        self.frame_count = 0    # Frame count keeping
        self.dt = 1/100          # Simulation time step
        self.roads = []         # Array to store roads
        self.qzone = 6         # How far from the instersection is considered "stopped and queued"
        self.times = {"LEFT": 3, "STRAIGHT": 2, "RIGHT": 2} # How long does each car need 
        self.generators = []
        self.traffic_signals = []
        
        self.env = sp.Environment()
        self.turn = sp.PriorityResource(self.env, capacity=1)  # one car at a time thru intersection
        self.carlog = deque()  # prioritizing who goes thru intersection when, for simpy environment
        
        self.q = [] # to manage the handoff to simpy at the intersection
        self.blocked_till = 0  # helps avoid some crashes in the intersection
        self.popped = [] # keeping track of who got sent through, and when, and time they need to complete
        
    def create_road(self, start, end):
        road = Road(start, end)
        self.roads.append(road)
        return road

    def create_roads(self, road_list):
        for road in road_list:
            self.create_road(*road)

    def create_gen(self, config={}):
        gen = VehicleGenerator(self, config)
        self.generators.append(gen)
        return gen

    def create_signal(self, roads, config={}):   # called from main run:  sim.create_signal([[0],[1],[2],[3]])
        roads = [[self.roads[i] for i in road_group] for road_group in roads]  # (equals same as above, in my case)
        sig = TrafficSignal(roads, config)
        self.traffic_signals.append(sig)
        return sig

    def next_car(self, road, direction, priority=1, name='carl'):
        
        t_enter = self.t
        
        with self.turn.request(priority=priority) as req:
            #print(f'{name} on road {road} requesting at {t_enter} with priority={priority}')
            yield req
            #print(f'{name} on road {road} entered the intersection at {t_enter}')
            yield self.env.timeout(self.times[direction])
            #print(f'{name} on road {road} left intersection at {env.now}')
            self.carlog.append((self.env.now - t_enter, road))

    
    @property
    def intersection_clear(self):
        return all([len(rd.vehicles) == 0 for rd in self.roads[8:]]) and self.t > self.blocked_till
        # roads 0-7 are the non-intersection ones
               
    
    def start_simpy(self, steps):
        self.env.run(until=steps)
    
    def update(self):
        # Update every road
        for road in self.roads:
            road.update(self.dt)   ## Note that this calls Vehicle.update(vehicle) for each vehicle on each road

        # Add vehicles
        for gen in self.generators:  ## Each road will send its own stochastically generated cars
            gen.update()

        for signal in self.traffic_signals:  
            signal.update(self)
        
        
        # Check roads for new cars in the queue zone
        for i, road in enumerate(self.roads):
            # If road has no vehicles, continue
            if len(road.vehicles) == 0: continue
            # If road has vehicles
            vehicle = road.vehicles[0]
            # If first vehicle is "close enough" to the intersection to join the official queue
            if vehicle.x >= road.length - self.qzone and i < 4:   # roads 0-3 end at the intersection
                if not vehicle.queued:    
                    direction = vehicle.direction
                    self.q.append((self.t, self.times[direction], i, vehicle, direction))   
                    # (t_enter, t_needed, rd #, Veh, dir) tuple added to sim Q
                    
                    vehicle.clr = self.QUEUED_COLOR  # for viz/debugging
                    vehicle.queued = True   # don't repeatedly process the Vehicle
                          
                                    
            # If first vehicle is out of road bounds, update viz
            if vehicle.x > road.length:
                if i < 4: self.blocked_till = self.t + self.times[vehicle.direction]
                # If vehicle has a next road
                if vehicle.current_road_index + 1 < len(vehicle.path):
                    # Update current road to next road
                    vehicle.current_road_index += 1
                    # Create a copy and reset some vehicle properties.  Note that the copy is not "equal to" the original
                    new_vehicle = deepcopy(vehicle)
                    new_vehicle.x = 0
                    new_vehicle.clr = self.FOREST
                    new_vehicle.queued = False   # to turn off blinker, among other things
                    new_vehicle.direction = 'STRAIGHT'  # possibly not needed
                    # Add it to the next road
                    next_road_index = vehicle.path[vehicle.current_road_index]
                    self.roads[next_road_index].vehicles.append(new_vehicle)
                    # Remove it from its road
                    road.vehicles.popleft() 
        # Increment time
        self.t += self.dt
        self.frame_count += 1


    def run(self, steps):
        for _ in range(steps):
            self.update()