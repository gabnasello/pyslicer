from pathlib import Path
import slicer

def imagestacks(first_image_file, spacing=False, quality='preview', volumeName='Volume'):
    '''
    Load stack of image files as a 3D volume into 3D Slicer.

    Note that the [SlicerMoprh](https://github.com/SlicerMorph/SlicerMorph#installation) extension is required! 

    Args:
        first_image_file (str): File path of the first image file of the stack
        spacing (list): [x_res, y_res, z_res] Image spacing in mm along the 3 dimensions. By default, the information is automatically retrieved from the image metadata.
        quality (str): Quality resolution of the output volume ['preview', 'half', 'full']. Default is 'preview'.

    Returns:
        masterVolumeNode (slicer.vtkMRMLScalarVolumeNode): Volume Node with of the loaded image stack.
    '''
    
    ## Set 'ImageStacks' as currently active module
    
    slicer.util.selectModule('ImageStacks')
    # Python scripted modules
    moduleWidget = slicer.modules.imagestacks.widgetRepresentation().self()
    
    ## load image stack
    
    # User selects a file like "/opt/data/image-0001.tif"
    moduleWidget.archetypeText.text = first_image_file
    
    # The populateFromArchetype method will populate the file list with all files 
    # that match the numbering pattern in that directory
    moduleWidget.populateFromArchetype()
    
    if spacing != False:
        moduleWidget.spacingWidget.coordinates = f"{spacing[0]},{spacing[1]},{spacing[2]}"
        
    # Modifying only the ```logic``` of the ImageStack module does not change the Quality Button at the User Interface (UI). 
    # However, the new quality is set, as indicated by the output spacing in the UI.
    if quality != 'preview':
        moduleWidget.logic.outputQuality = quality
        moduleWidget.updateWidgetFromLogic()
    
    ## Instantiate and add a VolumeNode to the scene.
    masterVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", volumeName)
    
    # Load the files in paths to outputNode.
    moduleWidget.logic.loadVolume(outputNode = masterVolumeNode)

    return masterVolumeNode


def model(model_file, name = None, color=None):
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

def zstack(zstack_file, spacing=None, channel='Channel:0:0', color='grey'):
    '''
    Load .czi z-stack images in Slicer. 
    Note that 3D Slicer takes individual channels as volume nodes

    Args:
        zstack_file (str): File path of the z-stack file
        spacing (list): [x_res, y_res, z_res] Image spacing in µm along the 3 dimensions. By default, the information is automatically retrieved from the image metadata.
        channel (str): Channel name in z-stack. Default is AICSImage output for images with only one channel ['Channel:0:0'].
        color (str): Display color of the Volume Node. Current colors are ('grey','yellow','red','green','blue'). Default is grey.

    Returns:
        masterVolumeNode (slicer.vtkMRMLScalarVolumeNode): Volume Node with of the loaded channel
    '''

    from aicsimageio import AICSImage
    from pandas import DataFrame

    clrs = ('grey','yellow','red','green','blue')

    # Get the AICSImage object
    img = AICSImage(zstack_file)  # selects the first scene found
    
    if spacing == None:
        ## Print pixel sizes
        x_res = img.physical_pixel_sizes.X  # returns the X dimension pixel size as found in the metadata
        y_res = img.physical_pixel_sizes.Y  # returns the X dimension pixel size as found in the metadata
        z_res = img.physical_pixel_sizes.Z  # returns the Z dimension pixel size as found in the metadata
        spacing = [x_res, y_res, z_res]

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
    "pixel_size": spacing,
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

