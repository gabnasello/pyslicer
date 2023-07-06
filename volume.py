import slicer

def set_window_level(window, level, volumeNode):
    '''
    Apply the Window and Level properties programmatically anytime you run again the same image.
    
    The funcitons gets the displayNode associate to the volumeNode. 

    For more information on the relationship between window/level and brightness/contrast, see [Window and Level Contrast Enhancement](http://fisica.ciens.ucv.ve/curs/dipcourse/html/one-oper/window-level/front-page.html)
    '''

    displayNode = volumeNode.GetDisplayNode()
    displayNode.AutoWindowLevelOff()
    displayNode.SetWindow(window)
    displayNode.SetLevel(level)
    
def plot_histogram(volumeNode, threshold=None, xlabel='Voxel Intensity', ylabel='Counts', ylog=None, xlog=None, bins=50, title=None):
    '''
    Plotting voxel histogram using matplotlib.
    
    Script take from [SlicerNotebook tutorial](https://github.com/Slicer/SlicerNotebooks/blob/master/01_Data_loading_and_display.ipynb). 
    
    Args:
        volumeNode (slicer.vtkMRMLVolumeNode): Volume Node to plot
        thresholds (list): list of thresholding values to display as vertical lines. Default None.
        xlabel (str): x-axis label of matplotlib plot. Default 'Voxel Intensity'.
        ylabel (str): y-axis label of matplotlib plot. Default 'Counts'.
        yscale (str): Set the yaxis' scale {"linear", "log", "symlog", "logit", ...}.
        xscale (str): Set the xaxis' scale {"linear", "log", "symlog", "logit", ...}.
        bins (int): it defines the number of equal-width bins in the given range (10, by default)
        title (str): title of matplotlib plot. Default None.
    '''
    import JupyterNotebooksLib as slicernb
    import numpy as np
    import matplotlib.pyplot as plt
    
    # Extract all voxels of the volume as numpy array
    volumeArray = slicer.util.arrayFromVolume(volumeNode)
    
    try:
      import matplotlib
    except ModuleNotFoundError:
      slicer.util.pip_install('matplotlib')
      import matplotlib

    matplotlib.use('Agg')

    # Get a volume from SampleData and compute its histogram
    histogram = np.histogram(volumeArray, bins=50)

    # Show a plot using matplotlib
    fig, ax = plt.subplots()
    ax.plot(histogram[1][1:], histogram[0].astype(float))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if title:
        plt.title(title)
     
    if yscale:
        plt.yscale(yscale)
    
    if xscale:
        plt.xscale(xscale)
       
    if threshold != None:
        for thresh in threshold:
            ax.axvline(thresh, color='r')
    
    return slicernb.MatplotlibDisplay(plt)