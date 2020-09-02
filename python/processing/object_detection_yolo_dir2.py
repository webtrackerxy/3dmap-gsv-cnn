# This code is written at BigVision LLC. It is based on the OpenCV project. It is subject to the license terms in the LICENSE file found in this distribution and at http://opencv.org/license.html

# Usage example:  
#                 python3 object_detection_yolo.py --path=image/path

import cv2 as cv
import argparse
import sys
import numpy as np
import os.path
import os,glob
import time

# Initialize the parameters
confThreshold = 0.5  #Confidence threshold
nmsThreshold = 0.4  #Non-maximum suppression threshold

inpWidth = 416  #608     #Width of network's input image
inpHeight = 416 #608     #Height of network's input image

parser = argparse.ArgumentParser(description='Object Detection using YOLO in OPENCV')
parser.add_argument('--path', help='Path to image path.')
#parser.add_argument('--video', help='Path to video file.')
args = parser.parse_args()
        
# Load names of classes
classesFile = "classes.names";

classes = None
with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')

# Give the configuration and weight files for the model and load the network using them.

modelConfiguration = "/home/bluesky/bin/tree/darknet-yolov3.cfg";
modelWeights = "/home/bluesky/bin/tree/weights/darknet-yolov3_final.weights";
#modelWeights = "/home/bluesky/bin/tree/weights/darknet-yolov3_1200.weights";


net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

# Get the names of the output layers
def getOutputsNames(net):
    # Get the names of all the layers in the network
    layersNames = net.getLayerNames()
    # Get the names of the output layers, i.e. the layers with unconnected outputs
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# Draw the predicted bounding box
def drawPred(classId, conf, left, top, right, bottom):
    # Draw a bounding box.
    #    cv.rectangle(frame, (left, top), (right, bottom), (255, 178, 50), 3)
    cv.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)

    label = '%.2f' % conf
        
    # Get the label for the class name and its confidence
    if classes:
        assert(classId < len(classes))
        label = '%s:%s' % (classes[classId], label)

    #Display the label at the top of the bounding box
    labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    top = max(top, labelSize[1])
    cv.rectangle(frame, (left, top - round(1.5*labelSize[1])), (left + round(1.5*labelSize[0]), top + baseLine), (0, 0, 255), cv.FILLED)
    #cv.rectangle(frame, (left, top - round(1.5*labelSize[1])), (left + round(1.5*labelSize[0]), top + baseLine),    (255, 255, 255), cv.FILLED)
    cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 2)

# Remove the bounding boxes with low confidence using non-maxima suppression
def postprocess(frame, outs, file, image_file):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]

    classIds = []
    confidences = []
    boxes = []
    # Scan through all the bounding boxes output from the network and keep only the
    # ones with high confidence scores. Assign the box's class label as the class with the highest score.
    classIds = []
    confidences = []
    boxes = []
    boxes_center = []

    detect = False
    for out in outs:
        print("out.shape : ", out.shape)
        for detection in out:
            #if detection[4]>0.001:
            scores = detection[5:]
            classId = np.argmax(scores)
            #if scores[classId]>confThreshold:
            confidence = scores[classId]
            if detection[4]>confThreshold:
                print(detection[4], " - ", scores[classId], " - th : ", confThreshold)
                print(detection)
                detect = True
            if confidence > confThreshold:
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])
                boxes_center.append([center_x, center_y])

    # Perform non maximum suppression to eliminate redundant overlapping boxes with
    # lower confidences.
    indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        drawPred(classIds[i], confidences[i], left, top, left + width, top + height)
        cv.circle(frame, (int(boxes_center[i][0]),int(boxes_center[i][1]+height/2)), 2, (255, 0, 0) , 3)

        print(file)
        f = open(file, "a")
        f.write(str(classIds[i]) +","+ image_file  + ","+ str(confidences[i])+"," + str(left)+ ","+ str(top) +","+ str(left + width)+
            ","+ str(top + height)+","+str(boxes_center[i][0]) + ","+str(boxes_center[i][1])+"\r\n")
        f.close()        

    return detect


road_array = []
#road_array.append("GLOUCESTER ROAD") #
#road_array.append("HENNESSY ROAD") #
#road_array.append("MAN CHEUNG STREET")
#road_array.append("LOCKHART ROAD")
#road_array.append("JOHNSTON ROAD")
#road_array.append("LUNG WO ROAD")
##road_array.append("UPPER ALBERT ROAD") #
#road_array.append("LOWER ALBERT ROAD") #
#road_array.append("GARDEN ROAD") #
#road_array.append("KENNEDY ROAD") #
#road_array.append("MACDONNELL ROAD") #
#road_array.append("HORNSEY ROAD") #
#road_array.append("ROBINSON ROAD") #
#road_array.append("CONDUIT ROAD") #
#road_array.append("LYTTELTON ROAD") #
#road_array.append("LEE NAM ROAD") #
#road_array.append("SHEK PAI WAN ROAD") # --
#road_array.append("CYBERPORT ROAD") #
#road_array.append("VICTORIA ROAD") #
road_array.append("POK FU LAM ROAD") #
road_array.append("SHING SAI ROAD") #
road_array.append("BONHAM ROAD") #
road_array.append("HOSPITAL ROAD")
road_array.append("PO SHAN ROAD") # --
road_array.append("STUBBS ROAD") #--
road_array.append("MOUNT BUTLER DRIVE")

for each_road in road_array:
    args.path2 = args.path + "/" + each_road + "/perspective/"
    print(args.path2)

    # Process inputs
    if not os.path.isdir(args.path2):
        print(args.path2 + " is not directory")
    else:
        print(args.path2 + " is a directory")  

    process_path = args.path2 + "processed"

    if not os.path.exists(process_path):
        os.makedirs(process_path)

    processed_tree_file = process_path + "/trees_detected.txt"
    f = open(processed_tree_file, "w")
    f.close()

    for file in glob.glob(args.path2+"*.jpg"):

        file_name=os.path.basename(file)
        #print(os.path.splitext(file))
        #print(file,file_name)

        # Open the image file
        if not os.path.isfile(file):
            print("Input image file ", file, " doesn't exist")
            sys.exit(1)
        cap = cv.VideoCapture(file)
        outputFile = process_path + "/"  + file_name[:-4]+'_yolo_out_py.jpg'
        print(outputFile)

            
        # get frame from the video
        hasFrame, frame = cap.read()
        
        # Create a 4D blob from a frame.
        blob = cv.dnn.blobFromImage(frame, 1/255, (inpWidth, inpHeight), [0,0,0], 1, crop=False)

        # Sets the input to the network
        net.setInput(blob)

        # Runs the forward pass to get output of the output layers
        outs = net.forward(getOutputsNames(net))

        # Remove the bounding boxes with low 
        detected = postprocess(frame, outs, processed_tree_file, file_name)
        print("Detected:", detected)

        # Put efficiency information. The function getPerfProfile returns the overall time for inference(t) and the timings for each of the layers(in layersTimes)
        t, _ = net.getPerfProfile()
        label = 'Inference time: %.2f ms' % (t * 1000.0 / cv.getTickFrequency())
        #cv.putText(frame, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))

        # Write the frame with the detection boxes
        if detected:
            cv.imwrite(outputFile, frame.astype(np.uint8))
        
        cap.release()
        time.sleep(0.2)

