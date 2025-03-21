import math
import queuing_simulator.constants as const
from queuing_simulator.dist_info import DistInfo


def cal_avg_queue_length_MM1(arrival_rate, service_rate):
    return (arrival_rate**2) / (service_rate * (service_rate - arrival_rate))


def calculate_prob_zero_customers(arrival_rate, service_rate, num_of_servers):
    rho = arrival_rate / (service_rate)
    denominator = 0
    for n in range(num_of_servers):
        denominator += (rho**n) / math.factorial(n)
    denominator += (rho**num_of_servers) / (
        math.factorial(num_of_servers) * (1 - (rho / num_of_servers))
    )
    return 1 / denominator


def cal_avg_queue_length_MMC(arrival_rate, service_rate, num_of_servers):
    rho = arrival_rate / service_rate
    prob_zero_customers = calculate_prob_zero_customers(
        arrival_rate, service_rate, num_of_servers
    )
    return (
        prob_zero_customers
        * rho ** (num_of_servers + 1)
        / (math.factorial(num_of_servers - 1) * (num_of_servers - rho) ** 2)
    )


def cal_avg_queue_length_MG1(arrival_rate, service_rate, service_time_var):
    rho = arrival_rate / service_rate
    return (arrival_rate**2 * service_time_var + rho**2) / (2 * (1 - rho))


def cal_avg_queue_length_GG1(
    arrival_rate, arrival_time_var, service_rate, service_time_var
):
    rho = arrival_rate / service_rate
    Ca_sqaured = arrival_time_var * arrival_rate**2
    Cs_sqaured = service_time_var * service_rate**2

    return (rho**2 * (1 + Cs_sqaured) * (Ca_sqaured + rho**2 * Cs_sqaured)) / (
        2 * (1 - rho) * (1 + rho**2 * Cs_sqaured)
    )


def cal_avg_queue_length_GGC(
    arrival_rate, arrival_time_var, service_rate, service_time_var, num_of_servers
):
    Ca_sqaured = arrival_time_var * arrival_rate**2
    Cs_sqaured = service_time_var * service_rate**2
    avg_queue_length_MMC = cal_avg_queue_length_MMC(
        arrival_rate, service_rate, num_of_servers
    )
    avg_queue_waiting_time_MMC = avg_queue_length_MMC / arrival_rate

    avg_queue_waiting_time_GGC = (
        avg_queue_waiting_time_MMC * (Cs_sqaured + Ca_sqaured) / 2
    )
    return avg_queue_waiting_time_GGC * arrival_rate


def cal_avg_queue_length_MGC(
    arrival_rate, service_rate, service_time_var, num_of_servers
):
    arrival_time_var = (1 / arrival_rate) ** 2
    return cal_avg_queue_length_GGC(
        arrival_rate, arrival_time_var, service_rate, service_time_var, num_of_servers
    )


def calculate_averages_by_formula(num_of_servers, dist_info: DistInfo):
    arrival_rate = 1 / dist_info.arrival_mean
    service_rate = 1 / dist_info.service_mean

    if dist_info.service_dist_type == const.UNIFORM_DIST:
        dist_info.service_variance = (
            dist_info.service_high - dist_info.service_low
        ) ** 2 / 12
    elif dist_info.service_dist_type == const.GAMMA_DIST:
        dist_info.service_variance = (
            dist_info.service_shape * dist_info.service_scale**2
        )

    if dist_info.arrival_dist_type == const.UNIFORM_DIST:
        dist_info.arrival_variance = (
            dist_info.arrival_high - dist_info.arrival_low
        ) ** 2 / 12
    elif dist_info.arrival_dist_type == const.GAMMA_DIST:
        dist_info.arrival_variance = (
            dist_info.arrival_shape * dist_info.arrival_scale**2
        )

    if (
        dist_info.arrival_dist_type in const.MARKOVIAN_DISTS
        and dist_info.service_dist_type in const.MARKOVIAN_DISTS
    ):
        avg_queue_length = cal_avg_queue_length_MMC(
            arrival_rate, service_rate, num_of_servers
        )
    elif (
        dist_info.arrival_dist_type in const.MARKOVIAN_DISTS
        and dist_info.service_dist_type in const.GENERAL_DISTS
    ):
        avg_queue_length = (
            cal_avg_queue_length_MG1(
                arrival_rate, service_rate, dist_info.service_variance
            )
            if num_of_servers == 1
            else cal_avg_queue_length_MGC(
                arrival_rate, service_rate, dist_info.service_variance, num_of_servers
            )
        )
    else:
        avg_queue_length = (
            cal_avg_queue_length_GG1(
                arrival_rate,
                dist_info.arrival_variance,
                service_rate,
                dist_info.service_variance,
            )
            if num_of_servers == 1
            else cal_avg_queue_length_GGC(
                arrival_rate,
                dist_info.arrival_variance,
                service_rate,
                dist_info.service_variance,
                num_of_servers,
            )
        )
    avg_queue_waiting_time = avg_queue_length / arrival_rate
    avg_system_waiting_time = avg_queue_waiting_time + 1 / service_rate
    avg_system_length = avg_system_waiting_time * arrival_rate
    server_utilization = arrival_rate / (num_of_servers * service_rate)

    return [
        {
            "name": "Average Turn Around Time (Ws)",
            "value": abs(avg_system_waiting_time),
        },
        {
            "name": "Average Wait Time (Wq)",
            "value": abs(avg_queue_waiting_time),
        },
        {
            "name": "Length of system (Ls)",
            "value": abs(avg_system_length),
        },
        {
            "name": "Length of queue (Lq)",
            "value": abs(avg_queue_length),
        },
        {
            "name": "Server Utilization",
            "value": abs(server_utilization),
        },
    ]


if __name__ == "__main__":
    arrival_rate = 1 / 10
    service_rate = 1 / 15
    service_var = 8.33
    num_of_servers = 2

    avg_queue_length = cal_avg_queue_length_MGC(
        arrival_rate, service_rate, service_var, num_of_servers
    )

    # Once we find Lq, we can find other averages using general formulas

    avg_queue_waiting_time = avg_queue_length / arrival_rate
    avg_system_waiting_time = avg_queue_waiting_time + 1 / service_rate
    avg_system_length = avg_system_waiting_time * arrival_rate
    server_utilization = arrival_rate / (num_of_servers * service_rate)

    print("Lq: ", avg_queue_length)
    print("Wq: ", avg_queue_waiting_time)
    print("Ws: ", avg_system_waiting_time)
    print("Ls: ", avg_system_length)
    print("Server utilization:", server_utilization)
