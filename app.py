from flask import Flask, render_template, request, session, redirect
from utils.navigator import Navigator
from utils.module_funtions import *
import os
import jsonify
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['CONFIG_FILE'] = './config/CONFIG.yml'

current_dir = os.path.dirname(os.path.abspath(__file__))

user_data_path = os.path.join(current_dir, "config", "user_data.json")

CONFIGURATION = read_config(
    app.config['CONFIG_FILE']
)

NODES_NUMBER = CONFIGURATION.get('nodes_number')
CONNECTIONS_NUMBER = CONFIGURATION.get('connections_number')
AMMOUNT_OF_NODES_WITH_CHARGERS = CONFIGURATION.get('amount_of_nodes_with_chargers')
MIN_TRAVEL_TIME = CONFIGURATION.get('min_travel_time')
MAX_TRAVEL_TIME = CONFIGURATION.get('max_travel_time')
MIN_TRAVEL_TIME_DIFFERENCE = CONFIGURATION.get('min_travel_time_difference')
MAX_TRAVEL_TIME_DIFFERENCE = CONFIGURATION.get('max_travel_time_difference')
VEHICLE_RANGE = CONFIGURATION.get('vehicle_range')

valid_node_range = [chr(ord('A') + i) for i in range(NODES_NUMBER)]

@app.route('/')
def landing_page():
    # valid_node_range_output = ', '.join(valid_node_range)
    nodes_map = display_nodes(NODES_NUMBER)
    return render_template('index.html',
                            map_path=nodes_map)


@app.route('/process_data', methods=['POST', 'GET'])
def process_data():
    try:
        start_node = (request.form['start']).upper()
        end_node = (request.form['destination']).upper()
        nodes_number = int(NODES_NUMBER)
        validation_output = validate_node_range(start_node, end_node, NODES_NUMBER)
        if validation_output == True:
            clear_static_folder(app)
            connections_number = int(CONNECTIONS_NUMBER)
            amount_of_nodes_with_chargers = float(AMMOUNT_OF_NODES_WITH_CHARGERS)
            min_travel_time = int(MIN_TRAVEL_TIME)
            max_travel_time = int(MAX_TRAVEL_TIME)
            min_travel_time_difference = int(MIN_TRAVEL_TIME_DIFFERENCE)
            max_travel_time_difference = int(MAX_TRAVEL_TIME_DIFFERENCE)
            vehicle_range = int(VEHICLE_RANGE)
            results, plot = Navigator(nodes_number, connections_number, amount_of_nodes_with_chargers, min_travel_time, max_travel_time, min_travel_time_difference, max_travel_time_difference, start_node, end_node, vehicle_range)
            if results is not None or results != '':
                return render_template('show_route.html', 
                                        results=json.loads(results), 
                                        plot_path=plot)
            else: 
                return "Results not found."
        else:
            nodes_map = display_nodes(NODES_NUMBER)
            return render_template('index.html', 
                                    error_message=validation_output,
                                    map_path=nodes_map)

    except Exception as e:

        print(f"An unexpected error occurred: {str(e)}")
        error_message = "No path available. Please try again"
        nodes_map = display_nodes(NODES_NUMBER)

        return render_template('index.html', 
                        error_message=error_message,
                        map_path=nodes_map)

@app.route('/my_profile', methods=['POST', 'GET'])
def my_profile():
    if request.method == 'GET':
        current_dir = os.path.dirname(os.path.abspath(__file__))
        user_data = read_user_info(user_data_path)
        print(user_data)
        return render_template('my_profile.html', 
                                user_data=user_data)

    elif request.method == 'POST':

        try:

            posted_data = request.get_json()
            user_data.update(posted_data)
            return jsonify({"message": "User data updated successfully"})
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return render_template('my_profile.html')

@app.route('/edit_profile', methods=['POST', 'GET'])
def edit_profile():
    if request.method == 'GET':
        return render_template('edit_profile.html')

    elif request.method == 'POST':
        try:
            new_user_data = request.form.to_dict()
            user_data = read_user_info(user_data_path)
            update_user_info(user_data_path, user_data, new_user_data)
        except Exception as e:
             return jsonify({"error": str(e)}), 400
        user_data = read_user_info(user_data_path)
    return render_template('my_profile.html', 
                            user_data=user_data)

if __name__ == '__main__':
    app.run(debug=True)