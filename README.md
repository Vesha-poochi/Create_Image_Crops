# Create_image_crops

This repository primarily focusses on creating 3D crops from huge datasets of images obtained from light microscopy. 

Why will this be useful?
To train a ML algorithm to segment specific features from tissues/organs, small crops from specific regions of interest need to be created first. 

The repository contains 2 files:

LoadAndCropImage.py lets the user select the channel on which the crop needs to be created. It then automatically creates crops randomly and makes sure that each of the 3D crops that are saved are not fully blank. We can choose the dimensions (in x,y and z) of the crops that are needed and also choose the % of non-emptiness that each crop needs to have (Default is 0.12). It uses entropy filter, Otsu's thresholding, binary filters to check if the crop in handed is fully empty. 

Crop_n5_PyQt5.py   This is the latest file, that lets the user fully interact with the big data and then choose the kind of crops they want. I used dask to be able to visualize the full complete dataset on napari and then have a GUI that lets the user select all of their specifications that are needed for them.  (Nobody needs to have any knowledge about programming wile using this GUI and that is something that I am absolutely proud of achieving!!! especially since it was all self-taught!)
