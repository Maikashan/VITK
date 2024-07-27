import itk


def image_diff(path1, path2):

    image1 = itk.imread(path1, itk.F)
    image2 = itk.imread(path2, itk.F)

    difference_image = itk.subtract_image_filter(image1, image2)
    itk.imwrite(difference_image, "image_diff.nrrd")
