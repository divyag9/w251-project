Setup on jetson and cloud

#### Steps performed:
##### Jetson
1. create network bridge

   sudo docker network create --driver bridge project
   
2. create mosquitto container using Dockerfile.mosquitto

   sudo docker run --name mosquitto --network project -p 1883:1883 mosquitto
   
3. create image detector container using Dockerfile.testfrcnn

   sudo docker run --name detector --device=/dev/video1:/dev/video1 -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v ~/251:/251 --network project --rm --privileged -ti projecttestfrcnn sh
   
   once inside bash run - python3 detector.py
   
4. create forwarder container to forward the messages(boxed images of strawberries) to VSI(Dockerfile.forwarder)

   sudo docker run --name forwarder -v ~/251/Project:/251 --network project -ti --rm projforwarder sh
   
   once inside shell client run - python forwarder.py

##### IBM VSI
1. create network bridge

   docker network create --driver bridge project
   
2. create mosquitto container

   docker run --name mosquitto --network project -p 1883:1883 mosquitto
   
3. create upload container to upload the boxed detected strawberries to object storage(Dockerfile.subscribercloud)

   docker run --name subscriber -v ~/251:/251 --network project -ti --rm subscriber sh
   
   once inside shell client run - python upload.py
   

Note:

1. I was not able to uplaod the model to github, but to run you need to have model_frcnn.hdf5 in the same directory where you are running the detector

2. Also make sure there are no files in TestData/images directory. To show how the structure looks i just created a sample file in it otherwise github will not let me have the folder structure
