import numpy as np
import cv2
import csv
import os
import platform
import datetime
import paho.mqtt.client as mqtt
from test_frcnn import detect_images
from s3_upload import upload_to_aws

# mosquitto broker address
broker_address="172.19.0.1"
#create new instance of client
client = mqtt.Client("strawpub")
#connect to broker
client.connect(broker_address)

# 1 should correspond to /dev/video1 , your USB camera. The 0 is reserved for the TX2 onboard camera
cap = cv2.VideoCapture(1)
#cv2.namedWindow("Target")
image_counter = 0
csv_file_name = f'TestData/csv/strawberries.csv'

# s3 config
BUCKET = 'w251'

while(True):
	# Capture frame-by-frame
	ret, frame = cap.read()
	# key capture the click
	key = cv2.waitKey(1) & 0xFF
	cv2.imshow('frame', frame)
	# if the key pressed is 'c' then capture the image and process it
	if key == ord("c"):
		# capturing the image and writing to TestData/images directocry
		image_name = f'TestData/images/strawberries_{image_counter}.png'
		cv2.imwrite(image_name, frame)
		#cv2.imshow('Target', frame)
		#cv2.destroyAllWindows()
		
		#rc, full_png = cv2.imencode('.png', img)
		#original_bytes = full_png.tobytes()
		# publish the original image
		#client.publish("strawberry/image", original_bytes, 1)

		print('captured image written')
		# running the model to detect ripe and unripe strawberries
		coordinates = detect_images('TestData/images')
		inner_image_counter = 0
		# index 0 stores ripe strawberry count index 1 unripe strawberry count
		class_counter = [0,0]
		#print('coordinate: ', coordinates)
		for (straw_class,x1,y1,x2,y2) in coordinates:
			strawberry = frame[y1:y2, x1:x2]
			#print('strawberry: ', strawberry)
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
		current_dt = str(datetime.datetime.now())
		device_name = platform.node()
		mode = 'a' if os.path.exists(csv_file_name) else 'w'
		with open(csv_file_name, mode) as csvFile:
			writer = csv.writer(csvFile)
			writer.writerow([current_dt, device_name, 'ripe_strawberry', class_counter[0]])
			writer.writerow([current_dt, device_name, 'unripe_strawberry', class_counter[1]])

		# writing to s3
		upload_to_aws(csv_file_name, BUCKET, csv_file_name)
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
		#if os.path.exists(file_name):
			#os.remove(file_name)

	image_counter+= 1

cap.release()
cv2.destroyAllWindows()
