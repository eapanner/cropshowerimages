# Import python modules and the plotly library
import os,sys # python modules
import plotly as pl # the entire plotly library
import plotly.graph_objects as go # provides functions to generate plot objects
import numpy as np # numpy library, provides definition of array data type used by plotly as input
import argparse
import plotly.io
from array import array
# Import the ROOT library
import ROOT as rt
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
# import our ubdl libraries
from larlite import larlite # defines data products
from larcv import larcv # defines data products focused around dealing with images for deep learning
from ublarcvapp import ublarcvapp # provides functions that helps connect larlite and larcv data
from larflow import larflow # library for reconstruction functions
from collections import namedtuple
import math as math
from helpers.larflowreco_ana_funcs import *
# classes and functions in the larutil namespace provides access to detector parameters
from larlite import larutil 
# our convenience functions that makes plotly plots from larlite or larcv data objects
import lardly
apply_sce = False

xptana = ublarcvapp.mctools.CrossingPointsAnaMethods


reco2tag = "/merged_dlreco_"
mytag = "Users/elizabethpanner/Desktop"
clustertag = "/cluster/tufts/wongjiradlabnu/epanne01"

def getMom(shower):

    showmom = math.sqrt(shower.Start().Px()*shower.Start().Px() + shower.Start().Py()*shower.Start().Py() + shower.Start().Pz()*shower.Start().Pz())
    return showmom

def kinetic (totale, mom):
    mass = math.sqrt(totale**2 - mom**2)
    return (totale - mass)


def getCandidateDistance(pos, show):
    truthShowerTrunkSCE = ublarcvapp.mctools.TruthShowerTrunkSCE()
    showSCE = truthShowerTrunkSCE.applySCE(show)
    showSCE_startPos = showSCE.Vertex()

    x1 = showSCE_startPos.X()
    y1 = showSCE_startPos.Y()
    z1 = showSCE_startPos.Z()

    x2 = pos[0]
    y2 = pos[1]
    z2 = pos[2]

    return math.sqrt(abs((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2))

mcNuVertexer = ublarcvapp.mctools.NeutrinoVertex()

parser = argparse.ArgumentParser("Make Image Crops")
parser.add_argument("-f", "--rootfiles", required=True, type=str, help="nu overlay input")
parser.add_argument("-r", "--recofiles", required = True, type = str, nargs = "+", help = "input kpsreco files")
parser.add_argument("-o", "--outdir", default="./", type=str, help="output file directory")
parser.add_argument("-v", "--versionTag", type=str, help="versiontag")
args = parser.parse_args()




# create instances of classes that are used to run various algorithms

# makes an image where pixels have value 1.0 if is due to bad wire channel, else 0.0 for good wire
badchmaker = ublarcvapp.EmptyChannelAlgo() 

inputfiles = args.rootfiles
outdir = args.outdir

filepairs = getFiles(reco2tag, args.recofiles, inputfiles)

outRootFile = rt.TFile("/cluster/tufts/wongjiradlabnu/epanne01/trainingimages/clusterdata" + args.versionTag + ".root", "RECREATE")


# Set names for getting images
wire_tree_name = "wire"
thrumu_tree_name = "thrumu" 
showerscore3_tree_name = "ubspurn_plane2"
segment_tree_name = "segment"

truefail = 0
numevents = 0
numfailed = 0
numcrops = 0

numTruePixelsBig = array('f', [0.])
numPixelsBig = array('f', [0.])
numTruePixelsSmall = array('f', [0.])
numPixelsSmall = array('f', [0.])
numClustersSmall = array('f', [0.])
numTrueClustersSmall = array('f', [0.])

nTPB = []
nPB = []
nTPS = []
nPS = []
nCS = []
nTCS = []


# create trees that will record information about the number of pixels per cluster and number
# of clusters for each round of clustering
smallClusterTree = rt.TTree("smallCluster", "smallCluster")
smallClusterTree.Branch("numPixelsSmall", numPixelsSmall, 'numPixelsSmall/f')

bigClusterTree= rt.TTree("bigClusterTree", 'bigClusterTree/f')
bigClusterTree.Branch("numPixelsBig", numPixelsBig, 'numPixelsBig/f')

trueSmallClusterTree = rt.TTree("trueSmallCluster", "trueSmallCluster")
trueSmallClusterTree.Branch("numTruePixelsSmall", numTruePixelsSmall, "numTruePixelsSmall/f")

trueBigClusterTree = rt.TTree("trueBigCluster", "trueBigCluster")
trueBigClusterTree.Branch("numTruePixelsBig", numTruePixelsBig, "numTruePixelsBig/f")

numClustersSmallTree = rt.TTree("numClustersSmall", "numClustersSmall")
numClustersSmallTree.Branch("numClustersSmall", numClustersSmall, 'numClustersSmall/f')

numTrueClustersSmallTree = rt.TTree("numTrueClustersSmall", "numTrueClustersSmall")
numTrueClustersSmallTree.Branch("numTrueClustersSmall", numTrueClustersSmall, 'numTrueClustersSmall/f')



# Initialize an storage_manager instance that will read out input file
for pair in filepairs:
    f = pair[1]
    ioll = larlite.storage_manager( larlite.storage_manager.kREAD )
    ioll.add_in_filename(pair[1])
    if not os.path.exists(f):
       raise ValueError("Did not find input file: ", f)
    ioll.set_verbosity(1)
    ioll.open()

    kpsfile = rt.TFile(pair[0])
    kpst = kpsfile.Get("KPSRecoManagerTree")

    try:
        nKPSTEntries = kpst.GetEntries()
    except:
        print("%s is empty. skipping...."%(pair[0]))
        ioll.close()
        iolcv.finalize()
        kpsfile.Close()
        continue

    errorfile = open("/cluster/tufts/wongjiradlabnu/epanne01/trainingimages/errorfile.txt", "a")
    infofile = open("/cluster/tufts/wongjiradlabnu/epanne01/trainingimages/imagedata.txt", "a")

    filename = f
    rootname = f.replace(".root", "_")
    rootname = rootname.replace("/cluster/tufts/wongjiradlabnu/nutufts/data/v2_me_05/epem_DarkNu_BenchmarkD/merged_dlreco/", '')
    #create a text file where we will write the information about each image

    # We use the larcv IOManager class to load the trees for us.


    iolcv = larcv.IOManager( larcv.IOManager.kREAD, "larcv", larcv.IOManager.kTickForward )

    iolcv.add_in_file(f)
    iolcv.initialize()


    # Now we load an event
    nentries = ioll.get_entries()
    ientry = 0
    while ientry < nentries and ientry < 15:
        numTruePixelsBig[0 ]= -1
        numPixelsBig[0] = -1
        numTruePixelsSmall[0] = -1
        numPixelsSmall[0] = -1
        numClustersSmall[0] = -1
        numTrueClustersSmall[0] = -1

        nTPB = []
        nPB = []
        nTPS = []
        nPS = []
        nCS = []
        nTCS = []


        ioll.go_to(ientry)
        iolcv.read_entry(ientry)
        kpst.GetEntry(ientry)
        numevents += 1 

        if kpst.run != ioll.run_id() or kpst.subrun != ioll.subrun_id() or kpst.event != ioll.event_id():
               print("EVENTS DON'T MATCH!!")
               print("truth run/subrun/event %i/%i/%i"%(ioll.run_id(), ioll.subrun_id(), ioll.event_id()))
               print("reco run/subrun/event %i/%i/%i"%(kpst.run, kpst.subrun, kpst.event))
               print("reco file: ", pair[0])
               print("truth file: ", pair[1])
               continue

        print("ientry", ientry)    
        ioll.go_to(ientry)
        iolcv.read_entry(ientry)
        ientry += 1
        #Get neutrino truth information 
        mc_truth = ioll.get_data(larlite.data.kMCTruth, "generator")
        gtruth = mc_truth.at(0)
        try:
            Neutrino = gtruth.GetNeutrino()
        except TypeError:
            print("couldn't find neutrino")
            continue

        # check to see if neutrino is in fiducial volume
        sce = larutil.SpaceChargeMicroBooNE()
        mcNuVertex = mcNuVertexer.getPos3DwSCE(ioll, sce)
        trueVtxPos = rt.TVector3(mcNuVertex[0], mcNuVertex[1], mcNuVertex[2])


        # Get the containers holding the mctrack and mcshower objects


        event_mcshower = ioll.get_data( larlite.data.kMCShower, "mcreco" )

        numShowers = event_mcshower.size()

        twoshower = False

        if numShowers == 2:
            twoshower = True

        time = []
        trueZ = []
        showerlist = []
        thisdict = {}
        for ishower in range(numShowers):
            
            shower = event_mcshower.at(ishower)
            showerpdg = shower.PdgCode()
            if shower.PdgCode == 22:
                det = shower.DetPofile()
            else:
                det = shower

            showmom = getMom(shower)

# record the position and time of each shower. The position must be scaled by a factor of 1/.3 and the time must be scaled by a factor of 1/6. The momentum of each shower is stored in thisdict and indexed by the position. The time of each shower is stored in thisdict and indexed by the momentum.

            trueZ.append(round(shower.DetProfile().Z() / .3))
            thisdict[trueZ[ishower]] = showmom
            thisdict[showmom] = round(1008 - (ublarcvapp.mctools.CrossingPointsAnaMethods.getTick(shower.DetProfile()) - 2400) /6)
            time.append(round(1008 - (ublarcvapp.mctools.CrossingPointsAnaMethods.getTick(shower.DetProfile()) - 2400) /6))

        #Wire images

        wire_ev_img = iolcv.get_data(larcv.kProductImage2D,wire_tree_name)
        wire_adc_v = wire_ev_img.as_vector()

        #thrumu images for both events

        thrumu_ev_img = iolcv.get_data(larcv.kProductImage2D,thrumu_tree_name)
        thrumu_adc_v = thrumu_ev_img.as_vector()

        ## Plot parts of wire with non-zero shower score
        showerscore3_ev_img = iolcv.get_data(larcv.kProductImage2D,showerscore3_tree_name)
        showerscore3_adc_v = showerscore3_ev_img.as_vector()

        thrumu_image = thrumu_adc_v.at(2)
        wire_image = wire_adc_v.at(2)

        metathru = thrumu_image.meta()
        metawire = wire_image.meta()

        imgnpthru = np.transpose(larcv.as_ndarray(thrumu_image), (1,0))
        imgnpwire = np.transpose(larcv.as_ndarray(wire_image),(1,0))

        if metathru.plane() in [0,1]:
            imgnpthru = imgnpthru[:,0:2400]
            maxx = 2400.0
        else:
            maxx = metathru.max_x()


        if metawire.plane() in [0,1]:
            imgnpwire = imgnpwire[:,0:2400]
            
        xaxis = np.linspace(metathru.min_x(), maxx, endpoint=False, num=int(maxx/metathru.pixel_width()))
        yaxis = np.linspace(metathru.min_y(), metathru.max_y(), endpoint=False, num=metathru.rows())

        unfiltered = np.copy(imgnpwire)
        wire_image3 = imgnpwire - imgnpthru

        wire_image3[wire_image3<0] = 0
        wire_image3[wire_image3>200] = 200

        shower3_image = showerscore3_adc_v.at(0)

        metashow3 = shower3_image.meta()
        metawire3 = wire_image.meta()

        imgnpshow3 = np.transpose(larcv.as_ndarray(shower3_image), (1,0))
        imgnpwire3 = wire_image3

        imgnpshow3 = imgnpshow3[:,0:2400]
        maxx = 2400.0

        imgnpwire3 = imgnpwire3[:, 0:2400]

        imgnpshow3[imgnpshow3 < 0] = 0
        imgnpshow3[imgnpshow3 >200] = 200

        imgnpwire3[imgnpwire3 < 0] = 0
        imgnpwire3[imgnpwire3 >200] = 200

        xaxis = np.linspace(metawire3.min_x()*.3, maxx*.3, endpoint=False, num=int(maxx/metawire3.pixel_width()))
        yaxis = np.linspace( metawire3.min_y()*.0555, metawire3.max_y()*.0555, endpoint=False, num=metawire3.rows())

        #impose a threshold of .5 shower score for each image

        imgnpdiffshow3 = np.empty([1008, 2400])
        a = np.where(imgnpshow3 < .5)
        b = np.where(imgnpshow3 >= .5)
        imgnpdiffshow3[a] = 0
        imgnpdiffshow3[b] = 1
        tocluster=np.copy(imgnpdiffshow3)

        
        outofrange = False
        badfile = ''
        
        #add a line across the image for the true position and time of the shower

        for position in trueZ:
            try:
                imgnpdiffshow3[:, round(position)] = .3
                toindex = thisdict[position]
                print(position)
                
                timepos = thisdict[toindex]
                imgnpdiffshow3[timepos, :] = .3

                imgnpdiffshow3[10, :] = .6
                imgnpdiffshow3[:, 10] = .6

            #record files where the position is out of range

            except IndexError:
                outofrange = True
                if rootname == badfile:
                    continue
                else:
                    errorfile.write(rootname + '\n')
                    badfile = rootname

                
        #plot the wireplane with the mask. Saved within the "contextimages" folder.

        diffshow3map = {
        "type": "heatmap",
        "z":imgnpdiffshow3,
        "x":xaxis,
        "y":yaxis,
        "colorscale":"Blackbody",
        }

        fig = go.Figure(data=diffshow3map)
        imagename = "/trainingimages/contextimages/" + rootname + "_" + str(ientry) + "fdiffshow3.png"
        fig.write_image(clustertag + imagename, scale=5)
            

        ## Create clusters for third shower plane. Use scaled x and y coordinates of non-zero values to find clusters
        ######################

        pointvx = []
        pointvy = []
        for i in range(0, tocluster.shape[0]):
            for j in range(0, tocluster.shape[1]):
                if tocluster[i, j] > 0:
                    pointvy.append(i*.055)
                    pointvx.append(j*.3)

        pointarr = [pointvx, pointvy]
        pointnump = np.array(pointarr)
        pointnump = np.transpose(pointnump)
        df3 = pd.DataFrame(pointnump)

        
        show3cluster = DBSCAN(eps=6.0, min_samples=40).fit(pointnump)

        df3['cluster'] = show3cluster.labels_


        df3_filtered=df3[df3.cluster>-1]
        labelset = set(show3cluster.labels_)

        #if no clusters were made create a "context" image
        if len(labelset) <= 1:
            print("made no clusters")

            # Look at the reconstruction to see if a neutrino was found

        
            noNu = True

            vertices = kpst.nuvetoed_v 
            
            for vtx in vertices:
                if vtx.keypoint_type != 0:
                    noNu = True
                else:
                    noNu = False

            category = ''
            momentum = ''
            energy = ''
            for ishower in range(numShowers):
                
                shower = event_mcshower.at(ishower)
                pdgcode = shower.PdgCode()
                if pdgcode == 11:
                    category += "e-"
                elif pdgcode == -11:
                    category += "e+"
                elif pdgcode == 22 or pdgcode == -22:
                    category += "photon"
                else:
                    category += "other " + str(pdgcode)

                if Neutrino.CCNC() == 0:
                    current = "CC"
                else:
                    current = "NC"
                if Neutrino.Nu().PdgCode()==12:
                    nutype = "nue"
                else:
                    nutype = "numu"

                if noNu == True:
                    hasNu = "hasNu"
                else:
                    hasNu = "noNu"


            numshowers = str(event_mcshower.size())

                
            for position in range(len(trueZ)):
                toadd = str(thisdict[trueZ[position]]) + ","
                momentum += toadd
                
            for ishower in range(numShowers):
                shower = event_mcshower.at(ishower)
                energy+= (str(kinetic(shower.Start().E(), getMom(shower))) + ", ")

            #create the string that will be written to the "info" file. Because no clusters were found here, many of these are irrelevant in this case. Format is:
            # 1. filepath
            # 2. name of root file, 
            # 3. event entry number
            # 4. crop number, 
            # 5. image type (ie context, true, background, etc.), 
            # 6. current, 
            # 7. neutrino type, 
            # 8. shower type, 
            # 9. energy, 
            # 10. momentum, 
            # 11. whether a neutrino was found 
            # 12. the number of showers.
            towrite = mytag + imagename + "    " + rootname + "    " + ientry + "    " + "contextnocluster" + "    " + current + "    " + nutype + "    " + category + "    " + energy + "    " + momentum + "     " + hasNu +  "    " + str(numShowers) + '\n'

            infofile.write(towrite)
            continue

        # If there were clusters, plot the clustering. Will be written to the "context" folder.
        fig = px.scatter(x=df3_filtered[0], y=df3_filtered[1], color=df3_filtered['cluster'], range_x=(0, 720), range_y=(0, 55.44))
        clustername = "/trainingimages/contextimages/" + rootname + "_" + str(ientry) + "fcluster3.png"
        fig.write_image(clustertag + clustername, scale=5)

        
        # Go through the reconstruction to find if there was a reconstructed neutrino. 
        
        noNu = True

        vertices = kpst.nuvetoed_v 


        ##Find the neutrino
        
        for vtx in vertices:
            if vtx.keypoint_type != 0:
                noNu = True
            else:
                noNu = False


        category = ''
        
        for ishower in range(numShowers):
            shower = event_mcshower.at(ishower)
            pdgcode = shower.PdgCode()
            if pdgcode == 11:
                category += " e-"
            elif pdgcode == -11:
                category += " e+"
            elif pdgcode == 22 or pdgcode == -22:
                category += " photon"
            else:
                category += " other " + str(pdgcode)

        if Neutrino.CCNC() == 0:
            current = "CC"
        else:
            current = "NC"
        if Neutrino.Nu().PdgCode()==12:
            nutype = "nue"
        else:
            nutype = "numu"

        if noNu == True:
            hasNu = "hasNu"
        else:
            hasNu = "noNu"

        numshowers = str(event_mcshower.size())

        momentum = ""
        energy = ""
        for position in range(len(trueZ)):
            toadd = str(thisdict[trueZ[position]]) + ","
            momentum += toadd
        
        for ishower in range(numShowers):
                shower = event_mcshower.at(ishower)
                energy+= (str(kinetic(shower.Start().E(), getMom(shower))) + ", ")


        #Go through each cluster and determine if it represents a true shower. Create crops around each cluster.


        for label in labelset:
            failed = False
            oglable = label
            if label == -1:
                continue
            
            #record the number of pixels in the cluster
            nPB.append(len(df3_filtered[df3_filtered['cluster']==label]))
            
            
            if(len(df3_filtered[df3_filtered['cluster']==label])<30):
                continue
            
            numcrops += 1
            cluster = pd.DataFrame(df3_filtered[df3_filtered['cluster'] == label])
            
            minx = round(min(cluster[0]/.3)) - 64
            maxx = round(max(cluster[0]/.3)) + 64
            miny = round(min(cluster[1]/.055)) - 64
            maxy = round(max(cluster[1])/.055) + 64
            if minx < 0:
                minx = 0
            if maxx >= 2400:
                maxx=2399
            if miny < 0:
                miny = 0
            if maxy >= 1008:
                maxy = 1007
                
            trueshow = False
            
            
            #determine if the true shower and time are within the crop range
            for ishower in range(numShowers):
                if (minx < trueZ[ishower] and maxx > trueZ[ishower]) and (miny < time[ishower] and maxy > time[ishower]):
                    trueshow = True
                    
                    #record the number of pixels for the true clusters
                    nTPB.append(len(df3_filtered[df3_filtered['cluster']==label]))
                    continue
                     

            
            clusterimage = tocluster[miny:maxy, minx:maxx]
            
            tocluster2 = clusterimage

            # Add a box in the wireplane image around the crop
            otherimage = np.copy(imgnpdiffshow3)
            otherimage[miny:maxy, maxx] = .6
            otherimage[miny:maxy, minx] = .6
            otherimage[miny, minx:maxx] = .6
            otherimage[maxy, minx:maxx] = .6

            # Add a box in the unfiltered wireplane image around the crop
            unfilteredcontext = np.copy(unfiltered)
            unfilteredcrop = unfiltered[miny:maxy, minx:maxx]
            unfilteredcontext[miny:maxy, maxx] = 400
            unfilteredcontext[miny:maxy, minx] = 400
            unfilteredcontext[miny, minx:maxx] = 400
            unfilteredcontext[maxy, minx:maxx] = 400
            
            #plot the cluster crop and the context images

            figmap = {
                        "type": "heatmap",
                        "z":clusterimage,
                        "colorscale":"Blackbody",
                    }
            figmap2 = {
                        "type": "heatmap",
                        "z":otherimage,
                        "colorscale":"Blackbody",
                    }

            figmap3 = {
                        "type": "heatmap",
                        "z":unfilteredcrop,
                        "colorscale":"Blackbody",

            }

            figmap4 = {
                        "type": "heatmap",
                        "z":unfilteredcontext,
                        "colorscale":"Blackbody",

            }

            # recluster each crop

            pointvx2 = []
            pointvy2 = []

            for i in range(0, tocluster2.shape[0]):
                for j in range(0, tocluster2.shape[1]):
                    if tocluster2[i, j] > 0:
                        pointvy2.append(i*.055)
                        pointvx2.append(j*.3)


            pointarr2 = [pointvx2, pointvy2]
            pointnump2 = np.array(pointarr2)
            pointnump2 = np.transpose(pointnump2)
            dfagain = pd.DataFrame(pointnump2)

            recluster = DBSCAN(eps=2, min_samples=40).fit(pointnump2)

            dfagain['cluster'] = recluster.labels_

            # this variable will record whether the re-clustering eliminated a true shower crop
            istruefail = False

            dfagain_filtered=dfagain[dfagain.cluster>-1]
            labelset2 = set(recluster.labels_)
            for label2 in labelset2:
               
                nPS.append(len(dfagain_filtered[dfagain_filtered['cluster']==label2]))
               
                if trueshow:
                  
                    nTPS.append(len(dfagain_filtered[dfagain_filtered['cluster']==label2]))
                       
            numlabels = len(labelset2)
            
            # Record the number of clusters made in the second clustering
            nCS.append(numlabels)
            
            if trueshow:
                nTCS.append(numlabels)
               
            # Record whether the re-clustering failed (if there is less than  1 cluster created)
            if numlabels  < 1:
                numfailed += 1
                if trueshow:
                    truefail += 1
                    istruefail = True


            if trueshow:
                # Create image crops for each cluster that passed the second round. 
                # 1 -> the crop 
                # 2 -> the full wireplane image
                # 3 -> the crop without the mask
                # 4 -> the full wireplane image without the mask (with a box around the crop area)

                filename1 = "/trainingimages/trueimages/" + rootname  + "_" + str(ientry)+ "_"  +  str(label) + ".png"
                filename2 = "/trainingimages/trueimages/" + rootname + "_" + str(ientry) + "context" + str(label) + ".png"
                filename3 = "/trainingimages/trueimages/" + rootname + "_" + str(ientry) + "unfiltered" + str(label) + ".png"
                filename4 = "/trainingimages/trueimages/" + rootname + "_" + str(ientry) + "unfilteredcontext" + str(label) + ".png"

                fig1 = go.Figure(data=figmap)
                fig1.write_image(clustertag + filename1, scale=5)
                

                fig2 = go.Figure(data=figmap2)
                fig2.write_image(clustertag + filename2, scale=5)
                

                fig3 = go.Figure(data=figmap3)
                fig3.write_image(clustertag + filename3, scale=5)
                

                fig4 = go.Figure(data=figmap4)
                fig4.write_image(clustertag + filename4, scale=5)
                
                # Strings that will be written to the "info" file.

                towrite= mytag + filename1  + "    " + rootname + "    " + str(ientry) +"     " + str(label) + "    " + "true" + "     " + current + "     " + hasNu + "    " + nutype + "    " + category + "    " + str(numlabels) + "    " + str(numShowers) + "    " + energy + "     " + momentum + '\n' 

                towrite2= mytag + filename2  + "    " + rootname +  "    " + str(ientry) + "     " + str(label) + "    " + "truecontext" + "     " + current + "     " + hasNu + "    " + nutype + "    " + category + "    "  + str(numlabels) + "    " + str(numShowers) + "    " + energy + "     " + momentum + '\n'

                towrite3= mytag + filename3  + "    " + rootname + "    " + str(ientry) + "     " + str(label) + "    " + "trueunfiltered" + "     " + current + "     " + hasNu + "    " + nutype + "    " + category + "    "  + str(numlabels) + "    " + str(numShowers) + "    " + energy + "     " + momentum + '\n'

                towrite4= mytag + filename4  + "    " + rootname + "     " + str(ientry) + "    " + str(label) + "    " + "truecontextunfiltered" + "     " + current + "     " + hasNu + "    " + nutype + "    " + category + "    "  + str(numlabels) + "    " + str(numShowers) + "    " + energy + "     " + momentum + '\n'

                infofile.write(towrite)
                infofile.write(towrite2)
                infofile.write(towrite3)
                infofile.write(towrite4)
            
            # Plot the same for the background images (except the unfiltered context image)
            else:
                
                    filename1 = "/trainingimages/backgroundimages/" + rootname  + str(ientry) + "_" + str(label) + ".png"
                    filename2 = "/trainingimages/backgroundimages/" + rootname  + str(ientry) + "_" + "unfiltered" + str(label) + ".png"
                    filename3 = "/trainingimages/backgroundimages/" + rootname  + str(ientry) + "_" + "context" + str(label) + ".png"
                    

                    fig = go.Figure(data=figmap)
                    fig2 = go.Figure(data=figmap2)
                    fig3 = go.Figure(data=figmap3)

                    towrite = (mytag + filename1 + "     " + rootname + "    " +  str(ientry) + "    " + str(label) + "     " + "background" + "    " + current + "    " + hasNu + "    " + nutype + "    " + category +  "    " + str(numlabels) + "    " + str(numShowers) + "    " + energy + "    " + momentum + '\n')
                    towrite1 = (mytag + filename2 + "     " + rootname + "    " + str(ientry) + "    " + str(label) + "     " + "backgroundcontext" + "    " + current + "    " + hasNu + "    " + nutype + "    " + category +  "    " + str(numlabels) + "    " + str(numShowers) + "    " + energy + "    " + momentum + '\n')
                    towrite2 = (mytag + filename3 + "     " + rootname + "    " + str(ientry) + "    " + str(label) + "     " + "backgroundunfiltered" + "    " + current + "    " + hasNu + "    " + nutype + "    " + category +  "    " + str(numlabels) + "    " + str(numShowers) + "    " + energy + "    " + momentum + '\n')

                    infofile.write(towrite)
                    infofile.write(towrite1)
                    infofile.write(towrite2)
                    fig.write_image(clustertag + filename1, scale=5)
                    fig2.write_image(clustertag + filename2, scale=5)
                    fig3.write_image(clustertag + filename3, scale=5)
                    

        #Record the information about crop and pixel numbers in the root trees.

        for pixel in nTPB:
            numTruePixelsBig[0] = pixel
            trueBigClusterTree.Fill()
            

        
        for pixel in nPB:
            numPixelsBig[0] = pixel
            bigClusterTree.Fill()
            

        
        for pixel in nTPS:
            numTruePixelsSmall[0] = pixel
            trueSmallClusterTree.Fill()
            

    
        for pixel in nPS:
            numPixelsSmall[0] = pixel
            smallClusterTree.Fill()
            

        
        for cluster in nCS:
            numClustersSmall[0] = cluster
            numClustersSmallTree.Fill()
            

        
        for cluster in nTCS:
            numTrueClustersSmall[0] = cluster
            numTrueClustersSmallTree.Fill()
            

    ioll.close()
    iolcv.finalize()
    kpsfile.Close()
    outRootFile.cd()
    numClustersSmallTree.Write()
    numTrueClustersSmallTree.Write()
    smallClusterTree.Write()
    trueSmallClusterTree.Write()
    bigClusterTree.Write()
    trueBigClusterTree.Write()

outRootFile.Close()
    
infofile.close()
errorfile.close()

#Print information about the total numbers of events, crops, and crops that failed the second round of clustering.
print("number of events", numevents)
print("number of crops:", numcrops)
print("number of fails:", numfailed)
print("number of true fails", truefail)
