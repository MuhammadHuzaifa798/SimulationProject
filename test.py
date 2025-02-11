from queuing_simulator.simulator import Simulator
from pprint import pprint

if __name__ == "__main__":
    num_of_servers = 2  # int(input("Enter number of servers: "))
    arrival_mean = 1.5  # eval(input("Enter mean of arrival distribution: "))
    service_mean = 0.1  # eval(input("Enter mean of service distribution: "))
    arrival_type = 0
    service_type = 0
    a = 55
    c = 9
    m = 1994
    sim = Simulator(
        num_of_servers,
        arrival_type,
        arrival_mean,
        service_type,
        service_mean,
        a,
        c,
        m,
        is_priority_based=True,
    )
    sim.run()
    sim.display_gantt_chart()
    print(sim.get_simulation_table())
    pprint(sim.calculate_averages())
