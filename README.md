# 3D Reconstruction Using Detected Wireframe Features and a Point Cloud Reconstruction

## Dependencies

1. OpenSfM: [https://www.openopensfm.org/docs/]
    a. `git submodule update --init --recursive # to get OpenSfM source files`
    b. See https://www.opensfm.org/docs/building.html for installing dependencies
2. LCNN: [https://github.com/zhou13/lcnn] 
    a. See `notebooks/WireframeDetection.ipynb` for installing dependencies and downloading the pretrained model.

## User Guide

Save the video you want to process to the root of the project repository and extract frames to the project directory.

```
mkdir -p data/project/images
cd tools 
python3 video_converter.py ../video_name.mp4 --outputdir ../data/project/images -n <save_every_n_images>
```

```
cd ../OpenSfM
bin/opensfm_run_all ../data/project
``
