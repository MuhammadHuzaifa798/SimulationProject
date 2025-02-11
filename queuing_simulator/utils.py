import math
from scipy import stats
from queuing_simulator import constants as const
from queuing_simulator.dist_info import DistInfo
import numpy as np
import random
import math


def get_service_time(dist_info: DistInfo):
    if dist_info.service_dist_type == const.EXP_POIS_RAND_DIST:
        return round(abs(np.random.exponential(scale=dist_info.service_mean)))
    if dist_info.service_dist_type == const.NORMAL_DIST:
        return round(abs(
            np.random.normal(
                loc=dist_info.service_mean, scale=math.sqrt(dist_info.service_variance)
            )
        ))
    if dist_info.service_dist_type == const.UNIFORM_DIST:
        return round(abs(
            np.random.uniform(low=dist_info.service_low, high=dist_info.service_high)
        ))
    return round(abs(np.random.gamma(dist_info.service_shape, dist_info.service_scale)))


def calculate_cdf(x, dist_info: DistInfo):
    if dist_info.arrival_dist_type == const.EXP_POIS_RAND_DIST:
        return stats.poisson.cdf(x, dist_info.arrival_mean)
    if dist_info.arrival_dist_type == const.NORMAL_DIST:
        return stats.norm.cdf(
            x, loc=dist_info.arrival_mean, scale=math.sqrt(dist_info.arrival_variance)
        )
    if dist_info.arrival_dist_type == const.UNIFORM_DIST:
        a = dist_info.arrival_low
        b = dist_info.arrival_high
        return stats.uniform.cdf(x, loc=a, scale=b - a)
    return stats.gamma.cdf(
        x, dist_info.arrival_shape, loc=0, scale=dist_info.arrival_scale
    )


def calculate_poisson_cdf(k, mean):
    cdf = 0.0
    for i in range(k + 1):
        cdf += (mean**i) * math.exp(-mean) / math.factorial(i)
    return cdf


def calculate_service_time(random_num, mean):
    return math.ceil(-(math.log(1 - random_num)) / mean)


def get_inter_arrival_time(random_num, df_avg_arrival_time_lookup):
    for index, row in df_avg_arrival_time_lookup.iterrows():
        if random_num >= row.cum_prob_lookup and random_num < row.cum_prob:
            return row.inter_arrival_time


def is_server_idle(arrival_time, server):
    return len(server) == 0 or server[-1]["end"] <= arrival_time


def find_server_index_with_min_time_left(servers):
    return servers.index(min(servers, key=lambda server: server[-1]["end"]))



# Exponential Distribution
def generate_exponential(lambda_val, size):
    return [-math.log(random.random()) / lambda_val for _ in range(size)]

# Uniform Distribution
def generate_uniform(a, b, size):
    return [a + (b - a) * random.random() for _ in range(size)]

# Normal (Gaussian) Distribution (using Box-Muller method)
def generate_normal(mu, sigma, size):
    def box_muller():
        u1 = random.random()
        u2 = random.random()
        z0 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        z1 = math.sqrt(-2 * math.log(u1)) * math.sin(2 * math.pi * u2)
        return z0, z1

    return [mu + sigma * box_muller()[0] for _ in range(size)]

# Gamma Distribution (using sum of exponential random variables)
def generate_gamma(k, theta, size):
    return [sum(generate_exponential(1 / theta, k)) for _ in range(size)]

# Exponential Distribution CDF
def exponential_cdf(x, lambda_val):
    return 1 - np.exp(-lambda_val * x)

# Uniform Distribution CDF
def uniform_cdf(x, a, b):
    return (x - a) / (b - a) if a <= x <= b else 0 if x < a else 1
