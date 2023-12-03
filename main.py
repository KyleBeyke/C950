import csv
from heapq import heappop, heappush
from datetime import datetime, timedelta

class Package:
    def __init__(self, package_id, address, city, state, zip_code, deadline, weight, notes=None):
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
    
    def __iter__(self):
        yield 'package_id', self.package_id
        yield 'address', self.address
        yield 'city', self.city
        yield 'state', self.state
        yield 'zip_code', self.zip_code
        yield 'deadline', self.deadline
        yield 'weight', self.weight
        yield 'notes', self.notes
        yield 'delivery_status', self.delivery_status
        yield 'delivery_time', self.delivery_time

class Truck:
    def __init__(self, truck_id, max_capacity=16):
        self.truck_id = truck_id
        self.max_capacity = max_capacity
        self.packages = []

class WGUPS:
    def __init__(self):
        self.trucks = [Truck(1), Truck(2), Truck(3)]  # Three trucks
        self.distance_table = {}
        self.hash_table = {}

    def load_packages(self, file_path):
        with open(file_path, mode='r') as file:
            flag = False
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row[0] == "Package\nID":
                    flag = True
                    print('true')
                if (row[0] != "Package\nID" and flag): 
                    package = Package(*row[:7])
                    print(row)
                    self.insert_into_hash_table(package)

    def load_distance_table(self, filename):
        with open(filename, mode='r', newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)

            header_row_index = next(
                (i for i, row in enumerate(rows) if "DISTANCE BETWEEN HUBS IN MILES" in row),
                None
            )

            if header_row_index is None:
                raise ValueError("Header row not found")

            header = rows[header_row_index][2:]
            self.distance_table = {location: {} for location in header}

            for i, row in enumerate(rows[header_row_index + 1:]):
                origin_address = self.extract_address(row[0])
                for j, distance in enumerate(row[2:]):
                    try:
                        distance_value = float(distance)
                        destination_address = self.extract_address(header[j])
                        self.distance_table[origin_address][destination_address] = distance_value
                    except ValueError:
                        pass

    def insert_into_hash_table(self, package):
        index = hash(package.package_id) % 100
        if index not in self.hash_table:
            self.hash_table[index] = package

    def look_up_package(self, package_id):
        index = hash(package_id) % 100
        if index in self.hash_table:
            package = self.hash_table[index]
            return package
        return None

    def dijkstra(self, start, end):
        distances = {location: float('inf') for location in self.distance_table}
        distances[start] = 0
        previous_nodes = {location: None for location in self.distance_table}

        # Handle case where 'WGUPS Hub' is not present in the distance table
        if start not in self.distance_table or end not in self.distance_table:
            return []

        priority_queue = [(0, start)]

        while priority_queue:
            current_distance, current_node = heappop(priority_queue)

            for neighbor, distance in self.distance_table.get(current_node, {}).items():
                new_distance = current_distance + distance
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous_nodes[neighbor] = current_node
                    heappush(priority_queue, (new_distance, neighbor))

        # Check if end is reachable from start
        if previous_nodes[end] is None:
            return []

        # Retrieve the path from start to end
        path = []
        current_node = end
        while previous_nodes[current_node] is not None:
            path.insert(0, current_node)
            current_node = previous_nodes[current_node]
        path.insert(0, start)

        return path

    def optimize_delivery_routes(self):
        for truck in self.trucks:
            start_location = "WGUPS Hub"
            end_location = "WGUPS Hub"
            optimized_route = self.dijkstra(start_location, end_location)
            truck.packages = self.route_truck_based_on_deadline(truck, optimized_route)

    def route_truck_based_on_deadline(self, truck, optimized_route):
        sorted_packages = sorted(
            [package for index in self.hash_table 
                for package in self.hash_table[index]
                if self.get_package_address(package) in optimized_route],
            key=lambda package: package.deadline
        )

        truck_packages = []
        current_time = datetime.strptime("08:00 AM", "%I:%M %p")

        for package in sorted_packages:
            if current_time < package.deadline * 60 and len(truck_packages) < truck.max_capacity:
                truck.packages.append(package)

                distance_to_package = self.calculate_distance(
                    ["WGUPS Hub", self.get_package_address(package)],
                    "WGUPS Hub"
                )
                if distance_to_package is not None:
                    travel_time = timedelta(hours=distance_to_package / 18)
                    current_time += travel_time
                    current_time += timedelta(minutes=15)  # 15 minutes assumed for delivery

        return truck.packages

    def calculate_distance(self, locations, end_location):
        total_distance = 0

        # Iterate through pairs of consecutive locations in the list
        for start_location, next_location in zip(locations, locations[1:] + [end_location]):
            # Check if locations exist in the distance table
            if start_location in self.distance_table:
                distances_for_start_location = self.distance_table[start_location]
                if next_location in distances_for_start_location:
                    distance = distances_for_start_location[next_location]
                    total_distance += distance
                else:
                    print(f"Missing distance information between {start_location} and {next_location}")
                    print(f"Distances for {start_location}: {distances_for_start_location}")
                    return None  # Return None if distance is missing
            else:
                print(f"Missing distance information for {start_location}")
                print(f"Available locations: {list(self.distance_table.keys())}")
                return None  # Return None if distance is missing

        return total_distance

    def simulate_delivery(self, start_time, end_time, time_interval):
        self.optimize_delivery_routes()

        current_time = start_time
        while current_time <= end_time:
            for truck in self.trucks:
                print(f"\nTruck {truck.truck_id} Status at {current_time.strftime('%Y-%m-%d %I:%M:%S %p')}:")
                self.update_package_statuses(truck, current_time)
                self.update_truck_status(truck, current_time)

            current_time += timedelta(minutes=time_interval)

        # Print the total mileage after all trucks have completed their routes
        self.print_total_mileage()

    def update_package_statuses(self, truck, current_time):
        for package in truck.packages:
            if package.delivery_time is not None:
                delivery_time = datetime.strptime(package.delivery_time, "%Y-%m-%d %I:%M:%S %p")
                if current_time >= delivery_time:
                    package.delivery_status = "Delivered"
                elif current_time >= delivery_time - timedelta(minutes=15):
                    package.delivery_status = "En Route"
                else:
                    package.delivery_status = "At Hub"

                print(f"  Package {package.package_id}: {package.delivery_status} at {package.delivery_time}")

    def update_truck_status(self, truck, current_time):
        # Update truck status here
        print(f"\nTruck {truck.truck_id} Status at {current_time.strftime('%Y-%m-%d %I:%M:%S %p')}:")
        for package in truck.packages:
            print(f"  Package {package.package_id}: {package.delivery_status} at {package.delivery_time}")

        # Print the total mileage after the truck has completed its route
        print(f"\nTotal Mileage Traveled by Truck {truck.truck_id}: {self.calculate_total_mileage(truck):.2f} miles")

    def calculate_total_mileage(self, truck):
        return sum(
            self.calculate_distance(["WGUPS Hub", self.get_package_address(package)] + ["WGUPS Hub"])
            for package in truck.packages
        )

    def print_total_mileage(self):
        total_mileage = sum(
            self.calculate_distance(["WGUPS Hub", self.get_package_address(package)] + ["WGUPS Hub"])
            for truck in self.trucks for package in truck.packages
        )

        print(f"\nTotal Mileage Traveled by All Trucks: {total_mileage:.2f} miles")

    def get_package_address(self, package):
        if isinstance(package, Package):
            return f"{package.address},{package.city},{package.state},{package.zip_code}"
        elif isinstance(package, tuple) and len(package) >= 5:
            # Ensure the tuple has at least 5 elements before accessing them
            return f"{package[1]},{package[2]},{package[3]},{package[4]}"
        else:
            return None  # Return None for unsupported types or insufficient data

    def extract_address(self, full_address):
        # Extract only the relevant part of the address
        parts = full_address.split(",")
        return ",".join(parts[0:4])

    def check_total_mileage(self):
        print("\nChecking Total Mileage:")
        for truck in self.trucks:
            total_mileage = self.calculate_total_mileage(truck)
            print(f"Truck {truck.truck_id}: {total_mileage:.2f} miles")

    def run_checks(self):
        self.check_total_mileage()

# Create an instance of WGUPS
wgups = WGUPS()

# Load packages and distance table
wgups.load_packages("package_details.csv")
wgups.load_distance_table("distance_table.csv")

package_9_wrong_address = Package("9", "Wrong Address", "Salt Lake City", "UT", "84111", "10:20 AM", "2", "At Hub")
wgups.insert_into_hash_table(package_9_wrong_address)

# Look up a package by ID
package_9 = wgups.look_up_package("9")
if package_9:
    package_9.delivery_status = "At Hub"
    package_9.delivery_time = None

# Set the delivery time for package #9 after the correction
package_9_corrected = wgups.look_up_package("9")
if package_9_corrected:
    package_9_corrected.delivery_time = "1900-01-01 10:20:00 AM"

# Scenario 1: Between 8:35 a.m. and 9:25 a.m.
start_time_1 = datetime.strptime("08:35 AM", "%I:%M %p")
end_time_1 = datetime.strptime("09:25 AM", "%I:%M %p")
wgups.simulate_delivery(start_time_1, end_time_1, time_interval=5)

# Scenario 2: Between 9:35 a.m. and 10:25 a.m.
start_time_2 = datetime.strptime("09:35 AM", "%I:%M %p")
end_time_2 = datetime.strptime("10:25 AM", "%I:%M %p")
wgups.simulate_delivery(start_time_2, end_time_2, time_interval=5)

# Scenario 3: Between 12:03 p.m. and 1:12 p.m.
start_time_3 = datetime.strptime("12:03 PM", "%I:%M %p")
end_time_3 = datetime.strptime("01:12 PM", "%I:%M %p")
wgups.simulate_delivery(start_time_3, end_time_3, time_interval=5)
