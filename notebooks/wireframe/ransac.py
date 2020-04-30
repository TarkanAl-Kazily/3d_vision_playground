#
# ransac.py
#
# Implements a base class to provide the RANSAC algorithm
#

import numpy as np

class RANSAC():
    """
    RANSAC

    A class intended to be subclassed to individual sampling problems

    Attributes:
    k -- maximum number of iterations to run
    n -- number of data samples to take each iteration
    t -- threshold on error defining inliers
    d -- number of inliers that allow shortcutting the algorithm
    """
    def __init__(self, max_iterations, num_samples, inlier_thresh, good_inlier_count):
        """
        Arguments:
        max_iterations -- maximum number of iterations to run
        num_samples -- number of data samples to take each iteration
        inlier_thresh -- threshold on error defining inliers
        good_inlier_count -- number of inliers that allow shortcutting the algorithm.
            if None max_iterations are always executed.
        """
        self.k = max_iterations
        self.n = num_samples
        self.t = inlier_thresh
        self.d = good_inlier_count

        self._rng = np.random.default_rng()

    def ransac(self, data):
        """
        Runs the RANSAC algorithm on the data provided.

        Arguments:
        data -- data points to fit a model to. must be at least n

        Returns:
        bestmodel -- the learned best model despite potential outliers
                     (best in terms of number of inliers)
        n_inliers -- the number of inliers with bestmodel
        """
        if data.shape[0] < self.n:
            # Not enough data to fit points to
            return np.array([]), 0

        # current best model
        bestmodel = None
        # current inliers that fits bestmodel 
        bestfit = None
        iteration = 0

        while iteration < self.k:
            iteration += 1
            samples = self._rng.choice(data, self.n, replace=False)
            model = self.fit(samples)
            error = self.get_error(data, model)
            inliers = data[self.get_error(data, model) < self.t]
            if bestmodel is None:
                # Initialize the model with this model (don't bother with refitting)
                bestmodel = model
                bestfit = inliers
            elif inliers.shape[0] > bestfit.shape[0]:
                # Choose best model as the one that fits all of these inliers
                bestmodel = self.fit(inliers)
                bestfit = data[self.get_error(data, model) < self.t]

            # Shortcut if we deem that we have a good enough number of inliers
            if self.d is not None and bestfit.shape[0] > self.d:
                return bestmodel, bestfit.shape[0]

        return bestmodel, bestfit.shape[0]

    def fit(self, samples):
        """
        Given a set of samples returns a model fitting them.

        Intended to be implemented by subclasses.

        Arguments:
        samples -- a numpy array of shape [N_SAMPLES, sample.shape].
                   all samples must be used as part of fitting process.

        Returns:
        model -- fitted model that can be used by caller to ransac and used in get_error
        """
        raise NotImplementedError()

    def get_error(self, data, model):
        """
        Given a set of samples and a model, returns the error for each sample from the model.

        Intended to be implemented by subclasses.

        Arguments:
        data -- a numpy array of shape [N_SAMPLES, sample.shape]
        model -- model that is being evaluated

        Returns:
        error -- a numpy array of shape [N_SAMPLES] corresponding to the error of data points
        """
        raise NotImplementedError()

