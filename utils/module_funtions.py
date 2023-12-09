import os
import yaml
import logging
import json
from utils.simulation import * 

def read_config(  
        config_filename: str,
        path_to_dir: str = None) -> dict:
    
    """
    Read a YAML configuration file.

    Args:
        config_filename (str): The name of the configuration file.
        path_to_dir (str, optional): The path to the directory containing the configuration file.
            Defaults to None.

    Returns:
        dict: The configuration data as a dictionary.
    """
    
    path_to_configfile = os.path.join(
        path_to_dir, 
        config_filename) \
            if path_to_dir is not None else config_filename
    
    with open(path_to_configfile) as yaml_file:
        config = yaml.load(yaml_file, Loader=yaml.SafeLoader)

    return config


def read_user_info(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File not found at {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {str(e)}")
        return None

def save_user_data(file_path, user_data):
    with open(file_path, 'w') as file:
        json.dump(user_data, file, indent=4)

def update_user_info(file_path, user_data, new_user_data):
    user_data = read_user_info(file_path)
    print(user_data)
    print(new_user_data)
    try:
        # Update user data based on the provided update_data
        for key, value in new_user_data.items():
            print(key, value)
            if key in user_data and value != '':
                print(user_data[key])
                user_data[key] = value

        # Save the updated user data to the JSON file
        save_user_data(file_path, user_data)

        return user_data
    except Exception as e:
        return {"error": str(e)}

def clear_static_folder(app):
    static_folder = app.static_folder

    # Ensure the static folder exists
    if os.path.exists(static_folder):
        # Iterate over all files in the static folder and delete them
        for filename in os.listdir(static_folder):
            file_path = os.path.join(static_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    else:
        print(f"The static folder '{static_folder}' does not exist.")


def validate_node_range(start_node, end_node, NODES_NUMBER):
    # Extract the valid range based on nodes_number
    valid_range = [chr(ord('A') + i) for i in range(NODES_NUMBER)]

    # Check if the provided nodes are within the valid range
    if start_node not in valid_range or end_node not in valid_range:
        return ValueError(f"Invalid node(s) in the range. Nodes should be in the range {', '.join(valid_range)}.")
    else:
        nodes_in_range = True
    # Return the valid range if input is correct
    return nodes_in_range # f"Valid range: {input_range}"

def display_nodes(nodes_number):
    plt.close()
    pos = {
    "A": np.array([3.5, 2]),
    "B": np.array([1, 4]),
    "C": np.array([4, 5]),
    "D": np.array([1, 2]),
    "E": np.array([3, 3]),
    "F": np.array([0, 5]),
    "G": np.array([1, 3]),
    "H": np.array([0, 2]),
    "I": np.array([5, 2]),
    "J": np.array([1, 0]),
    "K": np.array([5, 0]),
    "L": np.array([1.5, 7]),
    "M": np.array([3.5, 6.5]),
    "N": np.array([2, 5.5]),
    "O": np.array([5.5, 4.5]),
    "P": np.array([6, 3.5]),
    "R": np.array([4, 2.5]),
    "S": np.array([6, 1.5]),
    "T": np.array([7, 0.5]),
    "Q": np.array([7, 7]),
    }

    filename = 'map' + generate_unique_filename()
    filepath = 'static/' + filename
    # Create an empty graph
    G = nx.Graph()
    # Add nodes to the graph
    for node in pos:
        G.add_node(node, pos=pos[node])
    # Ensure the number of nodes in the graph is equal to nodes_number
    if len(G.nodes) > nodes_number:
        G.remove_nodes_from(list(G.nodes)[nodes_number:])
    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_size=700)
    nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")
    ax = plt.gca()
    ax.margins(0.08)
    plt.title(f"Map of available places\n")
    plt.axis("off")
    plt.tight_layout()

    plt.savefig(filepath, format="png")
    plt.close()

    return filename