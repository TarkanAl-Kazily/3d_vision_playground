### TO DO LIST

## Tarkan

### Accomplished

1. Created initial wireframe detection notebook, with short setup guide followed by the demo code.
1. Break down the wireframe demo code into more functions
    1. Apply a single image, but don't visualize or post process
    2. Returns the WireframeRecord class
2. Created WireframeRecord that wraps the prediction data
    1. The lines and points are accessible as numpy arrays indexing into the (resized) image
1. Break down the wireframe demo code into more functions
    1. Apply some post processing
    2. Visualize the results
1. WireframeGraph stores connected edges as graph form, and provides a way to get subgraphs
    1. We can visualize these subgraphs easily using plt (implemented in plot\_graph)
    2. Can filter based on the score threshold and number of required edges in subgraphs

### Planned

1. Given 2-5 closely overlapping images, give estimate feature matching the respective connected components
    1. Use OpenCV to get feature descriptors for vertices (actual? or approximate?) in graph
    1. For each vertex in one graph, try to match to a vertex in the other graph
    1. Choose the highest matching set passing some threshold, even if the number of vertices/edges doesn't match

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

