import csv
from heapq import heappop, heappush
from datetime import datetime, timedelta

class Package:
    def __init__(self, package_id, address, city, state, zip_code, deadline, weight, notes=None):
        # Initialize Package attributes with provided values
        self.package_id = package_id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = weight
        self.notes = notes
        self.location = "Hub"  # Initial location is set to "Hub"
        self.delivery_time = None  # Initialize delivery time as None

    def __iter__(self):
        # Define an iterator to yield key-value pairs for object attributes
        yield 'package_id', self.package_id
        yield 'address', self.address
        yield 'city', self.city
        yield 'state', self.state
        yield 'zip_code', self.zip_code
        yield 'deadline', self.deadline
        yield 'weight', self.weight
        yield 'notes', self.notes
        yield 'location', self.location
        yield 'delivery_time', self.delivery_time


class Truck:
    def __init__(self, truck_id, max_capacity=16):
        # Initialize Truck attributes with provided values
        self.truck_id = truck_id
        self.max_capacity = max_capacity
        self.packages = []  # List to store packages loaded onto the truck


class WGUPS:
    def __init__(self):
        # Initialize the WGUPS (World-Wide Package Unloading System)
        self.trucks = [Truck(1), Truck(2), Truck(3)]  # Three trucks are created
        self.distance_table = {}  # Dictionary to store distances between hubs
        self.hash_table = {}  # Dictionary to store packages hashed by package_id


    def load_packages(self, file_path):
        # Open the CSV file in read mode
        with open(file_path, mode='r') as file:
            # Initialize a flag to identify the start of package data
            flag = False
            # Create a CSV reader object
            csv_reader = csv.reader(file)
            
            # Iterate through each row in the CSV file
            for row in csv_reader:
                # Check if the current row indicates the start of package data
                if row[0] == "Package\nID":
                    # Set the flag to True when the start is found
                    flag = True
                    print('true')
                
                # Check if the flag is True and the current row is not a header
                if (row[0] != "Package\nID" and flag):
                    # Create a Package object with the data from the row
                    package = Package(*row[:7])
                    
                    # Print the attributes of the Package object
                    print(*package)
                    
                    # Insert the Package object into the hash table
                    self.insert_into_hash_table(package)


    def load_distance_data(self, filepath='distance_table.csv'):
        # List to store source values
        sources = []

        # Read CSV file and populate the hash table
        with open(filepath, 'r') as file:
            flag = False
            reader = csv.reader(file, dialect='excel')
            
            # Iterate through each row in the CSV file
            for row in reader:
                # Check if the current row is the header row
                if row[0] == 'DISTANCE BETWEEN HUBS IN MILES':
                    flag = True
                    
                    # Iterate through sources in the row (from index 2 to 30)
                    for source in row[2:31]:
                        # Split the string at newline characters, take the second part
                        # Split the result at commas, take the first part
                        # Strip any leading or trailing whitespace and append to the list
                        sources.append(source.split('\n')[1].split(',')[0].strip())
                elif flag:
                    # Split the string at newline characters, take the second part
                    # Split the result at commas, take the first part
                    # Strip any leading or trailing whitespace and assign to 'destination'
                    destination = row[0].split('\n')[1].split(',')[0].strip()
                    index = 0
                    
                    # Iterate through each source
                    for source in sources:
                        try:
                            distance = row[2 + index]
                            float_value = float(distance)
                            
                            # Check if the distance is greater than 0
                            if float_value > 0:
                                # Check if the source exists in the distance_table
                                if source in self.distance_table:
                                    # If source exists, append to the existing dictionary
                                    self.distance_table[source][destination] = float_value
                                else:
                                    # If source doesn't exist, add a new entry for the source
                                    self.distance_table[source] = {destination: float_value}
                            else:
                                # Handle case where distance is not greater than 0
                                pass
                        except ValueError:
                            # Handle case where conversion to float fails
                            pass
                        index += 1
                else:
                    # Skip rows until the header row is found
                    pass


    def insert_into_hash_table(self, package):
        # Use package_id as the key for hashing
        key = package.package_id
        index = hash(key) % 100
        
        # Check if the index exists in the hash_table
        if index not in self.hash_table:
            self.hash_table[index] = {key: package}
        else:
            # If the index exists, check if the key exists
            if key in self.hash_table[index]:
                # Handle collision by chaining (using a list to store multiple values at the same index)
                self.hash_table[index][key].append(package)
            else:
                self.hash_table[index][key] = package

    def look_up_package(self, address):

        for index in self.hash_table:
            for package_id, package in self.hash_table[index].items():
                # Check if the address matches
                if package.address == address:
                    ([]).append(package)

        # Return the list of matching packages
        return []

def main():
    # Create an instance of WGUPS
    wgups = WGUPS()

    # Load packages and distance table
    wgups.load_packages("package_details.csv")
    wgups.load_distance_data("distance_table.csv")
    print(wgups.distance_table)

if __name__ == "__main__":
    main()
