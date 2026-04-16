FROM ros:humble-ros-base

RUN apt update && apt install -y \
    python3-pip \
    python3-colcon-common-extensions \
    git \
    vim \
    i2c-tools \
    libgpiod-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ros_ws

RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc

CMD ["bash"]
