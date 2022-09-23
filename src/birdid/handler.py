from typing import OrderedDict, Tuple
from pathlib import Path

import boto3
import json
import os
import tensorflow as tf
import numpy as np
from PIL import Image, ImageOps
import csv

RUNNING_IN_LAMBDA=os.environ.get("AWS_EXECUTION_ENV") is not None

def get_directory(dir):
    if RUNNING_IN_LAMBDA:
        return f'/var/task/' + dir
    else:
        return dir

def get_model() -> Tuple:
    return tf.saved_model.load(get_directory('model'))

MODEL=get_model()

BIRDS=[]
with open(get_directory('model') + '/nederland.csv', 'r') as f:
    for bird in csv.DictReader(f):
        BIRDS.append(bird)
BIRD_MAP={bird.get('id'):bird.get('dutch_name') for bird in BIRDS}


def analyze_image(bucket_name, object_key):
    if event:
        print(bucket_name, object_key)
        client = boto3.resource('s3')
        bucket = client.Bucket(bucket_name)
        object = bucket.Object(object_key.replace('+', ' '))
        response = object.get()
        img = Image.open(response['Body'])
        img = ImageOps.fit(img, (244, 244))
        # img.save('./images/fitted.jpg')
    else:
        img = tf.keras.utils.load_img(get_directory('images') + '/ekster.jpeg', target_size=(224,224), keep_aspect_ratio=True)
    x = tf.keras.utils.img_to_array(img, dtype="float32")
    y = tf.cast(x, tf.float32) / 255.0
    z = tf.convert_to_tensor([y])

    output = MODEL.signatures["image_classifier"](z)
    scores = [x.numpy() for x in output['logits'][0]]
    bird_scores = [{ "idx": idx, "bird": BIRD_MAP.get(str(idx), {}), "score": '{0:.{1}f}%'.format(score * 100, 1), "raw_score": score } for idx,score in enumerate(scores)]
    bird_scores.sort(key=lambda x: x.get("raw_score", 0), reverse=True)
    bird_scores = bird_scores[:5]
    return bird_scores


def handler(event, context):
    s3_event = event.get('Records', [{}])[0].get('s3', {})
    bucket_name = s3_event.get('bucket', {}).get('name', '')
    object_key = s3_event.get('object', {}).get('key', '')
    fn, ext = os.path.splitext(object_key)
    if ext in ['.jpg', '.jpeg']:
        scores = analyze_image(bucket_name, object_key)
        s3 = boto3.resource('s3')
        s3object = s3.Object(bucket_name, fn + '.json')
        s3object.put(
            Body=(bytes(json.dumps(scores, indent=2, default=str).encode('UTF-8')))
        )
    else:
        print('skipping no image', object_key, ext)

if __name__ == '__main__':
    with open("./src/birdid/test.json", "r") as f:
        event = json.load(f)
    handler(event, {})