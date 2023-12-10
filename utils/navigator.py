from utils.graph import *
from utils.simulation import *
import json


def Navigator(nodes_number, connections_number, amount_of_nodes_with_chargers, min_travel_time, max_travel_time, min_travel_time_difference, max_travel_time_difference, start_node, end_node, vehicle_range):
    connections = []
    nodes = []
    edge_list = {}
    edge_distance = {}
    node_charger = {}
    add_nodes_with_connections(nodes, connections, edge_list, nodes_number, connections_number,min_travel_time, max_travel_time, min_travel_time_difference, max_travel_time_difference)
    edge_weights = list(edge_list.values())
    add_edge_distances_and_set_random_chargers(amount_of_nodes_with_chargers, edge_list, edge_distance, nodes, node_charger)
    scenarios = generate_scenarios(edge_weights)

    all_routes, results, charging_info = minmax_regret_range(start_node, end_node, connections, scenarios, edge_list, vehicle_range, edge_distance, node_charger)
    biggest_min = 0
    path_with_biggest_min = ""
    smallest_max = 99999999
    path_with_smallest_max = ""
    print("this is a result")
    print(results)
    results, path_with_biggest_min, path_with_smallest_max, smallest_max, biggest_min, shortest_path = update_results(results, biggest_min, smallest_max, path_with_biggest_min, path_with_smallest_max)
    plot = display_path_with_range(path_with_smallest_max, "Suggested road based on minmax regret", charging_info, connections, edge_list, edge_distance, node_charger)
    print(f"Path with worst best scenario {path_with_biggest_min}: {biggest_min}")
    print(f"Path with best worst scenario {path_with_smallest_max}: {smallest_max}")
    print(f"Shortest path {shortest_path}")
    print("Charging suggestions")
    charging_suggestions = generate_charging_suggestion(charging_info, path_with_smallest_max)
    response = {
        "route_connections": connections,
        "path_with_biggest_min": path_with_biggest_min,
        "path_with_smallest_max": path_with_smallest_max,
        "shortest_path": shortest_path,
        "smallest_max": smallest_max,
        "charging_info": charging_info,
        "charging_suggestions": charging_suggestions
        }
    return json.dumps(response), plot