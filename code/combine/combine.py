from envparse import env
import os
import time

from ab2_mqtt import MQTTClient

obstacle_data_list = ['0', '0', '0', '0', '0', '0', '0']
ir_right_data_list = ['0', '0', '0', '0', '0', '0', '0']
ir_left_data_list = ['0', '0', '0', '0', '0', '0', '0']

def on_behavior_obstacle(client, userdata, msg):
    global obstacle_data_list
    data = msg.payload.decode("utf-8")
    obstacle_data_list = data.split(" ")

def on_behavior_ir_right(client, userdata, msg):
    global ir_right_data_list
    data = msg.payload.decode("utf-8")
    ir_right_data_list = data.split(" ")

def on_behavior_ir_left(client, userdata, msg):
    global ir_left_data_list
    data = msg.payload.decode("utf-8")
    ir_left_data_list = data.split(" ")


# Parse environment variables
DOCKER_VARENV = ['MQTT_HOST', 'MQTT_PORT']

if set(DOCKER_VARENV).issubset(set(os.environ)):
    MQTT_HOST = env(DOCKER_VARENV[0], default='localhost')
    MQTT_PORT = env.int(DOCKER_VARENV[1], default=1883)
else:
    MQTT_HOST = 'localhost'
    MQTT_PORT = 1883

QOS = 0

client = MQTTClient("controler2", MQTT_HOST, MQTT_PORT, QOS)
client.message_callback_add("alphabot2/behavior/obstacle", on_behavior_obstacle)
client.message_callback_add("alphabot2/behavior/ir_right", on_behavior_ir_right)
client.message_callback_add("alphabot2/behavior/ir_left", on_behavior_ir_left)

client.loop_start()

if __name__ == '__main__':
    try:
        while True:
            time.sleep(0.2)
            
            data_list = [0, 0, 0, 0, 0, 0, 0]

            for idx, val in enumerate(obstacle_data_list):
                data_list[idx] = float(val)

            for idx, val in enumerate(ir_right_data_list):
                data_list[idx] = data_list[idx]+float(val)

            for idx, val in enumerate(ir_left_data_list):
                data_list[idx] = data_list[idx]+float(val)

            correct_idx = 0
            correct_value = 0

            for idx, val in enumerate(data_list):
                if val > correct_value:
                    correct_idx = idx
                    correct_value = val

            Vd = 50
            Vt = 25

            if correct_value == 0:
                correct_idx = 7
    
            if correct_idx == 0:
                # arrière gauche
                client.publish(client.TOPIC_MOTORS, str(-Vt)+" "+str(-Vt)) # "-25 -50"
            elif correct_idx == 1:
                # arrière
                client.publish(client.TOPIC_MOTORS, str(-Vd)+" "+str(-Vd)) # "-50 -50"
            elif correct_idx == 2:
                # arrière droit
                client.publish(client.TOPIC_MOTORS, str(-Vd)+" "+str(-Vt)) # "-50 -25"
            elif correct_idx == 3:
                # avant gauche
                client.publish(client.TOPIC_MOTORS, str(Vt)+" "+str(Vd)) # "25 50"
            elif correct_idx == 4:
                # avant
                client.publish(client.TOPIC_MOTORS, str(Vd)+" "+str(Vd)) # "50 50"
            elif correct_idx == 5:
                # avant droit
                client.publish(client.TOPIC_MOTORS, str(Vd)+" "+str(Vt)) # "50 25"
            elif correct_idx == 6:
                # demi-tour
                client.publish(client.TOPIC_MOTORS, str(Vd)+" "+str(0)) # "50 0"
            elif correct_idx == 7:
                # stop
                client.publish(client.TOPIC_MOTORS, "0 0") # "0 0"

    except KeyboardInterrupt:
        print("error")
