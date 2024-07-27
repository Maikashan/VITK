from render import render_images
from 3DView import render_3D
from segmentation import segmentation
from registration import register_images
import itk
import vtk

file_paths = ["Data/case6_gre1.nrrd",
             "Data/case6_gre2.nrrd"]

registered_paths =
            ["Data/case6_gre1.nrrd",
             "Data/registered.nrrd"]

segmented = ["segmented_1.nrrd", "segmented_2.nrrd"]

# REGISTRATION
register_images(file_paths[0], file_paths[1], registered_paths[1])


# SEGMENTATION
input_image = itk.imread(registered_paths[0], pixel_type=itk.D)
segmentation(input_image, segmented[0])

input_image = itk.imread(registered_paths[0], pixel_type=itk.D)
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

# VISUALIZATION
render_3D(registered_paths, segmented_paths)
# render_images(readers)
