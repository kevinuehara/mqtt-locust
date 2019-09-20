import logging
from locust import Locust
from iot_device import IoT_Device

class User(Locust):
    logging.info("Initializing user...")
    task_set = IoT_Device
    min_wait = 10000
    max_wait = 15000
    