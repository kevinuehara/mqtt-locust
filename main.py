import logging
from locust import Locust
from iot_device import IoT_Device

class User(Locust):
    logging.info("Initializing user...")
    task_set = IoT_Device
    min_wait = 2000
    max_wait = 5000
    