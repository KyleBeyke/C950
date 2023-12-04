import csv, re
import heapq
from datetime import datetime, timedelta

class Package:
    def __init__(self, package_id, address, city, state, zip_code, deadline, weight, notes=None):
        # Initialize Package attributes with provided values
        self.package_id = package_id
        self.address = address.upper()
        self.city = city.upper()
        self.state = state.upper()
        self.zip_code = zip_code
        self.deadline = deadline.upper()
        self.weight = weight
        self.notes = notes
        self.location = "Hub"  # Initial location is set to "Hub"
        self.no_load_before = None  # Initialize load time as None
        self.required_truck = None  # Initialize required truck as None
        self.package_accompaniment = None  # Initialize required package accompaniments


class Truck:
    def __init__(self, truck_id, max_capacity=16):
        # Initialize Truck attributes with provided values
        self.truck_id = truck_id
        self.max_capacity = max_capacity
        self.packages = set()  # Set to store package ids for packages loaded onto the truck


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
                    package = Package(*row[:8])
                    
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
                        # Strip any leading or trailing whitespace, convert to uppercase, and append to the list
                        sources.append(source.split('\n')[1].split(',')[0].strip().upper())

                    # Create the 'Source' key in distance_table and initialize it as an empty dictionary
                    self.distance_table['Source'] = {}
                elif flag:
                    # Split the string at newline characters, take the second part
                    # Split the result at commas, take the first part
                    # Strip any leading or trailing whitespace, convert to uppercase, and assign to 'destination'
                    destination = row[0].split('\n')[1].split(',')[0].strip().upper()
                    index = 0

                    # Iterate through each source
                    for source in sources:
                        try:
                            distance = row[2 + index]
                            float_value = float(distance)

                            # Check if the distance is greater than 0
                            if float_value > 0:
                                # Append the distance to the 'Source' key in distance_table
                                self.distance_table['Source'].setdefault(source, {})[destination] = float_value

                                # Add symmetric entry for destination to source with the same distance
                                self.distance_table['Source'].setdefault(destination, {})[source] = float_value
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
        # List to store matching packages
        matching_packages = []

        for index in self.hash_table:
            for package_id, package in self.hash_table[index].items():
                # Check if the address matches (case-insensitive)
                if package.address.upper() == address.upper():
                    matching_packages.append(package)

        # Return the list of matching packages
        return matching_packages

    def print_all_packages(self):
        # Iterate through each index in the hash table
        for index in self.hash_table:
            # Iterate through each package_id and package in the current index
            for package_id, package in self.hash_table[index].items():
                # Print information for each package
                print(f"Package ID: {package.package_id}")
                print(f"Address: {package.address}")
                print(f"City: {package.city}")
                print(f"State: {package.state}")
                print(f"Zip Code: {package.zip_code}")
                print(f"Deadline: {package.deadline}")
                print(f"Weight: {package.weight}")
                print(f"Notes: {package.notes}")
                print(f"Location: {package.location}")
                print(f"No load before: {package.no_load_before}")
                print(f"Required Truck: {package.required_truck}")
                print(f"Package must accompany: {package.package_accompaniment}")
                print("---")  # Separation between packages

    def get_all_package_addresses(self):
        """
        Return a set of all package addresses from the hash table.
        """
        all_addresses = []

        for index in self.hash_table:
            for package_id, package in self.hash_table[index].items():
                address = package.address
                if address:
                    all_addresses.append(address)

        return all_addresses

    def get_all_packages(self):
        """
        Return a list of all packages
        """
        all_packages = []
        
        for index in self.hash_table:
            for package in self.hash_table[index].items():
                if package:
                    all_packages.append(package)
        
        return all_packages

    def confirm_matching_addresses(self):
        """
        Check to make sure all address of packages have matches in the distance
        table and return those that do not with partial matches if present
        """
        # Create sets to store unique sources, destinations, and missing addresses
        sources = set()
        destinations = set()
        missing_addresses = set()

        # Iterate through keys in the 'Source' column of the distance_table
        for key in self.distance_table['Source'].keys():
            sources.add(key)

        # Iterate through values (dictionaries) in the 'Source' column of the distance_table
        for value in self.distance_table['Source'].values():
            # Iterate through keys in each dictionary (representing destinations)
            for key in value.keys():
                destinations.add(key)

        # Check for sources that are not found in destinations
        for source in sources:
            if source not in destinations:
                # Print a message and add the missing source to the set
                print(source + ': this source has no matching destination in distance table.')
                missing_addresses.add(source)
            else:
                pass  # Source found in destinations, no action needed

        # Get all unique addresses from the package_table
        addresses_set = set( self.get_all_package_addresses())

        # Check for package addresses that are not found in distance_table
        for address in addresses_set:
            if address not in sources:
                # Print a message and add the missing address to the set
                print(address + ': this package address not found in distance table.')
                missing_addresses.add(address)
                
                # Compare common words in the address and source for potential partial match
                for source in sources:
                    source_words = source.split()
                    address_words = address.split()
                    common_words = []
                    for word in source_words:
                        if word in address_words:
                            common_words.append(word)
                    
                    # If more than 2 common words, consider it a partial match
                    if len(common_words) > 2:
                        print('PARTIAL MATCH: ' + address + ' : ' + source)
                        # Look up package ID for the package with the bad address
                        packages = self.look_up_package(address)
                        # Update it to the partial match source address
                        # Add confirmation message
                        for package in packages:
                            self.edit_package_attribute(package.package_id, 'address', source)
                            print(f"New address {package.address}")
            else:
                pass  # Address found in sources, no action needed

        # Return the set of unique missing addresses
        return missing_addresses
    
    def extract_delayed_time(self, text):
        # Check if the string contains 'Delayed on flight'
        if 'Delayed on flight' in text:
            # Define a regex pattern to match time in the format hh:mm am/pm
            time_pattern = re.compile(r'(\d{1,2}:\d{2} [APMapm]{2})')

            # Search for the time pattern in the text
            match = time_pattern.search(text)
            if match:
                # Return the extracted time
                return match.group(1)

        # Return None if 'Delayed on flight' is not found or no match is found
        return None

    def extract_truck_id(self, text):
        # Check if the string contains 'Can only be on truck'
        if 'Can only be on truck' in text:
            # Extract the numerical truck id using regex
            truck_id_match = re.search(r'\d+', text)

            if truck_id_match:
                # Return the extracted numerical truck id
                return int(truck_id_match.group())

        # Return None if 'Can only be on truck' is not found or no match is found
        return None

    def extract_package_ids(self, text):
        # Check if the string contains 'Must be delivered with'
        if 'Must be delivered with' in text:
            # Extract comma-delimited numerical package ids using regex
            package_ids_match = re.search(r'\d+(,\s*\d+)*', text)

            if package_ids_match:
                # Split the matched string by commas and convert to a list of integers
                return [int(package_id) for package_id in package_ids_match.group().split(',')]

        # Return an empty list if 'Must be delivered with' is not found or no match is found
        return None
    
    def edit_package_attribute(self, package_id, attribute_name, new_value):
        # Use package_id as the key for hashing
        key = package_id
        index = hash(key) % 100

        # Check if the index exists in the hash_table
        if index in self.hash_table and key in self.hash_table[index]:
            # Get the package from the hash table
            package = self.hash_table[index][key]
            # Check if the attribute exists in the package
            if hasattr(package, attribute_name):
                # Update the attribute with the new value
                setattr(package, attribute_name, new_value)
            else:
                print(f"Error: Package does not have attribute '{attribute_name}'")
        else:
            print(f"Error: Package with package_id '{package_id}' not found in the hash table")


    def update_packages_with_notes(self):
        """
        Make changes to package attributes based on package notes
        """
        for index in self.hash_table:
            for package_id, package in self.hash_table[index].items():
                note = package.notes

                # Extract and update 'no_load_before' attribute
                if note is not None:
                    try:
                        no_load_before = self.extract_delayed_time(note.strip())
                        self.edit_package_attribute(package_id, 'no_load_before', no_load_before)
                    except TypeError as e:
                        pass

                    # Extract and update 'required_truck' attribute
                    try:
                        required_truck = self.extract_truck_id(note)
                        self.edit_package_attribute(package_id, 'required_truck', required_truck)
                    except TypeError as e:
                        pass

                    # Extract and update 'package_accompaniment' attribute
                    try:
                        package_accompaniment = self.extract_package_ids(note)
                        self.edit_package_attribute(package_id, 'package_accompaniment', package_accompaniment)
                    except TypeError as e:
                        pass
        
    def optimize_delivery_route(self):
        """
        Use Dijkstra's algorithm to optimize the delivery route of packages.
        Returns a list of package IDs in the optimal delivery order.
        """
        hub_address = "4001 SOUTH 700 EAST"  # Hub address

        # Get all package addresses
        all_addresses = self.get_all_package_addresses()

        # Initialize distance and previous dictionaries for Dijkstra's algorithm
        distances = {address: float('inf') for address in all_addresses}
        previous = {address: None for address in all_addresses}
        distances[hub_address] = 0

        # Priority queue for Dijkstra's algorithm
        priority_queue = [(0, hub_address)]

        while priority_queue:
            current_distance, current_address = heapq.heappop(priority_queue)

            if current_distance > distances[current_address]:
                continue

            for neighbor, weight in self.distance_table['Source'][current_address].items():
                new_distance = current_distance + weight
                try:
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous[neighbor] = current_address
                        heapq.heappush(priority_queue, (new_distance, neighbor))
                except KeyError as e:
                    print(f"Error: {e} while looking up distance in distance table")

        # Reconstruct the optimal route by backtracking from the destination to the hub
        optimal_route = []
        for address in all_addresses:
            current_address = address
            while current_address != hub_address:
                optimal_route.append(current_address)
                current_address = previous[current_address]

        # Reverse the route to get the starting from the hub
        optimal_route.reverse()

        # package_idsConvert addresses to package IDs
        package_ids = []
        for address in optimal_route:
            try:
                matching_packages = self.look_up_package(address)
                if matching_packages:
                    package_ids.extend(package.package_id for package in matching_packages)
            except KeyError as e:
                print(f"Error: {e} while matching addresses in package table")    

        return package_ids  # Return the package IDs



def main():
    """
    Function containing the main body of the program
    """
    # Create an instance of WGUPS
    wgups = WGUPS()
    # Load packages and distance table
    wgups.load_packages("package_data.csv")
    wgups.load_distance_data("distance_table.csv")
    # print(wgups.distance_table)
    # print(*wgups.look_up_package('410 S STATE ST'))
    missing_addresses = wgups.confirm_matching_addresses()
    print(missing_addresses)
    packages = wgups.get_all_packages()
    wgups.update_packages_with_notes()
    # Print all packages after updates
    # wgups.print_all_packages()
    print(wgups.optimize_delivery_route())


if __name__ == "__main__":
    main()
