![3D Map](https://raw.githubusercontent.com/webtrackerxy/3dmap-gsv-cnn/master/img/map.png?token=AQQ3OJVXVOUIYP4T7AHZC4C7I4SAE)

# 3dmap-gsv-cnn

This repository consists the source code for my master thesis paper [3D Map System For Tree Monitoring In Hong Kong Using Google Street View Imagery And Deep Learning](https://www.isprs-ann-photogramm-remote-sens-spatial-inf-sci.net/V-3-2020/765/2020/). You may watch the demo video [here](https://www.youtube.com/watch?v=_mwtc2FmyUw) and the [presentation slides](https://www.youtube.com/watch?v=_mwtc2FmyUw) .

My paper describes using Convolutional Neural Networks (CNNs) based object detector and classifier – YOLOv3 with pretrained model for detecting tree object from Google Street View Images. After applying "field of view" filter and spatial clustering, the average distance between the detected trees and ground truth data was achieved within 3 meters for selected roads used for the experiment. The result is plotted in 3D Map for visualizing the tree position and distribution. Source code and workflow have been uploaded to GitHub for sharing.


Below image shows the workflow.
 ![workflow](https://raw.githubusercontent.com/webtrackerxy/3dmap-gsv-cnn/master/img/workflow.png?token=AQQ3OJWUSW6ZD3JH7JTTJR27I4ROA)

#####A. Tree Localization
1.  Download google street view images for selected roads
2. Image projection from equirectangular to perspective
3. YOLOv3 CNN processing
4. Tree geographic coordinate estimation
5. Apply Field-of-View filter
6. Spatial clustering for removing duplicated trees


Run in Ubuntu 16.4 

#####B. 3D Map Platform
Source data: 
iB1000Map 
Height Map

FME conversion Software:
Feature classes for building model
DTM for Terrain

Run in Windows 8

TO DO LIST:
1. To automate the workflow for processing all roads in Hong Kong.
