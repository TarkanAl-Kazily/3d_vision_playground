#
# wireframe_record.py
#
# Declares the WireframeRecord class that stores wireframe data for processing
#

from lcnn.postprocess import postprocess

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

    def __init__(self, preds, imshape):
        """
        Initialize the wireframe record with the predictions of the LCNN model
        """
        self.preds = preds
        self.imshape = imshape

        self.num_lines = None
        for i in range(1, len(self.preds["lines"][0].cpu().numpy())):
            if (self.preds["lines"][0].cpu().numpy()[i] == self.preds["lines"][0].cpu().numpy()[0]).all():
                self.num_lines = i
                break
        if self.num_lines is None:
            self.num_lines = len(self.preds["lines"][0].cpu().numpy())

        self.num_juncs = None
        for i in range(1, len(self.preds["juncs"][0].cpu().numpy())):
            if (self.preds["juncs"][0].cpu().numpy()[i] == self.preds["juncs"][0].cpu().numpy()[0]).all():
                self.num_juncs = i
                break
        if self.num_juncs is None:
            self.num_juncs = len(self.preds["juncs"][0].cpu().numpy())

    ##########################
    # Getter functions here
    ##########################

    def lines(self):
        """
        Gets the predicted line information, endpoints in [0, 1] x [0, 1]

        Returns:
        lines -- numpy array [num_lines, 2, 2]
        """
        return (self.preds["lines"][0].cpu().numpy() / 128)[:self.num_lines]

    def scores(self):
        """
        Gets the predicted scores information
        """
        return (self.preds["score"][0].cpu().numpy())[:self.num_lines]

    def juncs(self):
        """
        Gets the predicted junction information
        """
        return (self.preds["juncs"][0].cpu().numpy() / 128)[:self.num_juncs]

    ##########################
    # Utility functions here
    ##########################

    def postprocess(self):
        """
        Filters the lines to remove close duplicates in the image.

        Arguments:
        imshape -- image dimensions

        Returns:
        nlines -- filtered lines
        nscores -- filtered scores
        """
        diag = (self.imshape[0] ** 2 + self.imshape[1] ** 2) ** 0.5
        # Multiply lines by image shape to get image point coordinates
        return postprocess(self.lines() * self.imshape[:2], self.scores(), diag * 0.01, 0, False)

    def lines_postprocess(self):
        return self.postprocess()[0]

    def scores_postprocess(self):
        return self.postprocess()[1]
