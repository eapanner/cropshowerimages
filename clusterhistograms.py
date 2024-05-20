import sys
import argparse
import ROOT as rt
import math as math

parser = argparse.ArgumentParser("Make Shower Info Plots")
parser.add_argument("-f", "--rootFile", required=True, type=str, help="nu overlay input")
parser.add_argument("-o", "--outdir", default="./", type=str, help="output file directory")
parser.add_argument("-v", "--versionTag", type=str, help="version")
args = parser.parse_args()


fnu = rt.TFile(args.rootFile)

numClustersSmallTree = fnu.Get("numClustersSmall")
numTrueClustersSmallTree = fnu.Get("numTrueClustersSmall")
smallClusterTree = fnu.Get("smallCluster")
bigClusterTree = fnu.Get("bigClusterTree")
trueSmallClusterTree = fnu.Get("trueSmallCluster")
trueBigClusterTree = fnu.Get("trueBigCluster")

rt.TH1.SetDefaultSumw2(rt.kTRUE)
rt.gStyle.SetOptStat(0)

truPixelsBig = rt.TH1F("truPixelsBig","",50, 0, 100)
truPixelsSmall = rt.TH1F("truPixelsSmall","",50, 0, 100)
pixelsBig = rt.TH1F("pixelsBig","",50, 0, 100)
pixelsSmall = rt.TH1F("pixelsSmall","",50, 0, 100)
clustersSmall = rt.TH1F("clustersSmall","",50, 0, 10)
truClustersSmall = rt.TH1F("truClustersSmall","",50, 0, 10)

#print("number of small clusters: ")
for i in range(numClustersSmallTree.GetEntries()):
    numClustersSmallTree.GetEntry(i)
    clustersSmall.Fill(numClustersSmallTree.numClustersSmall- 1)
    #print(numClustersSmallTree.numClustersSmall- 1)

#print("number of true clusters for small")
for i in range(numTrueClustersSmallTree.GetEntries()):
    numTrueClustersSmallTree.GetEntry(i)
    truClustersSmall.Fill(numTrueClustersSmallTree.numTrueClustersSmall - 1)
    #print(numTrueClustersSmallTree.numTrueClustersSmall - 1)

#print("number of pixels for big clusters: ")
for i in range(bigClusterTree.GetEntries()):
    bigClusterTree.GetEntry(i)
    if bigClusterTree.numPixelsBig > 0:
        pixelsBig.Fill(bigClusterTree.numPixelsBig)
        #print(bigClusterTree.numPixelsBig)
    
#print("number of true pixels big cluster")
for i in range(trueBigClusterTree.GetEntries()):
    trueBigClusterTree.GetEntry(i)
    if trueBigClusterTree.numTruePixelsBig > 0:
        truPixelsBig.Fill(trueBigClusterTree.numTruePixelsBig)
        #print(trueBigClusterTree.numTruePixelsBig)

#print("number of pixels true small clusters: ")
for i in range(trueSmallClusterTree.GetEntries()):
    trueSmallClusterTree.GetEntry(i)
    if trueSmallClusterTree.numTruePixelsSmall > 0:
        truPixelsSmall.Fill(trueSmallClusterTree.numTruePixelsSmall)
        #print(trueSmallClusterTree.numTruePixelsSmall)

#print("number of pixels small clusters: ")
for i in range(smallClusterTree.GetEntries()):
    smallClusterTree.GetEntry(i)
    if smallClusterTree.numPixelsSmall > 0:
        pixelsSmall.Fill(smallClusterTree.numPixelsSmall)
        #print(smallClusterTree.numPixelsSmall)
   
    
  


    
truPixelsBig.SetTitle("Number of Pixels for True Clusters (First)")
truPixelsBig.GetXaxis().SetTitle("number of pixels")
truPixelsBig.GetYaxis().SetTitle("count")


truPixelsSmall.SetTitle("Number of Pixels for True Clusters (Second)")
truPixelsSmall.GetXaxis().SetTitle("number of pixels")
truPixelsSmall.GetYaxis().SetTitle("count")

pixelsSmall.SetTitle("Number of Pixels for All Clusters (Second)")
pixelsSmall.GetXaxis().SetTitle("number of pixels")
pixelsSmall.GetYaxis().SetTitle("count")

pixelsBig.SetTitle("Number of Pixels for All Clusters (First)")
pixelsBig.GetXaxis().SetTitle("number of pixels")
pixelsBig.GetYaxis().SetTitle("count")

truClustersSmall.SetTitle("Number of Clusters (True) ")
truClustersSmall.GetXaxis().SetTitle("number of clusters")
truClustersSmall.GetYaxis().SetTitle("count")

clustersSmall.SetTitle("Number of Clusters")
clustersSmall.GetXaxis().SetTitle("number of clusters")
clustersSmall.GetYaxis().SetTitle("count")

canv1 = rt.TCanvas("canv1")
truPixelsBig.SetStats(1)
rt.gStyle.SetOptStat(100001110)
truPixelsBig.Draw("PFC")

canv2 = rt.TCanvas("canv2")
truPixelsSmall.SetStats(1)
rt.gStyle.SetOptStat(100001110)
truPixelsSmall.Draw("PFC")

canv3 = rt.TCanvas("canv3")
pixelsBig.SetStats(1)
rt.gStyle.SetOptStat(100001110)
pixelsBig.Draw("PFC")

canv4 = rt.TCanvas("canv4")
pixelsSmall.SetStats(1)
rt.gStyle.SetOptStat(100001110)
pixelsSmall.Draw("PFC")

canv5 = rt.TCanvas("canv5")
clustersSmall.SetStats(1)
rt.gStyle.SetOptStat(100001110)
clustersSmall.Draw("PFC")

canv6 = rt.TCanvas("canv6")
truClustersSmall.SetStats(1)
rt.gStyle.SetOptStat(100001110)
truClustersSmall.Draw("PFC")

outfile = rt.TFile("clusterPlots"+args.versionTag+".root","RECREATE")
canv1.Write()
canv2.Write()
canv3.Write()
canv4.Write()
canv5.Write()
canv6.Write()

truPixelsBig.Write()
truPixelsSmall.Write()
pixelsBig.Write()
pixelsSmall.Write()
clustersSmall.Write()
truClustersSmall.Write()
