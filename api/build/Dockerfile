# base image
FROM python:3.10.4-buster

# set working directory
WORKDIR /usr/src/app

# this is absolutely not needed anymore 
RUN apt-get update && apt-get install -y \
    libc6 \
    libc6-dev \
    libfreetype6-dev \
    libjpeg-dev  \
    zlib1g-dev \
    python3-dev \
    gcc \
    musl-dev \
    linux-headers-amd64 \
    build-essential \
    python-pil \
    && rm -rf /var/lib/apt/lists/*


RUN groupadd -g 1000 galleryapp && \
    useradd -r -u 1000 -g galleryapp galleryapp

RUN chown -R galleryapp:galleryapp /usr/src/app 
RUN mkdir /home/galleryapp
RUN chown -R galleryapp:galleryapp /home/galleryapp


USER galleryapp

ENV PATH=/home/galleryapp/.local/bin:$PATH

COPY requirements.txt .

RUN pip install -r requirements.txt
