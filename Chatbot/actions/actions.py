from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

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



