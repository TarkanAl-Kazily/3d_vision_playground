### TO DO LIST

1. Given 2-5 closely overlapping images, give estimate feature matching the respective connected components
    1. Use OpenCV to get feature descriptors for vertices (actual? or approximate?) in graph
    1. For each vertex in one graph, try to match to a vertex in the other graph
    1. Choose the highest matching set passing some threshold, even if the number of vertices/edges doesn't match

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
1. Created WireframePointCloud to generate point clouds related to wireframe features
    1. wireframe\_run\_ply.py constructs all the wireframe point clouds for lines
    2. Gives each one random colors to visualize in meshlab
    3. Can merge ply files with tools/merge\_ply.py for ease of viewing
1. Estimating the original line's 3D structure: DONE!
    1. We have a point cloud representing 3D points near the line (in reality these may be terrible points)
    2. Use RANSAC with principle component (https://stackoverflow.com/questions/2298390/fitting-a-line-in-3d) to get a more robust line
    3. Put line into ply file (optional: with point cloud)
    4. Optional: Throw out outlier points from point clouds - instead I just change their color

### Planned

1. For each image, we get OpenSfM and Wireframe information. Do stuff with it.
    1. OpenSfM gives camera intrinsics, rotation and translation, and a cloud of points seen by the image.
    2. Wireframe information is a list of lines that have endpoints.
    3. If we can estimate the 3D position of the line endpoints, then we could create our own "point cloud" of just the 3D line features and visualize that. This requires:
    4. For a line in an image, find points in the point cloud that reproject near it (Done - visualized in meshlab)
    5. Estimate the original line's 3D structure using the points in the point cloud
    6. Collect up all of the estimated 3D lines as edges (meaning capture their endpoints as vertices) to write out a new ply file for visualization.
1. Modify merge\_ply.py to optionally only do vertices or edges
2. Combining lines between images:
    1. We have a bunch of 3D lines and point clouds for each line.
    2. If the 3D lines overlap (check <endpt, dir> for each line, if falls in [0, len] they overlap) check the direction, if close to the same merge point clouds.
    3. With new merged point cloud generate new best fit line with RANSAC
3. Improve 3D line estimation:
    1. Get the coimage of the line in the image to define the plane that the line must fall into
    2. Do RANSAC with this constraint in mind by first projecting the point cloud into the plane, and performing 2D ransac fitting

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

