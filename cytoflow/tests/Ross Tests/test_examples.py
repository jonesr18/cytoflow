'''
Created on Jun 24, 2015

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
import numpy as np


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


def example1(tube1, tube2):
    '''
        Basic cytometry
    '''
    
    # Create an Experiment. Define an experimental condition (the amount of Dox inducer) 
    # and add the two tubes we just imported, specifying their experimental conditions 
    # in a dict.
    ex = flow.Experiment()
    ex.add_conditions({'Dox': 'float'})
#     cond = ex.getConditions()
#     print cond
    ex.add_tube(tube1, {'Dox': 10.0})
    ex.add_tube(tube2, {'Dox': 1.0})
    
    # Have a quick look at the experiment. Instantiate a View and tell it which channel 
    # we're looking at. The huefacet trait says 'plot each Dox condition a different 
    # color on the same axes.'
    hist = flow.HistogramView()
    hist.name = 'Histogram view, by color'
    hist.channel = 'Y2-A'
    hist.huefacet = 'Dox'
    hist.plot(ex)
    
    # Alternately, we could have the view plot the two conditions side-by-side.
    hist2 = flow.HistogramView()
    hist2.name = "Histogram view, side-by-side"
    hist2.channel = 'Y2-A'
    hist2.xfacet = 'Dox'
    hist2.plot(ex)
    
    # Because this is untransformed data, comparing these distributions is difficult. 
    # Let's do an HLog transformation to make them easier to visualize
    hlog = flow.HlogTransformOp()
    hlog.name = 'HLog Transformation'
    hlog.channels = ['V2-A', 'Y2-A', 'B1-A']
    ex2 = hlog.apply(ex)
    
    # Note that an operation's apply() method takes an Experiment as a parameter and 
    # returns an Experiment. The latter is derived from the former; it maintains the 
    #same metadata, but with transformed data. The operation is not performed in 
    # place. This is the beginning of the workflow concept, which sees more 
    # full realization in the GUI.
    
    # Also note that both the semantics of the histogram view and the hlog operation: 
    # they are parameterized separately from the Experiment they're operating on. 
    # So, we can just reuse a pre-existing HistogramView instance to view the new 
    # Experiment instance that the hlog operation gave us.
    hist.plot(ex2)
    
    # Now we can see a clear difference between the two tubes: one has a large 
    # population > 2000 in the Y2-A channel (transformed value), and the other 
    # tube doesn't. Let's create a threshold gate to separate the populations
    thresh = flow.ThresholdOp()
    thresh.name = 'Y2-A+'
    thresh.channel = 'Y2-A'
    thresh.threshold = 2005.0
    ex3 = thresh.apply(ex2)
    
    # One more important semantic note. A gate *does not remove events; it simply 
    # adds additional metadata to the events already there.* You can get at an 
    # Experiment's underlying pandas dataframe by looking at the Experiment.data 
    # trait and verifying that all three Experiments we've created have the same 
    # number of events.
    print ex.data.shape
    print ex2.data.shape
    print ex3.data.shape
    
    # The last experiment, though, has another column named 'Y2-A+', which is 
    # whether each event ended up above the threshold or not
    print ex.data.columns
    print ex2.data.columns
    print ex3.data.columns
    
    # Now we can plot using that additional piece of metadata....
    hist3 = flow.HistogramView()
    hist3.name = 'Histogram view, grid'
    hist3.channel = 'Y2-A'
    hist3.xfacet = 'Dox'
    hist3.yfacet = 'Y2-A+'
    hist3.plot(ex3)
    
    # ....or we can ask "how many events were above the threshold?" Eventually 
    # this will be a statistics view, like a bar chart, or a summary table. For 
    # now, we use the pandas API to answer the question.
    print ex3.data.groupby(['Dox', 'Y2-A+']).size()


def example2(tube1, tube2):
    '''
       Basic exmple cytometry workflow 
    '''
    
    # Create an Experiment. Define an experimental condition 
    # (the amount of Dox inducer) and add the two tubes we just 
    # imported, specifying their experimental conditions in a dict.
    ex = flow.Experiment()
    ex.add_conditions({'Dox': 'float'})
    
    ex.add_tube(tube1, {'Dox': 10.0})
    ex.add_tube(tube2, {'Dox': 1.0})
    
    hlog = flow.HlogTransformOp()
    hlog.name = 'Hlog transformation'
    hlog.channels = ['V2-A', 'Y2-A', 'B1-A']
    ex2 = hlog.apply(ex)
    
    thresh = flow.ThresholdOp()
    thresh.name = 'Y2-A+'
    thresh.channel = 'Y2-A'
    thresh.threshold = 2005.0
    ex3 = thresh.apply(ex2)
    
    # Have a quick look at the experiment. Instantiate a View and 
    # tell it which channel we're looking at. The huefacet trait 
    # says 'plot each Dox condition a different color on the same axes.'
    # -- not implemented yet? -- #
#     s = flow.BarChartView()
#     s.chanel = 'V2-A'
#     s.function = np.mean
#     s.group = 'Dox'
#     s.plot(ex3)
    
    # ...And the rest is the same as example 1
    
    
def example3(tube1, tube2):
    '''
        Example interactive plot
    '''
    
    # Create an Experiment. Define an experimental condition 
    # (the amount of Dox inducer) and add the two tubes we just 
    # imported, specifying their experimental conditions in a dict.
    ex = flow.Experiment()
    ex.add_conditions({'Dox': 'float'})
    
    ex.add_tube(tube1, {'Dox': 10.0})
    ex.add_tube(tube2, {'Dox': 1.0})
    
    hlog = flow.HlogTransformOp()
    hlog.name = 'Hlog transformation'
    hlog.channels = ['V2-A', 'Y2-A', 'B1-A']
    ex2 = hlog.apply(ex)
    
    h = flow.HistogramView()
    h.channel = 'Y2-A'
    h.huefacet = 'Dox'
    r = flow.RangeSelection(view = h)
    r.plot(ex2)
    r.low = 3000;
    r.high = 9000;
    
    r.interactive = True
    
    print r.min
    print r.max
    
    
if __name__ == '__main__':
    
    # Import data
    tube1, tube2 = importData()
    
    # Basic cytometry
    example1(tube1, tube2)
    print 'Example 1 complete'
    
    # Basic exmple cytometry workflow
    example2(tube1, tube2)
    print 'Example 2 complete'
    
    example3(tube1, tube2)
    print 'Example 3 complete'
    
    # Show plots
    plt.show()
    