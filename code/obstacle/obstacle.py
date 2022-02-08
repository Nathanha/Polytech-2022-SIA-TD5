from envparse import env
import os
import time

from ab2_mqtt import MQTTClient

TOPIC_BEHAVIOR_OBSTACLE = "alphabot2/behavior/obstacle"

state = 0
Cg = "False"
Cd = "False"

def on_left_obstacle_found(client, userdata, msg):
    global Cg
    Cg = msg.payload.decode("utf-8")

def on_right_obstacle_found(client, userdata, msg):
    global Cd
    Cd = msg.payload.decode("utf-8")

# Parse environment variables
DOCKER_VARENV = ['MQTT_HOST', 'MQTT_PORT']

if set(DOCKER_VARENV).issubset(set(os.environ)):
    MQTT_HOST = env(DOCKER_VARENV[0], default='localhost')
    MQTT_PORT = env.int(DOCKER_VARENV[1], default=1883)
else:
    MQTT_HOST = 'localhost'
    MQTT_PORT = 1883

QOS = 0

client = MQTTClient("controler", MQTT_HOST, MQTT_PORT, QOS)
client.message_callback_add(client.TOPIC_OBSTACLE_LEFT, on_left_obstacle_found)
client.message_callback_add(client.TOPIC_OBSTACLE_RIGHT, on_right_obstacle_found)

client.loop_start()

client.publish(client.TOPIC_LEDS, "0x0000FF 0x000000 0x000000 0x0000FF")

if __name__ == '__main__':
    try:
        while True:
            time.sleep(0.05)
            if state == 0:
                if Cg == "True":
                    state = 1
                elif Cd == "True":
                    state = 2
                elif Cg == "True" and Cd == "True":
                    state = 2
                else:
                    client.publish(TOPIC_BEHAVIOR_OBSTACLE, "0.2 0.2 0.2 0.8 1 0.8 0")
            elif state == 1:
                client.publish(TOPIC_BEHAVIOR_OBSTACLE, "1 -1 0.2 -1 -1 0.2 0")
                state = 0
            elif state == 2:
                client.publish(TOPIC_BEHAVIOR_OBSTACLE, "0.2 -1 1 0.2 -1 -1 0")
                state = 0

    except KeyboardInterrupt:
        print("error")
