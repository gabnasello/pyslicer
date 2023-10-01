import slicer

def points_from_markup(pointNodename = 'F'):   
    '''
    Extract points from a Point List Node 

    Args:
        nodename (str): Name of the markup node containing the poiunt list. Default "F"

    Returns:
        df_points (pandas.DataFrame): pandas dataframe listing all points in (r,s,a) coordinate system
    '''

    from pandas import DataFrame, concat
    from vtk import vtkVector3d

    lineListNode = slicer.util.getNode(pointNodename)

    #colnames = ['x', 'y', 'z']
    colnames = ['r', 'a', 's']
    df_points = DataFrame(columns=colnames)

    for i in range(lineListNode.GetNumberOfControlPoints()):
        pt = vtkVector3d(0,0,0)
        lineListNode.GetNthControlPointPosition(i,pt)

        # append point data to points_df
        df = DataFrame(data = [list(pt)], columns=colnames, index = [i])

        df_points = concat([df_points, df])
        
    return df_points


def minimumCylinder_from_pointMarkup(pointNodename = 'F', nameCylinder = 'Cylinder'):

    from trimesh.points import PointCloud
    from pyvista import wrap
    from trimesh.bounds import minimum_cylinder
    from trimesh.primitives import Cylinder
    
    df_points = points_from_markup(pointNodename)

    points_mesh = PointCloud(df_points.to_numpy())
    
    cylinder_dict = minimum_cylinder(points_mesh)
    
    cylinder_primitive = Cylinder(radius=cylinder_dict['radius'], 
                                  height=cylinder_dict['height'], 
                                  transform=cylinder_dict['transform'])
    
    cylinder = wrap(cylinder_primitive.to_mesh())
    
    cylinderNode = slicer.modules.models.logic().AddModel(cylinder)

    cylinderNode.SetName(nameCylinder)

    return cylinderNode, cylinder_dict


def project_markupPoints_to_plane(pointNodename, 
                                  plane_normal=(0,0,1), 
                                  plane_origin=(0,0,0), 
                                  return_planar=True):

    from trimesh.points import project_to_plane
    
    df_points = points_from_markup(pointNodename)
            
    projected_points = project_to_plane(df_points.to_numpy(), 
                                        plane_normal=plane_normal,
                                        plane_origin=plane_origin,
                                        return_planar=return_planar
                                       )  

    return projected_points

def voronoi_diagram(points, only_inside_vertices=True):

    from scipy.spatial import Voronoi
    
    # Get Voronoid diagram of the projected points
    vor = Voronoi(points)
    
    # Store only vertices inside convex hull of points
    if only_inside_vertices:
        def in_hull(p, hull):
            """
            Test if points in `p` are in `hull`
        
            `p` should be a `NxK` coordinates of `N` points in `K` dimensions
            `hull` is either a scipy.spatial.Delaunay object or the `MxK` array of the 
            coordinates of `M` points in `K`dimensions for which Delaunay triangulation
            will be computed
            """
            from scipy.spatial import Delaunay
            if not isinstance(hull,Delaunay):
                hull = Delaunay(hull)
        
            return hull.find_simplex(p)>=0

        inside_hull = in_hull(vor.vertices, points)
        
        return vor.vertices[inside_hull], vor

    return vor.vertices, vor

def get_furthest_voronoi_vertex(voronoid_vertices, points):
    
    from numpy import asarray, argmin
    from numpy.linalg import norm
    
    # Find furthest Voronoi node from the point cloud
    def closest_node(node, nodes):
        nodes = asarray(nodes)
        deltas = nodes - node
        dist = norm(deltas, axis=1)
        min_idx = argmin(dist)
        return nodes[min_idx], dist[min_idx], deltas[min_idx][1]/deltas[min_idx][0]  # point, distance, slope
    
    if len(points) >= 4:
        defect_radius = 0
        center_defect = None
        for v in voronoid_vertices:
            _, d, _ = closest_node(v, points)
            if d > defect_radius:
                defect_radius = d
                center_defect = v

    return center_defect, defect_radius