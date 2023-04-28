from __future__ import division, print_function

import pandas as pd
import numpy as np
import os

import cv2

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

from keras.applications.imagenet_utils import preprocess_input

#from keras.optimizers import Adam
from tensorflow.keras.optimizers import Adam

# Flask 
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename

#model = keras.models.load_model('model.h5')


width_shape = 224
height_shape = 224

names = ['congrafiti','singrafiti']

# Definimos una instancia de Flask
app = Flask(__name__)

# Path del modelo preentrenado
#MODEL_PATH = './model.h5'

# Cargamos el modelo preentrenado
#model = keras.models.load_model(MODEL_PATH)
model = keras.models.load_model('models/model.h5')

print('Modelo cargado exitosamente. Verificar http://127.0.0.1:5000/')

# Realizamos la predicción usando la imagen cargada y el modelo
def model_predict(img_path, model):

    img=cv2.resize(cv2.imread(img_path), (width_shape, height_shape), interpolation = cv2.INTER_AREA)
    x=np.asarray(img)
    x=preprocess_input(x)
    x = np.expand_dims(x,axis=0)
    
    preds = model.predict(x)
    return preds


@app.route('/', methods=['GET'])
def index():
    # Página principal
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Obtiene el archivo del request
        f = request.files['file']

        # Graba el archivo en ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Predicción
        preds = model_predict(file_path, model)

        print('PREDICCIÓN', names[np.argmax(preds)])
        
        # Enviamos el resultado de la predicción
        result = str(names[np.argmax(preds)])              
        return result
    return None


if __name__ == '__main__':
    app.run(debug=False, threaded=False)
