![3D Map](https://raw.githubusercontent.com/webtrackerxy/3dmap-gsv-cnn/master/img/map.png?token=AQQ3OJVXVOUIYP4T7AHZC4C7I4SAE)

# 3dmap-gsv-cnn

This repository consists the source code for my master thesis paper [3D Map System For Tree Monitoring In Hong Kong Using Google Street View Imagery And Deep Learning](https://www.isprs-ann-photogramm-remote-sens-spatial-inf-sci.net/V-3-2020/765/2020/). You may watch the demo video [here](https://www.youtube.com/watch?v=_mwtc2FmyUw).

In densely built urban areas such as Hong Kong, the positive effect of urban trees is to help maintain high environmental and social sustainability for the city while unmanaged trees lead to negative effects such as accidents, outbreaks of pests and diseases. The public awareness of urban tree population has been increasing and preserving all the benefits offered by trees, a continuous monitoring concept would be required.

I developed this prototype for a 3D map of tree inventory which  is  based on automated tree detection from publicly available Google street view (GSV) panorama images.

First, Convolutional Neural Networks (CNNs) based object detector and classifier – YOLOv3 with pretrained model is adopted to learn GSV images to detect tree objects. GSV depth image has been utilized to decode depth values of each GSV panorama image and will provide accurate information to calculate the tree geographic position. 

A “field of view” filter was designed to remove duplicated tree detection within the overlapped areas followed by spatial clustering applied to further increase the tree localization accuracy.  The average distance between the detected trees and ground truth data was achieved within 3 meters for selected roads used for the experiment. 

Second, a 3D Map platform prototype for facilitating the urban tree monitoring and management was developed to interpret the results of tree records. With the help of webGL technology, contemporary browsers are able to show 3D buildings, terrain and other scene components together with the obtained tree records in an open source 3D GIS platform (CesiumJS) , the level of visualization is enhanced as all the detected trees are placed on the 3D digital terrain model. Consequently, it is easy for end-users to know the actual position of the trees and their distribution. 

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
