### TO DO LIST

## Tarkan

### Accomplished

1. Created initial wireframe detection notebook, with short setup guide followed by the demo code.
1. Break down the wireframe demo code into more functions
    1. Apply a single image, but don't visualize or post process
    2. Returns the WireframeRecord class
2. Created WireframeRecord that wraps the prediction data
    1. The lines and points are accessible as numpy arrays indexing into the (resized) image

### Planned

1. Break down the wireframe demo code into more functions
    1. Apply some post processing
    2. Visualize the results
2. Create a class to store the processed wireframe information
    1. Graph theory it up - Chose [python-igraph](https://igraph.org/python/#docs)
       for backing graph library
    2. Create class for junction
    1. Create class for lines
1. Analyze the differences in output for low to high confidence edges

## Toby

### Accomplished
1. Video Parser: Complete

1. Preliminary SfM Testing
2. Create Interface for SfM pipeline
    1. get_camera_poses
    2. add_feature_points
    3. generate_feature_record
    4. get_3d
    5. generate_pointcloud
    6. view_pointcloud
    
### Planned

