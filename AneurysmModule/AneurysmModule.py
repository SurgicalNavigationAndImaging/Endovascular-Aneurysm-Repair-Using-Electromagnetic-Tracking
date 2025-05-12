# Necessary imports:
import logging
import os
import vtk
import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import numpy as np
import time
from pathlib import Path
import qt

#
# AneurysmModule
#
class AneurysmModule(ScriptedLoadableModule):
 
  def __init__(self, parent):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "AneurysmModule" 
    self.parent.categories = ["MyIGTModules"]
    self.parent.dependencies = []
    self.parent.contributors = ["Celia de la Fuente (Universidad Carlos III de Madrid), Ana González (Universidad Carlos III de Madrid), Duarte Moura (Universidad Carlos III de Madrid), Paula Ochotorena (Universidad Carlos III de Madrid), Sandra Eizaguerri (Universidad Carlos III de Madrid)"] 
    self.parent.helpText = """Electromagnetic tracking for Aortic Abdominal Aneurysm Surgery"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """Department of Bioengineering, Universidad Carlos III""" 

#
# AneurysmModuleWidget
#

class AneurysmModuleWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self.connect = True
        #self._parameterNode = None
        #self._updatingGUIFromParameterNode = False

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/AneurysmModule.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = AneurysmModuleLogic()
        

        # Connections

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).
        self.ui.loadDataButton.connect('clicked(bool)', self.onLoadDataButtonClicked)
        self.ui.connectToPlusButton.connect('clicked(bool)', self.onConnectToPlusButtonClicked)
        self.ui.buildTransformTreeButton.connect('clicked(bool)', self.onBuildTransformTreeButtonClicked)
        self.ui.addPointButton.connect('clicked(bool)', self.onAddPointButtonClicked)
        self.ui.RemovePointButton.connect('clicked(bool)', self.onRemovePointButtonClicked)
        self.ui.computeRegistrationButton.connect('clicked(bool)', self.onComputeRegistrationButtonClicked )
        self.ui.resetRegistrationButton.connect('clicked(bool)', self.onResetRegistrationButtonClicked)
        self.ui.aortaOpacitySlider.connect('valueChanged(double)', self.onAneurysmOpacityValueSliderWidgetChanged)
        self.ui.showOptimalPathButton.connect('clicked(bool)', self.onShow_optimal_pathClicked)
        self.ui.recordTrackingButton.connect('clicked(bool)', self.onRecordTrackingButtonClicked)
        self.ui.toggleDistanceButton.connect('clicked(bool)', self.onToggleDistanceClicked)
        self.ui.monitorDeviationButton.connect('clicked(bool)', self.onMonitorDeviationClicked)
        self.recording = False
    

    #
    # UI functions
    #

    def onLoadDataButtonClicked(self):
        
        # Load data
        
        print("Loading data")
        self.logic.loadData()
        

    def onConnectToPlusButtonClicked(self):
    
        # Update button state
        self.ui.connectToPlusButton.enabled = False

        # Update connection 
        if self.connect:
            hostname = 'localhost'
            port_tracker = 18944
            status = self.logic.startPlusConnection(hostname, port_tracker) # Start connection
            if status == 1:
                self.connect = False
                self.ui.connectToPlusButton.setText('Disconnect from Plus')
            else:
                self.logic.stopPlusConnection() # Stop connection
                self.connect = True
                self.ui.connectToPlusButton.setText('Connect to Plus')
        else:
            self.logic.stopPlusConnection() # Stop connection
            self.connect = True
            self.ui.connectToPlusButton.setText('Connect to Plus')       

        # Update button state
        self.ui.connectToPlusButton.enabled = True

    def onBuildTransformTreeButtonClicked(self):
        
        # Build transformation tree
        self.logic.buildTransformTree()
        pass
        
    def onAddPointButtonClicked(self):
        
        # Add point
        self.logic.addPoint()
        pass
        
    def onRemovePointButtonClicked(self):
        
        # Remove point
        self.logic.removePoint()
        pass
        
    def onComputeRegistrationButtonClicked(self):
        
        # Compute registration
        self.logic.computeRegistration()
        pass
        
    def onResetRegistrationButtonClicked(self):
        
        # Reset registration
        self.logic.resetRegistration()
        pass
        
    def onAneurysmOpacityValueSliderWidgetChanged(self, opacityValue):

        # Get opacity value
        opacityValue_norm = opacityValue/100.0
        
        # Update model opacity
        self.logic.updateAAAModelOpacity(opacityValue_norm)
        pass
    
    def onShow_optimal_pathClicked(self):

        # Show the optimal path for the catheter

        self.ui.showOptimalPathButton.enabled = False 

        if not hasattr(self, 'optimalPathVisible'):
            self.optimalPathVisible = False

        if not self.optimalPathVisible:
            self.logic.show_optimal_path()
            self.ui.showOptimalPathButton.setText('Hide optimal path')
            self.optimalPathVisible = True
        else:
            self.logic.hide_optimal_path()
            self.ui.showOptimalPathButton.setText('Show optimal path')
            self.optimalPathVisible = False

        self.ui.showOptimalPathButton.enabled = True  
        pass
    
    def onRecordTrackingButtonClicked(self):

        # Record the path performed by the catheter

        if self.ui.recordTrackingButton.text == "Record Tracking Path":
            self.ui.recordTrackingButton.setText("Stop Recording Path")
            self.recording = True
            self.logic.startTrackingRecording()
        else:
            self.ui.recordTrackingButton.setText("Record Tracking Path")
            self.recording = False
            self.logic.stopTrackingRecording()
    
    def onToggleDistanceClicked(self):

        # Show the distance from the catheter to the middle plane of the aneurysm

        if not hasattr(self.logic, 'distance_text_actor') or self.logic.distance_text_actor is None:
            self.logic.setup_3d_text_display()

        actor = self.logic.distance_text_actor
        isVisible = actor.GetVisibility()

        # Toggle visibility
        actor.SetVisibility(not isVisible)

        # Update button text
        if isVisible:
            self.ui.toggleDistanceButton.setText("Show Distance from Aneurysm")
        else:
            self.ui.toggleDistanceButton.setText("Hide Distance from Aneurysm")

        slicer.app.layoutManager().threeDWidget(0).threeDView().renderWindow().Render()


    def onMonitorDeviationClicked(self):

        # Monitor the deviation comparing the optimal and the tracking path

        if self.ui.monitorDeviationButton.text == "Compare Optimal and Tracking Path":
            self.ui.monitorDeviationButton.setText("Stop Comparing Paths")
            self.logic.startDeviationMonitoring()
        else:
            self.ui.monitorDeviationButton.setText("Compare Optimal and Tracking Path")
            self.logic.stopDeviationMonitoring()


    
#
# AneurysmModuleLogic
#

class AneurysmModuleLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)
        module_path = slicer.util.modulePath("AneurysmModule")
        self.data_path = module_path.replace("AneurysmModule.py", "") + 'Resources/Data'
        #self.data_path = slicer.modules.AneurysmModule.path.replace("AneurysmModule.py","") + 'Resources/Data'
        
        # Initialize monitoring variables
        self.is_monitoring = True
        self.monitoring_interval = 100  # default interval in milliseconds
        self.timer = None
        
        # Initialize 3D text display
        self.distance_text_actor = None
        #self.setup_3d_text_display()

        self.recording = False
        self.recordedPoints = []
        self.trajectoryCurveNode = None
    

    def process(self, inputVolume, outputVolume, imageThreshold, invert=False, showResult=True):
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputVolume: volume to be thresholded
        :param outputVolume: thresholding result
        :param imageThreshold: values above/below this threshold will be set to 0
        :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
        :param showResult: show output volume in slice viewers
        """

        if not inputVolume or not outputVolume:
            raise ValueError("Input or output volume is invalid")

        import time
        startTime = time.time()
        logging.info('Processing started')

        # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
        cliParams = {
            'InputVolume': inputVolume.GetID(),
            'OutputVolume': outputVolume.GetID(),
            'ThresholdValue': imageThreshold,
            'ThresholdType': 'Above' if invert else 'Below'
        }
        cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
        # We don't need the CLI module node anymore, remove it to not clutter the scene with it
        slicer.mrmlScene.RemoveNode(cliNode)

        stopTime = time.time()
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')

    def startPlusConnection(self, hostname, port_tracker):
        """
        Starts PLUS connection with electromagnetic tracker through selected port.
        """    
        # Open connection
        try:
            cnode = slicer.util.getNode('IGTLConnector_Tracker')
        except:
            cnode = slicer.vtkMRMLIGTLConnectorNode()
            slicer.mrmlScene.AddNode(cnode)
            cnode.SetName('IGTLConnector_Tracker')
        status = cnode.SetTypeClient(hostname, port_tracker)
        
        # Check connection status
        if status == 1:
            cnode.Start()
            logging.debug('Connection Successful')
        
        else:
            print ('ERROR: Unable to connect to PLUS')
            logging.debug('ERROR: Unable to connect to PLUS')

        return status

    def stopPlusConnection(self):
        """
        Stops PLUS connection with electromagnetic tracker.
        """    
        cnode = slicer.util.getNode('IGTLConnector_Tracker')
        cnode.Stop()

    def loadModelFromFile(self, modelFilePath, modelFileName, colorRGB_array, visibility_bool):
        try:
            node = slicer.util.getNode(modelFileName)
        except:
            node = slicer.util.loadModel(modelFilePath + '/' + modelFileName)
            node.GetModelDisplayNode().SetColor(colorRGB_array)
            node.GetModelDisplayNode().SetVisibility(visibility_bool)
            print (modelFileName + ' model loaded')

        return node

    def loadTransformFromFile(self, transformFilePath, transformFileName):
        try:
            node = slicer.util.getNode(transformFileName)
        except:
            node = slicer.util.loadTransform(transformFilePath +  '/' + transformFileName)
            if node == None:
                node=slicer.vtkMRMLLinearTransformNode()
                node.SetName(transformFileName)
                slicer.mrmlScene.AddNode(node)
                print ('ERROR: ' + transformFileName + ' transform not found in path. Creating node as identity...')
            
        return node

    def getOrCreateTransform(self, transformName):
        try:
            node = slicer.util.getNode(transformName)
        except:
            node=slicer.vtkMRMLLinearTransformNode()
            node.SetName(transformName)
            slicer.mrmlScene.AddNode(node)
            print ('ERROR: ' + transformName + ' transform was not found. Creating node as identity...')
        return node

    def loadFiducialsFromFile(self, fiducialsFilePath, fiducialsFileName, colorRGB_array, visibility_bool):
        """
        Load point set (fiducials) from FCSV file.
        """
        node = slicer.util.loadMarkups(fiducialsFilePath + '/' + fiducialsFileName)
        node.GetDisplayNode().SetColor(colorRGB_array)
        node.GetDisplayNode().SetVisibility(visibility_bool)
        node.LockedOn()
        print (fiducialsFileName + ' loaded')
        return node

    def getOrCreateFiducials(self, fiducialsName, colorRGB_array, visibility_bool):

        try:
            node = slicer.util.getNode(fiducialsName)
        except:
            node = slicer.vtkMRMLMarkupsFiducialNode()  
            node.SetName(fiducialsName)
            slicer.mrmlScene.AddNode(node)
            node.GetDisplayNode().SetSelectedColor(colorRGB_array)
            node.GetDisplayNode().SetVisibility(visibility_bool)
            node.LockedOn()
        return node

    def loadData(self):
        """
        Loads data for navigation.
        """
        print ('Loading Data...')

        # Load Models
        self.EM_tip_model = self.loadModelFromFile(self.data_path , 'EM_tip_model.stl' , [0.8, 0.8, 0.8], True)
        self.AAA_model = self.loadModelFromFile(self.data_path , 'AAA_model_position.stl' ,  [1, 0, 0], True)
        self.needle = self.loadModelFromFile(self.data_path , 'NeedleModel.stl' ,  [0.0, 0.0, 1.0], True)
        
        # Start position monitoring with default target fiducial (index 0)
        self.start_position_monitoring(plane_point = [-21.479, 196.977, 129.566], plane_normal = [-0.9284843614811378, -0.27504156840102965, -0.24953742431019876])

        # Load PointerTipToPointer transform
        self.PointerTipToPointer = self.loadTransformFromFile(self.data_path, 'PointerTipToPointer.h5')

        # Create referenceToRas transform
        self.ReferenceToRas = self.getOrCreateTransform('ReferenceToRas')

        # Load registration virtual fiducials
        self.registration_Virtual_Fiducials = self.loadFiducialsFromFile(self.data_path, 'RASpoints.fcsv', [0.00,1.00,0.00], True)

        # Load registration real fiducials
        self.registration_Real_Fiducials = self.loadFiducialsFromFile(self.data_path, 'registration_Real_Fiducials.mrk.json', [0.00,1.00,0.00], True) 

    def onTransformModified(self, caller, event):
        """
        Callback function that gets called whenever the transform is modified
        """
        self.get_tool_tip_position()

    def buildTransformTree(self):
        """
        Builds transform tree for navigation.
        """
        print ('Building transform tree...')

        # Get transforms if received from PLUS toolkit
        self.CatheterToReference = self.getOrCreateTransform('CatheterToReference')
        self.PointerToReference = self.getOrCreateTransform('PointerToReference')
        self.PointerTipToPointer = self.getOrCreateTransform('PointerTipToPointer')
        self.ReferenceToRas = self.getOrCreateTransform('ReferenceToRas')

        # Build transform tree
        self.needle.SetAndObserveTransformNodeID(self.PointerTipToPointer.GetID())
        self.EM_tip_model.SetAndObserveTransformNodeID(self.CatheterToReference.GetID())
        self.PointerTipToPointer.SetAndObserveTransformNodeID(self.PointerToReference.GetID())
        self.PointerToReference.SetAndObserveTransformNodeID(self.ReferenceToRas.GetID())
        self.CatheterToReference.SetAndObserveTransformNodeID(self.ReferenceToRas.GetID())
   

    def addPoint(self):
        """
        Adds new point for registration.
        """
        # Get stylus tip position
        m = vtk.vtkMatrix4x4()
        self.PointerTipToPointer.GetMatrixTransformToWorld(m)
        fiducial = [m.GetElement(0,3),m.GetElement(1,3),m.GetElement(2,3)]

        # Add fiducial to list
        self.registration_Real_Fiducials.AddControlPoint(fiducial)
        
        # Update fiducials display
        numFiducials = self.registration_Real_Fiducials.GetNumberOfControlPoints()
        print ('Number of fiducials: ', numFiducials)


    def removePoint(self):
        """
        Removes last recorded point.
        """
        # Get number of fiducials
        lastFiducials = self.registration_Real_Fiducials.GetNumberOfControlPoints() 

        # Delete last fiducial of the list
        self.registration_Real_Fiducials.RemoveNthControlPoint(lastFiducials-1) 

        # Update fiducials display
        numFiducials = self.registration_Real_Fiducials.GetNumberOfControlPoints()
        print ('Number of fiducials: ', numFiducials)
        pass

    def calculateRegistrationAndRMSError(self, fixedFiducials, movingFiducials, registrationResultTransform):
        """
        Computes registration between a moving and a fixed point set, and calculates the root mean squared error of the registration.
        """
        # Define parameters for registration
        parameters = {}
        parameters["fixedLandmarks"] = fixedFiducials.GetID()
        parameters["movingLandmarks"] = movingFiducials.GetID()
        parameters["saveTransform"] = registrationResultTransform.GetID()
        parameters["rms"] = 0.0
        parameters["transformType"] = "Rigid"

        # Perform registration
        node  = slicer.cli.createNode(slicer.modules.fiducialregistration)
        fidReg = slicer.modules.fiducialregistration
        slicer.cli.run(fidReg, node, parameters, True)
        
        # Output
        outputMessage = node.GetParameterAsString('outputMessage')
        errorRMS = node.GetParameterAsString('rms')

        return (errorRMS, outputMessage)

    def computeRegistration(self):

        # Compute registration 
        errorRMS, outputMessage = self.calculateRegistrationAndRMSError(self.registration_Virtual_Fiducials,self.registration_Real_Fiducials,self.ReferenceToRas)
        
        print ('RMS error: ' + errorRMS)
        print ('Output message: ' + outputMessage)
        
    def resetRegistration(self):

        # Delete fiducials
        self.registration_Real_Fiducials.RemoveAllControlPoints()

        # Update display
        numFiducials = self.registration_Real_Fiducials.GetNumberOfControlPoints()
        print ('Number of fiducials: ', numFiducials)

        # Set transform ReferenceToRas to identity
        identityTransform = vtk.vtkMatrix4x4()
        self.ReferenceToRas.SetMatrixTransformToParent(identityTransform)

    def updateAAAModelOpacity(self, opacityValue_norm):

        self.AAA_model.GetDisplayNode().SetOpacity(opacityValue_norm)
        pass
    
    def get_fiducial_position(self, fiducial_index):
        """
        Get the position of a specific fiducial.
        fiducial_index: index of the fiducial to get (0-based)
        """
        if self.registration_Virtual_Fiducials.GetNumberOfControlPoints() > fiducial_index:
            position = np.zeros(3)
            self.registration_Virtual_Fiducials.GetNthControlPointPosition(fiducial_index, position)
            print(f"Fiducial {fiducial_index} position: {position}")
            return position
        else:
            print(f"Fiducial {fiducial_index} not found")
            return None

    def get_tool_tip_position(self):
        matrix = vtk.vtkMatrix4x4()
        # Get the transform matrix
        self.CatheterToReference.GetMatrixTransformToWorld(matrix)
        # Get position from matrix (coordenadas del em tip) - luego esto hay que cambiar por el stilus 
        tip_position = np.array([matrix.GetElement(0,3), matrix.GetElement(1,3), matrix.GetElement(2,3)])
        
        # Get the first fiducial position (assuming it's the target)
        if self.registration_Virtual_Fiducials.GetNumberOfControlPoints() > 0:
            target_position = np.zeros(3)
            self.registration_Virtual_Fiducials.GetNthControlPointPosition(0, target_position)
            
            # Calculate distance
            distance = np.linalg.norm(target_position - tip_position)
            print(f"Distance to target: {distance:.2f} mm")
        else:
            print("No target fiducial found")
        
        return tip_position
    
    def setup_3d_text_display(self):
        self.distance_text_actor = vtk.vtkTextActor()
        self.distance_text_actor.GetTextProperty().SetFontSize(24)
        self.distance_text_actor.GetTextProperty().SetBold(True)
        self.distance_text_actor.GetTextProperty().SetColor(1.0, 1.0, 1.0)
        self.distance_text_actor.SetInput("Distance to target: -- mm")

        self.distance_text_actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        self.distance_text_actor.SetPosition(0.02, 0.02)

        renderer = slicer.app.layoutManager().threeDWidget(0).threeDView().renderWindow().GetRenderers().GetFirstRenderer()
        renderer.AddActor2D(self.distance_text_actor)

        self.distance_text_actor.SetVisibility(0)  # Start hidden

    def update_3d_text_display(self, distance):
        """
        Update the 3D text display with new distance and color
        """
        if self.distance_text_actor is None:
            return

        # Update text
        self.distance_text_actor.SetInput(f"Distance to target: {distance:.2f} mm")
        
        # Update color based on distance
        if distance < 5.0:  # very close - green
            self.distance_text_actor.GetTextProperty().SetColor(0.0, 1.0, 0.0)
            self.EM_tip_model.GetDisplayNode().SetColor(0.0, 1.0, 0.0)  
        elif distance < 40.0:  # getting closer - yellow
            self.distance_text_actor.GetTextProperty().SetColor(1.0, 1.0, 0.0)
            self.EM_tip_model.GetDisplayNode().SetColor(1.0, 1.0, 0.0)  
        else:  # far away - red
            self.distance_text_actor.GetTextProperty().SetColor(0.99, 0.99, 0.99)
            self.EM_tip_model.GetDisplayNode().SetColor(0.99, 0.99, 0.99)  
        
        # Force render update
        threeDWidget = slicer.app.layoutManager().threeDWidget(0)
        threeDView = threeDWidget.threeDView()
        threeDView.renderWindow().Render()

    def get_distance_to_plane(self, plane_point, plane_normal):
        """
        Calculate signed distance between EM tip and a plane defined by a point and a normal.
        plane_point: a point on the plane (3-element array)
        plane_normal: the normal vector of the plane (3-element array)
        """
        # Get tip position from EM tip transform
        matrix = vtk.vtkMatrix4x4()
        self.CatheterToReference.GetMatrixTransformToWorld(matrix)
        tip_position = np.array([
            matrix.GetElement(0, 3),
            matrix.GetElement(1, 3),
            matrix.GetElement(2, 3)
        ])

        # Normalize the normal vector just in case
        n = np.array(plane_normal)
        n = n / np.linalg.norm(n)

        # Vector from plane point to tip
        vec = tip_position - np.array(plane_point)

        # Signed distance
        distance = np.dot(vec, n)

        # Update 3D display
        self.update_3d_text_display(abs(distance))  

        return distance

    def start_position_monitoring(self, plane_point, plane_normal):
        """
        Start monitoring the distance to a defined plane.
        """
        if self.timer is None:
            self.timer = qt.QTimer()
            self.timer.timeout.connect(lambda: self.get_distance_to_plane(plane_point, plane_normal))
            self.timer.start(self.monitoring_interval)

            if self.distance_text_actor:
                self.distance_text_actor.SetInput("Monitoring distance to plane...")
    
   
   
    ## Function used for debugging:
    def list_all_fiducials(self):
        """
        Print information about all available fiducials.
        """
        num_fiducials = self.registration_Virtual_Fiducials.GetNumberOfControlPoints()
        print(f"\nTotal number of fiducials: {num_fiducials}")
        
        for i in range(num_fiducials):
            position = np.zeros(3)
            self.registration_Virtual_Fiducials.GetNthControlPointPosition(i, position)
            label = self.registration_Virtual_Fiducials.GetNthControlPointLabel(i)
            print(f"\nFiducial {i}:")
            print(f"  Label: {label}")
            print(f"  Position: {position}")  
    
    def show_optimal_path(self):
        if not hasattr(self, 'Centerline_model') or self.Centerline_model is None:
            self.Centerline_model = self.loadFiducialsFromFile(
                self.data_path, 'optimal_path_.mrk.json', [0.0, 1.0, 0.0], True)
        else:
            self.Centerline_model.SetDisplayVisibility(1)

    def hide_optimal_path(self):
        if hasattr(self, 'Centerline_model') and self.Centerline_model is not None:
            self.Centerline_model.SetDisplayVisibility(0)
    
    
    ############################################## TRACKING OF TRAJECTORY ########################################################

    def startTrackingRecording(self):
        self.recording = True
        self.recordedPoints = []
        logging.info("Tracking recording started")

        # create curve if it doesn't exist
        if not self.trajectoryCurveNode:
            self.trajectoryCurveNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsCurveNode", "EM_Tip_Trajectory")

        # Get the display node
        displayNode = self.trajectoryCurveNode.GetDisplayNode()

        # Set display properties
        if self.trajectoryCurveNode:
            displayNode = self.trajectoryCurveNode.GetDisplayNode()
            if displayNode:
                displayNode.SetSelectedColor(85/255.0, 173/255.0, 255/255.0)  


        # Set line thickness to 37% to match the thickness of the optimal path representation
        displayNode.SetLineThickness(0.37)

        # Set glyph type to Vertex2D (also to match the glyph type of the optimal path representation)
        displayNode.SetGlyphType(slicer.vtkMRMLMarkupsDisplayNode.Vertex2D) 
        
        self.trajectoryCurveNode.RemoveAllControlPoints()

        # Add initial position
        self.addTrackingPoint(self.getModelPosition(self.EM_tip_model))

        self.trackingTimer = qt.QTimer()
        self.trackingTimer.timeout.connect(self.recordTipPosition)
        self.trackingTimer.start(200)  # every 200 ms
    
    def getModelPosition(self, model):
        transformNode = model.GetParentTransformNode()
        if not transformNode:
            # Get the center
            bounds = [0]*6
            model.GetBounds(bounds)
            center = [
                (bounds[0] + bounds[1]) / 2.0,
                (bounds[2] + bounds[3]) / 2.0,
                (bounds[4] + bounds[5]) / 2.0
            ]
            return center
        else:
            matrix = vtk.vtkMatrix4x4()
            transformNode.GetMatrixTransformToWorld(matrix)
            bounds = [0]*6
            model.GetBounds(bounds)
            localCenter = [
                (bounds[0] + bounds[1]) / 2.0,
                (bounds[2] + bounds[3]) / 2.0,
                (bounds[4] + bounds[5]) / 2.0
            ]

            worldCenter = [0, 0, 0, 1]
            localCenter.append(1)
            matrix.MultiplyPoint(localCenter, worldCenter)

            return worldCenter[:3]


    def moveModel(self, newTransform):
        # Applies the new transformation to EM_tip_model
        self.EM_tip_model.SetAndObserveTransformNodeID(newTransform.GetID())

        # Records the new position
        if self.recording:
            self.addTrackingPoint(self.getModelPosition(self.EM_tip_model))

    def addTrackingPoint(self, position):
        if self.recording:
            self.recordedPoints.append(position)
            if self.trajectoryCurveNode:
                self.trajectoryCurveNode.AddControlPoint(vtk.vtkVector3d(*position))
            logging.info(f"Point added: {position}")


    def stopTrackingRecording(self):
        self.recording = False
        if hasattr(self, 'trackingTimer') and self.trackingTimer.isActive():
            self.trackingTimer.stop()
        logging.info("Tracking recording stopped")


    def recordTipPosition(self):
        position = self.getModelPosition(self.EM_tip_model)
        self.addTrackingPoint(position) 
        #self.moveCameraTo(position)

    def moveCameraTo(self, position):
        layoutManager = slicer.app.layoutManager()
        threeDWidget = layoutManager.threeDWidget(0)
        threeDView = threeDWidget.threeDView()
        cameraNode = threeDView.cameraNode()

        if cameraNode:
            cameraNode.SetPosition(position[0], position[1] - 100, position[2] + 100)
            cameraNode.SetFocalPoint(position[0], position[1], position[2])
            cameraNode.SetViewUp(0, 0, 1)
            threeDView.resetFocalPoint()


    def saveRecordedTrajectory(self):
        markupsNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
        for idx, point in enumerate(self.recordedPoints):
            markupsNode.AddFiducial(point[0], point[1], point[2])
        logging.info(f"Recorded trajectory saved with {len(self.recordedPoints)} points.")
    
    

    ###################### COMPARE PATHS ###################################
    def setup_deviation_text_display(self):
        # Actor for numeric deviation
        self.deviationValueActor = vtk.vtkTextActor()
        self.deviationValueActor.GetTextProperty().SetFontSize(20)
        self.deviationValueActor.GetTextProperty().SetBold(True)
        self.deviationValueActor.GetTextProperty().SetColor(0.0, 1.0, 0.0)  
        self.deviationValueActor.SetInput("Deviation: -- mm")
        self.deviationValueActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        self.deviationValueActor.SetPosition(0.70, 0.70)

        # Actor for deviation alert
        self.deviationAlertActor = vtk.vtkTextActor()
        self.deviationAlertActor.GetTextProperty().SetFontSize(20)
        self.deviationAlertActor.GetTextProperty().SetBold(True)
        self.deviationAlertActor.GetTextProperty().SetColor(1.0, 0.0, 0.0) 
        self.deviationAlertActor.SetInput("You are deviating")
        self.deviationAlertActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        self.deviationAlertActor.SetPosition(0.70, 0.74)

        renderer = slicer.app.layoutManager().threeDWidget(0).threeDView().renderWindow().GetRenderers().GetFirstRenderer()
        renderer.AddActor2D(self.deviationValueActor)
        renderer.AddActor2D(self.deviationAlertActor)

        self.deviationValueActor.SetVisibility(0)
        self.deviationAlertActor.SetVisibility(0)


    def calculateDeviationToOptimalPath(self):
        """
        Computes the distance from the EM tip to the closest point on the optimal path.
        """
        if not hasattr(self, 'Centerline_model') or not self.Centerline_model:
            return None

        if not self.EM_tip_model:
            return None

        # Get EM tip position
        tipPosition = self.getModelPosition(self.EM_tip_model)
        if not tipPosition:
            return None

        # Convert optimal path to polydata
        optimalPathPoints = vtk.vtkPoints()
        for i in range(self.Centerline_model.GetNumberOfControlPoints()):
            pos = self.Centerline_model.GetNthControlPointPositionVector(i)
            optimalPathPoints.InsertNextPoint(pos)

        polyData = vtk.vtkPolyData()
        polyData.SetPoints(optimalPathPoints)

        # Use locator to find closest point
        locator = vtk.vtkPointLocator()
        locator.SetDataSet(polyData)
        locator.BuildLocator()

        closestPointId = locator.FindClosestPoint(tipPosition)
        closestPoint = [0.0, 0.0, 0.0]
        polyData.GetPoint(closestPointId, closestPoint)

        # Compute distance
        deviation = np.linalg.norm(np.array(tipPosition) - np.array(closestPoint))
        return deviation


    def startDeviationMonitoring(self):
        if not hasattr(self, 'deviationValueActor') or not hasattr(self, 'deviationAlertActor'):
            self.setup_deviation_text_display()

        if not hasattr(self, 'deviationTimer'):
            self.deviationTimer = qt.QTimer()
            self.deviationTimer.timeout.connect(self.updateDeviationText)

        self.deviationValueActor.SetVisibility(1)
        self.deviationAlertActor.SetVisibility(1)
        self.deviationTimer.start(200)


    def stopDeviationMonitoring(self):
        if hasattr(self, 'deviationTimer'):
            self.deviationTimer.stop()
        if hasattr(self, 'deviationValueActor'):
            self.deviationValueActor.SetVisibility(0)
        if hasattr(self, 'deviationAlertActor'):
            self.deviationAlertActor.SetVisibility(0)


    def updateDeviationText(self):
        deviation = self.calculateDeviationToOptimalPath()

        if deviation is None:
            self.deviationValueActor.SetInput("Deviation: -- mm")
            self.deviationAlertActor.SetVisibility(0)
        else:
            self.deviationValueActor.SetInput(f"Deviation: {deviation:.2f} mm")

            if deviation > 10.0:
                self.deviationAlertActor.SetInput("You are deviating")
                self.deviationAlertActor.GetTextProperty().SetColor(1.0, 0.0, 0.0)
                self.deviationAlertActor.SetVisibility(1)
            else:
                self.deviationAlertActor.SetVisibility(0)

        slicer.app.layoutManager().threeDWidget(0).threeDView().renderWindow().Render()







        
    
