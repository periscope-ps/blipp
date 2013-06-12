import time


EVENT_TYPES={
    "dummy":"ps:testing:dummy"
}

class Probe:
    """
    Dummy probe that just sleeps and returns 1
    """

    def __init__(self, service, measurement):
        self.config = measurement["configuration"]
        self.duration = self.config.get("schedule_params", {}).get("duration", 0)

    def get_data(self):
        time.sleep(self.duration)
        return {EVENT_TYPES["dummy"]: 1}
