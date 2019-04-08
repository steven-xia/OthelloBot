import os

import tensorflow

NETWORK_LOCATION = os.path.join("..", "src", "network.h5")

keras_model = tensorflow.keras.models.load_model(NETWORK_LOCATION)
run_model = tensorflow.function(lambda x: keras_model(x))
concrete_function = run_model.get_concrete_function(
    [tensorflow.TensorSpec([None, 8, 8, 2], tensorflow.float32, name="board_input"),
     tensorflow.TensorSpec([None, 2], tensorflow.float32, name="extra_input")])

# tensorflow.saved_model.save(keras_model, ".")
# model = tensorflow.saved_model.load(".")
# concrete_function = model.signatures[
#     tensorflow.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY]

converter = tensorflow.lite.TFLiteConverter.from_keras_model_file(NETWORK_LOCATION)
# converter.optimizations = [tensorflow.lite.Optimize.OPTIMIZE_FOR_LATENCY]
# converter.optimizations = [tensorflow.lite.Optimize.OPTIMIZE_FOR_SIZE]
tensorflow_lite_model = converter.convert()
open("network.tflite", "wb+").write(tensorflow_lite_model)
