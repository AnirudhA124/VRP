from flask import Flask, request, jsonify
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from geopy.distance import geodesic

app = Flask(__name__)

def create_data_model(coordinates):
    """Stores the data for the problem."""
    data = {}
    data["distance_matrix"] = compute_distance_matrix(coordinates)
    data["num_vehicles"] = 1
    data["depot"] = 0
    return data

def compute_distance_matrix(coordinates):
    """Computes the distance matrix from the list of coordinates."""
    size = len(coordinates)
    distance_matrix = []
    for i in range(size):
        row = []
        for j in range(size):
            if i == j:
                row.append(0)
            else:
                row.append(int(geodesic(coordinates[i], coordinates[j]).meters))
        distance_matrix.append(row)
    return distance_matrix

def solve_vrp(coordinates):
    """Solves the VRP and returns the ordered coordinates."""
    # Instantiate the data problem.
    data = create_data_model(coordinates)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
    )

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = "Distance"
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3000000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name,
    )
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # If a solution is found, return the ordered coordinates.
    if solution:
        ordered_coords = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            ordered_coords.append(coordinates[node_index])
            index = solution.Value(routing.NextVar(index))
        ordered_coords.append(coordinates[manager.IndexToNode(index)])
        return ordered_coords
    else:
        return None

@app.route('/solve_vrp', methods=['POST'])
def solve_vrp_api():
    data = request.get_json()
    coordinates = data['coordinates']
    solution = solve_vrp(coordinates)
    if solution:
        return jsonify({'solution': solution})
    else:
        return jsonify({'error': 'No solution found'}), 400

if __name__ == '__main__':
    app.run(debug=True)
