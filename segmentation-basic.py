import itk
import os
import matplotlib
import matplotlib.pyplot as plt

# input_filepath = 'Data/brain.png'
input_filepath = "Data/case6_gre1.nrrd"
output_filepath = "test.nrrd"

seed1X = 122
seed1Y = 65
seed1Z = 84

seed2X = 100
seed2Y = 80
seed2Z = 84

# seedX = 85
# seedY = 120
# seedZ = 188

seed1 = itk.Index[3]([seed1X, seed1Y, seed1Z])
seed2 = itk.Index[3]([seed2X, seed2Y, seed2Z])

lower = 580.0
upper = 910.0

input_image = itk.imread(input_filepath, pixel_type=itk.D)

# plt.imshow(input_image[seed1Z], cmap="gray")
# plt.plot(seed1X, seed1Y, "ro")  # red dot for the seed point
# plt.title(f"Slice {seed1Z } with Seed Point")
# plt.show()
# plt.waitforbuttonpress()
# print("val", input_image[seedZ, seedX, seedY])

smoother = itk.GradientAnisotropicDiffusionImageFilter.New(
    Input=input_image, NumberOfIterations=20, TimeStep=0.04, ConductanceParameter=3
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
connected_threshold.AddSeed(seed1)
connected_threshold.AddSeed(seed2)
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
