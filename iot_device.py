import os
import random

from locust import TaskSet, task, seq_task
from mqtt_client import MQTT_Client

class IoT_Device(TaskSet):

    def on_start(self):
        self.device_id = random.randint(1,101)
        self.client_mqtt = MQTT_Client()  

        self.client_mqtt.connect()     

    @seq_task(1)
    @task(2)
    def loop(self):
        self.client_mqtt.loop()

    @seq_task(2)
    @task(1)
    def publish(self):
       self.client_mqtt.publishing()
    