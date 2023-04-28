# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 08:53:52 2020
@author: dreve
"""

from keras.applications.imagenet_utils import preprocess_input
from keras.models import load_model

import numpy as np
import cv2
import matplotlib.pyplot as plt


width_shape = 224
height_shape = 224


names = ['congrafiti','singrafiti']


modelt = load_model("models/model.h5")

print("Modelo cargado exitosamente")

imaget_path = "ImagenPrueba.jpeg"
imaget=cv2.resize(cv2.imread(imaget_path), (width_shape, height_shape), interpolation = cv2.INTER_AREA)

xt = np.asarray(imaget)
xt=preprocess_input(xt)
xt = np.expand_dims(xt,axis=0)

print("Predicción")
preds = modelt.predict(xt)

print("Predicción:", names[np.argmax(preds)])
plt.imshow(cv2.cvtColor(np.asarray(imaget),cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.show()