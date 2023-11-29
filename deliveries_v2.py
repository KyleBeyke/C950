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

def load_distance_data(filepath = 'distance_table.csv'):
    # Initialize an empty hash table (dictionary)
    graph = {}

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
                    source = substring_after_newline.strip()
                    graph['Source'] = source
            elif flag:
                destination = row[0]
                # # Find the index of the newline character
                newline_index = destination.find('\n')
                # # Disregard content before the newline character
                substring_after_newline = destination[newline_index + 1:]
                # # Keep the characters until the comma
                destination = substring_after_newline.strip()
                destination = destination.split(',')[0]
                index = 0
                for source in graph['Source']:
                    print(source)
                    graph['Destination'] = destination
                    distance = row[2 + index]
                    try:
                        float_value = float(obj)
                        if float_value > 0:
                            graph[destination] = distance
                        else:
                            graph[destination] = None
                    except ValueError:
                        graph[destination] = None
                    graph[destination] = distance
                    index += 1
            else:
                pass
    return graph

graph = load_distance_data()
for i in graph['Source']:
    print(graph)


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