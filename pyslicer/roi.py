import numpy as np
import slicer

def box_from_ROI(nodename = 'R'):
    '''
    Make a box model node from a ROI markup node

    Args:
        nodename (str): Name of the ROI markup node. Default "R"

    Returns:
        boxNode (MRMLCore.vtkMRMLModelNode()): pandas dataframe listing all points in (r,s,a) world coordinate system
    '''
    
    from trimesh.primitives import Box
    from pyvista import wrap

    roiNode = slicer.util.getNode(nodename)
    
    # Get ROI object bounds
    obj_bounds = objectBounds_from_markupROI(nodename = nodename)
    
    # Create a box centered in the origin (world coordinate system)
    box_primitive = Box(bounds=obj_bounds)
    box = wrap(box_primitive.to_mesh())
    boxNode = slicer.modules.models.logic().AddModel(box)   

    # Get the ROI transform and align the box to the ROI
    vtkmatrix = roiNode.GetObjectToWorldMatrix() 

    # Apply transformation to the box Model
    transformNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
    transformNode.SetMatrixTransformToParent(vtkmatrix);
    boxNode.SetAndObserveTransformNodeID(transformNode.GetID());
    
    return boxNode

def bounding_box_from_points(df_points):
    '''
    Make a box model node from point list

    Args:
        df_points (pandas.DataFrame): pandas dataframe listing all points in (r,s,a) coordinate system. Check ```pyslicer.points_from_markup()```

    Returns:
        boxNode (MRMLCore.vtkMRMLModelNode()): pandas dataframe listing all points in (r,s,a) coordinate system
    '''
    
    from trimesh.points import PointCloud
    from pyvista import wrap
    
    points_mesh = PointCloud(df_points.to_numpy())
    box_primitive = points_mesh.bounding_box_oriented
    
    box = wrap(box_primitive.to_mesh())
    
    boxNode = slicer.modules.models.logic().AddModel(box)
    
    return boxNode

def objectBounds_from_markupROI(nodename = 'R'):   
    '''
    Extract the bounds of the ROI Markup Node in a coordinate system centered in the ROI center and oriented as the ROI principal axes.

    Args:
        nodename (str): Name of the ROI markup node. Default "R"

    Returns:
        df_points (pandas.DataFrame): pandas dataframe listing the ROI boundary points in a (r,s,a) coordinate system centered in the ROI center and oriented as the ROI principal axes.
    '''

    from numpy import zeros
    from pandas import DataFrame

    roiNode = slicer.util.getNode(nodename)
    
    bounds = zeros(6)
    roiNode.GetObjectBounds(bounds)

    colnames = ['r', 'a', 's']
    df_points = DataFrame(data=bounds.reshape([3,2]).transpose(), columns=colnames)
        
    return df_points

def roi_bounding_segments(segmentationNode):
    '''
    Make ROI markup models with bounding boxes from each segment in a segmentation node.
    From slicer scripting repository [https://slicer.readthedocs.io/en/latest/developer_guide/script_repository.html#markups-roi]

    Args:
        segmentationNode (MRMLCore.vtkMRMLSegmentationNode()): input segmentation node 

    Returns:
        roi_list (list): list of vtkMRMLMarkupsROINode objects
    '''
    
    # Compute bounding boxes
    import SegmentStatistics
    
    segStatLogic = SegmentStatistics.SegmentStatisticsLogic()
    segStatLogic.getParameterNode().SetParameter("Segmentation", segmentationNode.GetID())
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.obb_origin_ras.enabled",str(True))
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.obb_diameter_mm.enabled",str(True))
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.obb_direction_ras_x.enabled",str(True))
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.obb_direction_ras_y.enabled",str(True))
    segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.obb_direction_ras_z.enabled",str(True))
    segStatLogic.computeStatistics()
    stats = segStatLogic.getStatistics()
    
    # Draw ROI for each oriented bounding box
    
    roi_list = []
    
    for segmentId in stats["SegmentIDs"]:
        # Get bounding box
        obb_origin_ras = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_origin_ras"])
        obb_diameter_mm = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_diameter_mm"])
        obb_direction_ras_x = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_direction_ras_x"])
        obb_direction_ras_y = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_direction_ras_y"])
        obb_direction_ras_z = np.array(stats[segmentId,"LabelmapSegmentStatisticsPlugin.obb_direction_ras_z"])
        # Create ROI
        segment = segmentationNode.GetSegmentation().GetSegment(segmentId)
        roi=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode")
        roi.SetName(segment.GetName() + " OBB")
        roi.GetDisplayNode().SetHandlesInteractive(False)  # do not let the user resize the box
        roi.SetSize(obb_diameter_mm)
        # Position and orient ROI using a transform
        obb_center_ras = obb_origin_ras+0.5*(obb_diameter_mm[0] * obb_direction_ras_x + obb_diameter_mm[1] * obb_direction_ras_y + obb_diameter_mm[2] * obb_direction_ras_z)
        boundingBoxToRasTransform = np.row_stack((np.column_stack((obb_direction_ras_x, obb_direction_ras_y, obb_direction_ras_z, obb_center_ras)), (0, 0, 0, 1)))
        boundingBoxToRasTransformMatrix = slicer.util.vtkMatrixFromArray(boundingBoxToRasTransform)
        roi.SetAndObserveObjectToNodeMatrix(boundingBoxToRasTransformMatrix)
        
        roi_list.append(roi)
    
    return roi_list

def roi_crop_volume(roi, inputVolume):
    '''
    From [SlicerDevelopmentToolbox](https://github.com/QIICR/SlicerDevelopmentToolbox/blob/master/SlicerDevelopmentToolboxUtils/mixins.py#L614-L623)
    As discussed in [the slicer forum](https://discourse.slicer.org/t/volume-cropping-from-scripted-module/11169)

    Args:
        roi (vtkMRMLMarkupsROINode): ROI markup node
        inputVolume (slicer.vtkMRMLVolumeNode): Volume node to crop

    Returns:
        croppedVolume (slicer.vtkMRMLVolumeNode): Volume node to cropped
    '''

    cropVolumeLogic = slicer.modules.cropvolume.logic()
    cropVolumeParameterNode = slicer.vtkMRMLCropVolumeParametersNode()
    cropVolumeParameterNode.SetROINodeID(roi.GetID())
    cropVolumeParameterNode.SetInputVolumeNodeID(inputVolume.GetID())
    cropVolumeParameterNode.SetVoxelBased(True)
    cropVolumeLogic.Apply(cropVolumeParameterNode)
    croppedVolume = slicer.mrmlScene.GetNodeByID(cropVolumeParameterNode.GetOutputVolumeNodeID())
    
    return croppedVolume