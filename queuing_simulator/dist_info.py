
class DistInfo:
    arrival_mean: float
    arrival_dist_type: int
    arrival_variance: float | None
    arrival_low: float | None
    arrival_high: float | None
    arrival_shape: float | None
    arrival_scale: float | None

    service_mean: float
    service_dist_type: int
    service_variance: float | None
    service_low: float | None
    service_high: float | None
    service_shape: float | None
    service_scale: float | None
