import itk
import os
import matplotlib
import matplotlib.pyplot as plt


def segmentation(input_image, save_path):
    seed1X = 122
    seed1Y = 65
    seed1Z = 84

    seed2X = 100
    seed2Y = 80
    seed2Z = 84

    seed1 = itk.Index[3]([seed1X, seed1Y, seed1Z])
    seed2 = itk.Index[3]([seed2X, seed2Y, seed2Z])

    lower = 580.0
    upper = 910.0

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

    print("Smoothing done")

    dimension = input_image.GetImageDimension()

    connected_threshold = itk.ConnectedThresholdImageFilter.New(smoother.GetOutput())
    connected_threshold.SetReplaceValue(1374)
    connected_threshold.SetLower(lower)
    connected_threshold.SetUpper(upper)
    connected_threshold.AddSeed(seed1)
    connected_threshold.AddSeed(seed2)
    connected_threshold.Update()

    print("Connected done")
    itk.imwrite(connected_threshold, save_path)
    return connected_threshold


if __name__ == "__main__":
    input_filepath = "Data/case6_gre1.nrrd"
    output_filepath = "test.nrrd"

    input_image = itk.imread(input_filepath, pixel_type=itk.D)
    connected_threshold = segmentation(input_image)
