import slicer

def labelmapNode(name='Labelmap'):
    '''

    '''
    
    labelmapNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode')
    labelmapNode.SetName(name)
    
    return labelmapNode