'''
Created on Jul 31, 2015

This follows Brian's CytoFlow examples to learn about the API.

@author: Ross Jones
@organization: Weiss Lab, MIT
'''

# Import the cytoflow module. 
# We currently depend on Eugene Yurtsev's FlowCytometryTools for basic import functionality;
# this may change in the future.
from __future__ import division
import cytoflow as flow
import FlowCytometryTools as fc
import matplotlib.pyplot as plt
from numpy import log10

print 'Finished imports'


def importData():
    '''
        Imports common data to this test script
    '''
    
    # Read in two example files
    filepath = '..\\data\\Plate01\\'
    filename = 'RFP_Well_A3.fcs'
    fullfile = filepath + filename
    tube1 = fc.FCMeasurement(ID = 'Test 1', datafile = fullfile)
    
    filename = 'CFP_Well_A4.fcs'
    fullfile = filepath + filename
    tube2 = fc.FCMeasurement(ID = 'Test 2', datafile = fullfile)
    
    return tube1, tube2


    
    
def test1(tube1, tube2):
    '''
        Testing the separation of two populations w/r/t one parameter
                
        -----
        
        From this test, it does in fact appear to work for two populations separated
        on the Y2-A parameter. 
    '''
    
    # Create an Experiment. Define an experimental condition 
    # (the amount of Dox inducer) and add the two tubes we just 
    # imported, specifying their experimental conditions in a dict.
    ex = flow.Experiment()
    ex.add_conditions({'Dox': 'float'})
    
    ex.add_tube(tube1, {'Dox': 10.0})
    ex.add_tube(tube2, {'Dox': 1.0})
    
    modelChannels = ['Y2-A']
    
    hlog = flow.HlogTransformOp()
    hlog.name = 'Hlog transformation'
    hlog.channels = modelChannels
    ex2 = hlog.apply(ex)
    
    print ex2[modelChannels]
    for key in ex2.metadata: print key, ": ", ex2.metadata[key]
    print ex2.conditions
    
    # Create GMM
    gmm = flow.MixtureModelOp()
    gmm.debug = True;
    gmm.name = "GMM"
    gmm.channels = modelChannels
    gmm.numPopulations = 2
    gmm.transform = "hlog"
    gmm.estimate(ex2, modelChannels)
    
    # Apply GMM probability to experiment
    ex3 = gmm.apply(ex2)
    
    print ex3[modelChannels]
    for key in ex3.metadata: print key, ": ", ex3.metadata[key]
    print ex3.conditions
    
    
    # --- Plotting --- #
    
    s = flow.ScatterplotView()
    s.huefacet = 'GMM'
    s.xchannel = 'Y2-A'
    s.ychannel = 'B1-A'
    s.plot(ex3, s = 10)
    
    h = flow.HistogramView()
    h.channel = 'Y2-A'
    h.huefacet = 'GMM'
    h.plot(ex3)
    
   
def test2(tube1, tube2):
    '''
        Testing the separation of two populations w/r/t three parameters
        
        -----
        
        From this test, it does in fact appear to work for two populations separated
        on the Y2-A, B1-A, and V2-A parameters together. 
    '''
    
    # Create an Experiment. Define an experimental condition 
    # (the amount of Dox inducer) and add the two tubes we just 
    # imported, specifying their experimental conditions in a dict.
    ex = flow.Experiment()
    ex.add_conditions({'Dox': 'float'})
    
    ex.add_tube(tube1, {'Dox': 10.0})
    ex.add_tube(tube2, {'Dox': 1.0})
    
    modelChannels = ['Y2-A', 'V2-A', 'B1-A']
    
    hlog = flow.HlogTransformOp()
    hlog.name = 'Hyperlog'
    hlog.channels = modelChannels
    ex2 = hlog.apply(ex)
    
    print ex2[modelChannels]
    for key in ex2.metadata: print key, ": ", ex2.metadata[key]
    print ex2.conditions
    
    # Create GMM
    gmm = flow.MixtureModelOp()
    gmm.debug = True;
    gmm.name = "GMM"
    gmm.channels = modelChannels
    gmm.numPopulations = 2
    gmm.transform = "hlog"
    gmm.estimate(ex2, modelChannels)
    
    # Apply GMM probability to experiment
    ex3 = gmm.apply(ex2)
    
    print ex3[modelChannels]
    for key in ex3.metadata: print key, ": ", ex3.metadata[key]
    print ex3.conditions
    
    
    # --- Plotting --- #
    
    s = flow.ScatterplotView()
    s.huefacet = 'GMM'
    s.xchannel = 'Y2-A'
    s.ychannel = 'B1-A'
    s.plot(ex3, s = 10)
    
    h = flow.HistogramView()
    h.channel = 'Y2-A'
    h.huefacet = 'GMM'
    h.plot(ex3)



if __name__ == '__main__':
    
    # Import data
    tube1, tube2 = importData()
    
    test1(tube1, tube2)
    print 'Test 1 complete'
    
    test2(tube1, tube2)
    print 'Test 2 complete'
    
    # Show plots
    plt.show()
    