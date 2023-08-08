
from typing import Text, Dict, Any, Callable, Awaitable
import os
import uuid
from rasa.core.channels.channel import InputChannel
from rasa.core.channels.channel import UserMessage
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse

class ImageChannel(InputChannel):
    @classmethod
    def name(cls) -> Text:
        return "image"

    def init(self, *args: Any, **kwargs: Any) -> None:
        super().init(*args, **kwargs)

    async def process_message(
        self, request: Request
    ) -> Dict[Text, Any]:
        rasa_request = await request.json()
        file = request.files.get('file')

        if file:
            filename = f"{uuid.uuid4().hex}.jpg"  # Genera un nombre único para el archivo
            file.save(os.path.join("images", filename))  # Guarda el archivo en la carpeta "images"
            rasa_request["image"] = filename

        return rasa_request

    @staticmethod
    async def health(request: Request) -> HTTPResponse:
        return response.text("Healthy")

    @staticmethod
    def blueprint(
        on_new_message: Callable[[UserMessage], Awaitable[Any]]
    ) -> Blueprint:
        custom_webhook = Blueprint("custom_webhook", __name__)

        @custom_webhook.route("/", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            sender_id = request.json.get("sender", None)
            text = request.json.get("message", None)

            if text:
                message = UserMessage(text, sender_id=sender_id)
                await on_new_message(message)

            return response.text("success")

        @custom_webhook.route("/health", methods=["GET"])
        async def health(request: Request) -> HTTPResponse:
            return await ImageChannel.health(request)

        return custom_webhook