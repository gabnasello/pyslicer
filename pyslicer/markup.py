import slicer

def fitPlane_from_pointMarkup(pointNodename = 'F',namePlane = 'Fitting Plane', slicerTransform = True):

    # from trimesh.points import PointCloud, plane_fit
    from pyvista import Plane, fit_plane_to_points
    from trimesh import Trimesh
    from trimesh.bounds import oriented_bounds
    from trimesh.transformations import inverse_matrix
    
    df_points = ps.markup.points_from_markup(pointNodename)
       
    fitted_plane, plane_origin, plane_normal = fit_plane_to_points(df_points.to_numpy(), return_meta = True)
    
    # pyvista PolyData to trimesh object
    triangle_polydata = fitted_plane.extract_surface().triangulate()
    faces_as_array = triangle_polydata.faces.reshape((triangle_polydata.n_cells, 4))[:, 1:] 
    tmesh = Trimesh(triangle_polydata.points, faces_as_array) 
    
    transform, _ = oriented_bounds(tmesh)

    if slicerTransform:
        # Convert to a Slicer-friendly transform (change of axis order from pyvista/VTK objects to Slicer
        transform = inverse_matrix(transform)
        first_column = transform[:,0].copy()
        third_column = transform[:,2].copy()
        transform[:,0] = third_column
        transform[:,2] = first_column
    
    plane_dict = {'origin' : plane_origin,
                  'normal' : plane_normal,
                  'transform' : transform}
    
    # fitted_plane = Plane(center=plane_origin, direction=plane_normal, i_size=i_size, j_size=j_size)
    
    planeNode = slicer.modules.models.logic().AddModel(fitted_plane)
    planeNode.SetName(namePlane)

    return planeNode, plane_dict


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

