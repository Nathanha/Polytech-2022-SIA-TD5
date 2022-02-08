from envparse import env
import os
import time

from ab2_mqtt import MQTTClient

TOPIC_BEHAVIOR_IR_RIGHT = "alphabot2/behavior/ir_right"

def on_irsensors(client, userdata, msg):
    data = msg.payload.decode("utf-8")
    data_list = data.split(", ")
    data_list[0] = data_list[0].split("[")[1]
    data_list[4] = data_list[4].split("]")[0]

    C1 = int(float(data_list[0]))
    C2 = int(float(data_list[1]))
    C3 = int(float(data_list[2]))
    C4 = int(float(data_list[3]))
    C5 = int(float(data_list[4]))

    detected = 900

    LEFT = C1 + C2
    CENTER = C3
    RIGHT = C4 + C5

    if RIGHT >= 1800 and CENTER >= detected and LEFT >= 1800:
        client.publish(TOPIC_BEHAVIOR_IR_LEFT, "0 0 0 0 0 0 1")
    elif RIGHT >= 1800 and CENTER < detected:
        client.publish(TOPIC_BEHAVIOR_IR_RIGHT, "0.2 0.8 0.2 0.5 1 0.5 0")
    elif RIGHT >= 1800 and CENTER >= detected:
        client.publish(TOPIC_BEHAVIOR_IR_RIGHT, "0.8 0.5 0 1 0.5 0 0")
    elif RIGHT < 1800 and CENTER < detected:
        client.publish(TOPIC_BEHAVIOR_IR_RIGHT, "0 0.5 0.8 0 0.5 1 0")

# Parse environment variables
DOCKER_VARENV = ['MQTT_HOST', 'MQTT_PORT']

if set(DOCKER_VARENV).issubset(set(os.environ)):
    MQTT_HOST = env(DOCKER_VARENV[0], default='localhost')
    MQTT_PORT = env.int(DOCKER_VARENV[1], default=1883)
else:
    MQTT_HOST = 'localhost'
    MQTT_PORT = 1883

QOS = 0

client = MQTTClient("controler4", MQTT_HOST, MQTT_PORT, QOS)
client.message_callback_add(client.TOPIC_IRSENSORS, on_irsensors)

client.loop_start()

if __name__ == '__main__':
    try:
        while True:
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("error")
