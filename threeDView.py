#!/usr/bin/env python

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
import vtk

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import VTK_VERSION_NUMBER, vtkVersion
from vtkmodules.vtkCommonDataModel import vtkMergePoints
from vtkmodules.vtkFiltersCore import vtkFlyingEdges3D, vtkMarchingCubes
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
from vtkmodules.vtkIOImage import vtkMetaImageReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
)

colors = vtkNamedColors()


def create_renderer(path, segmentedPath):
    # Create the pipeline.
    ren = vtkRenderer()

    reader = vtk.vtkNrrdReader()
    reader.SetFileName(segmentedPath)
    reader.Update()

    readerHead = vtk.vtkNrrdReader()
    readerHead.SetFileName(path)
    readerHead.Update()

    locator = vtkMergePoints()
    locator.SetDivisions(64, 64, 92)
    locator.SetNumberOfPointsPerBucket(2)
    locator.AutomaticOff()

    iso = vtkFlyingEdges3D()
    iso.SetInputConnection(reader.GetOutputPort())
    iso.ComputeGradientsOn()
    iso.ComputeScalarsOff()
    iso.SetValue(0, 50)

    iso_mapper = vtkPolyDataMapper()
    iso_mapper.SetInputConnection(iso.GetOutputPort())
    iso_mapper.ScalarVisibilityOff()

    iso_actor = vtkActor()
    iso_actor.SetMapper(iso_mapper)
    iso_actor.GetProperty().SetColor(colors.GetColor3d("Red"))

    outline = vtkOutlineFilter()
    outline.SetInputConnection(reader.GetOutputPort())

    opacityFun = vtk.vtkPiecewiseFunction()

    # Set a mapping going from 0.0 opacity at 90, up to 0.2 at 100,
    # and back down to 0.0 at 120.
    opacityFun.AddPoint(0.0, 0.0)
    opacityFun.AddPoint(90.0, 0.0)
    opacityFun.AddPoint(100.0, 0.2)
    opacityFun.AddPoint(120.0, 0.0)

    # Create a color transfer function for the mapping of scalar
    # value into color
    colorFun = vtk.vtkColorTransferFunction()

    # Set the color to a constant value, you might
    # want to try (0.8, 0.4, 0.2)
    colorFun.AddRGBPoint(1.0, 1.0, 1.0, 1.0)
    colorFun.AddRGBPoint(255.0, 0.8, 0.4, 0.2)

    # Create a volume property
    # Set the opacity and color. Change interpolation
    # to linear for a more pleasing image
    property = vtk.vtkVolumeProperty()
    property.SetScalarOpacity(opacityFun)
    property.SetColor(colorFun)
    property.SetInterpolationTypeToLinear()

    # Create the volume mapper
    mapper = vtk.vtkSmartVolumeMapper()

    # Set the input to the output of the reader
    mapper.SetInputConnection(readerHead.GetOutputPort())

    # Create the volume
    volume = vtk.vtkVolume()

    # Set the property and the mapper
    volume.SetProperty(property)
    volume.SetMapper(mapper)

    outline_mapper = vtkPolyDataMapper()
    outline_mapper.SetInputConnection(outline.GetOutputPort())

    outline_actor = vtkActor()
    outline_actor.SetMapper(outline_mapper)

    # Add the actors to the renderer, set the background and size.
    #
    ren.AddActor(outline_actor)
    ren.AddActor(volume)
    ren.AddActor(iso_actor)
    ren.SetBackground(colors.GetColor3d("SlateGray"))
    ren.GetActiveCamera().SetFocalPoint(0, 0, 0)
    ren.GetActiveCamera().SetPosition(0, -1, 0)
    ren.GetActiveCamera().SetViewUp(0, 0, -1)
    ren.ResetCamera()
    ren.GetActiveCamera().Dolly(1.5)
    ren.ResetCameraClippingRange()

    return ren


def render_3D(paths, segmentedPaths):
    if len(paths) == 2:
        xmins = [0, 0.5]
        xmaxs = [0.5, 1]
        ymins = [0, 0]
        ymaxs = [1, 1]
    else:
        xmins = [0, 0.5, 0.25]
        xmaxs = [0.5, 1, 0.75]
        ymins = [0, 0, 0.5]
        ymaxs = [0.5, 0.5, 1]

    names = ["First Tumor Segmentation", "Second Tumor Segmentation", "Difference of the 2 segmentations"]

    # Create the RenderWindow, Renderer and Interactor.
    ren_win = vtkRenderWindow()

    for i in range(len(paths)):
        ren = create_renderer(paths[i], segmentedPaths[i])
        ren.SetViewport(xmins[i], ymins[i], xmaxs[i], ymaxs[i])

        title = vtk.vtkTextActor()
        title.SetInput(names[i])
        title.GetTextProperty().SetFontSize(24)
        title.GetTextProperty().SetColor(1.0, 1.0, 1.0)
        title.SetPosition(50, 10)
        ren.AddActor2D(title)

        ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

    ren_win.SetSize(1400, 700 if len(paths) == 2 else 1400)
    ren_win.SetWindowName("VITK")

    ren_win.Render()
    iren.Start()


if __name__ == "__main__":

    # SWITCH TO HAVE DIFFERENCE
    # paths = ["Data/case6_gre1.nrrd", "Data/case6_gre2.nrrd"]
    # pathsSegmented = ["segmented_1.nrrd", "segmented_2.nrrd"]

    paths = ["Data/case6_gre1.nrrd", "Data/case6_gre2.nrrd", "Data/case6_gre1.nrrd"]
    pathsSegmented = ["segmented_1.nrrd", "segmented_2.nrrd", "image_diff.nrrd"]

    render_3D(paths, pathsSegmented)
