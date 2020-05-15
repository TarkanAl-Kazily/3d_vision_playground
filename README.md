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

## Key Files 


## Project Structure
