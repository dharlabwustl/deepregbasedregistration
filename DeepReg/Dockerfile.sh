

docker pull nvcr.io/nvidia/rapidsai/rapidsai-core:23.04-cuda11.8-runtime-ubuntu22.04-py3.10
docker run --gpus all --rm -it \
    --shm-size=1g --ulimit memlock=-1 --ulimit stack=67108864 \
    -p 8888:8888 -p 8787:8787 -p 8786:8786 \
    nvcr.io/nvidia/rapidsai/rapidsai-core:23.04-cuda11.8-runtime-ubuntu22.04-py3.10


