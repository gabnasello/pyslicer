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