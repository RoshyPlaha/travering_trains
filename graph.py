import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, text

from dataclasses import dataclass

@dataclass(eq=True, frozen=True)
class Route:
    entrySignal: str
    exitSignal: str
    tiploc: str# add something if the signal is at a TIPLOC. and then lets add an edge description for it similiar to traversal times
    traversalTime: int

df_route_panel_6 = pd.read_csv('routesPanel6.csv')
df_route_panel_5 = pd.read_csv('routesPanel5.csv')
df_route_panel_4 = pd.read_csv('routesPanel4.csv')
df_route_panel_3 = pd.read_csv('routesPanel3.csv')

routes = set([])
for index, row in df_route_panel_6.iterrows():
    routes.add(Route(row['OriginSignal'], row['Exit'], row['TipLocOriginate'], row['TraversalTimes']))

for index, row in df_route_panel_5.iterrows():
    routes.add(Route(row['OriginSignal'], row['Exit'], row['TipLocOriginate'], row['TraversalTimes']))

for index, row in df_route_panel_4.iterrows():
    routes.add(Route(row['OriginSignal'], row['Exit'], row['TipLocOriginate'], row['TraversalTimes']))

for index, row in df_route_panel_3.iterrows():
    routes.add(Route(row['OriginSignal'], row['Exit'], row['TipLocOriginate'], row['TraversalTimes']))

G = nx.DiGraph()
for route in routes:
    G.add_edge(route.entrySignal, route.exitSignal, isATiploc=route.tiploc, traversalTime=route.traversalTime)


def calculate_shortest_path(entry_signal, exit_signal):
    try:
        return nx.shortest_path(G, entry_signal, exit_signal, weight='traversalTime') # change weight to a function. Going to need make G everytime and and weight to signals in TIPLOCS so it passes through it.
    except Exception as e:
        print("Could not make a path from signals: ", e)
        return 0

def find_previous_signal_to_calculate_shortest_path(result, entry_signal, exit_signal):
    next_signal = exit_signal
    while result == 0:
        # add 2 to entrance signal - to see if the next closest signal can create a path
        next_signal = int(next_signal[1:]) + 2
        print("next number to try: ", next_signal)

        next_signal = 'S' + str(next_signal)
        result = calculate_shortest_path(entry_signal, next_signal)
    return result

entry_signal = 'S444'
exit_signal = 'S220'

result = calculate_shortest_path(entry_signal, exit_signal)
result = find_previous_signal_to_calculate_shortest_path(result, entry_signal, exit_signal)

print(result)


other_result = nx.shortest_path(G, 'S333', 'S439', weight='traversalTime')
print(other_result)


red_shortest_distance_edges = []
for i in range(len(result)):
    try:
        red_shortest_distance_edges.append((result[i], result[i+1]))
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

for node, (x, y) in pos.items(): # this is setting the size of the node font
    text(x, y, node, fontsize=5, ha='center', va='center')

# nx.draw_networkx_labels(G, pos)
nx.draw_networkx_edges(G, pos, edgelist=black_edges, arrows=True)
nx.draw_networkx_edges(G, pos, edgelist=red_shortest_distance_edges, edge_color='r', arrows=True)

# label drawing
# edge_label_time = nx.get_edge_attributes(G, 'traversalTime') # key is edge, pls check for your case
# formatted_edge_labels = {(elem[0], elem[1]):edge_label_time[elem] for elem in edge_label_time} # use this to modify the tuple keyed dict if it has > 2 elements, else ignore
# nx.draw_networkx_edge_labels(G, pos, edge_labels=formatted_edge_labels, font_color='red')
#
# edge_label_tippy = nx.get_edge_attributes(G, 'edge_label_tippy') # key is edge, pls check for your case
# formatted_edge_labels = {(elem[0], elem[1]):edge_label_tippy[elem] for elem in edge_label_tippy} # use this to modify the tuple keyed dict if it has > 2 elements, else ignore
# nx.draw_networkx_edge_labels(G, pos, edge_labels=formatted_edge_labels, font_color='red')

plt.show()
