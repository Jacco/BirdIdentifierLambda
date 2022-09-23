
import json
import os
import boto3
from PIL import Image, ImageOps
from tflite_runtime.interpreter import Interpreter
import numpy as np
import io

RUNNING_IN_LAMBDA=os.environ.get("AWS_EXECUTION_ENV") is not None

def get_directory(dir):
    if RUNNING_IN_LAMBDA:
        return f'/var/task/' + dir
    else:
        return dir

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
    # img.save('./images/fitted.jpg')
    # img = tf.keras.utils.load_img(get_directory('images') + '/ekster.jpeg', target_size=(224,224), keep_aspect_ratio=True)
    # x = tf.keras.utils.img_to_array(img, dtype="float32")
    # y = tf.cast(x, tf.float32) / 255.0
    # z = tf.convert_to_tensor([y])
    # x = [
    #     { 'name': 'module/hub_input/images_uint8',
    #       'index': 170, 
    #       'shape': array([  1, 224, 224,   3], dtype=int32), 
    #       'shape_signature': array([  1, 224, 224,   3], dtype=int32), 
    #       'dtype': <class 'numpy.uint8'>, 
    #       'quantization': (0.0078125, 128), 
    #       'quantization_parameters': {
    #         'scales': array([0.0078125], dtype=float32), 
    #         'zero_points': array([128], dtype=int32), 
    #         'quantized_dimension': 0},
    #         'sparsity_parameters': {}
    #     }]
    #print(input_details[0]['index'])
    CLASSIFIER.set_tensor(170, img)
    CLASSIFIER.invoke()
    predictions = CLASSIFIER.get_tensor(171)[0]
    print(predictions)

def handler(event, context):
    s3_event = event.get('Records', [{}])[0].get('s3', {})
    bucket_name = s3_event.get('bucket', {}).get('name', '')
    object_key = s3_event.get('object', {}).get('key', '')
    fn, ext = os.path.splitext(object_key)
    if ext in ['.jpg', '.jpeg']:
        scores = analyze_image(bucket_name, object_key)

if __name__ == '__main__':
    with open("./src/birdid/test.json", "r") as f:
        event = json.load(f)
    handler(event, {})
