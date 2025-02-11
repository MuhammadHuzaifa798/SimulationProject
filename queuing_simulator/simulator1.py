from queuing_simulator.server import Server
from queuing_simulator.customer import Customer
from queuing_simulator.arrival_table import construct_avg_arrival_lookup_table
import numpy as np
import math
from typing import List
from queuing_simulator.utils import (
    get_service_time,
    get_inter_arrival_time,
)
import pandas as pd


class Simulator:
    def __init__(
        self,
        num_of_servers,
        arrival_dist_type,
        arrival_mean,
        service_dist_type,
        service_mean,
        a,
        c,
        m,
        arrival_variance=None,
        service_variance=None,
        is_priority_based=False,
    ) -> None:
        self.num_of_servers = num_of_servers
        self.servers: List[Server] = [Server() for _ in range(self.num_of_servers)]
        self.arrival_dist_type = arrival_dist_type
        self.arrival_mean = arrival_mean
        self.service_dist_type = service_dist_type
        self.service_mean = service_mean
        self.arrival_variance = (arrival_variance,)
        self.service_variance = (service_variance,)
        self.a = a
        self.c = c
        self.m = m
        self.is_priority_based = is_priority_based
        self.num_of_customers_arrived = 0
        self.time_elapsed = 0

        self.queue: List[Customer] = []

        self.df_avg_arrival_time_lookup = construct_avg_arrival_lookup_table(
            self.arrival_dist_type, self.arrival_mean, self.arrival_variance
        )
        self.df_simulation_table = pd.DataFrame()
        self.num_of_customers = len(self.df_avg_arrival_time_lookup)
        self.customers: List[Customer] = self.initialize_customers()

    def get_customer_priority(self, u=3, l=1):
        seed = 10112166

        current_priority = seed
        # priority = []
        for _ in range(self.num_of_customers):
            current_priority = (self.a * current_priority + self.c) % self.m
            random_priority = current_priority / (self.m - 1)
            ranges = round((u - l) * random_priority + l)
            # priority.append(ranges)
            yield ranges

        # return priority

    def initialize_customers(self) -> List[Customer]:
        customers: List[Customer] = []
        priorities = self.get_customer_priority()
        for customer_idx in range(self.num_of_customers):
            arrival_random_num = np.random.rand()
            inter_arrival_time = (
                0
                if customer_idx == 0
                else get_inter_arrival_time(
                    arrival_random_num,
                    self.df_avg_arrival_time_lookup,
                )
            )
            arrival_time = (
                0
                if customer_idx == 0
                else inter_arrival_time + customers[-1].arrival_time
            )
            service_time = math.ceil(
                get_service_time(
                    self.service_dist_type, self.service_mean, self.service_variance
                )
            )
            priority = next(priorities) if self.is_priority_based else 0
            customer = Customer(
                customer_idx, inter_arrival_time, arrival_time, service_time, priority
            )
            customers.append(customer)

        return customers

    @property
    def should_continue(self):
        return (
            self.queue
            or self.num_of_customers_arrived < self.num_of_customers
            or not all(server.is_idle for server in self.servers)
        )

    @property
    def time_next_customer_arrives(self):
        return self.customers[self.num_of_customers_arrived].arrival_time

    def increase_time(self, time: int) -> None:
        self.time_elapsed += time

    def enqueue_customers(self) -> None:
        customers_to_be_enqueued = [
            customer
            for customer in self.customers[self.num_of_customers_arrived :]
            if customer.arrival_time <= self.time_elapsed
        ]
        for customer in customers_to_be_enqueued:
            self.queue.append(customer)
            self.num_of_customers_arrived += 1

    @property
    def next_customer(self) -> Customer:
        return min(self.queue, key=lambda c: c.priority)

    def pop_next_customer(self) -> Customer:
        next_customer = self.next_customer
        self.queue.remove(next_customer)
        return next_customer

    def run(self):
        while self.should_continue:
            self.enqueue_customers()

            for server in self.servers:
                if not server.is_idle and server.current_customer.is_finished:
                    server.terminate_customer_service(self.time_elapsed)

            if not self.should_continue:
                break

            if not self.queue and self.num_of_customers_arrived < self.num_of_customers:
                self.increase_time(self.time_next_customer_arrives - self.time_elapsed)
                continue

            for server in self.servers:
                if self.queue and server.is_idle:
                    server.start_customer_service(
                        self.pop_next_customer(), self.time_elapsed
                    )

            for server in self.servers:
                if (
                    self.queue
                    and self.next_customer.priority > server.current_customer.priority
                ):
                    self.queue.append(server.current_customer)
                    server.terminate_customer_service(self.time_elapsed)
                    server.start_customer_service(
                        self.pop_next_customer(), self.time_elapsed
                    )

            if self.num_of_customers_arrived < self.num_of_customers:
                allocated_time = min(
                    self.time_next_customer_arrives - self.time_elapsed,
                    *[
                        server.current_customer.remaining_time
                        for server in self.servers
                        if server.current_customer
                    ]
                )
            else:
                allocated_time = min(
                    server.current_customer.remaining_time
                    for server in self.servers
                    if server.current_customer
                )

            self.increase_time(allocated_time)
            for server in self.servers:
                server.allocate_customer_time(allocated_time)
            for customer in self.queue:
                customer.wait(allocated_time)

    def get_servers_gantt_chart_data(self):
        return [server.gantt_chart_data for server in self.servers]

    def display_gantt_chart(self):
        for server in self.servers:
            print(pd.DataFrame(server.gantt_chart_data))
            print("----------------------------")

    def get_simulation_table(self):
        simulation_data = []
        for customer in self.customers:
            simulation_data.append(
                {
                    "id": customer.customer_id,
                    "inter_arrival_time": customer.inter_arrival_time,
                    "arrival_time": customer.arrival_time,
                    "service_time": customer.service_time,
                    "priority": customer.priority,
                    "start_time": customer.start_time,
                    "end_time": customer.end_time,
                    "wait_time": customer.wait_time,
                    "turn_around_time": customer.turn_around_time,
                    "response_time": customer.response_time,
                }
            )

        self.df_simulation_table = pd.DataFrame(simulation_data)
        if not self.is_priority_based:
            self.df_simulation_table = self.df_simulation_table.drop(
                "priority", axis="columns"
            )
        return self.df_simulation_table

    def calculate_averages(self):
        return [
            {
                "name": "Average Inter Arrival Time",
                "value": self.df_simulation_table.inter_arrival_time.mean(),
            },
            {
                "name": "Average Service Time",
                "value": self.df_simulation_table.service_time.mean(),
            },
            {
                "name": "Average Turn Around Time (Ws)",
                "value": self.df_simulation_table.turn_around_time.mean(),
            },
            {
                "name": "Average Wait Time (Wq)",
                "value": self.df_simulation_table.wait_time.mean(),
            },
            {
                "name": "Length of system (Ls)",
                "value": self.df_simulation_table.turn_around_time.sum()
                / self.df_simulation_table.iloc[-1].end_time,
            },
            {
                "name": "Length of queue (Lq)",
                "value": self.df_simulation_table.wait_time.sum()
                / self.df_simulation_table.iloc[-1].start_time,
            },
            {
                "name": "Server Utilization",
                "value": self.df_simulation_table.service_time.sum()
                / (self.num_of_servers * max(self.df_simulation_table.end_time)),
            },
        ]
