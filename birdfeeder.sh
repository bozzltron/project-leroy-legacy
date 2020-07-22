#   Copyright 2019 Google LLC
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        https://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

#   Coral Smart Bird Feeder Script.
#   Automates running the bird_classify code.

#!/bin/bash

python3 bird_classify.py \
	--model /home/pi/Projects/project-birdfeeder/retrain-imprinting/retrained_imprinting_model.tflite \
	--labels /home/pi/Projects/project-birdfeeder/retrain-imprinting/retrained_imprinting_model.txt \
	--storage /home/pi/Projects/project-birdfeeder/storage \
	--sound sound_file.wav \
	--print True
