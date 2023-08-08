import requests
import logging
from copy import deepcopy
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from telebot.types import (
    InlineKeyboardButton,
    Update,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Message,
)
from typing import Dict, Text, Any, List, Optional, Callable, Awaitable

from rasa.core.channels.channel import InputChannel, UserMessage, OutputChannel
from rasa.shared.constants import INTENT_MESSAGE_PREFIX
from rasa.shared.core.constants import USER_INTENT_RESTART
from rasa.shared.exceptions import RasaException

logger = logging.getLogger(__name__)


class TelegramOutput(TeleBot, OutputChannel):
    """Output channel for Telegram."""

    # skipcq: PYL-W0236
    @classmethod
    def name(cls) -> Text:
        return "telegram"

    def __init__(self, access_token: Optional[Text]) -> None:
        super().__init__(access_token)

    async def send_text_message(
        self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        for message_part in text.strip().split("\n\n"):
            self.send_message(recipient_id, message_part)

    async def send_image_url(
        self, recipient_id: Text, image: Text, **kwargs: Any
    ) -> None:
        self.send_photo(recipient_id, image)

    async def send_text_with_buttons(
        self,
        recipient_id: Text,
        text: Text,
        buttons: List[Dict[Text, Any]],
        button_type: Optional[Text] = "inline",
        **kwargs: Any,
    ) -> None:
        """Sends a message with keyboard.
        For more information: https://core.telegram.org/bots#keyboards
        :button_type inline: horizontal inline keyboard
        :button_type vertical: vertical inline keyboard
        :button_type reply: reply keyboard
        """
        if button_type == "inline":
            reply_markup = InlineKeyboardMarkup()
            button_list = [
                InlineKeyboardButton(s["title"], callback_data=s["payload"])
                for s in buttons
            ]
            reply_markup.row(*button_list)

        elif button_type == "vertical":
            reply_markup = InlineKeyboardMarkup()
            [
                reply_markup.row(
                    InlineKeyboardButton(s["title"], callback_data=s["payload"])
                )
                for s in buttons
            ]

        elif button_type == "reply":
            reply_markup = ReplyKeyboardMarkup(
                resize_keyboard=False, one_time_keyboard=True
            )
            # drop button_type from button_list
            button_list = [b for b in buttons if b.get("title")]
            for idx, button in enumerate(buttons):
                if isinstance(button, list):
                    reply_markup.add(KeyboardButton(s["title"]) for s in button)
                else:
                    reply_markup.add(KeyboardButton(button["title"]))
        else:
            logger.error(
                "Trying to send text with buttons for unknown "
                "button type {}".format(button_type)
            )
            return

        self.send_message(recipient_id, text, reply_markup=reply_markup)

    async def send_custom_json(
        self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        json_message = deepcopy(json_message)

        recipient_id = json_message.pop("chat_id", recipient_id)

        send_functions = {
            ("text",): "send_message",
            ("photo",): "send_photo",
            ("audio",): "send_audio",
            ("document",): "send_document",
            ("sticker",): "send_sticker",
            ("video",): "send_video",
            ("video_note",): "send_video_note",
            ("animation",): "send_animation",
            ("voice",): "send_voice",
            ("media",): "send_media_group",
            ("latitude", "longitude", "title", "address"): "send_venue",
            ("latitude", "longitude"): "send_location",
            ("phone_number", "first_name"): "send_contact",
            ("game_short_name",): "send_game",
            ("action",): "send_chat_action",
            (
                "title",
                "decription",
                "payload",
                "provider_token",
                "start_parameter",
                "currency",
                "prices",
            ): "send_invoice",
        }

        for params in send_functions.keys():
            if all(json_message.get(p) is not None for p in params):
                args = [json_message.pop(p) for p in params]
                api_call = getattr(self, send_functions[params])
                api_call(recipient_id, *args, **json_message)


class TelegramInput(InputChannel):
    """Telegram input channel"""

    @classmethod
    def name(cls) -> Text:
        return "telegram"

    @classmethod
    def from_credentials(cls, credentials: Optional[Dict[Text, Any]]) -> InputChannel:
        if not credentials:
            cls.raise_missing_credentials_exception()

        return cls(
            credentials.get("access_token"),
            credentials.get("verify"),
            credentials.get("webhook_url"),
        )

    def __init__(
        self,
        access_token: Optional[Text],
        verify: Optional[Text],
        webhook_url: Optional[Text],
        debug_mode: bool = True,
    ) -> None:
        self.access_token = access_token
        self.verify = verify
        self.webhook_url = webhook_url
        self.debug_mode = debug_mode

    @staticmethod
    def _is_location(message: Message) -> bool:
        is_location = message.location is not None

        if is_location:
            logger.info("Location shared by user id: {}".format(message.from_user.id))

        return is_location
            

    @staticmethod
    def _is_user_message(message: Message) -> bool:
        return message.text is not None

    @staticmethod
    def _is_edited_message(message: Update) -> bool:
        return message.edited_message is not None

    @staticmethod
    def _is_button(message: Update) -> bool:
        return message.callback_query is not None
    
    ###############################################################################
    
    #Revisa si el mensaje contiene una imagen comprobando si alguno de los métodos de
    #Telegram (foto, sticker y documento) para recibirla fue usado.
    @staticmethod
    def _is_image(message) -> bool:
        photo = message.photo
        sticker = message.sticker
        document = message.document
        
        is_image = False
        
        # Return true only when an image is recived, not stickers or documents
        if photo:
            logger.info("An image was recived with id {}".format(photo[-1].file_id))
            is_image = True
        if sticker:
            logger.info("A sticker was recived with id {}".format(sticker.file_id))
            is_image = False
        if document:
            mime_type = document.mime_type
            if "image" in mime_type:
                is_image = True
                logger.info("An image as document was recived with id {}".format(document.file_id))
            else:
                logger.info("A document was recived with id {}".format(document.file_id))
        
        return is_image
    
    # Obtiene el id de la imagen
    @staticmethod
    def _get_image_id(message):
        photo = message.photo
        sticker = message.sticker
        document = message.document
        
        if photo:
            return photo[-1].file_id #el -1 es para obtener la última, que es la de mayor resolución
        if sticker:
            return sticker.file_id
        if document:
            return document.file_id
        return ""
    
    # Obtiene el nombre de la imagen
    @staticmethod
    def _get_name(path):
        sp = path.rsplit("/", 1)
        return sp[1]
    
    #descarga la imagen en el path dado
    @staticmethod
    def _download_file(token, url, path):
        file = requests.get('https://api.telegram.org/file/bot' + token + '/' + url)
        with open(path, 'wb') as f:
            f.write(file.content)
    
    ###############################################################################
    
    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[Any]]
    ) -> Blueprint:
        telegram_webhook = Blueprint("telegram_webhook", __name__)
        out_channel = self.get_output_channel()

        @telegram_webhook.route("/", methods=["GET"])
        async def health(_: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @telegram_webhook.route("/set_webhook", methods=["GET", "POST"])
        async def set_webhook(_: Request) -> HTTPResponse:
            s = out_channel.setWebhook(self.webhook_url)
            if s:
                logger.info("Webhook Setup Successful")
                return response.text("Webhook setup successful")
            else:
                logger.warning("Webhook Setup Failed")
                return response.text("Invalid webhook")

        @telegram_webhook.route("/webhook", methods=["GET", "POST"])
        async def message(request: Request) -> Any:
            if request.method == "POST":

                request_dict = request.json
                update = Update.de_json(request_dict)
                if not out_channel.get_me().username == self.verify:
                    logger.debug("Invalid access token, check it matches Telegram")
                    return response.text("failed")

                if self._is_button(update):
                    msg = update.callback_query.message
                    text = update.callback_query.data
                elif self._is_edited_message(update):
                    msg = update.edited_message
                    
                    # The condition in placed because of live location updates
                    # which cause an exception by setting text->None
                    if update.edited_message.text:
                        text = update.edited_message.text
                        logger.info("An edited message was recived")
                    else:
                        text = "/live_location"
                        logger.info("An edited live location was recived")

                else:
                    msg = update.message

                    if self._is_user_message(msg):
                        text = msg.text.replace("/bot", "")
                    elif self._is_location(msg):
                        text = '/location{{"lng":{0}, "lat":{1}, "location_shared":true}}'.format(
                            msg.location.longitude, msg.location.latitude
                        )
                    elif self._is_image(msg):
                        #Use this method to get basic information about a file 
                        #and prepare it for downloading.
                        file_id = self._get_image_id(msg)
                        file = out_channel.get_file(file_id)
                        name = self._get_name(file.file_path)
                        self._download_file(self.access_token, file.file_path, "./images/" + name)
                        
                        text = ('/image{{"imagename":"{0}"}}'.format(name))
                    else:                        
                        return response.text("success")
                
                sender_id = msg.chat.id
                metadata = self.get_metadata(request)
                try:
                    if text == (INTENT_MESSAGE_PREFIX + USER_INTENT_RESTART):
                        await on_new_message(
                            UserMessage(
                                text,
                                out_channel,
                                sender_id,
                                input_channel=self.name(),
                                metadata=metadata,
                            )
                        )
                        await on_new_message(
                            UserMessage(
                                "/start",
                                out_channel,
                                sender_id,
                                input_channel=self.name(),
                                metadata=metadata,
                            )
                        )
                    else:
                        await on_new_message(
                            UserMessage(
                                text,
                                out_channel,
                                sender_id,
                                input_channel=self.name(),
                                metadata=metadata,
                            )
                        )
                except Exception as e:
                    logger.error(f"Exception when trying to handle message.{e}")
                    logger.debug(e, exc_info=True)
                    if self.debug_mode:
                        raise
                    pass

                return response.text("success")

        return telegram_webhook

    def get_output_channel(self) -> TelegramOutput:
        """Loads the telegram channel."""
        channel = TelegramOutput(self.access_token)

        try:
            channel.set_webhook(url=self.webhook_url)
        except ApiTelegramException as error:
            raise RasaException(
                "Failed to set channel webhook: " + str(error)
            ) from error

        return channel