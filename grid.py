import itertools
import itk
from sklearn.model_selection import ParameterGrid

# Define the parameters grid
param_grid = {
    "learning_rate": [1.5, 3.0, 5.0],
    "minimum_step_length": [0.0001, 0.001, 0.01],
    "maximum_step_size": [0.01, 0.1, 1.0],
    "relaxation_factor": [0.1, 0.5, 0.9],
}


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

    best_metric_value = float("inf")
    best_parameters = None

    # Perform grid search
    for params in ParameterGrid(param_grid):
        optimizer = itk.RegularStepGradientDescentOptimizerv4.New()
        optimizer.SetLearningRate(params["learning_rate"])
        optimizer.SetMinimumStepLength(params["minimum_step_length"])
        optimizer.SetMaximumStepSizeInPhysicalUnits(params["maximum_step_size"])
        optimizer.SetNumberOfIterations(200)
        optimizer.SetRelaxationFactor(params["relaxation_factor"])

        iteration_update = CommandIterationUpdate(optimizer)

        image1_interpolation = itk.LinearInterpolateImageFunction[
            FixedImageType, itk.D
        ].New()
        metric = itk.MeanSquaresImageToImageMetricv4[
            FixedImageType, MovingImageType
        ].New()
        metric.SetFixedInterpolator(image1_interpolation)
        metric2 = itk.CorrelationImageToImageMetricv4[
            FixedImageType, MovingImageType
        ].New()
        metric2.SetFixedInterpolator(image1_interpolation)
        metric3 = itk.MattesMutualInformationImageToImageMetricv4[
            FixedImageType, MovingImageType
        ].New()
        metric3.SetFixedInterpolator(image1_interpolation)

        registration = itk.ImageRegistrationMethodv4[
            FixedImageType, MovingImageType
        ].New(
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
        registration.SetSmoothingSigmasPerLevel([4, 2, 1])
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
        metric_value = optimizer.GetValue()

        print(f"Parameters: {params}")
        print(" Translation X = " + str(translation_along_x))
        print(" Translation Y = " + str(translation_along_y))
        print(" Translation Z = " + str(translation_along_z))
        print(" Iterations    = " + str(number_of_iterations))
        print(" Metric value  = " + str(metric_value))

        if metric_value < best_metric_value:
            best_metric_value = metric_value
            best_parameters = params

    print("Best Parameters: ", best_parameters)
    print("Best Metric Value: ", best_metric_value)

    # Use best parameters to perform final registration
    optimizer.SetLearningRate(best_parameters["learning_rate"])
    optimizer.SetMinimumStepLength(best_parameters["minimum_step_length"])
    optimizer.SetMaximumStepSizeInPhysicalUnits(best_parameters["maximum_step_size"])
    optimizer.SetNumberOfIterations(200)
    optimizer.SetRelaxationFactor(best_parameters["relaxation_factor"])

    registration.Update()

    res_transform = registration.GetTransform()
    final_parameters = res_transform.GetParameters()
    translation_along_x = final_parameters.GetElement(0)
    translation_along_y = final_parameters.GetElement(1)
    translation_along_z = final_parameters.GetElement(2)

    number_of_iterations = optimizer.GetCurrentIteration()
    best_value = optimizer.GetValue()

    print("Final Result = ")
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


# Define a dummy CommandIterationUpdate class as a placeholder
class CommandIterationUpdate:
    def __init__(self, optimizer):
        self.optimizer = optimizer

    def __call__(self):
        iteration = self.optimizer.GetCurrentIteration()
        value = self.optimizer.GetValue()
        print(f"Iteration {iteration}: Value = {value}")


# Call the function with appropriate paths
register_images_optimizer(
    "Data/case6_gre1.nrrd", "Data/case6_gre2.nrrd", "output_image_path.nrrd"
)
