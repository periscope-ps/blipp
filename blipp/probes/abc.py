from unis.models import Service, Measurement

class Probe(object):
    def __init__(self, service: Service, measurement: Measurement) -> None:
        self.service, self.measurement = service, measurement
        self.config = measurement.configuration

    def get_data(self) -> dict:
        raise NotImplementedError

