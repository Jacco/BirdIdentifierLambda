# Pull the base image with python 3.8 as a runtime for your Lambda
FROM public.ecr.aws/lambda/python:3.8

# Install OS packages for Pillow-SIMD
RUN yum -y install tar gzip zlib freetype-devel \
    gcc \
    ghostscript \
    lcms2-devel \
    libffi-devel \
    libimagequant-devel \
    libjpeg-devel \
    libraqm-devel \
    libtiff-devel \
    libwebp-devel \
    make \
    openjpeg2-devel \
    rh-python36 \
    rh-python36-python-virtualenv \
    sudo \
    tcl-devel \
    tk-devel \
    tkinter \
    which \
    xorg-x11-server-Xvfb \
    zlib-devel \
    && yum clean all

# Copy the earlier created requirements.txt file to the container
COPY src/birdid/requirements.txt ./

# Install the python requirements from requirements.txt
RUN python3.8 -m pip install -r requirements.txt
# Replace Pillow with Pillow-SIMD to take advantage of AVX2
RUN pip uninstall -y pillow && CC="cc -mavx2" pip install -U --force-reinstall pillow-simd

# Copy the earlier created app.py file to the container
COPY src/birdid/handler.py ./

# Download ResNet50 and store it in a directory
RUN mkdir -p model
COPY model/aiy_vision_classifier_birds_V1_1.tar.gz ./model/model.tar.gz
RUN tar -xf model/model.tar.gz -C model/
RUN rm -r model/model.tar.gz
COPY model/nederland.csv ./model/nederland.csv
RUN chmod ugo+rwx model
RUN chmod ugo+rwx model/saved_model.pb
RUN mkdir -p images
COPY images/* images/
# Set the CMD to your handler
CMD ["handler.handler"]