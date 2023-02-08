from pathlib import Path
import slicer

def load_zstack(zstack_file, channel, color='grey'):
    '''
    Load .czi z-stack images in Slicer. 
    Note that 3D Slicer takes individual channels as volume nodes

    Args:
        zstack_file (str): File path of the z-stack file
        channel (str): Channel name in z-stack 
        color (str): Display color of the Volume Node. Current colors are ('grey','yellow','red','green','blue'). Default is grey.

    Returns:
        masterVolumeNode (slicer.vtkMRMLScalarVolumeNode): Volume Node with of the loaded channel
    '''

    from aicsimageio import AICSImage
    from pandas import DataFrame

    clrs = ('grey','yellow','red','green','blue')

    # Get the AICSImage object
    img = AICSImage(zstack_file)  # selects the first scene found

    ## Print pixel sizes
    x_res = img.physical_pixel_sizes.X  # returns the X dimension pixel size as found in the metadata
    y_res = img.physical_pixel_sizes.Y  # returns the X dimension pixel size as found in the metadata
    z_res = img.physical_pixel_sizes.Z  # returns the Z dimension pixel size as found in the metadata
    size = [x_res, y_res, z_res]

    # The lines below used to work but now they raise the error 
    # "cannot get a schema for XML data, provide a schema argument"
    # Check The default XML parser will be changing from 'xmlschema' to 'lxml' in version 0.4.0.  
    # To silence this warning, please provide the `parser` argument, specifying either 'lxml' 
    # (to opt into the new behavior), or'xmlschema' (to retain the old behavior).

    # metadata_dict = img.ome_metadata.dict()['images'][0]['pixels']
    # x_unit = metadata_dict['physical_size_x_unit'].value
    # y_unit = metadata_dict['physical_size_y_unit'].value
    # z_unit = metadata_dict['physical_size_z_unit'].value
    # unit = [x_unit, y_unit, z_unit]

    unit = ['µm', 'µm', 'µm']

    data = {
    "pixel_size": size,
    "unit": unit
    }

    rownames = ['x', 'y', 'z']
    pixel_df = DataFrame(data, index = rownames)

    pixel_df_mm = pixel_df.copy()
    pixel_df_mm.pixel_size = pixel_df.pixel_size/1000
    pixel_df_mm.unit = ['mm', 'mm', 'mm'] 

    print('\n--- Image Dimensions')
    print(img.dims)  # returns a Dimensions object

    print('\n--- Image Channel Names')
    print(img.channel_names)  # returns a list of string channel names found in the metadata

    print('\n--- Image Pixel Physical Size Table')
    print(pixel_df_mm)


    ## Get image data as numpy array

    imgdata = img.get_image_data("CZYX", T=0)  # returns 4D CZYX numpy array
    # imgdata.shape
    channel_data = imgdata[img.channel_names.index(channel),:]

    # Load image as Volume Node

    # Create a master volume node with geometry based on the input images
    # Instantiate and add a VolumeNode to the scene.
    # To create a volume from a numpy array, you need to initialize a ```vtkMRMLScalarVolumeNode``` [link](https://discourse.slicer.org/t/creating-volume-from-numpy/658/4)

    masterVolumeNode = slicer.vtkMRMLScalarVolumeNode()
    masterVolumeNode.SetSpacing(pixel_df_mm.pixel_size.to_list())

    # Importing images in czi file extension [link](https://discourse.slicer.org/t/importing-images-in-czi-file-extension/12291/1)
    slicer.util.updateVolumeFromArray(masterVolumeNode, channel_data)
    masterVolumeNode = slicer.mrmlScene.AddNode(masterVolumeNode)

    slicer.util.setSliceViewerLayers(background=masterVolumeNode, fit=True)
    masterVolumeNode.CreateDefaultDisplayNodes()

    if color in clrs:
        lookup_table = 'vtkMRMLColorTableNode' + color.capitalize()
        displayNode = masterVolumeNode.GetDisplayNode()
        displayNode.SetAndObserveColorNodeID(lookup_table)

    return masterVolumeNode

def load_model(model_file, name = None, color=None):
    '''
    Load model file (e.g. .vtk, .stl) in Slicer. 

    Args:
        model_file (str): File path of the model to load
        color (tuple): Display color of the Model Node. Insert the 3 RGB values in scale 0-1.

    Returns:
        modelNode (MRMLCore.vtkMRMLModelNode): model node 
    '''

    clrs = ('grey','yellow','red','green','blue')

    modelNode = slicer.util.loadModel(model_file)
    
    if name != None:
        modelNode.SetName(name)

    if color:
        displayNode = modelNode.GetDisplayNode()
        displayNode.SetColor(color)

    return modelNode