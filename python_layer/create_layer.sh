cd python_layer
rm python_2.7.0.zip
rm -R python
rm -R site-packages
docker rm tflite_2.7.0
docker build -t tflite_2.7.0 .
docker run -d --name=tflite_2.7.0 tflite_2.7.0
docker cp tflite_2.7.0:/var/lang/lib/python3.9/site-packages .
mv site-packages python
zip -q -r ../src/birdid_layer/python_2.7.0.zip python
rm -R python


