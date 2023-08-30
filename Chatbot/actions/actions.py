from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet

from keras.applications.imagenet_utils import preprocess_input
from keras.models import load_model

import numpy as np
import cv2
import matplotlib.pyplot as plt
import requests
import mimetypes
import re

import os
import requests
import json

import base64


flask_url = "http://localhost:5000"

#def clean_name(name):
#    return "".join([c for c in name if c.isalpha()])

class ValidateReportForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_report_form"

    def validate_first_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `first_name` value."""
        # If the name is super short, it might be wrong.
#        name = clean_name(slot_value)
#        if len(name) < 3:
        if len(slot_value) < 3:
            dispatcher.utter_message(text="That must've been a typo.")
            return {"first_name": None}
#        return {"first_name": name}
        dispatcher.utter_message(text=f"OK! Tu nombre es {slot_value}.")
        return {"first_name": slot_value}

    def validate_last_name(    
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `last_name` value."""

        # If the name is super short, it might be wrong.
#        name = clean_name(slot_value)
        if len(slot_value) < 3:
            dispatcher.utter_message(text="That must've been a typo.")
            return {"last_name": None}
        dispatcher.utter_message(text=f"My bien, tu apellido es {slot_value}.")
        return {"last_name": slot_value}

    def validate_location_report(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `location_report` value."""

        # If the name is super short, it might be wrong.
#        name = clean_name(slot_value)
#        if len(name) < 3:
        if len(slot_value) < 5:
            dispatcher.utter_message(text="That must've been a typo.")
            return {"location_report": None}
#        return {"first_name": name}
        return {"location_report": slot_value}


    def validate_imagename(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        
        imagename = tracker.get_slot('imagename')
        channel = tracker.get_latest_input_channel()
        if channel == 'telegram':
            #image_path = "./images/" +  imagename
            pattern = 'file_\w+\.jpg' # Define la expresión regular
            match = re.search(pattern, imagename) # Busca la primera coincidencia
            if match: # Si hay una coincidencia
                imagename = match.group()
            #if type(imagename) == dict:
            #    imagename = imagename.value
                imageDirectory = "./images/{}".format(imagename)
        elif channel == 'rest':
            image_json_str = tracker.get_slot("imagename")
            # Convertir la cadena JSON en un objeto Python (diccionario en este caso)
            image_data = json.loads(image_json_str)
    
            # Acceder al valor "base64" en el diccionario resultante y decodificarlo
            decoded_image_data = base64.b64decode(image_data["base64"])
    
            # Define el nombre de archivo específico
            image_filename = "image.jpg"  # Cambia el nombre según lo necesario
    
            # Directorio donde guardarás las imágenes
            save_directory = "./images/"
    
            # Crea el directorio si no existe
            os.makedirs(save_directory, exist_ok=True)
    
            # Guarda la imagen en el directorio
            image_path = os.path.join(save_directory, image_filename)
            with open(image_path, "wb") as f:
                f.write(decoded_image_data)
            #except Exception as e:
            #        dispatcher.utter_message(text="Error al guardar la imagen: {}".format(str(e)))
                imageDirectory = "./images/image.jpg"

        width_shape = 224
        height_shape = 224
        names = ['congrafiti','singrafiti']
        modelt = load_model("model-IA/model-v1.h5")


        imaget=cv2.resize(cv2.imread(imageDirectory), (width_shape, height_shape), interpolation = cv2.INTER_AREA)

        xt = np.asarray(imaget)
        xt=preprocess_input(xt)
        xt = np.expand_dims(xt,axis=0)

        preds = modelt.predict(xt)
        if names[np.argmax(preds)] == 'congrafiti':
            dispatcher.utter_message("✅ Su imagen fue catalogada como un graffiti.")
                    
        else:
            dispatcher.utter_message("❌ Lo siento, su imagen no fue catalogada como un graffiti")

        #ubicacion = tracker.get_slot("location_report")
        
        with open(imageDirectory, 'rb') as f:
            photo = f.read()
        photo_base64 = base64.b64encode(photo)
        photo_json = photo_base64.decode('ascii') 
        data = {"first_name": tracker.get_slot("first_name"), "last_name": tracker.get_slot("last_name"), "location_report": tracker.get_slot("location_report") , "imagename": photo_json}
        response = requests.post(flask_url + "/add_contact", json=data)
        if response.status_code == 200:
            # Mostrar un mensaje de confirmación al usuario
            dispatcher.utter_message(text="Datos enviados correctamente")
        else:
            # Mostrar un mensaje de error al usuario
            dispatcher.utter_message(text="Ocurrió un problema al enviar los datos")

        os.remove(imageDirectory)


        return []
    
    '''
            channel = tracker.get_latest_input_channel()
        if channel == 'telegram':
            imagename = tracker.get_slot('imagename')
            #image_path = "./images/" +  imagename
            pattern = 'file_\w+\.jpg' # Define la expresión regular
            match = re.search(pattern, imagename) # Busca la primera coincidencia
            if match: # Si hay una coincidencia
                imagename = match.group()
            #if type(imagename) == dict:
            #    imagename = imagename.value
                imageDirectory = "./images/{}".format(imagename)
        elif channel == 'rest':
            file = tracker.latest_message['file']
            image = base64.b64decode(file)
            with open('./images/image.jpg', 'wb') as f:
                f.write(image)    
            imageDirectory = "./images/image.jpg"
    '''
'''        first_name = tracker.get_slot("first_name")
        last_name = tracker.get_slot("last_name")
        location_report = tracker.get_slot("location_report")
        imagename = tracker.get_slot("imagename")'''

"        app.add_data(first_name, last_name, location_report, imagename)"
'''conn = mysql.connector.connect(
            host="LeCuack",
            user="rasaserver",
            password="Rasa#2023",
            database="rasa"
        )
        cursor = conn.cursor()

        cursor.execute(f"INSERT INTO report (firstName, lastName, location, image) VALUES ('{first_name}', '{last_name}', '{location_report}', '{imagename}')")
        conn.commit()
        
        dispatcher.utter_message('✅ Su reporte ha sio registrado en nuestra base de datos.')
        cursor.close()
        conn.close()
        return []
'''  
'''   def validate_location_report(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `first_name` value."""

        # If the name is super short, it might be wrong.
#        name = clean_name(slot_value)
#        if len(name) < 3:
        ubicacion = tracker.get_slot("ubicacion")
        if len(slot_value) < 10:
            dispatcher.utter_message(text="That must've been a typo.")
            return {"location_report": None}
#        return {"first_name": name}
        return {"location_report": slot_value}
'''   

'''
         # Get slots for the report
        file_url = tracker.latest_message['attachment']
        response = requests.get(file_url)
        mime_type = mimetypes.guess_type(file_url)[0]
        if mime_type == "image/jpeg":
            with open("images/user_image.jpg", "wb") as f:
                f.write(response.content)

'''

