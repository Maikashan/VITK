from render import render_images
from 3DView import render_3D
from segmentation import segmentation
import itk
import vtk

filePaths = ["Data/case6_gre1.nrrd",
             "Data/case6_gre2.nrrd"]
             # "test.nrrd"]

segmented = ["segmented_1.nrrd", "segmented_2.nrrd"]


input_image = itk.imread(filePaths[0], pixel_type=itk.D)
segmentation(input_image, segmented[0])

input_image = itk.imread(filePaths[0], pixel_type=itk.D)
segmentation(input_image, segmented[1])

# readers = []
# for i in range(2):
#     reader = vtk.vtkNrrdReader()
#     reader.SetFileName(filePaths[i])
#     readers.append(reader)
#
#     readerSegmented = vtk.vtkNrrdReader()
#     readerSegmented.SetFileName(segmented[i])
#     readers.append(readerSegmented)

paths = ["Data/case6_gre1.nrrd", "Data/case6_gre2.nrrd"]
pathsSegmented = ["segmented_1.nrrd", "segmented_2.nrrd"]
render_3D(paths, pathsSegmented)

render_images(readers)
