# 3D Reconstruction Using Detected Wireframe Features and a Point Cloud Reconstruction

## Dependencies

1. OpenSfM: [https://www.openopensfm.org/docs/]
    1. `git submodule update --init --recursive # to get OpenSfM source files`
    2. See https://www.opensfm.org/docs/building.html for installing dependencies
2. LCNN: [https://github.com/zhou13/lcnn] 
    1. See `notebooks/WireframeDetection.ipynb` for installing dependencies and downloading the pretrained model.

## User Guide

Save the video you want to process to the root of the project repository and extract frames to the project directory.

```
mkdir -p data/project/images
cd tools 
python3 video_converter.py ../video_name.mp4 --outputdir ../data/project/images -n <save_every_n_images>
```

Compute the merged point cloud for the set of project images

```
cd ../OpenSfM
bin/opensfm_run_all ../data/project
```

Compute the 2D wireframe information for our dataset

```
cd notebooks/
python3 wireframe_save_records.py ../data/project/
```

Obtain 3D line information and save as .PLY files in project directory

```
cd notebooks/
python3 wireframe_run_ply.py ../data/project
```

Combine all line information, enforce manhattan constraints and create final model

```
cd notebooks/
python3 filter_script.py ../data/project
```

## Project Structure
```
OpenSfM/                        # opensfm source code as a submodule
notebooks/                      # all source code
    lcnn/                       # lcnn source code 
    sfm/                        # utility functions for loading data from opensfm 
    myply/                      # PLY objects for loading, writing, and helper functions for grouping edges
    wireframe/                  # 
    wireframe_save_records.py
    wireframe_run_ply.py
    filter_script.py
    *.ipynb                     # various notebooks for running opensfm, wireframe detection and other modules
tools/                          # helper scripts for conveting files
```
