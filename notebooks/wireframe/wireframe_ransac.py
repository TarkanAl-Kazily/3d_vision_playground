#
# wireframe_ransac.py
#
# Implements RANSAC subclasses relevant to fitting wireframe
# features robust to outliers.
#

import wireframe.ransac
import numpy as np

class Line3DRANSAC(wireframe.ransac.RANSAC):
    """
    Line3DRANSAC

    Fits point cloud data to find a line in 3D that maximizes inliers

    Attributes:
    """
    def __init__(self, max_iterations, inlier_thresh, good_inlier_count):
        super().__init__(max_iterations, 2, inlier_thresh, good_inlier_count)


    def fit(self, samples):
        """
        Given a set of samples returns a model fitting them.

        Intended to be implemented by subclasses.

        Arguments:
        samples -- a numpy array of shape [N_SAMPLES, sample.shape].
                   all samples must be used as part of fitting process.

        Returns:
        model -- a line defined by two 3D points - np array [2, 3].
            Line also satisfies the property that all samples fall between the endpoints.
        """
        # Finding the principle component to fit a line to samples
        # Courtesy of https://stackoverflow.com/a/2333251
        mean_point = samples.mean(axis=0)
        _, _, vh = np.linalg.svd(samples - mean_point)
        direction = vh[0]
        direction /= np.linalg.norm(direction)

        # Project points to line to find the needed endpoints
        params = np.dot(samples - mean_point, direction)
        result = np.vstack([mean_point + direction * np.min(params),
                            mean_point + direction * np.max(params)])
        return result

    def get_error(self, data, model):
        """
        Given a set of samples and a model, returns the error for each sample from the model.

        Intended to be implemented by subclasses.

        Arguments:
        data -- a numpy array of shape [N_SAMPLES, sample.shape]
        model -- a line defined by two 3D points - np array [2, 3]

        Returns:
        error -- a numpy array of shape [N_SAMPLES] corresponding to the error of data points
        """
        N_SAMPLES = data.shape[0]
        point = model[0]
        direction = model[1] - model[0]
        direction /= np.linalg.norm(direction)

        params = np.dot(data - point, direction)
        error = np.linalg.norm(data - point - 
                    np.multiply(np.expand_dims(params, 1), direction), axis=1)
        return error

class ManhattanRANSAC(wireframe.ransac.RANSAC):
    """
    ManhattanRANSAC

    Given a set of lines, fits a best guess basis directions

    Attributes:
    """
    def __init__(self, max_iterations, inlier_thresh, good_inlier_count):
        super().__init__(max_iterations, 3, inlier_thresh, good_inlier_count, use_all=False)

    def fit(self, samples):
        """
        Given a set of samples returns a model fitting them.

        Intended to be implemented by subclasses.

        Arguments:
        samples -- a numpy array of shape [N_SAMPLES, 3]. (line directions)
                   all samples must be used as part of fitting process.

        Returns:
        model -- a numpy array of shape [3, 3].
            model[0], model[1], model[2] are the three basis directions found.
            satisfies a rotation matrix (orthonormal directions)
        """
        _, _, vh = np.linalg.svd(samples)
        return vh

    def get_error(self, data, model):
        """
        Given a set of samples and a model, returns the error for each sample from the model.

        Intended to be implemented by subclasses.

        Arguments:
        data -- a numpy array of shape [N_SAMPLES, 3] (line directions)
        model -- a numpy array of shape [3, 3]

        Returns:
        error -- a numpy array of shape [N_SAMPLES] corresponding to the error of data points
        """
        N_SAMPLES = data.shape[0]
        dot_prods = np.abs(np.matmul(data, model.transpose()))
        amax = np.amax(dot_prods, axis=1)
        error = np.sum(dot_prods, axis=1) - amax + (np.ones(N_SAMPLES) - amax)
        return error
