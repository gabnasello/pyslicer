import slicer
import vtk
import cv2
import numpy as np
import os

def create_rotation_video(output_video_path, rotation_degrees=360, steps=180, fps=30, resolution=(1280, 720)):
    """
    Creates a rotation video of a 3D model.

    Args:
        output_video_path (Path): The path where the output video will be saved.
        rotation_degrees (int, optional): The total rotation in degrees. Defaults to 360.
        steps (int, optional): The number of frames. Defaults to 180.
        fps (int, optional): The frames per second. Defaults to 30.
        resolution (tuple, optional): The width and height of the video. Defaults to (1280, 720).
    """

    # -------------------------
    # SETUP 3D VIEW
    # -------------------------
    layout_manager = slicer.app.layoutManager()
    three_d_widget = layout_manager.threeDWidget(0)
    three_d_view = three_d_widget.threeDView()
    render_window = three_d_view.renderWindow()

    camera = three_d_view.cameraNode().GetCamera()

    # Reset camera to nicely frame the model
    three_d_view.resetFocalPoint()
    three_d_view.resetCamera()
    slicer.app.processEvents()

    # -------------------------
    # VIDEO WRITER
    # -------------------------
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(
        output_video_path,
        fourcc,
        fps,
        resolution
    )

    # -------------------------
    # ROTATION + CAPTURE
    # -------------------------
    angle_step = rotation_degrees / steps

    for i in range(steps):
        camera.Azimuth(angle_step)
        render_window.Render()
        slicer.app.processEvents()

        # Capture image from render window
        wti = vtk.vtkWindowToImageFilter()
        wti.SetInput(render_window)
        wti.Update()

        vtk_image = wti.GetOutput()
        width, height, _ = vtk_image.GetDimensions()

        vtk_array = vtk_image.GetPointData().GetScalars()
        components = vtk_array.GetNumberOfComponents()
        image = np.frombuffer(vtk_array, dtype=np.uint8)
        image = image.reshape(height, width, components)

        # Convert RGB → BGR
        frame = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # FIX: flip vertically (VTK bottom-left → OpenCV top-left)
        frame = np.flipud(frame)

        # Resize and write
        frame = cv2.resize(frame, resolution)
        video_writer.write(frame)

    # -------------------------
    # CLEANUP
    # -------------------------
    video_writer.release()
    print("Video saved to:", output_video_path)

def default_dark_3D_view():
    set_windowsize(x=1980,y=1080)
    
    show_cube_labels(False)
    
    color = (28/255, 29/255, 36/255)
    set_background_color(color)

    # Set thick and white ruler
    # 2 - thick
    # 0 - white
    show_ruler(thickness=2, color=0)


def get_camera_3Dview(use_pandas=False, save_csv=False, csv_path="camera_view.csv"):
    import csv

    view = slicer.app.layoutManager().threeDWidget(0).threeDView()
    viewNode = view.mrmlViewNode()

    cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(viewNode)

    position = cameraNode.GetPosition()
    viewUp = cameraNode.GetViewUp()
    focalPoint = cameraNode.GetFocalPoint()
    viewAngle = cameraNode.GetViewAngle()
    parallelScale = cameraNode.GetParallelScale()

    data = [
        {
            "position": position[0],
            "viewUp": viewUp[0],
            "focalPoint": focalPoint[0],
            "viewAngle": viewAngle,
            "parallelScale": parallelScale,
        },
        {
            "position": position[1],
            "viewUp": viewUp[1],
            "focalPoint": focalPoint[1],
            "viewAngle": None,
            "parallelScale": None,
        },
        {
            "position": position[2],
            "viewUp": viewUp[2],
            "focalPoint": focalPoint[2],
            "viewAngle": None,
            "parallelScale": None,
        },
    ]

    # Save to CSV without pandas
    if save_csv:
        with open(csv_path, mode="w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["position", "viewUp", "focalPoint", "viewAngle", "parallelScale"],
            )
            writer.writeheader()
            writer.writerows(data)

    if use_pandas:
        try:
            import pandas as pd
            df = pd.DataFrame(data)
            df.index = [1, 2, 3]
            return df
        except ImportError:
            pass

    return data

def reset_camera_to_fit_all_visible_models():
    """
    Reset camera to fit all visible models in the 3D view.
    """
    threeDView = slicer.app.layoutManager().threeDWidget(0).threeDView()
    threeDView.resetCamera()

    renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()

    bounds = renderer.ComputeVisiblePropBounds()
    dx = bounds[1] - bounds[0]
    dy = bounds[3] - bounds[2]

    camera = threeDView.cameraNode()
    camera.SetParallelScale(max(dx, dy))

    threeDView.forceRender()

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