import os
import tensorflow


def simple_squeeze_excitation_block(layer_input, filters, activation, reduction_ratio, **kwargs):
    flow = tensorflow.keras.layers.GlobalAveragePooling2D()(layer_input)
    flow = tensorflow.keras.layers.Dense(filters // reduction_ratio, **kwargs)(flow)
    flow = tensorflow.keras.layers.Activation(activation)(flow)
    flow = tensorflow.keras.layers.Dense(filters, **kwargs)(flow)
    flow = tensorflow.keras.layers.Activation(tensorflow.keras.activations.sigmoid)(flow)
    flow = tensorflow.keras.layers.Multiply()([flow, layer_input])
    return flow


def residual_block(layer_input, block_size, activation, filters, **kwargs):
    flow = layer_input
    for _ in range(block_size):
        flow = tensorflow.keras.layers.BatchNormalization()(flow)
        flow = tensorflow.keras.layers.Activation(activation)(flow)
        flow = tensorflow.keras.layers.Conv2D(filters, **kwargs)(flow)
    flow = simple_squeeze_excitation_block(flow, filters, activation, reduction_ratio=16,
                                           kernel_initializer="glorot_normal", use_bias=True)
    flow = tensorflow.keras.layers.Add()([flow, layer_input])
    return flow


def dense_block(layer_input, block_size, activation, units, **kwargs):
    flow = layer_input
    for _ in range(block_size):
        flow = tensorflow.keras.layers.BatchNormalization()(flow)
        flow = tensorflow.keras.layers.Activation(activation)(flow)
        flow = tensorflow.keras.layers.Dense(units, **kwargs)(flow)
    flow = tensorflow.keras.layers.Concatenate()([flow, layer_input])
    return flow


def on_tpu():
    import pprint

    if 'COLAB_TPU_ADDR' not in os.environ:
        print('ERROR: Not connected to a TPU runtime!')
        return False
    else:
        tpu_address = 'grpc://' + os.environ['COLAB_TPU_ADDR']
        print('TPU address is', tpu_address)

        with tensorflow.Session(tpu_address) as session:
            devices = session.list_devices()

        print('TPU devices:')
        pprint.pprint(devices)

        return True


def compile_optimizer_for_tpu(optimizer):
    optimizer = tensorflow.contrib.tpu.CrossShardOptimizer(optimizer)
    return optimizer


def compile_model_for_tpu(model):
    tpu_address = 'grpc://' + os.environ['COLAB_TPU_ADDR']
    tensorflow.logging.set_verbosity(tensorflow.logging.INFO)

    model = tensorflow.contrib.tpu.keras_to_tpu_model(
        model,
        strategy=tensorflow.contrib.tpu.TPUDistributionStrategy(
            tensorflow.contrib.cluster_resolver.TPUClusterResolver(tpu_address)))

    return model


if __name__ == "__main__":
    import multiprocessing

    import numpy

    import networks.datafile_manager
    import networks.train_utils

    CPU_COUNT = multiprocessing.cpu_count()
    DATA_FILE = "networks/training_data.txt"

    print(f"Loading data from file: {DATA_FILE} ... ")
    data = networks.datafile_manager.load_data(DATA_FILE)

    print(f"Preprocessing data with {CPU_COUNT} threads ... ")
    print(f"  - Parsing data ... ")
    p = multiprocessing.Pool(CPU_COUNT)
    data = p.map(networks.train_utils.preprocess_game, data.items(), chunksize=int(len(data) / CPU_COUNT))

    print(f"  - Splitting data ... ")
    training_inputs, training_outputs = tuple(zip(*data))
    training_board_inputs, training_extra_inputs = tuple(zip(*training_inputs))

    training_board_inputs = numpy.array(training_board_inputs)
    training_extra_inputs = numpy.array(training_extra_inputs)
    training_outputs = numpy.array(training_outputs)

    # TRAINING BELOW ---------------------------------------------------------------------------------------------------

    ON_TPU = on_tpu()

    LOAD_FILE = False
    SAVE_FILE = "network.h5"

    CONVOLUTIONAL_BLOCKS = 4
    CONVOLUTIONAL_BLOCK_SIZE = 32

    DENSE_BLOCKS = 4
    DENSE_BLOCK_SIZE = 256

    ACTIVATION = tensorflow.keras.activations.relu
    OPTIMIZER = tensorflow.keras.optimizers.Adam()

    RESIDUAL_BLOCK_DROPOUT_RATE = 0.0
    DOWNSAMPLING_DROPOUT_RATE = 0.1
    DENSE_BLOCK_DROPOUT_RATE = 0.0
    DENSE_DROPOUT_RATE = 0.0

    if LOAD_FILE:
        network = tensorflow.keras.models.load_model(SAVE_FILE)
    else:
        board_input = tensorflow.keras.layers.Input(shape=(8, 8, 2))
        extra_input = tensorflow.keras.layers.Input(shape=(2,))

        x = board_input

        x = tensorflow.keras.layers.Conv2D(filters=CONVOLUTIONAL_BLOCK_SIZE, kernel_size=(3, 3), strides=(1, 1),
                                           padding="same", use_bias=True, kernel_initializer="glorot_normal")(x)
        x = tensorflow.keras.layers.Dropout(DOWNSAMPLING_DROPOUT_RATE)(x)

        for _ in range(CONVOLUTIONAL_BLOCKS):
            x = residual_block(x, 2, ACTIVATION, filters=CONVOLUTIONAL_BLOCK_SIZE, kernel_size=(3, 3), strides=(1, 1),
                               padding="same", use_bias=True, kernel_initializer="glorot_normal")
            x = tensorflow.keras.layers.Dropout(RESIDUAL_BLOCK_DROPOUT_RATE)(x)

        x = tensorflow.keras.layers.Conv2D(filters=CONVOLUTIONAL_BLOCK_SIZE, kernel_size=(2, 2), strides=(2, 2),
                                           padding="valid", use_bias=True, kernel_initializer="glorot_normal")(x)
        x = tensorflow.keras.layers.BatchNormalization()(x)
        x = tensorflow.keras.layers.Activation(ACTIVATION)(x)
        x = tensorflow.keras.layers.Dropout(DOWNSAMPLING_DROPOUT_RATE)(x)

        x = tensorflow.keras.layers.Flatten()(x)
        x = tensorflow.keras.layers.Concatenate()([x, extra_input])

        for _ in range(DENSE_BLOCKS):
            x = dense_block(x, 2, ACTIVATION, units=DENSE_BLOCK_SIZE, use_bias=True, kernel_initializer="glorot_normal")
            x = tensorflow.keras.layers.Dropout(DENSE_BLOCK_DROPOUT_RATE)(x)

            x = tensorflow.keras.layers.Dense(DENSE_BLOCK_SIZE, use_bias=True, kernel_initializer="glorot_normal")(x)
            x = tensorflow.keras.layers.BatchNormalization()(x)
            x = tensorflow.keras.layers.Activation(ACTIVATION)(x)
            x = tensorflow.keras.layers.Dropout(DENSE_DROPOUT_RATE)(x)

        network_output = tensorflow.keras.layers.Dense(units=1, activation=tensorflow.keras.activations.tanh,
                                                       use_bias=True, kernel_initializer="glorot_normal")(x)

        network = tensorflow.keras.models.Model(inputs=[board_input, extra_input], outputs=network_output)

        if ON_TPU:
            OPTIMIZER = compile_optimizer_for_tpu(OPTIMIZER)

        network.compile(
            OPTIMIZER,
            loss=tensorflow.keras.losses.mse,
        )

    if ON_TPU:
        network = compile_model_for_tpu(network)

    network.summary()

    try:
        network.fit(
            x=[training_board_inputs, training_extra_inputs],
            y=training_outputs,
            epochs=2048,
            validation_split=0.01,
            batch_size=256,
            callbacks=[
                tensorflow.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=5, verbose=1,
                                                             mode='auto', min_delta=0, cooldown=0, min_lr=0),
                tensorflow.keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=10, verbose=1,
                                                         mode='auto', baseline=None, restore_best_weights=True)
            ],
            verbose=True
        )
    except KeyboardInterrupt:
        pass
    finally:
        network.save(SAVE_FILE)
