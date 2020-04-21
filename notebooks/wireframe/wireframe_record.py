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
    """

    def __init__(self, preds):
        """
        Initialize the wireframe record with the predictions of the LCNN model
        """
        self.preds = preds

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
        Returns a copy of the predicted line information as points in [0, 1] x [0, 1]
        """
        return (self.preds["lines"][0].cpu().numpy() / 128)[:self.num_lines]

    def scores(self):
        """
        Returns a copy of the predicted scores information
        """
        return (self.preds["score"][0].cpu().numpy())[:self.num_lines]

    def juncs(self):
        """
        Returns a copy of the predicted junction information
        """
        return (self.preds["juncs"][0].cpu().numpy() / 128)[:self.num_juncs]

    ##########################
    # Utility functions here
    ##########################

    def postprocess(self, imshape):
        diag = (imshape[0] ** 2 + imshape[1] ** 2) ** 0.5
        # Multiply lines by image shape to get image point coordinates
        return postprocess(self.lines() * imshape[:2], self.scores(), diag * 0.01, 0, False)
