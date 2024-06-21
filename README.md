This is a repository of scripts for processing wire-plane LarTPC images to output 
crops around potential particle showers. This uses DBSCAN clustering on a masked
image of the third wireplane.

The scripts "submit_cropimages.py" and "run_cropimages.py" can be used to run 
cropimages.py on the cluster. Crops will be written to a folder called "trainingimages"
with subfolders "trueimages", "backgroundimages", and "contextimages".

Running this script will also create a list of imagepaths with their associated 
metadata called "imagedata.txt". The filepath that is written can be modified using 
the "mytag" variable in cropimage.py. This is useful if the processing of image crops (such as
creating slides) will be done somewhere else.

"clusterhistograms.py" is a script that can be used to create histograms from the root
trees created in cropimages.py. These histograms show data about the clusters output
from DBSCAN.

"createbeamer.py" is a script for creating a beamer from the imagedata.txt file. 
The usage is:
	-t textfile.txt -o slideshowname -m mode
where the mode can be "t" (and only slides of the true crops will be created) or any
other letter which will result in only slides of the background crops being created. It outputs
a slide for ech crop, along with the metadata. 


