import slicer

def decimate_model(modelNode, reductionFactor = 0.8):
    '''
    Model decimation from the [SurfaceToolbox module](https://github.com/Slicer/SlicerSurfaceToolbox/blob/master/SurfaceToolbox/SurfaceToolbox.py)
    
    Args:
        modelNode (MRMLCore.vtkMRMLModelNode): input model node 
        reductionFactor (double): reduction factor for element surface decimation. Default is 0.8

    Returns:
        modelNode_deciamted (MRMLCore.vtkMRMLModelNode): decimated model node 
    '''
    
    

    modelNode_deciamted = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode')
    modelNode_deciamted.SetName(modelNode.GetName()+'_decimated')

    parameters = {
      "inputModel": modelNode,
      "outputModel": modelNode_deciamted,
      "reductionFactor": reductionFactor,
      "method": "FastQuadric",
      "boundaryDeletion": True
      }

    # cliNode is a temporary node
    cliNode = slicer.cli.runSync(slicer.modules.decimation, None, parameters)
    slicer.mrmlScene.RemoveNode(cliNode)
    
    return modelNode_deciamted

def create_hollow_cylinder(height=1, 
                           radius_inner=0, radius_outer=1, space =5, 
                           center=(0.0, 0.0, 0.0),
                           direction=(0, 0, 1),
                           transform=False,
                           nameModel='Cylinder', 
                           color=(230/255, 230/255, 77/255), 
                           opacity=1):

    from pyvista import CylinderStructured
    from numpy import linspace
    from vtk import vtkMatrix4x4
    from numpy import ndarray
    
    cyl_hollow = CylinderStructured(radius=linspace(radius_inner, radius_outer, space), height=height, direction=direction, center=center)

    if transform is not False:
        if isinstance(transform, slicer.vtkMRMLTransformNode):
            transformMatrix = vtkMatrix4x4()
            transform.GetMatrixTransformToWorld(transformMatrix)
            transformArray = slicer.util.arrayFromVTKMatrix(transformMatrix)

        if isinstance(transform, ndarray):
            transformArray = transform
        
        cyl_hollow = cyl_hollow.transform(transformArray)

    cyl_node = slicer.modules.models.logic().AddModel(cyl_hollow.extract_surface())
        
    cyl_node.SetName(nameModel)
    
    modelDisplayNode = cyl_node.GetDisplayNode()
    modelDisplayNode.SetColor(color[0], color[1], color[2])
    modelDisplayNode.SetOpacity(opacity)

    return cyl_node

def register_model_to_points(inputModel, inputFiducials):

    from vtk import vtkMatrix4x4
    
    # Create output transform node
    transformNode = slicer.vtkMRMLTransformNode()

    # Run module logic with default settings
    fiducialsModelLogic = slicer.modules.fiducialstomodelregistration.widgetRepresentation().self().logic
    
    fiducialsModelLogic.run(inputFiducials, inputModel, transformNode)

    transformMatrix = vtkMatrix4x4()
    transformNode.GetMatrixTransformToWorld(transformMatrix)
    transformMatrix.Invert()

    # Create new transform node with the inverted transform matrix
    transformNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
    transformNode.SetName('Transform Cylinder Defect')
    transformNode.SetMatrixTransformToParent(transformMatrix);

    return transformNode

def sort_points_clockwise(points, clockwise=True):

    from numpy import ndarray, array
    from math import atan2

    if isinstance(points, ndarray):
        points_list = points.tolist()
    else:
        points_list = points
    
    def argsort(seq):
        #http://stackoverflow.com/questions/3382352/equivalent-of-numpy-argsort-in-basic-python/3382369#3382369
        #by unutbu
        #https://stackoverflow.com/questions/3382352/equivalent-of-numpy-argsort-in-basic-python 
        # from Boris Gorelik
        return sorted(range(len(seq)), key=seq.__getitem__)
    
    def rotational_sort(list_of_xy_coords, centre_of_rotation_xy_coord, clockwise=True):
        cx,cy=centre_of_rotation_xy_coord
        angles = [atan2(x-cx, y-cy) for x,y in list_of_xy_coords]
        indices = argsort(angles)
        if clockwise:
            return [list_of_xy_coords[i] for i in indices]
        else:
            return [list_of_xy_coords[i] for i in indices[::-1]]

    def centeroid_list_points(data):
        x, y = zip(*data)
        l = len(x)
        return sum(x) / l, sum(y) / l

    points_sorted = rotational_sort(points_list, centeroid_list_points(points), clockwise)

    if isinstance(points, ndarray):
        points_sorted = array(points_sorted)

    return points_sorted

def extrude_polygon_from_points(points,
                                height=1, 
                                rotate_z=0,
                                scale=(0, 0, 0),
                                transform=False,
                                nameModel='Extrude', 
                                color=(230/255, 230/255, 77/255), 
                                opacity=1):

    """
    Convert a sequence of 2d coordinates to an extruded polygon
    """
    
    from pyvista import PolyData
    from vtk import vtkMatrix4x4
    from numpy import ndarray
    
    z0 = 0

    if isinstance(points, ndarray):
        points = points.tolist()

    points = sort_points_clockwise(points, clockwise=True)
    
    # bounding polygon
    #Convert a sequence of 2d coordinates to a polydata with a polygon
    faces = [len(points), *range(len(points))]
    polygon = PolyData([p + [z0,] for p in points], faces=faces)
    
    # extrude
    solid = polygon.extrude((0, 0, height), capping=True)

    solid.translate((0, 0, -height/2), inplace=True)

    if scale!=(0, 0, 0):
        solid.scale(scale, inplace=True)
    
    if rotate_z!=0:
        solid.rotate_z(rotate_z, inplace=True)
        
    if transform is not False:
        if isinstance(transform, slicer.vtkMRMLTransformNode):
            transformMatrix = vtkMatrix4x4()
            transform.GetMatrixTransformToWorld(transformMatrix)
            transformArray = slicer.util.arrayFromVTKMatrix(transformMatrix)

        if isinstance(transform, vtkMatrix4x4):
            transformArray = slicer.util.arrayFromVTKMatrix(transform)

        if isinstance(transform, ndarray):
            transformArray = transform
        
        solid = solid.transform(transformArray)

    extrude_node = slicer.modules.models.logic().AddModel(solid.extract_surface())
        
    extrude_node.SetName(nameModel)
    
    modelDisplayNode = extrude_node.GetDisplayNode()
    modelDisplayNode.SetColor(color[0], color[1], color[2])
    modelDisplayNode.SetOpacity(opacity)

    return extrude_node