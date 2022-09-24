
import json
import os
import boto3
from PIL import Image, ImageOps
from tflite_runtime.interpreter import Interpreter
import numpy as np
import io
import csv

RUNNING_IN_LAMBDA=os.environ.get("AWS_EXECUTION_ENV") is not None

def get_model():
    # print(os.listdir('./'))
    interpreter = Interpreter(model_path='/opt/lite-model_aiy_vision_classifier_birds_V1_3.tflite')
    input_details = interpreter.get_input_details()
    print(input_details)
    output_details = interpreter.get_output_details()
    print(output_details)
    interpreter.allocate_tensors()
    return interpreter

CLASSIFIER=get_model()

BIRDS=[]
with open('/opt/nederland.csv', 'r') as f:
    for bird in csv.DictReader(f):
        BIRDS.append(bird)
BIRD_MAP={bird.get('id'):bird.get('dutch_name') for bird in BIRDS}

def analyze_image(bucket_name, object_key):
    print(bucket_name, object_key)
    client = boto3.resource('s3')
    bucket = client.Bucket(bucket_name)
    object = bucket.Object(object_key.replace('+', ' '))
    response = object.get()
    img = Image.open(response['Body'])
    img = ImageOps.fit(img, (224, 224))
    img = np.array(img)
    img = np.expand_dims(img, axis=0)
    CLASSIFIER.set_tensor(170, img)
    CLASSIFIER.invoke()
    scores = CLASSIFIER.get_tensor(171)[0]
    bird_scores = [
        { "idx": idx, "bird": BIRD_MAP.get(str(idx), {}), "score": '{0:.{1}f}%'.format(score / 255, 1), "raw_score": score } 
        for idx,score in enumerate(scores)]
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
