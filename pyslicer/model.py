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
                           radius_inf=0.5, radius_sup=1, space =5, 
                           direction=(1, 0, 0),
                           transformNode=False,
                           nameModel='Cylinder', 
                           color=(230/255, 230/255, 77/255), 
                           opacity=1):

    from pyvista import CylinderStructured
    from numpy import linspace
    from vtk import vtkMatrix4x4
    
    cyl_hollow = CylinderStructured(radius=linspace(radius_inf, radius_sup, space), height=height, direction=(0, 0, 1))

    if transformNode is not False:
        transformMatrix = vtkMatrix4x4()
        transformNode.GetMatrixTransformToWorld(transformMatrix)
        cyl_hollow = cyl_hollow.transform(slicer.util.arrayFromVTKMatrix(transformMatrix))

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