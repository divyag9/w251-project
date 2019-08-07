apt-get update
wget http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_10.0.130-1_amd64.deb
dpkg -i cuda-repo-ubuntu1604_10.0.130-1_amd64.deb
# the cuda 10.0 key
apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub
# install it!
apt-get update
apt-get install cuda

apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
	
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"	

apt-get update


# Dima validated on 01/13/19 that this below is still required; sigh
# apt-get install docker-ce=5:18.09.0~3-0~ubuntu-xenial
# As of 2/24/19 this works now
apt-get install -y docker-ce

#mkdir -m 777 /data
#mkfs.ext4 /dev/xvdc

#echo "/dev/xvdc /data                   ext4    defaults,noatime        0 0" >> /etc/fstab

#mount /data

#service docker stop
#cd /var/lib
#cp -r docker /data
#rm -fr docker
#ln -s /data/docker ./docker
#service docker start

curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | \
  sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
apt-get update

apt-get install -y nvidia-docker2
pkill -SIGHUP dockerd

docker run --runtime=nvidia --rm nvidia/cuda nvidia-smi

apt-get update

apt-get install git

cd /root/

git clone https://github.com/kbardool/keras-frcnn.git
git clone https://github.com/divyag9/w251-project.git

docker build -t strawberry -f w251-project/strawberries.build .

docker run --rm --runtime=nvidia -it -p 8888:8888 -d strawberry