FROM public.ecr.aws/lambda/python:3.9

WORKDIR /tflite

RUN pip3 install numpy pillow tflite-runtime==2.7.0

CMD tail -f /dev/null