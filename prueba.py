import pandas as pd
import numpy as np
import os
import tensorflow as tf
import keras
import matplotlib.pyplot as plt
from keras.layers import Dense,GlobalAveragePooling2D
#from keras.applications import MobileNet
from keras.applications.mobilenet import MobileNet
from keras.preprocessing import image
from keras.applications.mobilenet import preprocess_input
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Model
#from keras.optimizers import Adam
from tensorflow.keras.optimizers import Adam

base_model=MobileNet(weights='imagenet',include_top=False)

x=base_model.output
x=GlobalAveragePooling2D()(x) 
x=Dense(256,activation='relu')(x) 
x=Dense(64,activation='relu')(x) 
preds=Dense(2, activation='softmax')(x)

model=Model(inputs=base_model.input, outputs=preds)
print(model.summary())

for layer in model.layers[:-5]:
    layer.trainable=False
for layer in model.layers[-5:]:
    layer.trainable=True

train_datagen=ImageDataGenerator(zoom_range=0.2, horizontal_flip=True,
                                 width_shift_range=0.2,
                                 height_shift_range=0.2,
                                 preprocessing_function=preprocess_input)

train_generator=train_datagen.flow_from_directory('./train/',
                                                 target_size=(224,224),
                                                 color_mode='rgb',
                                                 batch_size=32,
                                                 class_mode='categorical',
                                                 shuffle=True)

test_datagen=ImageDataGenerator(zoom_range=0.2, horizontal_flip=True,
                                 width_shift_range=0.2,
                                 height_shift_range=0.2,
                                 preprocessing_function=preprocess_input)

test_generator=train_datagen.flow_from_directory('./test/',
                                                 target_size=(224,224),
                                                 color_mode='rgb',
                                                 batch_size=20,
                                                 class_mode='categorical',
                                                 shuffle=True)

model.compile(optimizer='Adam',loss='categorical_crossentropy',
              metrics=['accuracy'])

step_size_train=train_generator.n//train_generator.batch_size

model.fit_generator(generator=train_generator,
                    steps_per_epoch=step_size_train,
                    epochs=6,
                    validation_data=test_generator,
                    validation_steps=1)

model.save('model.h5')