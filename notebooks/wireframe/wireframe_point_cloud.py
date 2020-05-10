#
# wireframe_point_cloud.py
#
# Classes and functions related to point clouds and wireframe code
#

import numpy as np
import os
import cv2

import wireframe.wireframe_ransac

class WireframePointCloud():
    """
    WireframePointCloud

    A class that works with point clouds and generates PLY files for visualizing
    wireframe features.

    Important Attributes:
    info -- Structure for Motion information, including a point cloud
    cam -- camera parameters from OpenSfM

    _line_point_clouds -- Point clouds corresponding to detected line features
    _fitted_3d_lines   -- Fitted 3D lines given by (start, end) corresponding to detected line features
    """
    def __init__(self, project_dir, imname, rec, iminfo, caminfo, **kwargs):
        """
        imname, iminfo, and caminfo all correspond to above attributes.

        Optional keyword arguments:
        threshold -- line score threshold value in [0.0, 1.0]
        distance -- required distance projected 2D points need to be in line point cloud
        color -- [r, g, b] or None, in which case color is chosen randomly for each line
        """
        self.info = iminfo
        self.cam = caminfo

        self._wireframe_ply_dir = os.path.join(project_dir,
                "wireframe_ply/{}.ply_dir/".format(imname))

        self._threshold = kwargs.get("threshold", 0.95)
        self._2d_distance = kwargs.get("distance", 20.0)
        self._c = kwargs.get("color", None)
        self._line_ransac_iterations = kwargs.get("line_ransac_iterations", 20)
        self._line_inlier_thresh = kwargs.get("line_inlier_thresh", 0.25)
        self._min_line_inliers = kwargs.get("min_line_inliers", 5)
        self._color_inliers = kwargs.get("color_inliers", False)

        # The ::-1 reverses the endpoints from (y, x) to (x, y)
        initial_lines = rec.postprocess(self._threshold)[0][:, :, ::-1]

        self._points = np.array(self.info["vertices"])
        self._R = np.array(self.info["rotation"])
        self._T = np.array(self.info["translation"])
        self._K, self._distortion = get_K_dist(self.cam)
        self._points_proj = self.project_points(self._points)

        # Data structure for all the points corresponding to each line
        # Length is number of lines
        # Elements are numpy arrays of points
        self._line_point_clouds = []
        for l in initial_lines:
            l_points_idx, _ = get_points_near_line_2D(self._points_proj, l, dist=self._2d_distance)
            l_points_idx = l_points_idx[0]
            self._line_point_clouds.append(self._points[l_points_idx, :])

        # Data structure for all the fitted 3d lines corresponding to each point cloud
        # Length is number of lines
        # Elements are numpy arrays of shape [2, 3]
        self._fitted_3d_lines = []
        fitter = wireframe.wireframe_ransac.Line3DRANSAC(self._line_ransac_iterations, self._line_inlier_thresh, None)
        for cloud in self._line_point_clouds:
            line, n_inliers = fitter.ransac(cloud)
            if n_inliers < self._min_line_inliers:
                line = np.array([])
            self._fitted_3d_lines.append(line)

        if self._color_inliers:
            # Data structure for all the colors of inliers
            self._c = []
            for cloud, line in zip(self._line_point_clouds, self._fitted_3d_lines):
                if line.shape[0] == 0:
                    self._c.append(np.broadcast_to(np.array([255, 0, 0]), (cloud.shape[0], 3)))
                    continue
                error = fitter.get_error(cloud, line)
                colors = np.where(np.expand_dims(error < self._line_inlier_thresh, 1), np.array([[255, 255, 255]]), np.array([[255, 0, 0]]))
                colors = np.vstack([colors, np.broadcast_to(255, (4, 3))])
                self._c.append(colors)

    def project_points(self, points):
        """
        Computes point projection
        """
        res, _ = cv2.projectPoints(points, self._R, self._T, self._K, self._distortion)
        return np.array(res)

    def write_ply(self, vertices, edges, c=np.array([255, 255, 255])):
        """
        Outputs contents of a ply file
        Arguments:
        vertices -- vertices in the PLY file. If None, no vertex metadata is written
        edges -- edges in the PLY file. If None, no edge metadata is written
        c -- numpy array: color of vertices and edges (default white) if None, random
             if shape is (3), use np array for all vertices and edges
             otherwise if 2D use c[i] for v[i], c[i + n_vertices] for e[i]
        """
        if c is None:
            c = np.random.randint(0, high=256, size=3)

        do_vertices = False
        do_edges = False
        num_vertices = 0
        num_edges = 0
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
            num_vertices = vertices.shape[0]
        if (edges is not None) and (edges.shape[0] > 0):
            do_edges = True
            yield "element edge {}\n".format(edges.shape[0])
            yield "property int vertex1\n"
            yield "property int vertex2\n"
            yield "property uchar red\n"
            yield "property uchar green\n"
            yield "property uchar blue\n"
            num_edges = edges.shape[0]
        yield "end_header\n"

        if len(c.shape) == 1:
            c = np.broadcast_to(c, (num_vertices + num_edges, 3))
        
        if do_vertices:
            v_template = "{:4f} {:4f} {:4f} {} {} {}\n"
            for i, (x, y, z) in enumerate(vertices):
                yield v_template.format(x, y, z, c[i, 0], c[i, 1], c[i, 2])
        if do_edges:
            e_template = "{} {} {} {} {}\n"
            for i, (u, v) in enumerate(edges):
                yield e_template.format(u, v, c[i + num_vertices, 0], c[i + num_vertices, 1], c[i + num_vertices, 2])

    def write_line_point_clouds(self):
        """
        Creates ply files for each line point cloud
        """
        os.makedirs(self._wireframe_ply_dir, exist_ok=True)
        for i, (pt_cloud, line) in enumerate(zip(self._line_point_clouds, self._fitted_3d_lines)):
            if pt_cloud.shape[0] == 0 and line.shape[0] == 0:
                continue
            vertices = pt_cloud
            edges = None
            if line.shape[0] == 2:
                vertices = np.vstack((vertices, line))
                edges = np.array([np.arange(2) + pt_cloud.shape[0]])
            with open(os.path.join(self._wireframe_ply_dir, "line_{}.ply".format(i)), 'w') as f:
                text = self.write_ply(vertices, edges, c= self._c[i] if self._color_inliers else self._c)
                f.writelines(text)

    def combine(self, other_wpc):
        """
        Adds the point cloud and 3d line information from other_wpc to this point cloud object

        Arguments:
        other_wpc -- The other WireframePointCloud to add to this object
        """
        raise NotImplementedError()

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
