#
# wireframe_point_cloud.py
#
# Classes and functions related to point clouds and wireframe code
#

import numpy as np
import os
import cv2


class WireframePointCloud():
    """
    WireframePointCloud

    A class that works with point clouds and generates PLY files for visualizing
    wireframe features.

    Important Attributes:
    project_dir -- full directory storing all relevant data
    name -- original image name
    rec -- detected wireframe record
    info -- Structure for Motion information, including a point cloud
    cam -- camera parameters from OpenSfM
    """
    def __init__(self, project_dir, imname, rec, iminfo, caminfo, **kwargs):
        """
        imname, rec, iminfo, and caminfo all correspond to above attributes.

        Optional keyword arguments:
        threshold -- line score threshold value in [0.0, 1.0]
        distance -- required distance projected 2D points need to be in line point cloud
        """
        self.project_dir = project_dir
        self.name = imname
        self.rec = rec
        self.info = iminfo
        self.cam = caminfo

        self._wireframe_ply_dir = os.path.join(project_dir,
                "wireframe_ply/{}.ply_dir/".format(self.name))

        self._threshold = kwargs.get("threshold", 0.95)
        self._2d_distance = kwargs.get("distance", 20.0)

        # The ::-1 reverses the endpoints from (y, x) to (x, y)
        self._lines = rec.postprocess(self._threshold)[0][:, :, ::-1]

        self._points = np.array(self.info["vertices"])
        self._R = np.array(self.info["rotation"])
        self._T = np.array(self.info["translation"])
        self._K, self._distortion = get_K_dist(self.cam)
        self._points_proj = self.project_points(self._points)

        # Data structure for all the points corresponding to each line
        # Length is number of lines
        # Elements are numpy arrays of points
        self._line_point_clouds = []
        for l in self._lines:
            l_points_idx, _ = get_points_near_line_2D(self._points_proj, l, dist=self._2d_distance)
            l_points_idx = l_points_idx[0]
            self._line_point_clouds.append(self._points[l_points_idx, :])

    def project_points(self, points):
        """
        Computes point projection
        """
        res, _ = cv2.projectPoints(points, self._R, self._T, self._K, self._distortion)
        return np.array(res)

    def write_ply(self, vertices, edges, c=[255, 255, 255]):
        """
        Outputs contents of a ply file
        Arguments:
        vertices -- vertices in the PLY file. If None, no vertex metadata is written
        edges -- edges in the PLY file. If None, no edge metadata is written
        c -- rgb list: color of vertices and edges (default white)
        """
        do_vertices = False
        do_edges = False
        yield "ply\n"
        yield "format ascii 1.0\n"
        if (vertices is not None) and (vertices.shape[0] > 0):
            do_vertices = True
            yield "element vertex {}\n".format(vertices.shape[0])
            yield "property float x\n"
            yield "property float y\n"
            yield "property float z\n"
            yield "property uchar red\n"
            yield "property uchar green\n"
            yield "property uchar blue\n"
        if (edges is not None) and (edges.shape[0] > 0):
            do_edges = True
            yield "element edge {}\n".format(edges.shape[0])
            yield "property int vertex1\n"
            yield "property int vertex2\n"
            yield "property uchar red\n"
            yield "property uchar green\n"
            yield "property uchar blue\n"
        yield "end_header\n"
        
        if do_vertices:
            v_template = "{:4f} {:4f} {:4f} {} {} {}\n"
            for x, y, z in vertices:
                yield v_template.format(x, y, z, c[0], c[1], c[2])
        if do_edges:
            e_template = "{} {} {} {} {}\n"
            for u, v in edges:
                yield e_template.format(u, v, c[0], c[1], c[2])

    def write_line_point_clouds(self):
        """
        Creates ply files for each line point cloud
        """
        os.makedirs(self._wireframe_ply_dir, exist_ok=True)
        for i, pt_cloud in enumerate(self._line_point_clouds):
            if pt_cloud.shape[0] == 0:
                continue
            with open(os.path.join(self._wireframe_ply_dir, "line_{}.ply".format(i)), 'w') as f:
                text = self.write_ply(pt_cloud, None, c=[255, 0, 0])
                f.writelines(text)


#########################################################
# Other utility functions
#########################################################

def get_K_dist(camera):
    camera_name = next(iter(camera.keys()))
    width = camera[camera_name]["width"]
    height = camera[camera_name]["height"]
    focal = camera[camera_name]["focal"]
    k1 = camera[camera_name]["k1"]
    k2 = camera[camera_name]["k2"]

    K = np.array([[focal * max(width, height), 0, 0.5 * (width - 1)],
                  [0, focal * max(width, height), 0.5 * (height - 1)],
                  [0, 0, 1]])
    distortion = np.array([k1, k2, 0, 0, 0])
    return K, distortion

def get_points_near_line_2D(points, line, dist=20.0):
    """
    Returns the indices and points close to line.
    2D case.

    Arguments:
    points -- one or more points in a numpy array of shape [num_points, 2]
    line -- numpy array of shape [2, 2]
    """
    start, end = line
    perp_dir = (np.array([[0, -1], [1, 0]]) @ (end - start)) / np.linalg.norm(end - start)
    distances = np.dot(points - start, perp_dir)
    close_enough = np.abs(distances) < dist
    ts = np.dot(points - start, end - start)
    in_interval = np.logical_and(0 < ts, ts < np.linalg.norm(end - start) ** 2)
    condition = np.logical_and(close_enough, in_interval)
    return np.nonzero(condition), points[condition]
