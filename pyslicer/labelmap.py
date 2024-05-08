import slicer
import numpy as np

def get_erode_shell_labelmap(erosion_level, labelmap, eroded_name = 'labelEroded', shell_name = 'labelShell'):
    '''
    
    '''
    
    # Get numpy array from Volume nodes. Make a deep-copy of the returned VTK-managed array if the array will not not be reallocated
    label_array = np.copy(slicer.util.arrayFromVolume(labelmap))
    
    array_eroded, array_shell = get_erode_shell_array(erosion_level, label_array)
        
    # Create new labelmap nodes for the eroded array
    labelmapEroded = slicer.vtkSlicerVolumesLogic().CloneVolume(slicer.mrmlScene, labelmap, 'out')
    labelmapEroded.SetName(eroded_name)
    slicer.util.updateVolumeFromArray(labelmapEroded, array_eroded)
    
    # Create new labelmap nodes for the shell array
    labelmapShell = slicer.vtkSlicerVolumesLogic().CloneVolume(slicer.mrmlScene, labelmap, 'out')
    labelmapShell.SetName(shell_name)
    slicer.util.updateVolumeFromArray(labelmapShell, array_shell)
    
    return labelmapEroded, labelmapShell

def get_erode_shell_array(erosion_level, label_array):
    '''
    
    '''
    
    from scipy import ndimage
       
    # Image erosion implemented with [`scipy.ndimage.binary_erosion`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.binary_erosion.html#scipy-ndimage-binary-erosion) function.
    struct = np.ones((erosion_level, erosion_level, erosion_level))
    array_eroded = ndimage.binary_erosion(label_array, structure=struct).astype(label_array.dtype)
    
    # Shell array (`array_shell`) is simply the element-wise difference between `label_array` and `array_eroded`
    array_shell = label_array - array_eroded
       
    return array_eroded, array_shell

def labelmapNode(name='Labelmap'):
    '''

    '''
    
    labelmapNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode')
    labelmapNode.SetName(name)
    
    return labelmapNode