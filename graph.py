import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, text
import json
from os import listdir
from os.path import isfile, join

from dataclasses import dataclass

@dataclass(eq=True, frozen=True)
class Route:
    entrySignal: str
    exitSignal: str
    tiploc: str# add something if the signal is at a TIPLOC. and then lets add an edge description for it similiar to traversal times
    traversalTime: int

@dataclass()
class Tiploc:
    station: str
    signal: str
    arrival_time: str
    departure_time: str

@dataclass()
class Journey:
    headcode: str
    tiplocs: list

def load_panel_data(routes):
    df_route_panel_6 = pd.read_csv('routesPanel6.csv')
    df_route_panel_5 = pd.read_csv('routesPanel5.csv')
    df_route_panel_4 = pd.read_csv('routesPanel4.csv')
    df_route_panel_3 = pd.read_csv('routesPanel3.csv')

    for index, row in df_route_panel_6.iterrows():
        routes.add(Route(row['OriginSignal'], row['Exit'], row['TipLocOriginate'], row['TraversalTimes']))

    for index, row in df_route_panel_5.iterrows():
        routes.add(Route(row['OriginSignal'], row['Exit'], row['TipLocOriginate'], row['TraversalTimes']))

    for index, row in df_route_panel_4.iterrows():
        routes.add(Route(row['OriginSignal'], row['Exit'], row['TipLocOriginate'], row['TraversalTimes']))

    for index, row in df_route_panel_3.iterrows():
        routes.add(Route(row['OriginSignal'], row['Exit'], row['TipLocOriginate'], row['TraversalTimes']))
    return routes

def weight_calculator(u, v, d):
    return d['traversalTime']

def calculate_shortest_path(entry_signal, exit_signal):
    try:
        return nx.shortest_path(G, entry_signal, exit_signal, weight=weight_calculator) # change weight to a function. Going to need make G everytime and and weight to signals in TIPLOCS so it passes through it.
    except Exception as e:
        print("Could not make a path from signals: ", e)
        return 0

def find_previous_signal_to_calculate_shortest_path(result, entry_signal, exit_signal):
    next_signal = exit_signal
    while result == 0:
        print('Warning - could not get to next TIPLOC for signal: ', exit_signal, ' there is a data error')
        # add 2 to entrance signal - to see if the next closest signal can create a path
        next_signal = int(next_signal[1:]) + 2
        print("The next previous signal to try to connect to is: ", next_signal)

        next_signal = 'S' + str(next_signal)
        result = calculate_shortest_path(entry_signal, next_signal)
    return result


def setup_infrastructure(graph):
    routes = set([])
    routes = load_panel_data(routes)

    for route in routes:
        graph.add_edge(route.entrySignal, route.exitSignal, isATiploc=route.tiploc, traversalTime=route.traversalTime)


def load_trains_journey(filename):
    with open('trains_dir/train_journey_1.json') as f:
      loaded = json.load(f)
      tiplocs = []
      for i in loaded['tiplocs']:
          tiplocs.append(Tiploc(i['station'], i['signal'], i['arrival_time'], i['departure_time']))
    return Journey(loaded['headcode'], tiplocs)

def load_train_file_names(path_to_trains_dir):
    onlyfiles = [f for f in listdir(path_to_trains_dir) if isfile(join(path_to_trains_dir, f))]
    return onlyfiles


def generate_path(loaded_train):
    # calculate paths from TipLoc to TipLoc in journey - as opposed to just whole journey
    paths = []
    flattened_routes = []
    for i in range(len(loaded_train.tiplocs) - 1):
        entrance_signal, exit_signal = loaded_train.tiplocs[i].signal, loaded_train.tiplocs[i + 1].signal
        entrance_tiploc, exit_tiploc = loaded_train.tiplocs[i].station, loaded_train.tiplocs[i + 1].station
        print('Signals to be used that map to TipLocs %s - %s are %s - %s: ' %(entrance_tiploc, exit_tiploc, entrance_signal, exit_signal))
        result_to_next_tiploc = calculate_shortest_path(entrance_signal, exit_signal)
        print('Routes found between signals are: ', result_to_next_tiploc)
        result = find_previous_signal_to_calculate_shortest_path(result_to_next_tiploc, entrance_signal, exit_signal)
        for r in result:
            if r not in flattened_routes:
                flattened_routes.append(r)
        path = {
            'TipLocs':
                {
                    'start_tiploc_name': train.tiplocs[i].station,
                    'end_tiploc_name': train.tiplocs[i + 1].station,
                    'preferred_path': result,
                    'alternative_path': [],
                }
        }
        paths.append(path)

    return paths, flattened_routes


G = nx.DiGraph()
setup_infrastructure(graph=G)# in the future, based off what infrastructure is available, we can turn on / off nodes

filenames = load_train_file_names('trains_dir')
print('There are this many file names to generate paths for: ', len(filenames))

for filename in filenames:
    train = load_trains_journey(filename)
    print('> > > >  New train %s goes from / to %s, which are Tiplocs from / to %s' %(train.headcode, (train.tiplocs[0].signal, train.tiplocs[-1].signal), (train.tiplocs[0].station, train.tiplocs[-1].station)))
    tiploc_paths, all_routes = generate_path(train)

    print('< < < < Finished pathing for train ', train.headcode)

    red_shortest_distance_edges = []
    for i in range(len(all_routes) - 1):
        try:
            red_shortest_distance_edges.append((all_routes[i], all_routes[i + 1]))
        except:
            print('index failure')

    # Specify the edges you want here
    edge_colours = ['black' if not edge in red_shortest_distance_edges else 'red'
                    for edge in G.edges()]
    black_edges = [edge for edge in G.edges() if edge not in red_shortest_distance_edges]

    # Need to create a layout when doing
    # separate calls to draw nodes and edges
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'),
                           node_color='yellow', node_size=25)

    for node, (x, y) in pos.items():  # this is setting the size of the node font
        text(x, y, node, fontsize=5, ha='center', va='center')

    # nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, edgelist=black_edges, arrows=True)
    nx.draw_networkx_edges(G, pos, edgelist=red_shortest_distance_edges, edge_color='r', arrows=True)

    plt.show()

# other_result = nx.shortest_path(G, 'S333', 'S439', weight=weight_calculator)
# print('ignore ', other_result)


# label drawing
# edge_label_time = nx.get_edge_attributes(G, 'traversalTime') # key is edge, pls check for your case
# formatted_edge_labels = {(elem[0], elem[1]):edge_label_time[elem] for elem in edge_label_time} # use this to modify the tuple keyed dict if it has > 2 elements, else ignore
# nx.draw_networkx_edge_labels(G, pos, edge_labels=formatted_edge_labels, font_color='red')
#
# edge_label_tippy = nx.get_edge_attributes(G, 'edge_label_tippy') # key is edge, pls check for your case
# formatted_edge_labels = {(elem[0], elem[1]):edge_label_tippy[elem] for elem in edge_label_tippy} # use this to modify the tuple keyed dict if it has > 2 elements, else ignore
# nx.draw_networkx_edge_labels(G, pos, edge_labels=formatted_edge_labels, font_color='red')

