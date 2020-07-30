#!/bin/bash

cd /usr/share/edgetpu/examples/

TRAINING_DIR=/home/pi/Projects/project-birdfeeder/retrain-imprinting

printf '\nExpecting Female House Sparrow'
python3 classify_image.py \
--model ${TRAINING_DIR}/retrained_imprinting_model.tflite \
--label ${TRAINING_DIR}/retrained_imprinting_model.txt \
--image ${TRAINING_DIR}/test_images/female-sparrow-1.png
