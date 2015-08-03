from numpy import array, concatenate
from sklearn.mixture import GMM
from traits.api import CStr, HasTraits, ListStr, Int, provides

from cytoflow.operations.i_operation import IOperation


@provides(IOperation)
class MixtureModelOp(HasTraits):
    """Estimate means of gaussians in mixture model. Computes 
    
    Attributes
    ----------
    id : Str
        a unique identifier for this class. prefix: edu.mit.synbio.cytoflow.operations
        
    friendly_id : Str
        The operation's human-readable id (like "Logicle" or "Hyperlog").  Used
        for UI implementations.
        
    name : Str
        The name of this IOperation instance (like "Debris Filter").  Useful for
        UI implementations; sometimes used for naming gates' metadata
    """
    
    # interface traits
    id = "edu.mit.synbio.cytoflow.operations.mixtureModel"
    friendly_id = "Mixture Model"
    name = CStr()
    channels = ListStr()
    numPopulations = Int()
    transform = CStr()     # Must be a canonical name (see FlowCytometryTools.core.transforms)
    debug = False
    _mixtureModel = []
    _estimated = False

    
    def is_valid(self, experiment):
        """Validate this operation instance against an experiment.
        
        Parameters
        ----------
        experiment : Experiment
            The Experiment against which to validate this op.
            
        Returns
        -------
        True if this is a valid operation on the given experiment; 
        False otherwise.
        """
        
        if not experiment:
            return False
        
        if not self.name:
            return False
        
        if not set(self.channels).issubset(set(experiment.channels)):
            return False
        
        if not self.numPopulations:
            return False
        
        if not self.transform:
            return False
        
        return True
        
        
    def estimate(self, experiment, subset = None):
        """Estimate multiple population means from the experimental data.
        
        Protein expression generally follows a lognormal distribution, 
        so N gaussians (given by numPopulations) are fit to the 
        data to determine population means. 
        
        The data should be transformed in some way prior to the fitting to
        remove boundary effects around zero and the issue of negative values
        following compensation. I typically do a hyperlog transform, then the
        mixture can be computed with the new, linear values. This method does
        a linear fit, so the result of the transformation must be a linearization
        of the lognormal populations.
        
        Parameters
        ----------
        experiment : Experiment
            the Experiment to use in the estimation.
        
        subset : Str (optional)
            a string passed to pandas.DataFrame.query() to select the subset
            of data on which to run the parameter estimation.
            
        Returns
        -------
        means : Float
            the mean of each population. Row := population, Col := channel.
        """ 
        
        self.checkTransform(experiment)
                
        # Iterate over the tubes
        for i, tube in enumerate(set(experiment["Tube"])):
            
            # Get channel data to fit from experiment
            if self.debug: 
                print tube
                print experiment.conditions
            tubeData = experiment[experiment.data.Tube == tube]
            if subset:
                tubeData = tubeData.query(subset)
            cellData = tubeData[self.channels]
            
            # Create mixture model
            self._mixtureModel.append(GMM(self.numPopulations))
            self._mixtureModel[i].fit(cellData)
            score = self._mixtureModel[i].score_samples(cellData)
            
            if self.debug: print "Log likelihood: ", score
            
        # Return means to client and unblock apply method
        self._estimated = True
        return [m.means_ for m in self._mixtureModel]
    
    
    def apply(self, experiment):
        """
        Predicts the probability of each cell to be in each population.
        The number of populations must be set prior to running this method.
        
        Returns a new experiment with new metadata added with classified
        samples and population probability. The method will first break up
        the data by sample (ie by .fcs file), then fit the model. 
        
        The data should be transformed in some way prior to the fitting to
        remove boundary effects around zero and the issue of negative values
        following compensation. I typically do a hyperlog transform, then the
        mixture can be computed with the new, linear values.
        
        Parameters
        ----------
            old_experiment : Experiment
                the Experiment to apply this op to.
                    
        Returns
        -------
            Experiment
                the old Experiment with this operation applied.
        """
        
        # Validate model has been created
        if not self._estimated:
            raise RuntimeError("Must run 'estimate' before applying model to data!")
        self.checkTransform(experiment)
        
        newExperiment = experiment.clone()
        
        # Do prediction for each tube
        classifications = array([]).T
        predictions = array([[]] * self.numPopulations).T
        for i, tube in enumerate(set(newExperiment["Tube"])):
            
            tubeData = newExperiment[newExperiment.data.Tube == tube]
            cellData = tubeData[self.channels]
                        
            classification = self._mixtureModel[i].predict(cellData)
            prediction = self._mixtureModel[i].predict_proba(cellData)
            if self.debug:
                print type(classification)
                print "Shape of classification: ", classification.shape
                print "Shape of classifications: ", classifications.shape
                print type(prediction)
                print "Shape of prediction: ", prediction.shape
                print "Shape of predictions: ", predictions.shape
                print "Shape of data: ", newExperiment.data.shape
            classifications = concatenate((classifications, classification))
            predictions = concatenate((predictions, prediction))
            
            
        # Add data columns
        newExperiment["GMM"] = classifications
        for i in range(self.numPopulations):
            newExperiment["Pop_" + str(i)] = predictions[:, i]
        
        newExperiment.metadata["GMM"] = {}
        return newExperiment
        
        
    def checkTransform(self, experiment):
        '''
            Checks to see if the transformation has been applied to the correct channels,
            and returns transformed channels regardless.
            
            The transformation of interest is defined by the field 'transform'
            
            Parameteres
            -----------
                experiment : Experiment
                    the experiment whose channels we are looking at
                    
        '''
        
        for channel in self.channels:
            for xform in experiment.metadata[channel]['xforms']:
                if self.debug:
                    print "Data transforms: ", [t.tname for t in experiment.metadata[channel]['xforms']]
                    print "Set transform: ", self.transform
                if self.transform == xform.tname:
                    return
                
                
        # This is only reached if the transform is not found
        raise RuntimeError("Channel must be transformed with " + 
                            self.transform + " to create GMM")
        
        
        
        
        
        