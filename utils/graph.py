import networkx as nx
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import heapq
import itertools
import numpy as np

def dijkstra(graph, start, end):
    distances = {node: float('inf') for node in graph.nodes()}
    distances[start] = 0
    heap = [(0, start)]
    while heap:
        (current_distance, current_node) = heapq.heappop(heap)
        if current_node == end:
            break
        if current_distance > distances[current_node]:
            continue
        for neighbor, attr in graph[current_node].items():
            distance = current_distance + attr['weight']
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(heap, (distance, neighbor))
    return distances[end]

def dijkstra_on_scenarios(scenarios, connections, start_node, end_node):
    dijkstra_outcome = []
    for idx, i in enumerate(scenarios):
        scenario_connections = []
        for jdx, j in enumerate(connections):
            j_l = list(j)
            j_l.append(i[jdx])
            scenario_connections.append(j_l)
        G = nx.Graph()
        G.add_weighted_edges_from(scenario_connections)
        scenario_dijkstra_coutcome = {'idx': idx, 'Dijkstra outcome':dijkstra(G, start_node, end_node)}
        dijkstra_outcome.append(scenario_dijkstra_coutcome)
    return dijkstra_outcome

def get_weights_interval(list1):
    start,stop = list1[0], list1[1]
    # interval = range(start, stop+1)
    interval = [list1[0],list1[1]]
    result = list(interval) 
    return result

def generate_scenarios(list_of_edges_weights):
    list_of_edges_weights_interval = []
    for i in list_of_edges_weights:
        list_of_edges_weights_interval.append(get_weights_interval(i))
    result = list(itertools.product(*list_of_edges_weights_interval))
    return result

def get_cost(scenarios):
    costs = []
    for i in scenarios:
        costs.append(sum(i))
    return costs

def compare_cost_djikstra(costs, min_path):
    delta = []
    for i in costs:
        delta.append(i - min_path['Dijkstra outcome'])
    return delta

def max_min_regret_for_action(costs):
    max_regret = max(costs)
    min_regret = min(costs)
    return max_regret, min_regret

def connections_of_node(node, connections):
    con = []
    for connection in connections:
        if connection[0] == node:
            con.append(connection[1])
        elif connection[1] == node:
            con.append(connection[0])
    return con


def find_all_routes(start_node, end_node, connections):
    routes = []
    visited = set()

    def dfs(node, route):
        visited.add(node)
        route.append(node)
        if node == end_node:
            routes.append(route[:])
        else:
            for conn in connections_of_node(node, connections):
                if conn not in visited:
                    dfs(conn, route)

        route.pop()
        visited.remove(node)

    dfs(start_node, [])
    return routes