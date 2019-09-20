"""
    Handles Paho MQTT-Client operations like publish/subscription, connection,
    loop function.
"""
import paho.mqtt.client as mqtt
import os
import logging
import time
import json
import random
import threading

from utils import Utils
from locust import TaskSet, task, seq_task

TENANT = "admin"
REQUEST_TYPE = 'MQTT'
MESSAGE_TYPE_PUB = 'PUB'
PUBLISH_TIMEOUT = 5000

class MQTT_Client:
    
    def __init__(self):
        self.mqttc = mqtt.Client()
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_publish = self.locust_on_publish
        self.pubmmap = {}

    def get_client(self):
        return self.mqttc

    def connect(self):
        self.mqttc.connect("localhost", 1883, 60)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
    
    def start_loop(self):
        logging.info("Starting loop...")
        self.mqttc.loop(0.5)

    def publishing(self):
        topic = "/{0}/{1}/attrs".format(TENANT, '4929cf')
        payload = {'humidity': int(5.5)}

        start_time = time.time()

        logging.info(f"Publishing in topic {topic}")
        try:
            res = self.mqttc.publish(
                    topic=topic,
                    payload=json.dumps(payload),
                    qos=1,
                    retain=False
                )

            [ err, mid ] = res

            if err:
                logging.error(str(err))
                Utils.fire_locust_failure(
                    request_type=REQUEST_TYPE,
                    name='publish',
                    response_time=Utils.time_delta(start_time, time.time()),
                    exception=ValueError(err)
                )

                logging.info("publish ERROR: err,mid:"+str(err)+","+str(mid)+"")
                logging.error(err)

            self.pubmmap[mid] = {
                'name': MESSAGE_TYPE_PUB, 
                'qos': 1, 
                'topic': topic,
                'payload': payload,
                'start_time': start_time, 
                'timed_out':10000, 
                'messages': 'messages'
            }

        except Exception as e:
            logging.error(str(e))
            Utils.fire_locust_failure(
                request_type=REQUEST_TYPE,
                name='publish',
                response_time=Utils.time_delta(start_time, time.time()),
                exception=e,
            )

    def locust_on_publish(self, client, userdata, mid):
        logging.info("--locust_on_publish--")

        end_time = time.time()
        print(self.pubmmap)
        message = self.pubmmap.pop(mid, None)

        if message is None:
            logging.info("message is none")
            Utils.fire_locust_failure(
                request_type=REQUEST_TYPE,
                name="message_found",
                response_time=0,
                exception=ValueError("Published message could not be found"),
            )
            return

        total_time = Utils.time_delta(message.start_time, end_time)
        logging.info("total time: " + str(total_time))

        if message.timed_out(total_time):
            logging.error("publish timed out")
            Utils.fire_locust_failure(
                request_type=REQUEST_TYPE,
                name=message.name,
                response_time=total_time,
                exception=TimeoutError("publish timed out"),
            )
        else:
            logging.info("message sent")
            Utils.fire_locust_success(
                request_type=REQUEST_TYPE,
                name=message.name,
                response_time=total_time,
                response_length=len(message.payload),
            )