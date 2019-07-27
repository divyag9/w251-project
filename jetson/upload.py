import paho.mqtt.client as mqtt
from ibm_botocore.client import Config
import ibm_boto3
import time

cos_credentials={
  "apikey": "elN20BTDza8vvIUTFmGBAXE0XE5X_4mgI-OBgGQB3MrV",
  "endpoints": "https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints",
  "iam_apikey_description": "Auto-generated for key 4095d86e-6fff-4517-825c-3814efe3e35f",
  "iam_apikey_name": "Service credentials-1",
  "iam_role_crn": "crn:v1:bluemix:public:iam::::serviceRole:Writer",
  "iam_serviceid_crn": "crn:v1:bluemix:public:iam-identity::a/aab07460f21744099baab02e85a3685a::serviceid:ServiceId-0ca255c9-b402-4795-94ca-c9efef3b0924",
  "resource_instance_id": "crn:v1:bluemix:public:cloud-object-storage:global:a/aab07460f21744099baab02e85a3685a:6c62fd61-1c0f-44fa-bd15-3ffe9cf96b29::"
}

auth_endpoint = 'https://iam.bluemix.net/oidc/token'
service_endpoint = 'https://s3.us-south.cloud-object-storage.appdomain.cloud'

cos = ibm_boto3.resource('s3',
                         ibm_api_key_id=cos_credentials['apikey'],
                         ibm_service_instance_id=cos_credentials['resource_instance_id'],
                         ibm_auth_endpoint=auth_endpoint,
                         config=Config(signature_version='oauth'),
                         endpoint_url=service_endpoint)
i = 1
j = 1
def on_message(client, userdata, message):
	#print('in message upload')
        global i
	global j
	#if message.topic == 'remotestraw/image':
	print("image received on IBM VSI subscriber")
        key = 'strawberry' + str(i) + '.png'
	cos.Bucket(name='w251-divya').put_object(Key=key, Body=message.payload)
	print("image uploaded to object storage")
	i += 1

	#if message.topic == 'remotestraw/count':
		#print("count data received on IBM VSI subscriber", message.payload)
		#class_counts = list(message.payload)
                #print('class_count: ', class_counts)
                #file_name = 'strawberry_counts' + str(j) + '.csv'
		#cos.Bucket(name='w251-divya').upload_file('strawberry.txt', 'strawberry.txt')
                #print('uploaded test')
                #with open(file_name, 'wb') as csvFile:
			#writer = csv.writer(csvFile)
			#writer.writerow(['ripe_strawberry', class_counts[0]])
			#writer.writerow(['unripe_strawberry', class_counts[1]])
		
		#cos.Bucket(name='w251-divya').put_object(file_name, file_name) 
		#cos.Bucket(name='w251-divya').put_object(Key=key, Body=message.payload)
		#print("csv uploaded to object storage")
		#j += 1

# mosquitto broker on IBM VSI docker container
broker_address="172.18.0.1"
# creating new instance of client
client = mqtt.Client("strawsubremote")
#attach function to callback
client.on_message=on_message
#connect to broker
client.connect(broker_address,1883,200)
print('in upload')
client.subscribe("remotestraw/image",1)
#client.subscribe([("remotestraw/image",1),("remotestraw/count",1)])
#wait to process callback
time.sleep(4)

client.loop_forever()
