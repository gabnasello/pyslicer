import slicer

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

def logical_intersect(segment_name, modifier_segment_name, segmentationNode, segmentEditorNode, segmentEditorWidget):
    '''
    '''
    
    segmentEditorNode.SetSelectedSegmentID(segment_name)
    
    modifier_segmentId = segmentationNode.GetSegmentation().GetSegmentIdBySegmentName(modifier_segment_name)
    
    segmentEditorWidget.setActiveEffectByName("Logical operators")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("Operation","INTERSECT")
    effect.setParameter("ModifierSegmentID", modifier_segmentId)
    effect.self().onApply()

def margin_segmentation(
    segmentationNode,
    masterVolumeNode,
    segmentEditorNode,
    segmentEditorWidget,
    segment_name=None,
    shrink_pixels=None,
    shrink_mm=None,
    apply_to_all_visible=False
):
    """
    Apply Margin effect (grow/shrink) to segmentation.

    Exactly ONE of `shrink_pixels` or `shrink_mm` must be provided.

    Parameters
    ----------
    shrink_pixels : int, optional
        Number of voxels to grow (+) or shrink (−).
        Example: -5 → shrink by 5 pixels.
    shrink_mm : float, optional
        Margin size in millimeters.
        Example: -0.1 → shrink by 0.1 mm.
    """

    # --- Safety checks ---------------------------------------------------------
    if (shrink_pixels is None and shrink_mm is None) or \
       (shrink_pixels is not None and shrink_mm is not None):
        raise ValueError("Provide exactly one of shrink_pixels or shrink_mm")

    # --- Convert pixels → mm if needed ----------------------------------------
    if shrink_mm is None:
        spacing = masterVolumeNode.GetSpacing()
        shrink_mm = shrink_pixels * spacing[0]

    # --- Configure Segment Editor ---------------------------------------------
    segmentEditorWidget.setActiveEffectByName("Margin")
    effect = segmentEditorWidget.activeEffect()

    if apply_to_all_visible:
        effect.setParameter("ApplyToAllVisibleSegments", 1)
    else:
        segmentID = segmentationNode.GetSegmentation().GetSegmentIdBySegmentName(segment_name)
        segmentEditorNode.SetSelectedSegmentID(segmentID)

    effect.setParameter("MarginSizeMm", str(shrink_mm))
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

def stats_to_dataframe(stats, orientation="long"):
    """
    Convert SegmentStatisticsLogic.getStatistics() dict to a pandas DataFrame.

    Parameters
    ----------
    stats : dict
        Output of SegmentStatisticsLogic.getStatistics().
    orientation : {"long", "wide"}, default "long"
        "long" returns one row per segment per measurement with full metadata.
        "wide" returns one row per segment with one column per measurement value.

    Returns
    -------
    pandas.DataFrame
    """
    try:
        import pandas as pd
    except Exception as e:
        raise ImportError(
            "pandas is required to build a DataFrame. "
            "Install pandas in your Slicer Python environment."
        ) from e

    segment_ids = stats.get("SegmentIDs", [])
    measurement_info = stats.get("MeasurementInfo", {})

    # Collect rows from tuple keys: (segmentName, measurementKey) -> value
    rows = []
    for k, v in stats.items():
        if not isinstance(k, tuple) or len(k) != 2:
            continue

        segment, measurement_key = k

        # Skip the identity row
        if measurement_key == "Segment":
            continue

        info = measurement_info.get(measurement_key, {})
        plugin, short_key = measurement_key.split(".", 1) if "." in measurement_key else ("", measurement_key)

        row = {
            "segment": segment,
            "measurement_key": measurement_key,
            "plugin": plugin,
            "short_key": short_key,
            "value": v,
            "name": info.get("name"),
            "title": info.get("title"),
            "description": info.get("description"),
            "units": info.get("units"),
        }

        # Include any available DICOM metadata as separate columns
        for mk, mv in info.items():
            if isinstance(mk, str) and mk.startswith("DICOM."):
                row[mk] = mv

        rows.append(row)

    df_long = pd.DataFrame(rows)

    if df_long.empty:
        return df_long

    # A human readable display name like "Mean [HU]" when units are present
    def make_display_name(row):
        nm = row.get("name") or row.get("title") or row.get("short_key")
        units = row.get("units")
        return f"{nm} [{units}]" if units else nm

    df_long["display_name"] = df_long.apply(make_display_name, axis=1)

    # Sort for stable presentation
    df_long = df_long.sort_values(["segment", "plugin", "short_key"]).reset_index(drop=True)

    if orientation == "long":
        return df_long

    # Build wide layout
    df_wide = (
        df_long
        .pivot_table(index="segment", columns="display_name", values="value", aggfunc="first")
        .reset_index()
    )
    df_wide.columns.name = None
    cols = ["segment"] + [c for c in df_wide.columns if c != "segment"]
    df_wide = df_wide[cols]
    return df_wide

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

def segment_statistics(segmentationNode, masterVolumeNode=None, extra_keys=None):
    """
    Compute segment statistics with optional extra keys from the
    LabelmapSegmentStatisticsPlugin.

    Parameters
    ----------
    segmentationNode : vtkMRMLSegmentationNode
        Segmentation to analyze.
    masterVolumeNode : vtkMRMLScalarVolumeNode, optional
        Needed for intensity‑based metrics.
    extra_keys : list of str, optional
        Example: ["centroid_ras", "feret_diameter_mm", "surface_area_mm2", "roundness", 
              "flatness", "elongation","principal_moments"].

    Returns
    -------
    dict
        Nested dictionary with statistics for each segment.
    """

    import SegmentStatistics

    logic = SegmentStatistics.SegmentStatisticsLogic()
    paramNode = logic.getParameterNode()

    # Required segmentation parameter
    paramNode.SetParameter("Segmentation", segmentationNode.GetID())

    # Optional scalar volume parameter (if you want intensity statistics)
    if masterVolumeNode:
        paramNode.SetParameter("ScalarVolume", masterVolumeNode.GetID())

    # Extra statistic keys from LabelmapSegmentStatisticsPlugin
    if extra_keys:
        for key in extra_keys:
            paramNode.SetParameter(f"LabelmapSegmentStatisticsPlugin.{key}.enabled", "True")

    # Compute statistics
    logic.computeStatistics()
    stats = logic.getStatistics()

    return stats

      
def set_segments_color(segments_color, segmentationNode):
    '''
    
    '''
    
    segmentation = segmentationNode.GetSegmentation()
    
    for segmentName in segments_color:
        
        segmentID = segmentation.GetSegmentIdBySegmentName(segmentName)
        segment = segmentation.GetSegment(segmentID)
        
        color = segments_color[segmentName]
        segment.SetColor(color)
        

        
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
      
