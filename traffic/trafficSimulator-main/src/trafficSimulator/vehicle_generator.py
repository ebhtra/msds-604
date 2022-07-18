from .vehicle import Vehicle
from numpy.random import randint

class VehicleGenerator:
    def __init__(self, sim, config={}):
        self.sim = sim

        # Set default configurations
        self.set_default_config()

        # Update configurations  [i.e. overwrite the default params that were just set]
        for attr, val in config.items():
            setattr(self, attr, val)

        # Calculate properties
        self.init_properties()

    def set_default_config(self):
        """Set default configuration"""
        self.vehicle_rate = 20
        self.vehicles = [
            (1, {})
        ]
        self.last_added_time = 0
        
        self.random_driver = False

    def init_properties(self):
        self.upcoming_vehicle = self.generate_vehicle()
        if self.random_driver:
            drivers = [(22, 7), (20, 6), (18, 5), (16, 4), (14, 3), (12, 2)] # from aggressive to pokey
            driver = randint(len(drivers))
            rv, ra = drivers[driver]
            self.upcoming_vehicle.v_max = rv
            self.upcoming_vehicle.a_max = ra

    def generate_vehicle(self):
        """Uses the first element of the vehicle tuples as weights 
        then draws uniformly according to the normalized weights
        """
        total = sum(pair[0] for pair in self.vehicles)
        r = randint(1, total+1)
        for (weight, config) in self.vehicles:
            r -= weight
            if r <= 0:
                return Vehicle(config)

    def update(self):
        """Add vehicles"""
        if self.sim.t - self.last_added_time >= 60 / self.vehicle_rate:
            # If time elasped after last added vehicle is
            # greater than vehicle_period; generate a vehicle
            road = self.sim.roads[self.upcoming_vehicle.path[0]]      
            if len(road.vehicles) == 0\
               or road.vehicles[-1].x > self.upcoming_vehicle.s0 + self.upcoming_vehicle.l:
                # If there is space for the generated vehicle; add it
                self.upcoming_vehicle.time_added = self.sim.t
                road.vehicles.append(self.upcoming_vehicle)
                # Reset last_added_time and upcoming_vehicle
                self.last_added_time = self.sim.t
            self.upcoming_vehicle = self.generate_vehicle()

