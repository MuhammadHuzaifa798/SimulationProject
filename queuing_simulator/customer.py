class Customer:
    def __init__(
        self, customer_id: int, inter_arrival_time, arrival_time, service_time, priority
    ) -> None:
        self.customer_id: str = f"C{customer_id}"
        self.inter_arrival_time = inter_arrival_time
        self.arrival_time = arrival_time
        self.service_time = service_time
        self.remaining_time = self.service_time
        self.priority = priority
        self.wait_time: int = 0
        self.start_time = None
        self.end_time = None

    @property
    def turn_around_time(self) -> int:
        return self.wait_time + self.service_time

    @property
    def is_finished(self):
        return self.remaining_time <= 0

    @property
    def response_time(self) -> int:
        return self.start_time - self.arrival_time

    @property
    def completion_time(self) -> int:
        return self.arrival_time + self.execution_time + self.wait_time

    def wait(self, time) -> None:
        self.wait_time += time

    def allocate(self, allocated_time) -> None:
        self.remaining_time -= allocated_time
