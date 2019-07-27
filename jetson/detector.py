import numpy as np
import cv2
import csv
import os
import paho.mqtt.client as mqtt
from test_frcnn import detect_images
from s3_upload import upload_to_aws

print('before mqtt')
# mosquitto broker address
broker_address="172.19.0.1"
#create new instance of client
client = mqtt.Client("strawpub")
#connect to broker
print('before connect')
client.connect(broker_address)
print('after mqtt')

# 1 should correspond to /dev/video1 , your USB camera. The 0 is reserved for the TX2 onboard camera
cap = cv2.VideoCapture(1)
cv2.namedWindow("Target")
image_counter = 0

# s3 config
BUCKET = 'w251'

while(True):
	# Capture frame-by-frame
	ret, frame = cap.read()
	print('before key waiting')
	# key capture the click
	key = cv2.waitKey(1) & 0xFF
	print('key waiting')
	# if the key pressed is 'c' then capture the image and process it
	if key == ord("c"):
		print('key pressed')
		# capturing the image and writing to TestData/images directory
		image_name = f'TestData/images/strawberries_{image_counter}.png'
		cv2.imwrite(image_name, frame)
		#cv2.imshow('Target', frame)
		cv2.destroyAllWindows()
		
		#rc, full_png = cv2.imencode('.png', img)
		#original_bytes = full_png.tobytes()
		# publish the original image
		#client.publish("strawberry/image", original_bytes, 1)

		print('captured image written')
		# running the model to detect ripe and unripe strawberries
		coordinates = detect_images('TestData/images')
		print('after coordinates')
		inner_image_counter = 0
		# index 0 stores ripe strawberry count index 1 unripe strawberry count
		class_counter = [0,0]
		for (straw_class,x1,y1,x2,y2) in coordinates:
			strawberry = frame[y1:y2, x1:x2]
			#cv2.imwrite(f'strawberries_{image_counter}_{inner_image_counter}.png', strawberry)
			rc, png = cv2.imencode('.png', strawberry)
			image_bytes = png.tobytes()
			
			# keep track of the count for each class
			if straw_class == 'ripe_strawberry':
				class_counter[0] += 1
			elif straw_class == 'unripe_strawberry':
				class_counter[1] += 1
			
			inner_image_counter += 1
		   
			# publish the boxed ripe and unripe strawberries
			client.publish("strawberry/image", image_bytes, 1)

        	

		# write to csv
		file_name = f'TestData/images/strawberries_{image_counter}.csv'
		with open(file_name, 'w') as csvFile:
			writer = csv.writer(csvFile)
			writer.writerow(['ripe_strawberry', class_counter[0]])
			writer.writerow(['unripe_strawberry', class_counter[1]])

		# writing to s3
		upload_to_aws(file_name, BUCKET, file_name)
		upload_to_aws(image_name, BUCKET, image_name)
		
		# convert the data about counts into bytes
		#count_bytes = bytes(class_counter)
		# publish class,counts
		#client.publish("strawberry/count", count_bytes, 1)
		print('done with image')

		# remove the processed image
		if os.path.exists(image_name):
			os.remove(image_name)
		# remove the csv
		if os.path.exists(file_name):
			os.remove(file_name)

	image_counter+= 1
	print('image counter', image_counter)

cap.release()
cv2.destroyAllWindows()
