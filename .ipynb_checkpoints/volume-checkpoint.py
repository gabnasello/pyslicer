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