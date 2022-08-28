from django.apps import AppConfig
from django.conf import settings

import tensorflow as tf
from tensorflow import keras
import os
import urllib.request
import requests

from tensorflow.keras import layers
from tensorflow.keras import Model, Input
from tensorflow.keras.applications.inception_resnet_v2 import InceptionResNetV2
from tensorflow.keras.applications.densenet import DenseNet201
from tensorflow.keras.applications import EfficientNetB4, EfficientNetB6
from tensorflow.keras.optimizers import Adam


class ApiConfig(AppConfig):
    name = 'api'

    input_shape = (192, 256, 3)
    model_input = Input(shape=input_shape)

    # EfficientNet B4
    # --------------------------------------------------
    efficientNet = EfficientNetB4(
        input_shape=input_shape, input_tensor=model_input, include_top=False, weights=None)

    for layer in efficientNet.layers:
        layer.trainable = True

    efficientNet_last_layer = efficientNet.get_layer('top_activation')
    # print('last layer output shape:', efficientNet_last_layer.output_shape)
    efficientNet_last_output = efficientNet_last_layer.output

    x_efficientNet = layers.GlobalMaxPooling2D()(efficientNet_last_output)
    x_efficientNet = layers.Dense(512, activation='relu')(x_efficientNet)
    x_efficientNet = layers.Dropout(0.5)(x_efficientNet)
    x_efficientNet = layers.Dense(2, activation='softmax')(x_efficientNet)

    efficientNet_model = Model(model_input, x_efficientNet)
    optimizer = Adam(lr=0.0001, beta_1=0.9, beta_2=0.999,
                     epsilon=None, decay=0.0, amsgrad=True)
    efficientNet_model.compile(loss='categorical_crossentropy',
                               optimizer=optimizer,
                               metrics=['accuracy'])
    print("EfficientNet B4 Loaded ...")
    # --------------------------------------------------

    # EfficientNet B6
    # --------------------------------------------------
    efficientNetB6 = EfficientNetB6(
        input_shape=input_shape, input_tensor=model_input, include_top=False, weights=None)

    for layer in efficientNetB6.layers:
        layer.trainable = True

    efficientNetB6_last_layer = efficientNetB6.get_layer('top_activation')
    # print('last layer output shape:', efficientNetB6_last_layer.output_shape)
    efficientNetB6_last_output = efficientNetB6_last_layer.output

    x_efficientNetB6 = layers.GlobalMaxPooling2D()(efficientNetB6_last_output)
    x_efficientNetB6 = layers.Dense(512, activation='relu')(x_efficientNetB6)
    x_efficientNetB6 = layers.Dropout(0.5)(x_efficientNetB6)
    x_efficientNetB6 = layers.Dense(2, activation='softmax')(x_efficientNetB6)

    efficientNetB6_model = Model(model_input, x_efficientNetB6)
    optimizer = Adam(lr=0.0001, beta_1=0.9, beta_2=0.999,
                     epsilon=None, decay=0.0, amsgrad=True)
    efficientNetB6_model.compile(loss='categorical_crossentropy',
                                 optimizer=optimizer,
                                 metrics=['accuracy'])
    for i, layer in enumerate(efficientNetB6_model.layers):
        layer._name = 'layer_' + str(i) + '_' + layer._name

    print("EfficientNet B6 Loaded ...")
    # --------------------------------------------------

    # DenseNet201
    # --------------------------------------------------
    denseNet = DenseNet201(input_shape=input_shape,
                           input_tensor=model_input, include_top=False, weights=None)

    for layer in denseNet.layers:
        layer.trainable = True

    denseNet_last_layer = denseNet.get_layer('relu')
    # print('last layer output shape:', denseNet_last_layer.output_shape)
    denseNet_last_output = denseNet_last_layer.output

    x_denseNet = layers.GlobalMaxPooling2D()(denseNet_last_output)
    x_denseNet = layers.Dense(512, activation='relu')(x_denseNet)
    x_denseNet = layers.Dropout(0.5)(x_denseNet)
    x_denseNet = layers.Dense(2, activation='softmax')(x_denseNet)

    denseNet_model = Model(model_input, x_denseNet)
    optimizer = Adam(lr=0.0001, beta_1=0.9, beta_2=0.999,
                     epsilon=None, decay=0.0, amsgrad=True)
    denseNet_model.compile(loss='categorical_crossentropy',
                           optimizer=optimizer,
                           metrics=['accuracy'])
    print("DenseNet201 Loaded ...")
    # --------------------------------------------------

    # InceptionResNetV2
    # --------------------------------------------------
    inception = InceptionResNetV2(
        input_shape=input_shape, input_tensor=model_input, include_top=False, weights=None)

    for layer in inception.layers:
        layer.trainable = True

    inception_last_layer = inception.get_layer('conv_7b_ac')
    inception_last_output = inception_last_layer.output

    x_inception = layers.GlobalMaxPooling2D()(inception_last_output)
    x_inception = layers.Dense(512, activation='relu')(x_inception)
    x_inception = layers.Dropout(0.5)(x_inception)
    x_inception = layers.Dense(2, activation='softmax')(x_inception)

    inception_model = Model(model_input, x_inception)
    optimizer = Adam(lr=0.0001, beta_1=0.9, beta_2=0.999,
                     epsilon=None, decay=0.0, amsgrad=True)
    inception_model.compile(loss='categorical_crossentropy',
                            optimizer=optimizer,
                            metrics=['accuracy'])
    print("InceptionResNetV2 Loaded ...")
    # --------------------------------------------------

    models = [inception_model, denseNet_model,
              efficientNet_model, efficientNetB6_model]
    outputs = [model.outputs[0] for model in models]
    y = layers.Average()(outputs)
    ensemble_model = Model(model_input, y, name='ensemble')

    optimizer = Adam(learning_rate=0.0001, beta_1=0.9, beta_2=0.999,
                     epsilon=None, decay=0.0, amsgrad=True)

    ensemble_model.compile(loss='categorical_crossentropy',
                           optimizer=optimizer,
                           metrics=['accuracy'])

    print("ENVIRONMENT: ", os.getenv('USER'))

    # Print files inside the models directory
    onlyfiles = [f for f in os.listdir(settings.BASE_DIR + settings.STATIC_URL)
                 if os.path.isfile(os.path.join(settings.BASE_DIR + settings.STATIC_URL, f))]
    print("Models Directory", onlyfiles)

    print('Running on Local Machine')
    MODEL_PATH = settings.BASE_DIR + settings.STATIC_URL + "ensemble_model.h5"
    ensemble_model.load_weights(MODEL_PATH)
    print("Model loaded from disk")

    print("Tensorflow Version", tf.__version__)
    model = ensemble_model
    print("Ensemble Model loaded")
