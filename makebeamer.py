#script that creates a beamer from a textfile with a list of image file paths and associated metadata using pylatex
#see https://jeltef.github.io/PyLaTeX/current/index.html

from pylatex import Document, Section, Subsection, Tabular, Command, Figure, Enumerate, HorizontalSpace
from pylatex.base_classes import Environment, Arguments, CommandBase
from pylatex.utils import  NoEscape
from array import array
import argparse as argparse
import os

#input to command line is a textfile and the name of the output beamer. 
    # eg: python3 createbeamer.py -t imagedata.txt -o slideshow -m mode

parser = argparse.ArgumentParser("Make Beamer")
parser.add_argument("-t", "--textfile", required=True, type=str, help="image data")
parser.add_argument("-o", "--outfile", required = True, type = str, help = "outputbeamerfile")
parser.add_argument("-m", "--mode", required=True, type=str, help="b = background, t=truth")
args = parser.parse_args()


mytag = "Users/elizabethpanner/Desktop/trainingimages/"
#define environments to use column and columns
class Columns(Environment):
    
    _latex_name = 'columns'

class Column(Environment):

    _latex_name = 'column'

class Vspace(CommandBase):

    _latex_name = 'vspace*'




def getRootname(filepath):
    rootname = filepath[filepath.find("merged"):]
    rootname = rootname.replace(rootname[rootname.find(".png"):], "")
    return rootname

def arrangeMetadata(metadata):
    dataList = []
    for item in range(0, 13):
        dataList.append("na")
    
    dataList[1] = "File: " + metadata[1]
    dataList[2] = "Event Number: " + metadata[2]
    dataList[3] = "Crop Number: " + metadata[3]
    if metadata[4] == "true":
        dataList[0] = "True"
    elif metadata[4] == "truecontext":
        dataList[0] == "True"
    elif metadata[4] == "background":
        dataList[0] = "Background"
    elif metadata[4] == "backgroundcontext":
        dataList[0] = "Background"
    elif metadata[4] == "trueunfiltered":
        dataList[0] = "True Unfiltered"
    elif metadata[4] == "truecontextunfiltered":
        dataList[0] = "True Unfiltered"
    elif metadata[4] == "backgroundunfiltered":
        dataList[0] = "Background Unfiltered"
    dataList[4] = "Current: " + metadata[5]
    dataList[5] = "Neutrino Type: " + metadata[7]
    if metadata[6] == "hasNu":
        dataList[6] = "Has neutrino keypoint"
    else:
        dataList[6] = "No neutrino keypoint found"
    dataList[7] = "Type of shower particle: " + metadata[8]
    dataList[8] = "Number of clusters within crop: " + metadata[9]
    dataList[9] = "Number of true showers: " + metadata[10]
    dataList[10] = "Energy (meV): " + metadata[11]
    dataList[11] = "Momentum (meV): " + metadata[12]
    dataList[12] = metadata[0]

    return dataList
    




if args.mode == "b":
    backgroundMode = True
else:
    backgroundMode = False

readfile = open(args.textfile, 'r')


metadata = []

metadataDict = {}

#examples of categories that could be created based on sorted metadata
trueImages = []
trueOneCluster = []
trueNoNu = []
trueNu = []
trueContext = []
background = []
backgroundOne = []

while True:
    line = readfile.readline()
    metadata = []
    if not line:
        break
    
    for word in line.split():
        metadata.append(word)
        
    #the line below assumes that the first entry in each line is the filepath of the image
    imagepath = "/" + metadata[0]
    if not os.path.exists(imagepath):
       continue

    # each entry in the dictionary will save the metadata with the associated filepath. The key will
	# be the type of image it is (cropped and/or unfiltered) along with the root filename, event number,
	# and crop number. This way different images from the same cluster can be accessed together.
    
    key = metadata[4] + metadata[1] + metadata[2] + metadata[3]
    metadataDict[key] = arrangeMetadata(metadata)
    name = metadata[1] + metadata[2] + metadata[3]
    
    if metadata[4] == "true":
        trueImages.append(name)
        if metadata[9] == "1":
            trueOneCluster.append(name)
        #if metadata[4] == "hasNu":
            #trueNu.append(imagepath)
        #else:
            #trueNoNu.append(imagepath)
            
    elif metadata[4] == "background" and backgroundMode:
        if metadata[9] == "1":
            backgroundOne.append(imagepath)
        else:
            background.append(imagepath)
    

if not backgroundMode:  
    ##########################################################################################
    #set the geometry options of the document of all true images
    geometry_options = {"tmargin": ".3cm", "lmargin":".1cm", "margin": ".1cm", "marginparsep": ".1cm"}

    #create a document of class beamer
    docTrue = Document(geometry_options=geometry_options, documentclass="beamer", fontenc = 'T1', inputenc = 'utf8', font_size= "tiny")



    #create a slide for each image in a given list
    for name in trueImages:
        docTrue.create(Section('Slide'))
        data = metadataDict["true" + name]

        with docTrue.create(Columns()):
            with docTrue.create(Column(arguments=Arguments((NoEscape(r".2\textwidth"))))):
        #create a bulleted list of the metadata for each image
                with docTrue.create(Enumerate(enumeration_symbol="*",
                                    options={})) as enum:
                    for i in range(0, 12):
                        enum.add_item(data[i])
                        
            with docTrue.create(Column(arguments=Arguments((NoEscape(r".8\textwidth"))))):
                with docTrue.create(Figure(position='t')) as fig_map:
                    fig_map.add_image("/" + data[12], width = '200px')
                   


                    

                with docTrue.create(Figure(position='b')) as fig_map2:
                    contextimage = metadataDict["truecontext" + name]
                    docTrue.append(Vspace(arguments=Arguments(NoEscape("-10cm"))))
                    fig_map2.add_image("/" + contextimage[12], width='200px')
                    

        docTrue.create(Section('Slide'))
        dataunfiltered = metadataDict["trueunfiltered" + name]

        with docTrue.create(Columns()):
            with docTrue.create(Column(arguments=Arguments((NoEscape(r".2\textwidth"))))):
        #create a bulleted list of the metadata for each image
                with docTrue.create(Enumerate(enumeration_symbol="*",
                                    options={})) as enum:
                    for i in range(0, 12):
                        enum.add_item(dataunfiltered[i])
                        
            with docTrue.create(Column(arguments=Arguments((NoEscape(r".8\textwidth"))))):
                with docTrue.create(Figure(position='t')) as fig_map:
                    fig_map.add_image("/" + dataunfiltered[12], width = '200px')
                   


                    

                with docTrue.create(Figure(position='b')) as fig_map2:
                    contextimageunfiltered = metadataDict["truecontextunfiltered" + name]
                    docTrue.append(Vspace(arguments=Arguments(NoEscape("-10cm"))))
                    fig_map2.add_image("/" + contextimageunfiltered[12], width='200px')
                   


    #Generate the beamer. This uses pdflatex by default.
    docTrue.generate_pdf(args.outfile + "true", clean_tex=False, clean=True)

    #######################################################################################################

    # #set the geometry options of the document of all true images with 1 crop found
    # geometry_options = {"tmargin": ".5cm", "lmargin":".5cm", "margin": ".5cm"}

    # #create a document of class beamer
    # docTrueOne = Document(geometry_options=geometry_options, documentclass="beamer", fontenc = 'T1', inputenc = 'utf8', font_size= "tiny")


    # #create a slide for each image in a given list
    # for image in trueOneCluster:
    #     docTrueOne.create(Section('Slide'))
        
    #     with docTrueOne.create(Columns()):
    #         with docTrueOne.create(Column(arguments=Arguments((NoEscape(r".2\textwidth"))))):
    #     #create a bulleted list of the metadata for each image
    #             with docTrueOne.create(Enumerate(enumeration_symbol="*",
    #                                 options={})) as enum:
    #                 for data in metadataDict[image]:
    #                     enum.add_item(data)
            
    #         with docTrueOne.create(Column(arguments=Arguments((NoEscape(r".8\textwidth"))))):
    #             with docTrueOne.create(Figure(position='h!')) as fig_map:
    #                 fig_map.add_image(image, width = '250px')

    # #Generate the beamer. This uses pdflatex by default.
    # docTrueOne.generate_pdf(args.outfile + "trueOne", clean_tex=False, clean=True)

    # ####################################################################################################

    # #set the geometry options of the document of all true images with neutrino
    # geometry_options = {"tmargin": ".5cm", "lmargin":".5cm", "margin": ".5cm"}

    # #create a document of class beamer
    # docTrueNu = Document(geometry_options=geometry_options, documentclass="beamer", fontenc = 'T1', inputenc = 'utf8', font_size= "tiny")



    # #create a slide for each image in a given list
    # for image in trueNu:
    #     docTrueNu.create(Section('Slide'))
        
    #     with docTrueNu.create(Columns()):
    #         with docTrueNu.create(Column(arguments=Arguments((NoEscape(r".2\textwidth"))))):
    #     #create a bulleted list of the metadata for each image
    #             with docTrueNu.create(Enumerate(enumeration_symbol="*",
    #                                 options={})) as enum:
    #                 for data in metadataDict[image]:
    #                     enum.add_item(data)
            
    #         with docTrueNu.create(Column(arguments=Arguments((NoEscape(r".8\textwidth"))))):
    #             with docTrueNu.create(Figure(position='h!')) as fig_map:
    #                 fig_map.add_image(image, width = '250px')

    # #Generate the beamer. This uses pdflatex by default.
    # docTrueNu.generate_pdf(args.outfile + "trueNu", clean_tex=False, clean=True)

    # ######################################################################################################

    # #set the geometry options of the document of all true images
    # geometry_options = {"tmargin": ".5cm", "lmargin":".5cm", "margin": ".5cm"}

    # #create a document of class beamer
    # docTrueNoNu = Document(geometry_options=geometry_options, documentclass="beamer", fontenc = 'T1', inputenc = 'utf8', font_size= "tiny")



    # #create a slide for each image in a given list
    # for image in trueNoNu:
    #     docTrueNoNu.create(Section('Slide'))
        
    #     with docTrueNoNu.create(Columns()):
    #         with docTrueNoNu.create(Column(arguments=Arguments((NoEscape(r".2\textwidth"))))):
    #     #create a bulleted list of the metadata for each image
    #             with docTrueNoNu.create(Enumerate(enumeration_symbol="*",
    #                                 options={})) as enum:
    #                 for data in metadataDict[image]:
    #                     enum.add_item(data)
            
    #         with docTrueNoNu.create(Column(arguments=Arguments((NoEscape(r".8\textwidth"))))):
    #             with docTrueNoNu.create(Figure(position='h!')) as fig_map:
    #                 fig_map.add_image(image, width = '250px')

    # #Generate the beamer. This uses pdflatex by default.
    # docTrueNoNu.generate_pdf(args.outfile + "trueNoNu", clean_tex=False, clean=True)

######################################################################################################



# ###################################################################################################
if backgroundMode:
    
    #set the geometry options of the document of all background images
    geometry_options = {"tmargin": ".5cm", "lmargin":".5cm", "margin": ".5cm"}

    #create a document of class beamer
    docBackground = Document(geometry_options=geometry_options, documentclass="beamer", fontenc = 'T1', inputenc = 'utf8', font_size= "tiny")



    #create a slide for each image in a given list
    for image in background:
        docBackground.create(Section('Slide'))
        
        with docBackground.create(Columns()):
            with docBackground.create(Column(arguments=Arguments((NoEscape(r".2\textwidth"))))):
        #create a bulleted list of the metadata for each image
                with docBackground.create(Enumerate(enumeration_symbol="*",
                                    options={})) as enum:
                    for data in metadataDict[image]:
                        enum.add_item(data)
            
            with docBackground.create(Column(arguments=Arguments((NoEscape(r".8\textwidth"))))):
                with docBackground.create(Figure(position='h!')) as fig_map:
                    fig_map.add_image(image, width = '250px')

    #Generate the beamer. This uses pdflatex by default.
    docBackground.generate_pdf(args.outfile + "background", clean_tex=False, clean=True)






########################################################################################
        #create a slide for each image in a given list
    for image in backgroundOne:
        docBackground.create(Section('Slide'))
        
        with docBackground.create(Columns()):
            with docBackground.create(Column(arguments=Arguments((NoEscape(r".2\textwidth"))))):
        #create a bulleted list of the metadata for each image
                with docBackground.create(Enumerate(enumeration_symbol="*",
                                    options={})) as enum:
                    for data in metadataDict[image]:
                        enum.add_item(data)
            
            with docBackground.create(Column(arguments=Arguments((NoEscape(r".8\textwidth"))))):
                with docBackground.create(Figure(position='h!')) as fig_map:
                    fig_map.add_image(image, width = '250px')

    #Generate the beamer. This uses pdflatex by default.
    docBackground.generate_pdf(args.outfile + "backgroundOne", clean_tex=False, clean=True)
