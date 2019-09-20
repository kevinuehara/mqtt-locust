import paho.mqtt.client as mqtt
import os
import logging
import time
import json
import random
import threading

from utils import Utils
from locust import TaskSet, task, seq_task

REQUEST_TYPE = "mqtt"
TENANT = "admin"
  
class MQTT_Client:

    def __init__(self, device_id):
        self.mqttc = mqtt.Client()
        self.mqttc.connect("test.mosquitto.org", 1883, 60)
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message

    def get_client(self):
        return self.mqttc

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        
    def on_message(self, client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))


class IoT_Device(TaskSet):

    def on_start(self):
        self.device_id = random.randint(1,101)
        self.client_mqtt = MQTT_Client(self.device_id)       


    @seq_task(1)
    @task(2)
    def start_loop(self):
        logging.info("Starting loop...")
        self.client_mqtt.get_client().loop()
        

    @seq_task(2)
    @task(1)
    def publish(self):
        topic = "/{0}/{1}/attrs".format(TENANT, 1)
        payload = "{'temperature': random.randint(1, 21)}"
        start_time = time.time()

        logging.info(f"Publishing in topic {topic}")
        try:
            res = self.client_mqtt.get_client().publish(
                    topic=topic,
                    payload=payload,
                    qos=0,
                    retain=False
                )

            [ err, mid ] = res

            if err:
                logging.error(str(err))
                Utils.fire_locust_failure(
                    request_type=REQUEST_TYPE,
                    name='messages',
                    response_time=Utils.time_delta(start_time, time.time()),
                    exception=ValueError(err)
                )

                logging.info("publish ERROR: err,mid:"+str(err)+","+str(mid)+"")
                logging.error(err)

            else:
                logging.info("#### SUCESSO")

        except Exception as e:
            logging.error(str(e))
            Utils.fire_locust_failure(
                request_type=REQUEST_TYPE,
                name='messages',
                response_time=Utils.time_delta(start_time, time.time()),
                exception=e,
            )
        

    