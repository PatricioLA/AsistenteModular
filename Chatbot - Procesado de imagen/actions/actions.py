from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import testModel

from keras.applications.imagenet_utils import preprocess_input
from keras.models import load_model

import numpy as np
import cv2
import matplotlib.pyplot as plt

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
        
        first_name = tracker.get_slot("first_name")
        if len(first_name) + len(slot_value) < 6:
            dispatcher.utter_message(text="That's a very short name. We fear a typo. Restarting!")
            return {"first_name": None, "last_name": None}
        dispatcher.utter_message(text=f"My bien, tu apellido es {slot_value}.")
        return {"last_name": slot_value}

    def validate_location_report(
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
        if len(slot_value) < 10:
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

        # Get slots for the report
        imagename = tracker.get_slot('imagename')
        image_path = "./images/" + imagename

        width_shape = 224
        height_shape = 224
        names = ['congrafiti','singrafiti']
        modelt = load_model("model-IA/model-v1.h5")


        imaget=cv2.resize(cv2.imread(image_path), (width_shape, height_shape), interpolation = cv2.INTER_AREA)

        xt = np.asarray(imaget)
        xt=preprocess_input(xt)
        xt = np.expand_dims(xt,axis=0)

        preds = modelt.predict(xt)
        if names[np.argmax(preds)] == 'congrafiti':
            dispatcher.utter_message("✅ Su imagen fue catalogada como un graffiti.")
                    
        else:
            dispatcher.utter_message("❌ Lo siento, su imagen no fue catalogada como un graffiti")
            
        return []



