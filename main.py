# main.py
# Student ID: 000629736

import csv
from heapq import heappop, heappush
from datetime import datetime, timedelta

class Package:
    def __init__(self, package_id, address, city, state, zip_code, deadline, weight, notes):
        self.package_id = package_id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = weight
        self.notes = notes
        self.delivery_status = "At Hub"
        self.delivery_time = None

class Truck:
    def __init__(self, truck_id):
        self.truck_id = truck_id
        self.packages = []

class WGUPS:
    def __init__(self):
        self.packages = []
        self.trucks = [Truck(1), Truck(2), Truck(3)]  # Three trucks
        self.distance_table = {}
        self.hash_table = {}

    def load_packages(self, file_path):
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row and row[0] != "WGUPS Package File":
                    package = Package(*row[:8])
                    self.packages.append(package)
                    self.insert_into_hash_table(package)

    def load_distance_table(self, file_path):
        with open(file_path, mode='r') as file:
            reader = csv.reader(file)
            rows = list(reader)

            # Extract hub names and distances
            hub_names = rows[0][1:]
            for row in rows[1:]:
                hub_name = row[1]
                distances = {hub_names[i]: float(row[i + 1]) for i in range(len(hub_names))}
                self.distance_table[hub_name] = distances

    def insert_into_hash_table(self, package):
        index = hash(package.package_id) % 100
        if index not in self.hash_table:
            self.hash_table[index] = []
        self.hash_table[index].append(package)

    def look_up_package(self, package_id):
        index = hash(package_id) % 100
        if index in self.hash_table:
            for package in self.hash_table[index]:
                if package.package_id == package_id:
                    return package
        return None

    def dijkstra(self, start, end):
        # Dijkstra's algorithm implementation
        distances = {location: float('inf') for location in self.distance_table}
        distances[start] = 0
        previous_nodes = {location: None for location in self.distance_table}
        priority_queue = [(0, start)]

        while priority_queue:
            current_distance, current_node = heappop(priority_queue)

            for neighbor, distance in self.distance_table[current_node].items():
                new_distance = current_distance + distance
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous_nodes[neighbor] = current_node
                    heappush(priority_queue, (new_distance, neighbor))

        # Retrieve the path from start to end
        path = []
        current_node = end
        while previous_nodes[current_node] is not None:
            path.insert(0, current_node)
            current_node = previous_nodes[current_node]
        path.insert(0, start)

        return path

    def optimize_delivery_routes(self):
        # Dijkstra's Algorithm for each truck
        for truck in self.trucks:
            start_location = "WGUPS Hub"
            end_location = "WGUPS Hub"  # Truck returns to the hub after deliveries
            optimized_route = self.dijkstra(start_location, end_location)

            # Assign the optimized route to the truck
            truck.packages = self.route_truck_based_on_deadline(truck, optimized_route)

    def route_truck_based_on_deadline(self, truck, optimized_route):
        # Sort packages based on deadline for each truck
        sorted_packages = sorted(
            [package for package in self.packages if package.address in optimized_route],
            key=lambda package: package.deadline
        )

        # Assign packages to the truck based on deadline constraints
        truck_packages = []
        current_time = 8 * 60  # Start time at 8:00 a.m. in minutes

        for package in sorted_packages:
            if current_time < package.deadline * 60:
                truck.packages.append(package)
                current_time += self.calculate_distance(
                    optimized_route[optimized_route.index(package.address):]
                ) / 18 * 60  # Update time based on travel distance

        return truck.packages

    def calculate_distance(self, locations):
        total_distance = 0
        for i in range(len(locations) - 1):
            total_distance += self.distance_table[locations[i]][locations[i + 1]]
        return total_distance

    def simulate_delivery(self):
        # Optimize delivery routes
        self.optimize_delivery_routes()

        # Initialize delivery time and status for each package
        delivery_times = {package.package_id: None for package in self.packages}
        delivery_statuses = {package.package_id: "At Hub" for package in self.packages}

        # Simulate package delivery
        for truck in self.trucks:
            current_time = datetime.strptime("08:00 AM", "%I:%M %p")
            for package in truck.packages:
                distance_to_package = self.distance_table["WGUPS Hub"][package.address]
                travel_time = timedelta(hours=distance_to_package / 18)  # Assuming average speed of 18 mph

                # Update delivery status and time
                delivery_statuses[package.package_id] = "En Route"
                delivery_times[package.package_id] = current_time.strftime("%I:%M %p")

                # Simulate travel time
                current_time += travel_time

                # Update delivery status and time upon arrival
                delivery_statuses[package.package_id] = "Delivered"
                delivery_times[package.package_id] = current_time.strftime("%I:%M %p")

        return delivery_statuses, delivery_times

    # Function to print delivery status at specific times
    def print_delivery_status(self, delivery_statuses, delivery_times):
        print("Delivery Status:")
        for package_id, status in delivery_statuses.items():
            delivery_time = delivery_times[package_id]
            if delivery_time is not None:
                print(f"Package {package_id}: {status} at {delivery_time}")
            else:
                print(f"Package {package_id}: {status}")
        print()

# Load distance table and package details from CSV files
wgups = WGUPS()
wgups.load_packages("package_details.csv")
wgups.load_distance_table("distance_table.csv")

# Simulate delivery at different time points and print delivery status
simulation_times = ["08:35 AM", "09:35 AM", "12:03 PM"]
for sim_time in simulation_times:
    current_simulation_time = datetime.strptime(sim_time, "%I:%M %p")
    delivery_statuses, delivery_times = wgups.simulate_delivery()
    wgups.print_delivery_status(delivery_statuses, delivery_times)
