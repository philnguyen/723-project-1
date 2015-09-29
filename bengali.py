from FSM import *
import FSM
from util import *
import util

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

def fancySourceModel(segmentations):
      # 
      # unigrams
#       tokens = 0
#       uni = Counter()
#       uni['end'] = 1
#       for s in segmentations:
#         for c in s:
#             uni[c] = uni[c] + 1
#             tokens += 1
#       types = len(uni.keys())
#       denom = tokens + types
#       for c in uni.keys():
#         uni[c] = uni[c]/denom
#
#       # compute all bigrams
#       bi = {}
#       for s in segmentations:
#           prev = 'start'
#           for c in s:
#               if not bi.has_key(prev): bi[prev] = Counter()
#               bi[prev][c] = bi[prev][c] + 1
#               prev = c
#           if not bi.has_key(prev): bi[prev] = Counter()
#           bi[prev]['end'] = bi[prev]['end'] + 1
#
#       for prev in bi.iterkeys():
#           for c in uni.keys():
#               if bi[prev][c] == 0:
#                  bi[prev][c] = uni[c]
#               else:
#                  types = len(bi[prev].keys())
#                  tokens = uni[prev]
#                  denom = types + tokens
#                  bi[prev][c] =  bi[prev][c]/denom
#
#       for prev in bi.iterkeys():
#          for c in uni.iterkeys():
#              bi[prev][c] = bi[prev][c] + .15
#          bi[prev].normalize()

#       # convert to a FSA
#       fsa = FSM.FSM(isProbabilistic=True)
#       fsa.setInitialState('start')
#       fsa.setFinalState('end')
#
#       for i in bi.iterkeys():
#           for c in bi[i].iterkeys():
#               if c == 'end':
#                   fsa.addEdge(i, c, None, None, prob=bi[i][c])
#               else:
#                   fsa.addEdge(i, c, c, c, prob=bi[i][c])
#
#       return fsa
    # compute all bigrams
    lm = {}
    vocab = {}
    vocab['end'] = 1
    for s in segmentations:
        prev = 'start'
        for c in s:
            if not lm.has_key(prev): lm[prev] = Counter()
            lm[prev][c] = lm[prev][c] + 1
            prev = c
            vocab[c] = 1
        if not lm.has_key(prev): lm[prev] = Counter()
        lm[prev]['end'] = lm[prev]['end'] + 1

    # smooth and normalize
    for prev in lm.iterkeys():
        for c in vocab.iterkeys():
            lm[prev][c] = lm[prev][c] + .5   # add 0.5 smoothing
        lm[prev].normalize()

    # convert to a FSA
    fsa = FSM.FSM(isProbabilistic=True)
    fsa.setInitialState('start')
    fsa.setFinalState('end')
       
    for i in lm.iterkeys(): 
        for c in lm[i].iterkeys():
            if c == 'end': 
                fsa.addEdge(i, c, None, None, prob=lm[i][c])
            else:    
                fsa.addEdge(i, c, c, c, prob=lm[i][c])
                   
    return fsa
      
def fancyChannelModel(words, segmentations):
    fst = FSM.FSM(isTransducer=True, isProbabilistic=True)
    fst.setInitialState('start')
    fst.setFinalState('end')
    
    # Add each possible segment
    for s in segmentations:
       for w in s.split('+'):
          fst.addEdgeSequence('start', 'end', w)

    fst.addEdge('end', 'start', '+', None)

    # Self transitions for smoothing
    fst.addEdge('start', 'start', '+', None, 0.1)
    seen_chars = set([])
    for w in words:
        for c in w:
            if not (c in seen_chars): 
                fst.addEdge('start', 'start', c, c, 0.1)
                seen_chars.add(c)

    return fst
    

def stupidChannelModel(words, segmentations):
    # figure out the character vocabulary
    vocab = Counter()
    for w in words:
        for c in w:
            vocab[c] = vocab[c] + 1

    # build the FST    
    fst = FSM.FSM(isTransducer=True, isProbabilistic=True)
    fst.setInitialState('s')
    fst.setFinalState('s')
    for w in words:
        for c in w:
            fst.addEdge('s', 's', c, c, prob=1.0)    # copy the character
    fst.addEdge('s', 's', '+', None, prob=0.1)       # add a random '+'
    return fst

def stupidSourceModel(segmentations):
    # figure out the character vocabulary
    vocab = Counter()
    for s in segmentations:
        for c in s:
            vocab[c] = vocab[c] + 1
    # convert to probabilities
    vocab.normalize()

    # build the FSA
    fsa = FSM.FSM(isProbabilistic=True)
    fsa.setInitialState('s')
    fsa.setFinalState('s')
    for c,v in vocab.iteritems():
        fsa.addEdge('s', 's', c, prob=v)
    return fsa

def bigramSourceModel(segmentations):
    # compute all bigrams
    lm = {}
    vocab = {}
    vocab['end'] = 1
    for s in segmentations:
        prev = 'start'
        for c in s:
            if not lm.has_key(prev): lm[prev] = Counter()
            lm[prev][c] = lm[prev][c] + 1
            prev = c
            vocab[c] = 1
        if not lm.has_key(prev): lm[prev] = Counter()
        lm[prev]['end'] = lm[prev]['end'] + 1

    # smooth and normalize
    for prev in lm.iterkeys():
        for c in vocab.iterkeys():
            lm[prev][c] = lm[prev][c] + .5   # add 0.5 smoothing
        lm[prev].normalize()

    # convert to a FSA
    fsa = FSM.FSM(isProbabilistic=True)
    fsa.setInitialState('start')
    fsa.setFinalState('end')
       
    for i in lm.iterkeys(): 
        for c in lm[i].iterkeys():
            if c == 'end': 
                fsa.addEdge(i, c, None, None, prob=lm[i][c])
            else:    
                fsa.addEdge(i, c, c, c, prob=lm[i][c])
                   
    return fsa

def buildSegmentChannelModel(words, segmentations):
    fst = FSM.FSM(isTransducer=True, isProbabilistic=True)
    fst.setInitialState('start')
    fst.setFinalState('end')

    # Add each possible segment
    for s in segmentations:
       for w in s.split('+'):
          fst.addEdgeSequence('start', 'end', w)

    fst.addEdge('end', 'start', '+', None)

    # Self transitions for smoothing
    fst.addEdge('start', 'start', '+', None, 0.1)
    seen_chars = set([])
    for w in words:
        for c in w:
            if not (c in seen_chars): 
                fst.addEdge('start', 'start', c, c, 0.1)
                seen_chars.add(c)

    return fst

def runTest(trainFile='bengali.train', devFile='bengali.dev', channel=stupidChannelModel, source=stupidSourceModel, skipTraining=False):
    (words, segs) = readData(trainFile)
    (wordsDev, segsDev) = readData(devFile)
    fst = channel(words, segs)
    fsa = source(segs)

    preTrainOutput = runFST([fsa, fst], wordsDev, quiet=True)
    for i in range(len(preTrainOutput)):
        if len(preTrainOutput[i]) == 0: preTrainOutput[i] = words[i]
        else:                           preTrainOutput[i] = preTrainOutput[i][0]
    preTrainEval   = evaluate(segsDev, preTrainOutput)
    print 'before training, P/R/F = ', str(preTrainEval)

    if skipTraining:
        return preTrainOutput
    
    fst.trainFST(words, segs)

    postTrainOutput = runFST([fsa, fst], wordsDev, quiet=True)
    for i in range(len(postTrainOutput)):
        if len(postTrainOutput[i]) == 0: postTrainOutput[i] = words[i]
        else:                            postTrainOutput[i] = postTrainOutput[i][0]
    postTrainEval   = evaluate(segsDev, postTrainOutput)
    print 'after  training, P/R/F = ', str(postTrainEval)
    
    return postTrainOutput

def saveOutput(filename, output):
    h = open(filename, 'w')
    for o in output:
        h.write(o)
        h.write('\n')
    h.close()
    
