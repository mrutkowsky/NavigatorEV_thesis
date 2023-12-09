from utils.graph import * 
import base64
from io import BytesIO
from datetime import datetime
import random
import string
import os

def generate_unique_filename():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_chars = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
    return f"plot_{timestamp}_{random_chars}.png"

def add_edge_distances_and_set_random_chargers(amount_of_nodes_with_chargers, edge_list, edge_distance, nodes, node_charger):
    for edge in edge_list:
        edge_distance[edge] = (edge_list[edge][0]+edge_list[edge][1])/2
    for node in nodes:
        random_num = random.randint(0,1000)/1000
        if random_num > amount_of_nodes_with_chargers:
            node_charger[node] = False
        else:
            node_charger[node] = True

def display_path_with_range(graph_connections, title, charging_info, connections, edge_list, edge_distance, node_charger):
    plt.close()
    filename = generate_unique_filename()
    filepath = 'static/' + filename
    type_range = True
    G = nx.Graph()
    pos = nx.spring_layout(G, seed=7)  # positions for all nodes - seed for reproducibility
    G, pos, connections = add_display_path_info(G, pos, connections, graph_connections, edge_list, edge_distance, type_range)
    G.clear()
    for node in node_charger:
        if node_charger[node]:
            G.add_node(node)

    nx.draw_networkx_nodes(G, pos, node_size=700, node_color="darkgreen")
    ax = plt.gca()
    ax.margins(0.08)
    plt.title(f"{title}")
    plt.axis("off")
    plt.tight_layout()

    plt.savefig(filepath, format="png")
    plt.close()

    return filename


def add_nodes_with_connections(nodes, connections, edge_list, nodes_number, connections_number, min_travel_time, max_travel_time, min_travel_time_difference, max_travel_time_difference):
    char = "A"
    # Add nodes (names are letters in alphabetic order)
    for i in range(nodes_number):
        nodes.append(char)
        char = chr(ord(char)+1)

    # Connect nodes randomly and assign them random values
    for _ in range(connections_number):
        random_num1 = 0
        random_num2 = 0
        random_num3 = random.randint(min_travel_time,max_travel_time)
        random_num4 = random.randint(min_travel_time_difference,max_travel_time_difference) + random_num3
        correct_number = False
        while not correct_number:
            random_num1 = random.randint(0,nodes_number-1)
            random_num2 = random.randint(0,nodes_number-1)
            if random_num2 != random_num1 and (nodes[random_num1],nodes[random_num2]) not in connections and (nodes[random_num2],nodes[random_num1]) not in connections:
                correct_number = True

        if nodes[random_num1]<nodes[random_num2]:
            connections.append((nodes[random_num1],nodes[random_num2]))
            edge_list[(nodes[random_num1],nodes[random_num2])] = (random_num3,random_num4)
        else:
            connections.append((nodes[random_num2],nodes[random_num1]))
            edge_list[(nodes[random_num2],nodes[random_num1])] = (random_num3,random_num4)


def show_bruteforce_info(route_node_scenarios, route_scenarios, compare_cost, min_regret, max_regret):
        print("Path of the route")
        print(route_node_scenarios)
        print("All possible configurations of the route path")
        print(route_scenarios)
        print("Difference between best path and all of the route scenarios")
        print(compare_cost)
        print(f"Min Regret of route {min_regret}")
        print(f"Max Regret of route {max_regret}")
        print()

def brutforce_without_range(start_node, end_node, connections, scenarios, edge_list):
    all_routes = find_all_routes(start_node, end_node, connections)
    dijkstra_scenarios = dijkstra_on_scenarios(scenarios,connections, start_node, end_node)
    min_path = min(dijkstra_scenarios, key=lambda x: x['Dijkstra outcome'])
    regret_results = {}
    for route in all_routes:
        route_node_scenarios = []
        weights_of_scenario = []
        for i in range(len(route)-1):
            route_node_scenarios.append((route[i], route[i+1]))
            if (route[i], route[i+1]) in edge_list:
                weights_of_scenario.append(list(edge_list[(route[i], route[i+1])]))
            else:
                weights_of_scenario.append(list(edge_list[(route[i+1], route[i])]))

        route_scenarios = generate_scenarios(weights_of_scenario)
        compare_costs = compare_cost_djikstra(get_cost(route_scenarios), min_path)
        min_regret, max_regret = max_min_regret_for_action(compare_costs)
        regret_results[str(route)] = [min_regret, max_regret]
        show_bruteforce_info(route_node_scenarios, route_scenarios, compare_costs, min_regret, max_regret)

    return all_routes, regret_results


def minmax_regret_range(start_node, end_node, connections, scenarios, edge_list, vehicle_range, edge_distance, node_charger):
    all_routes = find_all_routes(start_node, end_node, connections)
    dijkstra_scenarios = dijkstra_on_scenarios(scenarios,connections, start_node, end_node)
    min_path = min(dijkstra_scenarios, key=lambda x: x['Dijkstra outcome'])
    regret_results = {}
    charging_route_info = {}
    for route in all_routes:
        possible_route_scenario = check_route_if_possible(route, vehicle_range, edge_distance, node_charger)
        if not possible_route_scenario:
            continue
        route_node_scenarios = []
        weights_of_scenario = []
        for i in range(len(route)-1):
            route_node_scenarios.append((route[i], route[i+1]))
            if (route[i], route[i+1]) in edge_list:
                weights_of_scenario.append(list(edge_list[(route[i], route[i+1])]))
            else:
                weights_of_scenario.append(list(edge_list[(route[i+1], route[i])]))
        charging_info_temp = show_minimal_charging(route, vehicle_range, node_charger, edge_list, edge_distance)
        charging_route_info[str(route)] = charging_info_temp
        route_scenarios = generate_scenarios(weights_of_scenario)
        compare_costs = compare_cost_djikstra(get_cost(route_scenarios), min_path)
        max_regret, min_regret = max_min_regret_for_action(compare_costs)
        regret_results[str(route)] = [min_regret, max_regret]
        show_bruteforce_info(route_node_scenarios, route_scenarios, compare_costs, min_regret, max_regret)
    return all_routes, regret_results, charging_route_info

def check_route_if_possible(route, vehicle_range, edge_distance, node_charger):
    print("Route")
    print(route)
    segments = []
    for i in range(len(route)-1):
            segments.append((route[i], route[i+1]))

    print(f"segments {segments}")
    max_range = vehicle_range
    print(segments)
    distance_since_last_charging = []
    for segment in segments:
        if segment in edge_distance:
            vehicle_range -= edge_distance[segment]
            if vehicle_range < 0:
                return False
            if node_charger[segment[1]]:
                vehicle_range = max_range
                distance_since_last_charging.append(0)
            else:
                distance_since_last_charging.append(edge_distance[segment])
        else:
            segment = (segment[1], segment[0])
            vehicle_range -= edge_distance[segment]
            if vehicle_range < 0:
                return False
            if node_charger[segment[1]]:
                vehicle_range = max_range
                distance_since_last_charging.append(0)
            else:
                distance_since_last_charging.append(edge_distance[segment])

        print(f"Segment:{segment}, distance: {vehicle_range}")

    print("=======================")
    print(f"Distance since last charging {distance_since_last_charging}")
    return True

def show_minimal_charging(route, vehicle_range, node_charger, edge_list, edge_distance):

    temp = [route[0]]
    splits = []
    for node in route:
        if route[0] != node:
            if node_charger[node]:
                temp.append(node)
                splits.append(temp)
                temp = [node]
    temp.append(node)
    splits.append(temp)

    node_distances = []
    for split in splits:
        temp = 0
        visited_start = False
        for i in range(len(route)-1):
            if route[i] == split[0] or visited_start:
                if (route[i],route[i+1]) in edge_list.keys():
                    temp += edge_distance[route[i],route[i+1]]
                else:
                    temp += edge_distance[route[i+1],route[i]]
                visited_start = True
                if route[i+1] == split[1]:
                    node_distances.append(temp)
                    break

    splits.pop()
    print(vehicle_range)
    print(splits)
    print(node_distances)
    charging_info = []
    for i in range(len(splits)):
        print(f"{splits[i][0]}, {node_distances[i]}")
        charging_info.append([splits[i][0], node_distances[i]])

    return charging_info

def add_display_path_info(G, pos, connections, graph_connections, edge_list, edge_distance,type_range):
    pos["A"] = np.array([3.5, 2])
    pos["B"] = np.array([1, 4])
    pos["C"] = np.array([4, 5])
    pos["D"] = np.array([1, 2])
    pos["E"] = np.array([3, 3])
    pos["F"] = np.array([0, 5])
    pos["G"] = np.array([1, 3])
    pos["H"] = np.array([0, 2])
    pos["I"] = np.array([5, 2])
    pos["J"] = np.array([1, 0])
    pos["K"] = np.array([5, 0])
    pos["L"] = np.array([1.5, 7])
    pos["M"] = np.array([3.5, 6.5])
    pos["N"] = np.array([2, 5.5])
    pos["O"] = np.array([5.5, 4.5])
    pos["P"] = np.array([6, 3.5])
    pos["R"] = np.array([4, 2.5])
    pos["S"] = np.array([6, 1.5])
    pos["T"] = np.array([7, 0.5])
    pos["Q"] = np.array([7, 7])

    graph_connections = graph_connections.replace("'", '').strip('][').split(', ')
    list_of_connections = []
    G.clear()
    for connection in connections:
        if (connection[0],connection[1]) in edge_list:
            weight_of_connection = edge_list[(connection[0],connection[1])]
        else:
            weight_of_connection = edge_list[(connection[1],connection[0])]
        weight = f"({weight_of_connection[0]}, {weight_of_connection[1]})"
        G.add_edge(str(connection[0]), str(connection[1]), weight=weight)

    nx.draw_networkx_nodes(G, pos, node_size=700)
    # edges
    nx.draw_networkx_edges(G, pos, width=6, edge_color="grey")
    # node labels
    nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")
    # edge weight labels
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels)
    G.clear()
    for i in range(len(graph_connections) - 1):
        list_of_connections.append([graph_connections[i], graph_connections[i + 1]])
    for connection in list_of_connections:
        if (connection[0],connection[1]) in edge_list:
            weight_of_connection = edge_list[(connection[0],connection[1])]
        else:
            weight_of_connection = edge_list[(connection[1],connection[0])]
        weight = f"({weight_of_connection[0]}, {weight_of_connection[1]})"
        G.add_edge(str(connection[0]), str(connection[1]), weight=weight)


    # edges
    nx.draw_networkx_edges(G, pos, width=6, edge_color="black")
    nx.draw_networkx_edges(
        G, pos, width=6, alpha=0.5, edge_color="b", style="dashed"
    )

    # node labels
    nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")
    # edge weight labels
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels)

    return G, pos, connections

def display_path_without_range(graph_connections, title, connections, edge_list, edge_distance):
    type_range = False
    G = nx.Graph()
    pos = nx.spring_layout(G, seed=7)  # positions for all nodes - seed for reproducibility
    G, pos, connections = add_display_path_info(G, pos, connections, graph_connections, edge_list, edge_distance, type_range)
    ax = plt.gca()
    ax.margins(0.08)
    plt.title(f"{title}\n Values on edges are equal to best/worst travel time between nodes")
    plt.axis("off")
    plt.tight_layout()
    plt.show()

def update_results(results, biggest_min, smallest_max, path_with_biggest_min, path_with_smallest_max):
    for elem in results:
        if results[elem][0]>biggest_min:
            biggest_min = results[elem][0]
            path_with_biggest_min = elem

        if results[elem][1]<smallest_max:
            smallest_max = results[elem][1]
            path_with_smallest_max = elem

        if results[elem][0] == 0:
            shortest_path = elem

    return results, path_with_biggest_min, path_with_smallest_max, smallest_max, biggest_min, shortest_path

def generate_charging_suggestion(charging_info, path):
    result = ""
    for elem in charging_info[str(path)]:
        result += f"{elem[0]} (minimal battery level: {elem[1]})" + ' -> '
    result += " (Finish)"
    return result
