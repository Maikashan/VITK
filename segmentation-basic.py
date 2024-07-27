import itk
import os
import matplotlib
import matplotlib.pyplot as plt

# input_filepath = 'Data/brain.png'
input_filepath = 'Data/case6_gre1.nrrd'
output_filepath = 'test.nrrd'

seedX = 79
seedY = 97
seedZ = 100

# seedX = 85
# seedY = 120
# seedZ = 188

lower = 300.0
upper = 1200.0

input_image = itk.imread(input_filepath, pixel_type=itk.F)

smoother = itk.GradientAnisotropicDiffusionImageFilter.New(
    Input=input_image,
    NumberOfIterations=20,
    TimeStep=0.04,
    ConductanceParameter=3
)
smoother.Update()
itk.imwrite(smoother, "smoother.nrrd")

# plt.imshow(smoother.GetOutput(), cmap='gray')
print("Smoother")
# plt.waitforbuttonpress()

dimension = input_image.GetImageDimension()

# plt.imshow(itk.GetArrayViewFromImage(input_image), cmap='gray')
print("Input")
# plt.waitforbuttonpress()

connected_threshold = itk.ConnectedThresholdImageFilter.New(smoother.GetOutput())
connected_threshold.SetReplaceValue(1374)
connected_threshold.SetLower(lower)
connected_threshold.SetUpper(upper)
connected_threshold.SetSeed((seedX, seedY, seedZ))
# connected_threshold.SetSeed((seedX + 10, seedY - 10, seedZ + 5))
connected_threshold.Update()

# plt.imshow(itk.GetArrayViewFromImage(connected_threshold), cmap='gray')
print("COnnected")
# plt.waitforbuttonpress()

# in_type = itk.output(connected_threshold)
# out_type = itk.Image[itk.UC, dimension]
# rescaler = itk.RescaleIntensityImageFilter[in_type, out_type].New(connected_threshold)
# rescaler.SetOutputMinimum(0)
# rescaler.SetOutputMaximum(255)

itk.imwrite(connected_threshold, output_filepath)

