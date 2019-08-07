## W251 Final Project
### Detecting Ripe and Unripe Strawberries in an Image
##### Ahsen Qamar, David Hou, Divya Gorantla, Lance Miles

This GitHub repo contains relevant code used to build out the cloud instance for training as well as deploy the trained models on Jetson for inference and storage of data in the cloud.

It is important to note that we used the following

#### Data - Images and Annotations
* **StrawberryFieldData** - Contains data aggregated from visiting strawberry farms in Santa Cruz
* **TestData** - Contains images stored for testing our model
* **TrainData** - Contains images and annotations for training our model

#### Deployment - Jetson TX2
* **Jetson** - Contains all files needed for deployment of model onto Jetson TX2 - Includes Docker Files for building MQTT messaging system to store data in the cloud

#### Model Training and Inference
It is important to note that the model used came for training and inference came from the following source:
https://github.com/kbardool/keras-frcnn

Please clone kbardool's repo if you would like to replicate this project.

* **download.sh** - Shell script used in cloud instance to download and spin up relevant files
* **strawberries.build** - Docker build file used to spin up container for training
* **ModelTraining.ipynb** - Notebook used to run the training script
* **TestAnalysis.ipynb** - Notebook used to gather results from testing our models
* **XMLtoTXT_BoundingBoxExtraction.ipynb** - Notebook used to gather bounding box coordinates from each XML file to write into a txt file for training
* **annotate_full_train.txt** - Annotations in format needed to pass data into faster-rcnn training script
* **augment.ipynb** - Testing out augmentations on images
* **config.pickle** - Config file for training and inference
* **requirements.txt** - Install relevant requirements in order to run the training script
* **runInference.ipynb** - Run the test script on selected epochs as well as selected images
* **test_frcnn.py** - Original test script provided by kbardool for running inference
* **test_frcnn_iou.py** - Modified test script to derive key metrics to evaluate model performance on test images
* **train_frcnn_tensorboard.py** - Modified training script to hook up tensorboard
* **utils.py** - utilities file for augmenting data
