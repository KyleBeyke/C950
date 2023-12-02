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

    def load_distance_data(self, filepath = 'distance_table.csv'):
        sources = []
        # Read CSV file and populate the hash table
        with open(filepath, 'r') as file:
            flag = False
            reader = csv.reader(file, dialect='excel')
            for row in reader:
                if row[0] == 'DISTANCE BETWEEN HUBS IN MILES':
                    flag = True
                    for source in row[2:31]:
                        # Find the index of the newline character
                        newline_index = source.find('\n')
                        # Disregard content before the newline character
                        substring_after_newline = source[newline_index + 1:]
                        # Keep the characters until the comma
                        address_before_comma = substring_after_newline.split(',')[0]
                        # Strip any leading or trailing whitespace
                        source = address_before_comma.strip()
                        sources.append(source)
                elif flag:
                    destination = row[0]
                    # Find the index of the newline character
                    newline_index = destination.find('\n')
                    # Disregard content before the newline character
                    substring_after_newline = destination[newline_index + 1:]
                    # Keep the characters until the comma
                    address_before_comma = substring_after_newline.split(',')[0]
                    # Strip any trailing or leading whitespace
                    destination = address_before_comma.strip()
                    index = 0
                    for source in sources:
                        try:
                            distance = row[2 + index]
                            float_value = float(distance)
                            if float_value > 0:
                                # Check if the source exists
                                if source in self.distance_table:
                                    # If source exists, append to the existing dictionary
                                    self.distance_table[source][destination] = float_value
                                else:
                                    # If source doesn't exist, add a new entry for the source
                                    self.distance_table[source] = {destination: float_value}
                            else:
                              pass
                        except ValueError:
                            pass
                        index += 1
                else:
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

def main():
    # Create an instance of WGUPS
    wgups = WGUPS()

    # Load packages and distance table
    wgups.load_packages("package_details.csv")
    wgups.load_distance_data("distance_table.csv")
    print(wgups.distance_table)

if __name__ == "__main__":
    main()


#             source = row['Source']
#             destination = row['Destination']
#             distance = float(row['Distance'])  # Convert distance to a numerical value if needed

#             # If source is not in the graph, add it
#             if source not in graph:
#                 graph[source] = {}

#             # Add the destination and distance to the source vertex
#             graph[source][destination] = distance

#             # If the graph is undirected, add the reverse edge
#             if destination not in graph:
#                 graph[destination] = {}
#             graph[destination][source] = distance

#     return graph

# # Example CSV file (replace 'your_file.csv' with the actual file path)
# file_path = 'your_file.csv'

# # Load distance data into a hash table (dictionary)
# distance_hash_table = load_distance_data(file_path)

# # Print the resulting hash table
# print(distance_hash_table)