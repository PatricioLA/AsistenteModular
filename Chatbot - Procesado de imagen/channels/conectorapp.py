#from flask import Flask, request, jsonify
#import requests

#app = Flask(conectorapp)
#rasa_server_url = 'http://localhost:5055/webhooks/rest/webhook'#http://localhost:5005/webhooks/mobile_app/webhook'

#@app.route('/messages', methods=['POST'])
#def handle_message():
#    message = request.json['message']

#Enviar el mensaje al servidor Rasa utilizando el canal personalizado
#    rasa_response = requests.post(rasa_server_url, json={'message': message}).json()

#    return jsonify(rasa_response)

#if conectorapp == 'main':
#    app.run(host='0.0.0.0', port=5005)

from typing import Text, Dict, Any
from rasa.core.channels.channel import InputChannel
from rasa.core.channels.channel import OutputChannel
from rasa.core.channels.channel import UserMessage
from sanic import Blueprint, response
from sanic.request import Request

class CustomChannel(InputChannel):
    @classmethod
    def name(cls) -> Text:
        return "custom"  # Nombre del canal personalizado

    @staticmethod
    def process_message(request: Request) -> Dict[Text, Any]:
        # Implementa el procesamiento de la imagen aquí
        # Accede a la imagen enviada desde la solicitud (request) y realiza el procesamiento necesario
        # Puedes utilizar librerías como Pillow para manipular la imagen
        # Devuelve un diccionario con los datos relevantes de la imagen
        file = request.files.get("file")
        image_path = "/path/to/save/image.jpg"  # Ruta donde deseas guardar la imagen
        file.save(image_path)
        image_data = {
            "image_path": image_path,
            "image_name": file.name,
            "image_type": file.type,
        }
        return image_data

    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:
        custom_webhook = Blueprint("custom_webhook", __name__)

        @custom_webhook.route("/", methods=["POST"])
        async def receive(request: Request) -> response.HTTPResponse:
            data = self.process_message(request)
            metadata = self.get_metadata(request)
            user_message = UserMessage(data.get("message"), output_channel, metadata)
            await on_new_message(user_message)
            return response.json({"status": "success"})

        return custom_webhook