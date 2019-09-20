import paho.mqtt.client as mqtt


class MQTTClient(mqtt.Client):

    def __init__(self, *args, **kwargs):
        super(MQTTClient, self).__init__(*args, **kwargs)
        self.on_connect = self.locust_on_connect
        self.on_publish = self.locust_on_publish
        self.pubmmap = {}
        self.is_connected = False

    def locust_on_connect():
        pass
    
    def locust_on_publish():
        pass