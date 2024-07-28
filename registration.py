import itk
import itk.itkAffineTransformPython
import itk.itkNormalVariateGeneratorPython
import itk.itkOnePlusOneEvolutionaryOptimizerv4Python
import itk.itkTranslationTransformPython
from observer import CommandIterationUpdate
from itk.support.types import PixelTypes


def register_images(fixed_path, moving_path, save_path):
    PixelType = itk.D
    fixed_image = itk.imread(fixed_path, PixelType)
    moving_image = itk.imread(moving_path, PixelType)
    dimension = fixed_image.GetImageDimension()
    FixedImageType = type(fixed_image)
    MovingImageType = type(moving_image)

    TransformType = itk.TranslationTransform[itk.D, dimension]
    initial_transform = TransformType.New()
    initial_transform.SetIdentity()

    # This paramaters were found by grid search to get optimal results
    optimizer = itk.RegularStepGradientDescentOptimizerv4.New()
    optimizer.SetLearningRate(1.0)
    optimizer.SetMinimumStepLength(0.01)
    optimizer.SetMaximumStepSizeInPhysicalUnits(0.01)
    optimizer.SetNumberOfIterations(200)
    optimizer.SetRelaxationFactor(0.5)

    iteration_update = CommandIterationUpdate(optimizer)

    image1_interpolation = itk.LinearInterpolateImageFunction[
        FixedImageType, itk.D
    ].New()
    metric = itk.MeanSquaresImageToImageMetricv4[FixedImageType, MovingImageType].New()
    metric.SetFixedInterpolator(image1_interpolation)
    metric2 = itk.CorrelationImageToImageMetricv4[FixedImageType, MovingImageType].New()
    metric2.SetFixedInterpolator(image1_interpolation)
    metric3 = itk.MattesMutualInformationImageToImageMetricv4[
        FixedImageType, MovingImageType
    ].New()
    metric3.SetFixedInterpolator(image1_interpolation)

    registration = itk.ImageRegistrationMethodv4[FixedImageType, MovingImageType].New(
        FixedImage=fixed_image,
        MovingImage=moving_image,
        Metric=metric,
        Optimizer=optimizer,
        InitialTransform=initial_transform,
    )
       # Set moving initial transform to identity
    moving_initial_transform = TransformType.New()
    moving_initial_transform.SetIdentity()
    registration.SetMovingInitialTransform(moving_initial_transform)
    registration.SetNumberOfLevels(3)
    registration.SetSmoothingSigmasPerLevel([4,2,1])
    registration.SetShrinkFactorsPerLevel([4, 2, 1])

    moving_initial_transform = TransformType.New()
    initial_parameters = moving_initial_transform.GetParameters()
    initial_parameters[0] = 0
    initial_parameters[1] = 0
    moving_initial_transform.SetParameters(initial_parameters)
    registration.SetMovingInitialTransform(moving_initial_transform)

    # identity_transform = TransformType.New()
    # identity_transform.SetIdentity()
    # registration.SetFixedInitialTransform(identity_transform)

    registration.Update()

    res_transform = registration.GetTransform()
    final_parameters = res_transform.GetParameters()
    translation_along_x = final_parameters.GetElement(0)
    translation_along_y = final_parameters.GetElement(1)
    translation_along_z = final_parameters.GetElement(2)

    number_of_iterations = optimizer.GetCurrentIteration()
    best_value = optimizer.GetValue()

    print("Result = ")
    print(" Translation X = " + str(translation_along_x))
    print(" Translation Y = " + str(translation_along_y))
    print(" Translation Z = " + str(translation_along_z))
    print(" Iterations    = " + str(number_of_iterations))
    print(" Metric value  = " + str(best_value))

    CompositeTransformType = itk.CompositeTransform[itk.D, dimension]
    output_composite_transform = CompositeTransformType.New()
    output_composite_transform.AddTransform(moving_initial_transform)
    output_composite_transform.AddTransform(registration.GetModifiableTransform())

    resample = itk.ResampleImageFilter.New(
        Input=moving_image,
        Transform=output_composite_transform,
        UseReferenceImage=True,
        ReferenceImage=fixed_image,
        Interpolator=image1_interpolation,
    )
    resample.SetDefaultPixelValue(130)
    resample.Update()
    resampled_image = resample.GetOutput()

    itk.imwrite(resampled_image, save_path)


def register_images_optimizer(fixed_path, moving_path, save_path):
    PixelType = itk.D
    fixed_image = itk.imread(fixed_path, PixelType)
    moving_image = itk.imread(moving_path, PixelType)
    dimension = fixed_image.GetImageDimension()
    FixedImageType = type(fixed_image)
    MovingImageType = type(moving_image)

    TransformType = itk.TranslationTransform[itk.D, dimension]
    initial_transform = TransformType.New()
    initial_transform.SetIdentity()

    optimizer = itk.RegularStepGradientDescentOptimizerv4.New()
    optimizer.SetLearningRate(0.5)
    optimizer.SetMinimumStepLength(0.001)
    optimizer.SetMaximumStepSizeInPhysicalUnits(0.1)
    optimizer.SetNumberOfIterations(200)
    optimizer.SetRelaxationFactor(0.5)

    iteration_update = CommandIterationUpdate(optimizer)

    image1_interpolation = itk.LinearInterpolateImageFunction[
        FixedImageType, itk.D
    ].New()
    metric = itk.MeanSquaresImageToImageMetricv4[FixedImageType, MovingImageType].New()
    metric.SetFixedInterpolator(image1_interpolation)
    metric2 = itk.CorrelationImageToImageMetricv4[FixedImageType, MovingImageType].New()
    metric2.SetFixedInterpolator(image1_interpolation)
    metric3 = itk.MattesMutualInformationImageToImageMetricv4[
        FixedImageType, MovingImageType
    ].New()
    metric3.SetFixedInterpolator(image1_interpolation)

    registration = itk.ImageRegistrationMethodv4[FixedImageType, MovingImageType].New(
        FixedImage=fixed_image,
        MovingImage=moving_image,
        Metric=metric,
        Optimizer=optimizer,
        InitialTransform=initial_transform,
    )
       # Set moving initial transform to identity
    moving_initial_transform = TransformType.New()
    moving_initial_transform.SetIdentity()
    registration.SetMovingInitialTransform(moving_initial_transform)
    registration.SetNumberOfLevels(3)
    registration.SetSmoothingSigmasPerLevel([4,2,1])
    registration.SetShrinkFactorsPerLevel([4, 2, 1])

    moving_initial_transform = TransformType.New()
    initial_parameters = moving_initial_transform.GetParameters()
    initial_parameters[0] = 0
    initial_parameters[1] = 0
    moving_initial_transform.SetParameters(initial_parameters)
    registration.SetMovingInitialTransform(moving_initial_transform)

    # identity_transform = TransformType.New()
    # identity_transform.SetIdentity()
    # registration.SetFixedInitialTransform(identity_transform)

    registration.Update()

    res_transform = registration.GetTransform()
    final_parameters = res_transform.GetParameters()
    translation_along_x = final_parameters.GetElement(0)
    translation_along_y = final_parameters.GetElement(1)
    translation_along_z = final_parameters.GetElement(2)

    number_of_iterations = optimizer.GetCurrentIteration()
    best_value = optimizer.GetValue()

    print("Result = ")
    print(" Translation X = " + str(translation_along_x))
    print(" Translation Y = " + str(translation_along_y))
    print(" Translation Z = " + str(translation_along_z))
    print(" Iterations    = " + str(number_of_iterations))
    print(" Metric value  = " + str(best_value))

    CompositeTransformType = itk.CompositeTransform[itk.D, dimension]
    output_composite_transform = CompositeTransformType.New()
    output_composite_transform.AddTransform(moving_initial_transform)
    output_composite_transform.AddTransform(registration.GetModifiableTransform())

    resample = itk.ResampleImageFilter.New(
        Input=moving_image,
        Transform=output_composite_transform,
        UseReferenceImage=True,
        ReferenceImage=fixed_image,
        Interpolator=image1_interpolation,
    )
    resample.SetDefaultPixelValue(130)
    resample.Update()
    resampled_image = resample.GetOutput()

    itk.imwrite(resampled_image, save_path)

def registerEvolutionary(fixed_path, moving_path, save_path):
    PixelType = itk.D
    fixed_image = itk.imread(fixed_path, PixelType)
    moving_image = itk.imread(moving_path, PixelType)
    dimension = fixed_image.GetImageDimension()
    FixedImageType = type(fixed_image)
    MovingImageType = type(moving_image)
    image1_interpolation = itk.LinearInterpolateImageFunction[
        FixedImageType, itk.D
    ].New()
    metric = itk.MattesMutualInformationImageToImageMetricv4[
        FixedImageType, MovingImageType
    ].New()
    metric.SetFixedInterpolator(image1_interpolation)

    TransformType = itk.AffineTransform[itk.D, dimension]
    initial_transform = TransformType.New()
    initial_transform.SetIdentity()

    metric.SetNumberOfHistogramBins(60)

    generator = itk.itkNormalVariateGeneratorPython.itkNormalVariateGenerator_New()
    generator.Initialize(12345)

    optimizer = (
        itk.itkOnePlusOneEvolutionaryOptimizerv4Python.itkOnePlusOneEvolutionaryOptimizerv4D_New()
    )

    optimizer.SetNormalVariateGenerator(generator)
    optimizer.Initialize(15)
    optimizer.SetEpsilon(3.0)
    optimizer.SetMaximumIteration(400)

    iteration_update = CommandIterationUpdate(optimizer)

    registration = itk.ImageRegistrationMethodv4[FixedImageType, MovingImageType].New(
        FixedImage=fixed_image,
        MovingImage=moving_image,
        Metric=metric,
        Optimizer=optimizer,
        InitialTransform=initial_transform,
    )
    moving_initial_transform = TransformType.New()
    moving_initial_transform.SetIdentity()
    registration.SetMovingInitialTransform(moving_initial_transform)

    registration.SetNumberOfLevels(3)
    registration.SetSmoothingSigmasPerLevel([4, 2, 1])
    registration.SetShrinkFactorsPerLevel([4, 2, 1])
    registration.SamplingStrategy = "Random"
    registration.SamplingPercentage = 0.1
    registration.Update()

    res_transform = registration.GetTransform()
    final_parameters = res_transform.GetParameters()
    translation_along_x = final_parameters.GetElement(0)
    translation_along_y = final_parameters.GetElement(1)
    translation_along_z = final_parameters.GetElement(2)

    number_of_iterations = optimizer.GetCurrentIteration()
    best_value = optimizer.GetValue()

    print("Result = ")
    print(" Translation X = " + str(translation_along_x))
    print(" Translation Y = " + str(translation_along_y))
    print(" Translation Z = " + str(translation_along_z))
    print(" Iterations    = " + str(number_of_iterations))
    print(" Metric value  = " + str(best_value))

    # CompositeTransformType = itk.CompositeTransform[itk.D, dimension]
    # output_composite_transform = CompositeTransformType.New()
    # output_composite_transform.AddTransform(moving_initial_transform)
    # output_composite_transform.AddTransform(registration.GetModifiableTransform())

    resample = itk.ResampleImageFilter.New(
        Input=moving_image,
        Transform=res_transform,
        UseReferenceImage=True,
        ReferenceImage=fixed_image,
        Interpolator=image1_interpolation,
    )
    resample.SetDefaultPixelValue(130)
    resample.Update()
    resampled_image = resample.GetOutput()

    itk.imwrite(resampled_image, save_path)

    mse_calculator = itk.MeanSquaresImageToImageMetricv4[
        FixedImageType, MovingImageType
    ].New()
    mse_calculator.SetFixedImage(fixed_image)
    mse_calculator.SetMovingImage(moving_image)
    mse_calculator.SetFixedInterpolator(image1_interpolation)
    mse_calculator.SetMovingInterpolator(image1_interpolation)
    mse_calculator.SetTransform(res_transform)
    mse_calculator.Initialize()
    print("MSE Value:", mse_calculator.GetValue())


if __name__ == "__main__":
    fixed = "Data/case6_gre1.nrrd"
    moving = "Data/case6_gre2.nrrd"
    save = "registered.nrrd"
    register_images(fixed, moving, save)
