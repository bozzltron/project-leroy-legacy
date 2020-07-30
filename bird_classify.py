# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#!/usr/bin/python3

"""
Coral Smart Bird Feeder

Uses ClassificationEngine from the EdgeTPU API to analyze animals in
camera frames. Sounds a deterrent if a squirrel is detected.

Users define model, labels file, storage path, deterrent sound, and
optionally can set this to training mode for collecting images for a custom
model.

"""
import sys
import argparse
import time
import re
import imp
import logging
import gstreamer
from edgetpu.classification.engine import ClassificationEngine
from PIL import Image
from playsound import playsound
from picamera import PiCamera
from time import sleep
from twython import Twython

# generate your own auth.py file with credentials
from auth import (
    app_key,
    app_key_secret,
    oauth_token,
    oauth_token_secret
)

twitter = Twython(app_key, app_key_secret,
                  oauth_token, oauth_token_secret)

#camera = PiCamera()

def take_a_picture(path, ext='png'):
    print('Take a picture!')
    tag = '%010d' % int(time.monotonic()*1000)
    name = '%s/hiRes-img-%s.%s' %(path,tag,ext)
    camera.capture(name)
    return name

def tweet(status, filename):
    imageFile = open(filename, 'rb')
    response = twitter.upload_media(media=imageFile)
    media_id = [response['media_id']]
    logging.info('media id : %s', response['media_id'])
    twitter.update_status(status=status, media_ids=media_id)

def save_data(image,results,path,ext='png'):
    """Saves camera frame and model inference results
    to user-defined storage directory."""
    tag = '%010d' % int(time.monotonic()*1000)
    name = '%s/img-%s.%s' %(path,tag,ext)
    image.save(name)
    print('Frame saved as: %s' %name)
    logging.info('Image: %s Results: %s', tag,results)
    return name

def load_labels(path):
    """Parses provided label file for use in model inference."""
    p = re.compile(r'\s*(\d+)(.+)')
    with open(path, 'r', encoding='utf-8') as f:
      lines = (p.match(line).groups() for line in f.readlines())
      return {int(num): text.strip() for num, text in lines}

def print_results(start_time, last_time, end_time, results):
    """Print results to terminal for debugging."""
    inference_rate = ((end_time - start_time) * 1000)
    fps = (1.0/(end_time - last_time))
    print('\nInference: %.2f ms, FPS: %.2f fps' % (inference_rate, fps))
    for label, score in results:
      print(' %s, score=%.2f' %(label, score))

def do_training(results,last_results,top_k):
    """Compares current model results to previous results and returns
    true if at least one label difference is detected. Used to collect
    images for training a custom model."""
    new_labels = [label[0] for label in results]
    old_labels = [label[0] for label in last_results]
    shared_labels  = set(new_labels).intersection(old_labels)
    if len(shared_labels) < top_k:
      print('Difference detected')
      return True

def user_selections():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True,
                        help='.tflite model path')
    parser.add_argument('--labels', required=True,
                        help='label file path')
    parser.add_argument('--top_k', type=int, default=3,
                        help='number of classes with highest score to display')
    parser.add_argument('--threshold', type=float, default=0.1,
                        help='class score threshold')
    parser.add_argument('--storage', required=True,
                        help='File path to store images and results')
    parser.add_argument('--sound', required=True,
                        help='File path to deterrent sound')
    parser.add_argument('--print', default=False, required=False,
                        help='Print inference results to terminal')
    parser.add_argument('--training', default=False, required=False,
                        help='Training mode for image collection')
    args = parser.parse_args()
    return args


def main():
    """Creates camera pipeline, and pushes pipeline through ClassificationEngine
    model. Logs results to user-defined storage. Runs either in training mode to
    gather images for custom model creation or in deterrent mode that sounds an
    'alarm' if a defined label is detected."""
    args = user_selections()
    print("Loading %s with %s labels."%(args.model, args.labels))
    engine = ClassificationEngine(args.model)
    labels = load_labels(args.labels)
    storage_dir = args.storage

    #Initialize logging files
    logging.basicConfig(filename='%s/results.log'%storage_dir,
                        format='%(asctime)s-%(message)s',
                        level=logging.DEBUG)

    last_time = time.monotonic()
    last_results = [('label', 0)]
    last_tweet = None

    def user_callback(image,svg_canvas):
        nonlocal last_time
        nonlocal last_results
        nonlocal last_tweet
     
        start_time = time.monotonic()
        results = engine.classify_with_image(image, threshold=args.threshold, top_k=args.top_k)
        end_time = time.monotonic()
        results = [(labels[i], score) for i, score in results]
    
        if args.print:
          print_results(start_time,last_time, end_time, results)

        if args.training:
          print("training mode")
          if do_training(results,last_results,args.top_k):
            save_data(image,results, storage_dir)
        else:
          print("looking for birds")
          # Custom model mode:
          # Save the images if the label is one of the targets and its probability is relatively high
          if results[0][1] >= 0.8:
            filename = save_data(image, results, storage_dir)
            if (last_tweet is None) or ((time.time() - last_tweet > 300 ) and results[0][1] >= 0.9):
              try:
                #imageFile = take_a_picture(storage_dir)
                status = "I'm %d percent sure this is a %s. #ai"%(results[0][1] * 100, results[0][0])
                logging.info('Trying to tweet : %s', status)
                logging.info('Reading file %s', filename)
                tweet(status, filename)
                last_tweet = time.time()
              except:
                logging.exception('Failed to send tweet')
                last_tweet = None

        last_results=results
        last_time = end_time
    result = gstreamer.run_pipeline(user_callback)

if __name__ == '__main__':
    main()
