#!/usr/bin/env python

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
import vtk
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    VTK_VERSION_NUMBER,
    vtkVersion
)
from vtkmodules.vtkCommonDataModel import vtkMergePoints
from vtkmodules.vtkFiltersCore import (
    vtkFlyingEdges3D,
    vtkMarchingCubes
)
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
from vtkmodules.vtkIOImage import vtkMetaImageReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)


def main():
    # vtkFlyingEdges3D was introduced in VTK >= 8.2
    use_flying_edges = vtk_version_ok(8, 2, 0)

    file_name = get_program_parameters()

    readerHead = vtk.vtkNrrdReader()
    readerHead.SetFileName("Data/case6_gre1.nrrd")
    readerHead.Update()

    colors = vtkNamedColors()

    # Create the RenderWindow, Renderer and Interactor.
    ren = vtkRenderer()
    ren_win = vtkRenderWindow()
    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    # Create the pipeline.
    reader = vtk.vtkNrrdReader()
    reader.SetFileName(file_name)
    reader.Update()

    locator = vtkMergePoints()
    locator.SetDivisions(64, 64, 92)
    locator.SetNumberOfPointsPerBucket(2)
    locator.AutomaticOff()

    if use_flying_edges:
        try:
            using_marching_cubes = False
            iso = vtkFlyingEdges3D()
        except AttributeError:
            using_marching_cubes = True
            iso = vtkMarchingCubes()
    else:
        using_marching_cubes = True
        iso = vtkMarchingCubes()

    # iso = vtk.vtkSurfaceNets3D()
    iso.SetInputConnection(reader.GetOutputPort())
    iso.ComputeGradientsOn()
    iso.ComputeScalarsOff()
    iso.SetValue(0, 50)
    print(using_marching_cubes)
    if using_marching_cubes:
        iso.SetLocator(locator)

    iso_mapper = vtkPolyDataMapper()
    iso_mapper.SetInputConnection(iso.GetOutputPort())
    iso_mapper.ScalarVisibilityOff()

    iso_actor = vtkActor()
    iso_actor.SetMapper(iso_mapper)
    iso_actor.GetProperty().SetColor(colors.GetColor3d('Red'))

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
    colorFun.AddRGBPoint(0.0, .8, .4, .2)
    colorFun.AddRGBPoint(255.0, .8, .4, .2)

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
    ren.SetBackground(colors.GetColor3d('SlateGray'))
    ren.GetActiveCamera().SetFocalPoint(0, 0, 0)
    ren.GetActiveCamera().SetPosition(0, -1, 0)
    ren.GetActiveCamera().SetViewUp(0, 0, -1)
    ren.ResetCamera()
    ren.GetActiveCamera().Dolly(1.5)
    ren.ResetCameraClippingRange()

    ren_win.SetSize(640, 480)
    ren_win.SetWindowName('HeadBone')

    ren_win.Render()
    iren.Start()


def get_program_parameters():
    import argparse
    description = 'Marching cubes surface of human bone.'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='FullHead.mhd.')
    args = parser.parse_args()
    return args.filename


def vtk_version_ok(major, minor, build):
    """
    Check the VTK version.

    :param major: Major version.
    :param minor: Minor version.
    :param build: Build version.
    :return: True if the requested VTK version is greater or equal to the actual VTK version.
    """
    needed_version = 10000000000 * int(major) + 100000000 * int(minor) + int(build)
    try:
        vtk_version_number = VTK_VERSION_NUMBER
    except AttributeError:  # as error:
        ver = vtkVersion()
        vtk_version_number = 10000000000 * ver.GetVTKMajorVersion() + 100000000 * ver.GetVTKMinorVersion() \
                             + ver.GetVTKBuildVersion()
    if vtk_version_number >= needed_version:
        return True
    else:
        return False


if __name__ == '__main__':
    main()
