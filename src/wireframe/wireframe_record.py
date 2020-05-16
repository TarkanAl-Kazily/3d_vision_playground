#
# wireframe_record.py
#
# Declares the WireframeRecord class that stores wireframe data for processing
#

from lcnn.postprocess import postprocess

import os
import numpy as np

import wireframe.project

class WireframeRecord():
    """
    WireframeRecord

    Stores extracted line and junction data from images

    Attributes:
    num_lines -- The number of detected and unique lines (edges)
    num_juncs -- The number of detected and unique junctions (vertices)
    imshape -- The shape of the image that generated this record

    Functions:
    lines -- returns the line information with endpoints in [0,1] x [0,1]
    scores -- returns the scores of the line information
    juncs -- returns the junction information with endpoints in [0,1] x [0,1]
    postprocess -- runs the LCNN postprocess function on the lines and scores
    """
    def __init__(self, preds, imshape, imnum, to_cpu=True):
        """
        Initialize the wireframe record with the predictions of the LCNN model
        """
        self.preds = preds
        self.imshape = (imshape[0], imshape[1])
        self.imnum = imnum
        if to_cpu:
            self._lines = self.preds["lines"][0].cpu().numpy()
            self._score = self.preds["score"][0].cpu().numpy()
            self._juncs = self.preds["juncs"][0].cpu().numpy()
        else:
            self._lines = np.array(self.preds["lines"], copy=True)
            self._score = np.array(self.preds["score"], copy=True)
            self._juncs = np.array(self.preds["juncs"], copy=True)

        self.num_lines = None
        for i in range(1, len(self._lines)):
            if (self._lines[i] == self._lines[0]).all():
                self.num_lines = i
                break
        if self.num_lines is None:
            self.num_lines = len(self._lines)

        self.num_juncs = None
        for i in range(1, len(self._juncs)):
            if (self._juncs[i] == self._juncs[0]).all():
                self.num_juncs = i
                break
        if self.num_juncs is None:
            self.num_juncs = len(self._juncs)

    ##########################
    # Getter functions here
    ##########################

    def lines(self):
        """
        Gets the predicted line information, endpoints in [0, 1] x [0, 1]

        Returns:
        lines -- numpy array [num_lines, 2, 2]
        """
        return (self._lines / 128)[:self.num_lines]

    def scores(self):
        """
        Gets the predicted scores information
        """
        return (self._score)[:self.num_lines]

    def juncs(self):
        """
        Gets the predicted junction information
        """
        return (self._juncs / 128)[:self.num_juncs]

    ##########################
    # Utility functions here
    ##########################

    def postprocess(self, threshold=0):
        """
        Filters the lines to remove close duplicates in the image.

        Arguments:
        imshape -- image dimensions
        threshold -- returned lines must have greater score (default 0)

        Returns:
        nlines -- filtered lines
        nscores -- filtered scores
        """
        diag = (self.imshape[0] ** 2 + self.imshape[1] ** 2) ** 0.5
        # Multiply lines by image shape to get image point coordinates
        nlines, nscores = postprocess(self.lines() * self.imshape[:2], self.scores(), diag * 0.01, 0, False)
        return nlines[nscores > threshold], nscores[nscores > threshold]

    def save(self, filename):
        """
        Saves the record in numpy format for later use loading with WireframeRecord.load

        Arguments:
        filename -- file to write. Will create directories. Overwrites destination. Appends .npz
        """
        directory = os.path.dirname(filename)
        os.makedirs(directory, exist_ok=True)
        np.savez_compressed(filename, lines=self._lines, score=self._score, juncs=self._juncs, imshape=self.imshape)

    ##########################
    # Static class functions here
    ##########################

    @staticmethod
    def load(filename):
        """
        Loads a record from the filename and returs a WireframeRecord instance
        """
        imname = os.path.basename(filename)
        imnum = wireframe.project.imnum_from_imname(imname)
        record = None
        with open(filename, 'rb') as f:
            data = np.load(filename)
            record = WireframeRecord(data, data["imshape"], imnum, to_cpu=False)
            data.close()
        return record
