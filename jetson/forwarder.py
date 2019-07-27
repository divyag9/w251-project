import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, message):
    print("message received on jetson subscriber", str(message.topic))
    remote_client.publish('remotestraw/image', message.payload, 1)
    #if message.topic == 'strawberry/image':
        #print('in straw')
        #remote_client.publish('remotestraw/image', message.payload, 1)
    #else:
	#print ('message: ', message.payload)
        #remote_client.publish('remotestraw/count', message.payload, 1)
    #print("message published to cloud topic")

def image_callback(client, userdata, message):
    print("message received on jetson subscriber", str(message.topic))
    try:
        remote_client.publish('remotestraw/image', message.payload, 1)
    except Exception as e:
	print('exception occured')
        print(e)

def count_callback(client, userdata, message):
    print("message received on jetson subscriber", str(message.topic))
    try:
        remote_client.publish('remotestraw/count', message.payload, 1)
    except Exception as e:
	print('exception occured')
        print(e)

# remote mosquitto broker address on IBM virtual server
remote_broker_address="169.45.10.136"
#create new instance of client
remote_client = mqtt.Client("strawpubremote")
#authentication
remote_client.username_pw_set(username="root",password="KhQBku6s")
#connect to broker
remote_client.connect(remote_broker_address,1883,1000)

# mosquitto broker on jetson docker container
broker_address="172.19.0.1"
# creating new instance
client = mqtt.Client("strawsub")
# attach function to callback
client.on_message=on_message
#client.message_callback_add("strawberry/image", image_callback)
#client.message_callback_add("strawberry/count", count_callback)
#connect to broker
client.connect(broker_address)
print('in forwareder')

# subscribe to topics
#client.subscribe([("strawberry/image",1),("strawberry/count",1)])
client.subscribe("strawberry/image",1)

#wait to process callback
time.sleep(4)


client.loop_forever()
