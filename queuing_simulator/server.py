from typing import Union
from queuing_simulator.customer import Customer


class Server:
    def __init__(self) -> None:
        self.current_customer: Customer | None = None
        self.gantt_chart_data = []
        self.start_time = None

    @property
    def is_idle(self) -> bool:
        return self.current_customer is None

    def allocate_customer_time(self, allocated_time):
        if not self.is_idle:
            self.current_customer.allocate(allocated_time)

    def start_customer_service(self, customer: Customer, time):
        self.current_customer = customer
        self.start_time = time
        if self.current_customer.start_time is None:
            self.current_customer.start_time = time

    def terminate_customer_service(self, time):
        if self.current_customer.priority ==1:
            color = "red"
        elif self.current_customer.priority ==2:
            color = "yellow"
        elif self.current_customer.priority ==3:
            color = "green"
        else:
            color = "blue"
        self.gantt_chart_data.append(
            {
                "id": self.current_customer.customer_id,
                "legend": self.current_customer.customer_id,
                "start": self.start_time,
                "end": time,
                "color": color
            }
        )
        if self.current_customer.remaining_time <= 0:
            self.current_customer.end_time = time
        self.current_customer = None
