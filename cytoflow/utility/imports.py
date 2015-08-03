'''
Created on Aug 1, 2015

@author: Ross
'''
from __future__ import division

import csv
from os.path import exists

from numpy import array
import FlowCytometryTools as fc
import cytoflow as flow


def getExptSetup(fullfile, debug = False):
    '''
        Given the full file/path name of a setup file, imports the tubes/plates
        in an experiment and initializes their conditions.
        
        parameters
        ----------
            fullfile : Str
                The full-path filename of a .txt setup file
                MUST BE COMMA OR TAB DELIMITED to work - method finds out which it is
                Column headers are conditions
                The first row below headers should have the data type (eg 'float')
                The remaining rows contain condition metadata
                The first column must be 'filename', and the data should be strings
                with a valid .fcs filename corresponding with a sample.
        
        returns
        -------
            Experiment
                Returns an Experiment that has all the tubes/wells and conditions
                from the input file established
    '''
    
    # Validate filename
    if not exists(fullfile):
        raise RuntimeError("Setup file not found:\n" + fullfile)
    
    if debug: print "File validated: \n", fullfile
    
    with open(fullfile, 'rb') as setupFile:
        dlm = csv.Sniffer().sniff(setupFile.readline(), '\t,').delimiter
        if debug: print "Delimiter: ", dlm
        setupFile.seek(0)
        setupInfo = list(csv.reader(setupFile, delimiter = dlm))
        if debug: print setupInfo
        
    # wrap the experiment building in this function for clarity
    return buildExperiment(setupInfo, debug)



def buildExperiment(setupInfo, debug = False):
    '''
        Does the experiment building from a 2D list, representative of a setup file.
        
        parameters
        ----------
            setupInfo : Array-type
                An exact array representation of the setup file
        
        returns
        -------
            Experiment
                Returns an Experiment that has all the tubes/wells and conditions
                from the input file established
    '''
    
    ex = flow.Experiment()
    setupInfo = array(setupInfo)
    
    # header and type in first two rows
    #     ignore first col (.fcs filename)
    conditions = setupInfo[0:2, 1:].transpose() 
    if debug: print conditions
    
    # Tube info in the remaining rows
    sampleInfo = setupInfo[2:, :]
    if debug: print sampleInfo
    
    # Add conditions
    for condition, dataType in conditions:
        if debug:
            print '{' + condition + ' : ' + dataType + '}'
        ex.add_conditions({condition : dataType})
    
    # Add tubes
    for i, sample in enumerate(sampleInfo):
        
        fullfile = sample[0]
        
        # This appears to tbe the rate-limiting speed step
        tube = fc.FCMeasurement(ID = 'Tube ' + str(i + 1), datafile = fullfile)
        
        # Add tube with conditions, don't include filename
        if debug: print sample
        treatments = {}
        for j, value in enumerate(sample[1:]):
            
            # Check what the dataType is so we can convert it before adding
            if conditions[j, 1] == 'float':
                value = float(value)
            elif conditions[j, 1] == 'int':
                value = int(value)
            elif conditions[j, 1] == 'bool':
                value = bool(value)
            else:
                # value is a string of some sort
                pass
            
            # Add entry
            treatments[conditions[j, 0]] = value
            
        # Add tube to experiment
        if debug: print treatments
        ex.add_tube(tube, treatments)
    
    return ex
    

if __name__ == '__main__':
    
    getExptSetup('..\\tests\\Ross Tests\\testSetup.txt', True)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    