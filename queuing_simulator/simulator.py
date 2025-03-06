from queuing_simulator.server import Server
from queuing_simulator.customer import Customer
from queuing_simulator.arrival_table import construct_avg_arrival_lookup_table
from queuing_simulator.dist_info import DistInfo
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
        dist_info: DistInfo,
        is_priority_based,
    ) -> None:
        self.num_of_servers = num_of_servers
        self.servers = [Server(server_id=i) for i in range(num_of_servers)]  # Assign IDs
        self.dist_info = dist_info
        self.is_priority_based = is_priority_based
        self.num_of_customers_arrived = 0
        self.time_elapsed = 0

        self.queue: List[Customer] = []

        self.df_avg_arrival_time_lookup = construct_avg_arrival_lookup_table(
            self.dist_info
        )
        self.df_simulation_table = pd.DataFrame()
        self.num_of_customers = len(self.df_avg_arrival_time_lookup)
        self.customers: List[Customer] = self.initialize_customers()

    def get_customer_priority(self, u=3, l=1):
        seed = 10112166
        a = 55
        c = 9
        m = 1994

        current_priority = seed
        for _ in range(self.num_of_customers):
            current_priority = (a * current_priority + c) % m
            random_priority = current_priority / (m - 1)
            ranges = round((u - l) * random_priority + l)
            yield ranges

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
            # print(custosmer_idx)
            arrival_time = (
                0
                if customer_idx == 0
                else inter_arrival_time + customers[-1].arrival_time
            )
            service_time = get_service_time(self.dist_info)
            service_time = service_time if service_time > 0 else 1
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

            # Assign customers to idle servers
            for server in self.servers:
                if self.queue and server.is_idle:
                    customer = self.pop_next_customer()
                    customer.server_id = server.id
                    server.start_customer_service(customer, self.time_elapsed)

            if not self.should_continue:
                break

            # Calculate time until next event
            time_options = []
            if self.num_of_customers_arrived < self.num_of_customers:
                time_options.append(self.time_next_customer_arrives - self.time_elapsed)
            
            server_times = []
            for server in self.servers:
                if server.current_customer:
                    server_times.append(server.current_customer.remaining_time)
            
            allocated_time = min(time_options + server_times) if (time_options + server_times) else 0

            # Progress time and handle completions
            self.increase_time(allocated_time)
            for server in self.servers:
                if server.current_customer:
                    server.allocate_customer_time(allocated_time)
                    # NEW: Check for completion after time allocation
                    if server.current_customer.is_finished:
                        server.terminate_customer_service(self.time_elapsed)  # Release server

            for customer in self.queue:
                customer.wait(allocated_time)

    def get_servers_gantt_chart_data(self):
        return [server.gantt_chart_data for server in self.servers]

    def display_gantt_chart(self):
        for server in self.servers:
            print(pd.DataFrame(server.gantt_chart_data))
            print("----------------------------")

    def get_arrival_table(self):
        return self.df_avg_arrival_time_lookup.rename(
            columns={
                "cum_prob": "Cumulative Probability",
                "cum_prob_lookup": "Cumulative Probability Lookup",
                "inter_arrival_time": "Inter Arrival Time",
            }
        )

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
                    "server_id": customer.server_id,
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
        return self.df_simulation_table.drop("inter_arrival_time", axis='columns').rename(
            columns={
                "id": "ID",
                "inter_arrival_time": "Inter Arrival Time",
                "arrival_time": "Arrival Time",
                "service_time": "Service Time",
                "priority": "Priority",
                "start_time": "Start Time",
                "end_time": "End Time",
                "wait_time": "Wait time",
                "turn_around_time": "Turn Around Time",
                "response_time": "Response Time",
            }
        )

    def calculate_averages(self):
        df = self.df_simulation_table
        max_end_time = df['end_time'].max() if not df.empty else 0
        averages = []

        # System-wide metrics
        system_metrics = {
            'Average Inter Arrival Time': df['inter_arrival_time'].mean(),
            'Average Wait Time (Wq)': df['wait_time'].mean(),
            'Average Turn Around Time (Ws)': df['turn_around_time'].mean(),
            'Average Response Time': df['response_time'].mean(),
            'Length of system (Ls)': df['turn_around_time'].sum() / max_end_time if max_end_time > 0 else 0,
            'Length of queue (Lq)': df['wait_time'].sum() / (df['start_time'].max() if df['start_time'].max() > 0 else 1)
        }
        
        # Add system metrics
        for name, value in system_metrics.items():
            averages.append({"name": name, "value": value})

        # Server-specific metrics
        for server in self.servers:
            # Calculate from Gantt chart data
            server_tasks = server.gantt_chart_data
            busy_time = sum(task['end'] - task['start'] for task in server_tasks)
            num_customers = len(server_tasks)
            
            server_metrics = {
                'Utilization': busy_time / max_end_time if max_end_time > 0 else 0,
                'Customers Served': num_customers,
                'Throughput (cust/time unit)': num_customers / max_end_time if max_end_time > 0 else 0,
                'Avg Service Time': busy_time / num_customers if num_customers > 0 else 0,
                'Total Busy Time': busy_time
            }
            
            # Add server-specific metrics
            for metric_name, value in server_metrics.items():
                averages.append({
                    "name": f"Server {server.id+1} - {metric_name}",
                    "value": value
                })
        

        # Add priority-wise metrics if priority-based
        if self.is_priority_based:
            # Get unique priorities
            priorities = self.df_simulation_table['priority'].unique()
            
            for priority in priorities:
                priority_df = self.df_simulation_table[self.df_simulation_table['priority'] == priority]
                
                priority_metrics = {
                    'Average Wait Time': priority_df['wait_time'].mean(),
                    'Average Turn Around Time': priority_df['turn_around_time'].mean(),
                    'Average Response Time': priority_df['response_time'].mean(),
                    'Number of Customers': len(priority_df)
                }
                
                for metric_name, value in priority_metrics.items():
                    averages.append({
                        "name": f"Priority {priority} - {metric_name}",
                        "value": value
                    })


        return averages
