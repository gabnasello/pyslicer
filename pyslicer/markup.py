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