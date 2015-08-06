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
    _mixtureModel = {}
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
            {Str: float}
                Tube ID: the mean of each population. 
                Row := population, Col := channel.
        """ 
        
        if self.debug: 
            print "\nEstimating GMM from experiment: ", experiment, \
                  "\nwith subset selected: ", subset, '\n'
        
        self.checkTransform(experiment)
                
        # Iterate over the tubes
        for i, tube in enumerate(set(experiment["Tube"])):
            
            # Get channel data to fit from experiment
            
            tubeData = experiment[experiment.data.Tube == tube]
            if subset:
                tubeData = tubeData.query(subset)
            cellData = tubeData[self.channels]
            
            # Create mixture model
            gmm = GMM(self.numPopulations)
            gmm.fit(cellData.values)
            self._mixtureModel[tube] = gmm
            
            if self.debug: 
                print "\n>> MixtureModelOp.estimate() loop ", i, " debug output:"
                print "Tube: ", tube
                print "Conditions: ", experiment.conditions
                print "Cell data:\n", cellData
                print "Log likelihood: ", gmm.score_samples(cellData)
            
        # Return means to client and unblock apply method
        self._estimated = True
        return {tube: model.means_ for (tube, model) in self._mixtureModel.iteritems()}
    
    
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
        
        if self.debug: 
            print "\nApplying GMM to experiment: ", experiment, "\n"
        
        # Validate model has been created
        if not self._estimated:
            raise RuntimeError("Must run 'estimate' before applying model to data!")
        self.checkTransform(experiment)
        
        newExperiment = experiment.clone()
        
        # Do prediction for each tube
        for i, tube in enumerate(set(newExperiment["Tube"])):
            
            tubeData = newExperiment[newExperiment.data.Tube == tube]
            cellData = tubeData[self.channels]
            
            gmm = self._mixtureModel[tube]
            classification = gmm.predict(cellData.values)
            prediction = gmm.predict_proba(cellData.values)
            
            if self.debug:
                print "\n>> MixtureModelOp.apply() loop ", i, " debug output:"
                print "Tube: ", tube
                print "Shape of tube data: ", cellData.shape
                print "Classification: ", classification
                print "Prediction: ", prediction
            
            # This is needed since the order is not preserved when selecting from the set of tubes
            newExperiment.data.loc[newExperiment.data.Tube == tube, "GMM"] = classification
            for j in range(self.numPopulations):
                newExperiment.data.loc[newExperiment.data.Tube == tube, "Pop_ " + str(j)] = prediction[:, j]
            
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
        
        
        
        
        
        