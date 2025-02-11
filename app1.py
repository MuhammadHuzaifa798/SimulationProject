from flask import Flask, request, jsonify
from flask_cors import CORS

from queuing_simulator.arrival_table import construct_avg_arrival_lookup_table
from queuing_simulator.simulator import Simulator
from queuing_simulator.queuing_formulae import calculate_averages_by_formula

app = Flask(__name__)
CORS(app)


@app.route("/get-interarrival-lookup-table", methods=["GET"])
def get_interarrival_lookup_table():
    print(request.args)
    arrival_dist_type = eval(request.args.get("arrivalDistType"))
    arrival_mean = eval(request.args.get("meanArrival"))
    arrival_variance = eval(request.args.get("varianceArrival"))
    arrival_table = construct_avg_arrival_lookup_table(
        arrival_dist_type, arrival_mean, arrival_variance
    )
    response = arrival_table.values.tolist()
    return jsonify(response), 200


@app.route("/get-complete-simulation", methods=["GET"])
def get_complete_simulation():
    print(request.args)
    num_of_servers = eval(request.args.get("numOfServers"))
    # num_of_observations = eval(request.args.get("numOfObservations"))
    arrival_dist_type = eval(request.args.get("arrivalDistType"))
    arrival_mean = eval(request.args.get("meanArrival"))
    service_dist_type = eval(request.args.get("serviceDistType"))
    service_mean = eval(request.args.get("meanService"))
    arrival_variance = eval(request.args.get("varianceArrival"))
    service_variance = eval(request.args.get("varianceService"))
    a = eval(request.args.get("a"))
    c = eval(request.args.get("c"))
    m = eval(request.args.get("m"))
    is_priority_based = eval(request.args.get("isPriority"))

    sim = Simulator(
        num_of_servers,
        arrival_dist_type,
        arrival_mean,
        service_dist_type,
        service_mean,
        a,
        c,
        m,
        is_priority_based=is_priority_based,
    )
    sim.run()
    sim.display_gantt_chart()

    simulation_table = sim.get_simulation_table()
    servers = sim.get_servers_gantt_chart_data()
    averages = sim.calculate_averages()

    response = {
        "simulationTable": simulation_table.values.tolist(),
        "servers": servers,
        "averages": averages,
    }
    return jsonify(response), 200


@app.route("/get-averages", methods=["GET"])
def get_averages():
    print(request.args)
    num_of_servers = eval(request.args.get("numOfServers"))
    arrival_dist_type = eval(request.args.get("arrivalDistType"))
    arrival_mean = eval(request.args.get("meanArrival"))
    service_dist_type = eval(request.args.get("serviceDistType"))
    service_mean = eval(request.args.get("meanService"))
    arrival_variance = eval(request.args.get("varianceArrival"))
    service_variance = eval(request.args.get("varianceService"))

    response = calculate_averages_by_formula(
        num_of_servers,
        arrival_dist_type,
        arrival_mean,
        service_dist_type,
        service_mean,
        arrival_variance,
        service_variance,
    )

    return jsonify(response), 200


if __name__ == "__main__":
    app.run(debug=True)
