import os
import argparse
import json
import cv2

#from  utils2 import  get_yolo_boxes, makedirs
#from bbox import draw_boxes
from tensorflow.keras.models import load_model
from tqdm import tqdm
import numpy as np
from flask import Flask, render_template, request, jsonify, Response, abort
import  tensorflow as tf
from  bbox1 import  draw_boxes, bboxes_info
from  utils3 import  get_yolo_boxes, makedirs



app = Flask(__name__, static_url_path='')


port = int(os.getenv('process.env.PORT', 9000))
host = int(os.getenv('process.env.IP'))


@app.route('/')
def root():
    return 'flask is running(1)'


# Draw bounding boxes on an image .
@app.route('/image',methods=['POST'])
def get_image():
    image1 = request.files.get('imageFile', '')
    imageData = request.files['imageFile'].read()
    npArrayImage = np.fromstring(imageData, np.uint8)
    image = cv2.imdecode(npArrayImage, cv2.IMREAD_UNCHANGED)

    if len(image.shape) > 2 and image.shape[2] == 4:
        # convert the image from RGBA2RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)



    # predict the bounding boxes
    boxes = get_yolo_boxes(infer_model, [image], net_h, net_w, config['model']['anchors'], obj_thresh, nms_thresh)[
            0]

    # draw bounding boxes on the image using labels
    draw_boxes(image, boxes, config['model']['labels'], obj_thresh)
    #print(image)
    # write the image with bounding boxes to file
    cv2.imwrite(output_path + 'detection.jpg', np.uint8(image))
    print("Image loaded to output folder")
    #return 'Image loaded to output folder'




    # prepare image for response
    _, img_encoded = cv2.imencode('.png', image)
    response = img_encoded.tostring()

    # remove temporary image
        #os.remove(image_name)
        
        
    try:
        return Response(response=response, status=200, mimetype='image/png')

    except FileNotFoundError:
        abort(404)

#  API that returns JSON with classes found in images

@app.route('/detect', methods=['POST'])
def detect():
    image1 = request.files.get('imageFile', '')
    imageData = request.files['imageFile'].read()
    npArrayImage = np.fromstring(imageData, np.uint8)
    image = cv2.imdecode(npArrayImage, cv2.IMREAD_UNCHANGED)

    if len(image.shape) > 2 and image.shape[2] == 4:
        # convert the image from RGBA2RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)


    # predict the bounding boxes
    boxes = get_yolo_boxes(infer_model, [image], net_h, net_w, config['model']['anchors'], obj_thresh, nms_thresh)[0]
    #boxList = draw_boxes(image, boxes, config['model']['labels'], obj_thresh)
    boxList = bboxes_info(image, boxes, config['model']['labels'], obj_thresh)

    #print('boxes', boxes)
    #print('boxList', boxList)
    print("=====--------------------------------------==>", boxes)
    return jsonify({
             "success": True,
             "data": boxList[0],
             "count": boxList[1],
             #"model_version": modelLoadInitzd.modelVersion
         })




if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
