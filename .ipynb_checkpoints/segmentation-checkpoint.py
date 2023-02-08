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
    
def gaussian_smoothing(gaussiaSD_mm, segment_name, segmentEditorNode, segmentEditorWidget):
    
    segmentEditorNode.SetSelectedSegmentID(segment_name)
    
    segmentEditorWidget.setActiveEffectByName("Smoothing")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("SmoothingMethod", "GAUSSIAN")
    effect.setParameter("GaussianStandardDeviationMm", gaussiaSD_mm)
    effect.self().onApply()