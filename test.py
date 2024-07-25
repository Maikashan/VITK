import vtk
import os
from vtk.util.numpy_support import vtk_to_numpy
import numpy as np

filePath = "Data/case6_gre1.nrrd"
reader = vtk.vtkNrrdReader()
reader.SetFileName(filePath)

reader.Update()
(xMin, xMax, yMin, yMax, zMin, zMax) = reader.GetExecutive().GetWholeExtent(reader.GetOutputInformation(0))
(xSpacing, ySpacing, zSpacing) = reader.GetOutput().GetSpacing()
(x0, y0, z0) = reader.GetOutput().GetOrigin()

center = [x0 + xSpacing * 0.5 * (xMin + xMax),
          y0 + ySpacing * 0.5 * (yMin + yMax),
          z0 + zSpacing * 0.5 * (zMin + zMax)]

# Matrices for axial, coronal, sagittal, oblique view orientations
axial = vtk.vtkMatrix4x4()
axial.DeepCopy((1, 0, 0, center[0],
                0, 1, 0, center[1],
                0, 0, 1, center[2],
                0, 0, 0, 1))

coronal = vtk.vtkMatrix4x4()
coronal.DeepCopy((1, 0, 0, center[0],
                  0, 0, 1, center[1],
                  0,-1, 0, center[2],
                  0, 0, 0, 1))

sagittal = vtk.vtkMatrix4x4()
sagittal.DeepCopy((0, 0,-1, center[0],
                   1, 0, 0, center[1],
                   0,-1, 0, center[2],
                   0, 0, 0, 1))

oblique = vtk.vtkMatrix4x4()
oblique.DeepCopy((1, 0, 0, center[0],
                  0, 0.866025, -0.5, center[1],
                  0, 0.5, 0.866025, center[2],
                  0, 0, 0, 1))

matrices = [ axial, coronal, sagittal, oblique]

# Extract a slice in the desired orientation
reslice = vtk.vtkImageReslice()
reslice.SetInputConnection(reader.GetOutputPort())
reslice.SetOutputDimensionality(2)
reslice.SetResliceAxes(oblique)
reslice.SetInterpolationModeToLinear()

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
renderer.AddActor(actor)

window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
window.SetSize(1000, 1000)

# Set up the interaction
interactorStyle = vtk.vtkInteractorStyleImage()
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetInteractorStyle(interactorStyle)
window.SetInteractor(interactor)
window.Render()

# vtkNew<vtkTexturedButtonRepresentation2D> buttonRepresentation;
#   buttonRepresentation->SetNumberOfStates(2);
#   buttonRepresentation->SetButtonTexture(0, image1);
#   buttonRepresentation->SetButtonTexture(1, image2);

# image1 = vtk.vtkImageData()
# image1.SetDimensions(10, 10, 1)
# frame = vtk_to_numpy(image1.GetScalarPointer(0, 0, 0))
#
# image2 = vtk.vtkImageData()
# image2.SetDimensions(10, 10, 1)
#
# buttonRepresentation = vtk.vtkTexturedButtonRepresentation2D()
# buttonRepresentation.SetNumberOfStates(2)
# buttonRepresentation.SetButtonTexture(0, image1)
# buttonRepresentation.SetButtonTexture(1, image2)

buttonActor = vtk.vtkButtonWidget()
buttonActor.SetInteractor(interactor)

# Create callbacks for slicing the image
actions = {}
actions["Slicing"] = 0
actions["Axes"] = oblique
actions["matrices_index"] = 3

matrices_index = 2

def ButtonCallback(obj, event):
    actions["Slicing"] = event == "LeftButtonPressEvent"
    if event == "RightButtonPressEvent":
        actions["matrices_index"] += 1
        actions["matrices_index"] %= 4
        actions["Axes"] = matrices[actions["matrices_index"]]
        reslice.SetResliceAxes(actions["Axes"])
        reslice.Update()
        window.Render()

def MouseMoveCallback(obj, event):
    (lastX, lastY) = interactor.GetLastEventPosition()
    (mouseX, mouseY) = interactor.GetEventPosition()
    if actions["Slicing"] == 1:
        deltaY = mouseY - lastY
        reslice.SetResliceAxes(actions["Axes"])
        reslice.Update()
        sliceSpacing = reslice.GetOutput().GetSpacing()[2]
        matrix = reslice.GetResliceAxes()
        # move the center point that we are slicing through
        center = matrix.MultiplyPoint((0, 0, sliceSpacing*deltaY, 1))
        matrix.SetElement(0, 3, center[0])
        matrix.SetElement(1, 3, center[1])
        matrix.SetElement(2, 3, center[2])
        window.Render()
    else:
        interactorStyle.OnMouseMove()


interactorStyle.AddObserver("MouseMoveEvent", MouseMoveCallback)
interactorStyle.AddObserver("LeftButtonPressEvent", ButtonCallback)
interactorStyle.AddObserver("RightButtonPressEvent", ButtonCallback)
interactorStyle.AddObserver("LeftButtonReleaseEvent", ButtonCallback)
# interactorStyle.SetInteractionModeToImage3D()

# Start interaction
interactor.Start()
del renderer
del window
del interactor
