import slicer

def default_dark_3D_view():
    set_windowsize(x=1980,y=1080)
    
    show_cube_labels(False)
    
    color = (28/255, 29/255, 36/255)
    set_background_color(color)

    # Set thick and white ruler
    # 2 - thick
    # 0 - white
    show_ruler(thickness=2, color=0)

def screenshot_3Dview(outputfile):
    import ScreenCapture
    cap = ScreenCapture.ScreenCaptureLogic()
    view = slicer.app.layoutManager().threeDWidget(0).threeDView()
    cap.captureImageFromView(view, outputfile)


def set_background_color(color):
    view = slicer.app.layoutManager().threeDWidget(0).threeDView()
    viewNode = view.mrmlViewNode()
    
    # Set view background to RGB color of choice
    viewNode.SetBackgroundColor(color[0], color[1], color[2])
    viewNode.SetBackgroundColor2(color[0], color[1], color[2])

def set_camera_3Dview(position=[], 
                      viewAngle=0, 
                      viewUp=[], 
                      focalPoint=[], 
                      parallelScale=0,
                      resetFocalPoint=True
                     ):
    view = slicer.app.layoutManager().threeDWidget(0).threeDView()
    viewNode = view.mrmlViewNode()
    
    # Get camera position
    cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(viewNode)

    if any(position):
        cameraNode.SetPosition(position)
    if viewAngle!=0:
        cameraNode.SetViewAngle(viewAngle)
    if any(viewUp):
        cameraNode.SetViewUp(viewUp)
    if any(focalPoint):
        cameraNode.SetFocalPoint(focalPoint)
    if parallelScale!=0:
        cameraNode.SetParallelScale(parallelScale)

    if resetFocalPoint:
        layoutManager = slicer.app.layoutManager()
        threeDWidget = layoutManager.threeDWidget(0)
        threeDView = threeDWidget.threeDView()
        threeDView.resetFocalPoint()#just resets the focal point, camera might be tilted off still
    
#adjust window size and fill slice to space
def set_windowsize(x=1980,y=1080):
    """Set window size viewer, to set size of screenshot. Can drag and re-maximize windows to reset window size
    Example usage:
    set_windowsize(1500,1500)
    """
    from qt import QSize
    slicer.util.mainWindow().size=QSize(x,y)

def show_cube_labels(show=False):
    view = slicer.app.layoutManager().threeDWidget(0).threeDView()
    viewNode = view.mrmlViewNode()
    
    # Switch off cube and labels
    viewNode.SetAxisLabelsVisible(show)
    viewNode.SetBoxVisible(show)

def show_ruler(thickness=2, color=0):

    view = slicer.app.layoutManager().threeDWidget(0).threeDView()
    viewNode = view.mrmlViewNode()
    
    # Set Orthographic rendering, which is required to show the ruler in a 3D view
    viewNode.SetRenderMode(viewNode.Orthographic)
    
    # Set thick and white ruler
    viewNode.SetRulerType(thickness) # 2 - thick
    viewNode.SetRulerColor(color) # 0 - white