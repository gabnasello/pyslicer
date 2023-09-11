import slicer

def segmentationNode(name='Segmentation'):
    '''

    '''

    segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
    segmentationNode.CreateDefaultDisplayNodes() # only needed for display
    segmentationNode.SetName(name)
    
    return segmentationNode


def segmentEditorWidget(segmentationNode, masterVolumeNode):
    '''

    '''

    segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
    segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
    segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
    segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
    segmentEditorWidget.setSegmentationNode(segmentationNode)
    segmentEditorWidget.setMasterVolumeNode(masterVolumeNode)
    
    return segmentEditorWidget, segmentEditorNode

def segment_statistics(segmentationNode):
    '''

    '''
    
    import SegmentStatistics
    segStatLogic = SegmentStatistics.SegmentStatisticsLogic()
    segStatLogic.getParameterNode().SetParameter("Segmentation", segmentationNode.GetID())
    segStatLogic.computeStatistics()
    stats = segStatLogic.getStatistics()
    
    return stats

def compute_threshold(method, volumeNode):
    '''
    **kwargs: arguments for pyslicer.volume.plot_histogram()
    '''
    from vtkITK import vtkITKImageThresholdCalculator

    thresholdCalculator = vtkITKImageThresholdCalculator()
    thresholdCalculator.SetInputData(volumeNode.GetImageData())

    method_number = thresholdCalculator.__getattribute__('METHOD_' + method.upper())

    thresholdCalculator.SetMethod(method_number)
    thresholdCalculator.Update()

    threshold = thresholdCalculator.GetThreshold()
       
    return threshold

def copy_segment_newNode(segment_name, input_segmentationNode, output_segmentationNode):
    '''

    '''

    segmentation = input_segmentationNode.GetSegmentation()
    sourceSegmentId = segmentation.GetSegmentIdBySegmentName(segment_name)
    
    output_segmentation = output_segmentationNode.GetSegmentation()
    output_segmentation.CopySegmentFromSegmentation(segmentation, sourceSegmentId)


def segments_by_thresholding(segments_greyvalues, segmentationNode, segmentEditorNode, segmentEditorWidget):
    '''

    '''
    
    for segmentName in segments_greyvalues:

        thresholdMin = segments_greyvalues[segmentName][0]
        thresholdMax = segments_greyvalues[segmentName][1]

        # Create segment
        addedSegmentID = segmentationNode.GetSegmentation().AddEmptySegment(segmentName)
        segmentEditorNode.SetSelectedSegmentID(addedSegmentID)

        # Fill by thresholding
        segmentEditorWidget.setActiveEffectByName("Threshold")
        effect = segmentEditorWidget.activeEffect()
        effect.setParameter("MinimumThreshold",str(thresholdMin))
        effect.setParameter("MaximumThreshold",str(thresholdMax))
        effect.self().onApply()
        
def set_segments_color(segments_color, segmentationNode):
    '''
    
    '''
    
    segmentation = segmentationNode.GetSegmentation()
    
    for segmentName in segments_color:
        
        segmentID = segmentation.GetSegmentIdBySegmentName(segmentName)
        segment = segmentation.GetSegment(segmentID)
        
        color = segments_color[segmentName]
        segment.SetColor(color)
        
def individual_segment_to_labelmapNode(segmentName, segmentationNode, volumeNode):
    '''

    '''
    
    labelmapNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode')
    labelmapNode.SetName('labelmapSegments')  
    
    segmentId = segmentationNode.GetSegmentation().GetSegmentIdBySegmentName(segmentName)
    
    from vtk import vtkStringArray
    segmentId_array = vtkStringArray()
    segmentId_array.InsertNextValue(segmentId)
    
    slicer.modules.segmentations.logic().ExportSegmentsToLabelmapNode(segmentationNode, segmentId_array, labelmapNode, volumeNode)
    
    labelmapNode.SetName(segmentName)
    
    return labelmapNode
        
def remove_small_islands(minimum_size, segment_name, segmentEditorNode, segmentEditorWidget):
    '''
    REMOVE_SMALL_ISLANDS operation from the [SegmentEditorIslandsEffect](https://github.com/Slicer/Slicer/blob/294ef47edbac2ccb194d5ee982a493696795cdc0/Modules/Loadable/Segmentations/EditorEffects/Python/SegmentEditorIslandsEffect.py#L402)
    '''
    
    segmentEditorNode.SetSelectedSegmentID(segment_name)
    
    segmentEditorWidget.setActiveEffectByName("Islands")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MinimumSize",str(minimum_size))
    effect.setParameter("Operation","REMOVE_SMALL_ISLANDS")
    effect.self().onApply()

def split_islands(minimum_size, segment_name, segmentEditorNode, segmentEditorWidget):
    '''
    SPLIT_ISLANDS_TO_SEGMENTS operation from the [SegmentEditorIslandsEffect](https://github.com/Slicer/Slicer/blob/294ef47edbac2ccb194d5ee982a493696795cdc0/Modules/Loadable/Segmentations/EditorEffects/Python/SegmentEditorIslandsEffect.py#L402)
    '''
    
    segmentEditorNode.SetSelectedSegmentID(segment_name)
    
    segmentEditorWidget.setActiveEffectByName("Islands")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MinimumSize",str(minimum_size))
    effect.setParameter("Operation","SPLIT_ISLANDS_TO_SEGMENTS")
    effect.self().onApply()
    
def keep_largest_island(minimum_size, segment_name, segmentEditorNode, segmentEditorWidget):
    '''
    KEEP_LARGEST_ISLAND operation from the [SegmentEditorIslandsEffect](https://github.com/Slicer/Slicer/blob/294ef47edbac2ccb194d5ee982a493696795cdc0/Modules/Loadable/Segmentations/EditorEffects/Python/SegmentEditorIslandsEffect.py#L402)
    '''
    
    segmentEditorNode.SetSelectedSegmentID(segment_name)
    
    segmentEditorWidget.setActiveEffectByName("Islands")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MinimumSize",str(minimum_size))
    effect.setParameter("Operation","KEEP_LARGEST_ISLAND")
    effect.self().onApply()
    
def gaussian_smoothing(gaussiaSD_mm, segment_name, segmentEditorNode, segmentEditorWidget):
    '''
    GAUSSIAN smoothing from the [SegmentEditorSmoothingEffect] (https://github.com/Slicer/Slicer/blob/294ef47edbac2ccb194d5ee982a493696795cdc0/Modules/Loadable/Segmentations/EditorEffects/Python/SegmentEditorSmoothingEffect.py)
    '''
    
    
    segmentEditorNode.SetSelectedSegmentID(segment_name)
    
    segmentEditorWidget.setActiveEffectByName("Smoothing")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("SmoothingMethod", "GAUSSIAN")
    effect.setParameter("GaussianStandardDeviationMm", gaussiaSD_mm)
    effect.self().onApply()
    

def closing_holes(kernelSize_mm, segment_name, segmentEditorNode, segmentEditorWidget):
    '''
    Closing (fill holes) [MORPHOLOGICAL_CLOSING] smoothing from the [SegmentEditorSmoothingEffect] (https://github.com/Slicer/Slicer/blob/294ef47edbac2ccb194d5ee982a493696795cdc0/Modules/Loadable/Segmentations/EditorEffects/Python/SegmentEditorSmoothingEffect.py)
    '''
    
    segmentEditorNode.SetSelectedSegmentID(segment_name)
    
    segmentEditorWidget.setActiveEffectByName("Smoothing")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("SmoothingMethod", "MORPHOLOGICAL_CLOSING")
    effect.setParameter("KernelSizeMm", kernelSize_mm)
    effect.self().onApply()