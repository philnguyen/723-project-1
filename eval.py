#!/usr/bin/python
import sys

def readData(filename):
    h = open(filename, 'r')
    words = []
    segmentations = []
    for l in h.readlines():
        a = l.split()
        if len(a) == 1:
            words.append(a[0])
            segmentations.append(None)
        elif len(a) == 2:
            words.append(a[0])
            segmentations.append(a[1])
    return (words, segmentations)

def evaluate(truth, hypothesis):
    I = 0
    T = 0
    H = 0
    for n in range(len(truth)):
        if truth[n] is None: continue
        t = truth[n].split('+')
        allT = {}
        cumSum = 0
        for ti in t:
            cumSum = cumSum + len(ti)
            allT[cumSum] = 1

        h = hypothesis[n].split('+')
        allH = {}
        cumSum = 0
        for hi in h:
            cumSum = cumSum + len(hi)
            allH[cumSum] = 1

        T = T + len(allT) - 1
        H = H + len(allH) - 1
        for i in allT.iterkeys():
            if allH.has_key(i):
                I = I + 1
        I = I - 1
        
    Pre = 1.0
    Rec = 0.0
    Fsc = 0.0
    if I > 0:
        Pre = float(I) / H
        Rec = float(I) / T
        Fsc = 2 * Pre * Rec / (Pre + Rec)
    return (Pre, Rec, Fsc)

def runEval(truthFile, hypFile, name):
    (tWords, tSegs) = readData(truthFile)
    (hSegs,  hNothing) = readData(hypFile)
    (Pre,Rec,Fsc) = evaluate(tSegs, hSegs)
    print Fsc, Pre, Rec, name

if __name__ == "__main__":
    runEval(sys.argv[1], sys.argv[2], sys.argv[3])
    
