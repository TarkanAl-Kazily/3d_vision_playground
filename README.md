# 3D Reconstruction Using Detected Wireframe Features and a Point Cloud Reconstruction

## Dependencies

1. OpenSfM: [https://www.openopensfm.org/docs/]
    1. `git submodule update --init --recursive # to get OpenSfM source files`
    2. See https://www.opensfm.org/docs/building.html for installing dependencies
2. LCNN: [https://github.com/zhou13/lcnn] 
    1. See `notebooks/WireframeDetection.ipynb` for installing dependencies and downloading the pretrained model.
    2. You may need to update your model configuration file location information in wireframe\_run\_ply.py.

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

Main project entry point - Estimate 3D line line information, enforce manhattan constraints, determine line intersections and create final model

```
cd notebooks/
python3 main_wireframe_reconstruction.py ../data/project
```

Optional - Obtain just the initial 3D line segments and save as .PLY files in project directory seperately (done as part of main entry point)

```
cd notebooks/
python3 wireframe_run_ply.py ../data/project
```


## Project Structure
```
OpenSfM/                                        # opensfm source code as a submodule
notebooks/                                      # all source code
    lcnn/                                       # lcnn source code 
    sfm/                                        # utility functions for loading data from opensfm 
    myply/                                      # PLY classes for loading, writing, and helper functions for working with edges and point clouds
    wireframe/                                  # python module for interacting with LCNN wireframe detection, and performing model fitting
    wireframe_save_records.py                   # python script for saving detected 2D wireframe features
    wireframe_run_ply.py                        # python script for inferring initial 3D line segments as part of project
    main_wireframe_reconstruction.py            # Main project entry point
    *.ipynb                                     # various notebooks for running opensfm, wireframe detection and other modules
tools/                                          # helper scripts for converting files
```
