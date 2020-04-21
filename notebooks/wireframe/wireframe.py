#
# wireframe.py
#
# Declares the wireframe class which initializes lcnn to parse and process wireframe information in scenes
#

import os
import os.path as osp
import random

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import skimage.io
import skimage.transform
import torch
import yaml

import lcnn
from lcnn.config import C, M
from lcnn.models.line_vectorizer import LineVectorizer
from lcnn.models.multitask_learner import MultitaskHead, MultitaskLearner
from lcnn.postprocess import postprocess
from lcnn.utils import recursive_to

from wireframe import WireframeRecord

PLTOPTS = {"color": "#33FFFF", "s": 15, "edgecolors": "none", "zorder": 5}
cmap = plt.get_cmap("jet")
norm = mpl.colors.Normalize(vmin=0.9, vmax=1.0)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])

def c(x):
    return sm.to_rgba(x)

class Wireframe():
    """
    Wireframe class
    
    Used for extracting junction and line information in photos.
    
    Depends on the lcnn package
    """
    
    def __init__(self, config_file, model_file, gpu_devices):
        self._config_file = config_file
        self._model_file = model_file
        self._gpu_devices = gpu_devices
        self._device = None
        self._checkpoint = None
        self._model = None
        
        
        self.initialized = False
    

    def setup(self):
        """
        Loads the LCNN model and parameters.
        Must be called before any processing can occur.
        
        Returns:
         - bool resulting initialized status
        """
        if self.initialized:
            print("Wireframe already initialized!")
            return self.initialized
        
        try:
            C.update(C.from_yaml(filename=self._config_file))
            M.update(C.model)
            random.seed(0)
            np.random.seed(0)
            torch.manual_seed(0)
            
            
            device_name = "cpu"
            os.environ["CUDA_VISIBLE_DEVICES"] = self._gpu_devices
            if torch.cuda.is_available():
                device_name = "cuda"
                torch.backends.cudnn.deterministic = True
                torch.cuda.manual_seed(0)
                print("Let's use", torch.cuda.device_count(), "GPU(s)!")
            else:
                print("CUDA is not available")
            self._device = torch.device(device_name)
            self._checkpoint = torch.load(self._model_file, map_location=self._device)

            # Load model
            self._model = lcnn.models.hg(
                depth=M.depth,
                head=lambda c_in, c_out: MultitaskHead(c_in, c_out),
                num_stacks=M.num_stacks,
                num_blocks=M.num_blocks,
                num_classes=sum(sum(M.head_size, [])),
            )
            self._model = MultitaskLearner(self._model)
            self._model = LineVectorizer(self._model)
            self._model.load_state_dict(self._checkpoint["model_state_dict"])
            self._model = self._model.to(self._device)
            self._model.eval()
            
            self.initialized = True
            
        except Exception as e:
            self.error = e
            print("Setup failed. Check self.error for more information")
            self.initialized = False
            
        return self.initialized
    
    def parse(self, imname):
        """
        Returns a WireframeRecord of the predictions for the input image filename
        """
        im = skimage.io.imread(imname)
        if im.ndim == 2:
            im = np.repeat(im[:, :, None], 3, 2)
        im = im[:, :, :3]
        im_resized = skimage.transform.resize(im, (512, 512)) * 255
        image = (im_resized - M.image.mean) / M.image.stddev
        image = torch.from_numpy(np.rollaxis(image, 2)[None].copy()).float()
        with torch.no_grad():
            input_dict = {
                "image": image.to(self._device),
                "meta": [
                    {
                        "junc": torch.zeros(1, 2).to(self._device),
                        "jtyp": torch.zeros(1, dtype=torch.uint8).to(self._device),
                        "Lpos": torch.zeros(2, 2, dtype=torch.uint8).to(self._device),
                        "Lneg": torch.zeros(2, 2, dtype=torch.uint8).to(self._device),
                    }
                ],
                "target": {
                    "jmap": torch.zeros([1, 1, 128, 128]).to(self._device),
                    "joff": torch.zeros([1, 1, 2, 128, 128]).to(self._device),
                },
                "mode": "testing",
            }
            H = self._model(input_dict)["preds"]

        return WireframeRecord(H)
        
    
    def visualize(self, imname):
        print(f"Processing {imname}")
        im = skimage.io.imread(imname)
        if im.ndim == 2:
            im = np.repeat(im[:, :, None], 3, 2)
        im = im[:, :, :3]

        rec = self.parse(imname)
        # postprocess lines to remove overlapped lines
        diag = (im.shape[0] ** 2 + im.shape[1] ** 2) ** 0.5
        # Multiply lines by image shape to get image point coordinates
        nlines, nscores = postprocess(rec.lines() * im.shape[:2], rec.scores(), diag * 0.01, 0, False)

        for i, t in enumerate([0.94, 0.95, 0.96, 0.97, 0.98, 0.99]):
            plt.gca().set_axis_off()
            plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
            plt.margins(0, 0)
            for (a, b), s in zip(nlines, nscores):
                if s < t:
                    continue
                plt.plot([a[1], b[1]], [a[0], b[0]], c=c(s), linewidth=2, zorder=s)
                plt.scatter(a[1], a[0], **PLTOPTS)
                plt.scatter(b[1], b[0], **PLTOPTS)
            plt.gca().xaxis.set_major_locator(plt.NullLocator())
            plt.gca().yaxis.set_major_locator(plt.NullLocator())
            plt.imshow(im)
            plt.savefig(imname.replace(".png", f"-{t:.02f}.svg"), bbox_inches="tight")
            plt.show()
            plt.close()
