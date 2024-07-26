import vtk
import os
from vtk.util.numpy_support import vtk_to_numpy
import numpy as np

class MouseInteractorHighLightActor(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, parent=None):
        self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)

        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()

    def leftButtonPressEvent(self, obj, event):
        clickPos = self.GetInteractor().GetEventPosition()
        print(clickPos)

        self.OnLeftButtonDown()
        return

filePaths = ["Data/case6_gre1.nrrd",
             # "Data/case6_gre2.nrrd"]
             "test.nrrd"]

xmins = [0, .5]
xmaxs = [0.5, 1]
ymins = [0, 0]
ymaxs = [1, 1]

window = vtk.vtkRenderWindow()
reslices = []

# Create callbacks for slicing the image
actions = {}
actions["Slicing"] = 0
actions["Axes"] = []
actions["AxesNames"] = ["Sagittal", "Axial", "Coronal"] #, "Oblique"]
actions["matrices_index"] = 0

for i in range(2):
    reader = vtk.vtkNrrdReader()
    reader.SetFileName(filePaths[i])

    reader.Update()
    (xMin, xMax, yMin, yMax, zMin, zMax) = reader.GetExecutive().GetWholeExtent(reader.GetOutputInformation(0))
    (xSpacing, ySpacing, zSpacing) = reader.GetOutput().GetSpacing()
    (x0, y0, z0) = reader.GetOutput().GetOrigin()

    center = [x0 + xSpacing * 0.5 * (xMin + xMax),
              y0 + ySpacing * 0.5 * (yMin + yMax),
              z0 + zSpacing * 0.5 * (zMin + zMax)]

    # Matrices for axial, coronal, sagittal, oblique view orientations
    sagittal = vtk.vtkMatrix4x4()
    sagittal.DeepCopy((1, 0, 0, center[0],
                    0, -1, 0, center[1],
                    0, 0, 1, center[2],
                    0, 0, 0, 1))

    axial = vtk.vtkMatrix4x4()
    axial.DeepCopy((1, 0, 0, center[0],
                      0, 0, 1, center[1],
                      0,-1, 0, center[2],
                      0, 0, 0, 1))

    coronal = vtk.vtkMatrix4x4()
    coronal.DeepCopy((0, 0,-1, center[0],
                       1, 0, 0, center[1],
                       0,-1, 0, center[2],
                       0, 0, 0, 1))

    oblique = vtk.vtkMatrix4x4()
    oblique.DeepCopy((1, 0, 0, center[0],
                      0, 0.866025, -0.5, center[1],
                      0, 0.5, 0.866025, center[2],
                      0, 0, 0, 1))

    actions["Axes"].append( [sagittal, axial, coronal, oblique] )


    # Extract a slice in the desired orientation
    reslice = vtk.vtkImageReslice()
    reslice.SetInputConnection(reader.GetOutputPort())
    reslice.SetOutputDimensionality(2)
    reslice.SetResliceAxes(sagittal)
    reslice.SetInterpolationModeToLinear()
    reslices.append(reslice)

    # Create a greyscale lookup table
    table = vtk.vtkLookupTable()
    table.SetRange(0, 2000) # image intensity range
    table.SetValueRange(0.0, 1.0) # from black to white
    table.SetSaturationRange(0.0, 0.0) # no color saturation
    table.SetRampToLinear()
    table.Build()

    # Map the image through the lookup table
    color = vtk.vtkImageMapToColors()
    color.SetLookupTable(table)
    color.SetInputConnection(reslice.GetOutputPort())

    # Display the image
    actor = vtk.vtkImageActor()
    actor.GetMapper().SetInputConnection(color.GetOutputPort())

    renderer = vtk.vtkRenderer()
    renderer.SetViewport(xmins[i], ymins[i], xmaxs[i], ymaxs[i]);
    renderer.AddActor(actor)

    window.AddRenderer(renderer)

window.SetSize(1000, 500)
window.SetWindowName("VITK Sagittal")

# Set up the interaction
interactorStyle = vtk.vtkInteractorStyleImage()
# picker = vtk.vtkPointPicker()

# interactorStyle = MouseInteractorHighLightActor()

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetInteractorStyle(interactorStyle)
# interactor.SetPicker(picker)
window.SetInteractor(interactor)
window.Render()

def ButtonCallback(obj, event):
    actions["Slicing"] = event == "LeftButtonPressEvent"
    if event == "RightButtonPressEvent":
        actions["matrices_index"] += 1
        actions["matrices_index"] %= len(actions["AxesNames"])

        for i in range(2):
            reslices[i].SetResliceAxes(actions["Axes"][i][actions["matrices_index"]])
            reslices[i].Update()
        window.Render()
        window.SetWindowName("VITK " + actions["AxesNames"][actions["matrices_index"]])

def MouseMoveCallback(obj, event):
    (lastX, lastY) = interactor.GetLastEventPosition()
    (mouseX, mouseY) = interactor.GetEventPosition()
    if actions["Slicing"] == 1:
        deltaY = mouseY - lastY

        for i in range(2):
            reslices[i].SetResliceAxes(actions["Axes"][i][actions["matrices_index"]])
            reslices[i].Update()
            sliceSpacing = reslices[i].GetOutput().GetSpacing()[2]
            matrix = reslices[i].GetResliceAxes()
            # move the center point that we are slicing through
            center = matrix.MultiplyPoint((0, 0, sliceSpacing*deltaY, 1))
            matrix.SetElement(0, 3, center[0])
            matrix.SetElement(1, 3, center[1])
            matrix.SetElement(2, 3, center[2])
            print(matrix)
        window.Render()
    else:
        interactorStyle.OnMouseMove()


interactorStyle.AddObserver("MouseMoveEvent", MouseMoveCallback)
interactorStyle.AddObserver("LeftButtonPressEvent", ButtonCallback)
interactorStyle.AddObserver("RightButtonPressEvent", ButtonCallback)
interactorStyle.AddObserver("LeftButtonReleaseEvent", ButtonCallback)

# Start interaction
interactor.Start()
del renderer
del window
del interactor
