import logging
import urllib
from typing import Union, TypedDict
import requests
from telegram import __version__ as TG_VER
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler
)

"""
Commands to use in the bot
start - Start the bot
set_language - To choose language of your choice
"""

uuid_number = "UUID_NUMBER"
bot = Bot(token="TELEGRAM_BOT_TOKEN_KEY")

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class ApiResponse(TypedDict):
    query: str
    answer: str
    source_text: str


class ApiError(TypedDict):
    error: Union[str, requests.exceptions.RequestException]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_name = update.message.chat.first_name
    welcome_message = (
        f"Hi {user_name}, Welcome to the <CUSTOM_NAME> bot, "
        "your friendly AI powered bot to answer your queries. "
        "Please be advised not to take these AI generated responses as "
        "standard/correct information. Always consult with the concerned "
        "personnel for availing relevant information."
    )
    await bot.send_message(chat_id=update.effective_chat.id,
                           text=welcome_message)
    await relay_handler(update, context)


async def relay_handler(update: Update, context: CallbackContext):
    await language_handler(update, context)


async def language_handler(update: Update, context: CallbackContext):
    english_button = InlineKeyboardButton('English', callback_data='lang_English')
    hindi_button = InlineKeyboardButton('हिंदी', callback_data='lang_Hindi')
    kannada_button = InlineKeyboardButton('ಕನ್ನಡ', callback_data='lang_Kannada')

    inline_keyboard_buttons = [[english_button], [hindi_button], [kannada_button]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard_buttons)

    await bot.send_message(chat_id=update.effective_chat.id, text="Choose a Language:", reply_markup=reply_markup)


async def preferred_language_callback(update: Update, context: CallbackContext):
    callback_query = update.callback_query
    preferred_language = callback_query.data.lstrip('lang_')
    context.user_data['language'] = preferred_language

    text_message = ""
    if preferred_language == "English":
        text_message = "You have chosen English. \nPlease give your query now"
    elif preferred_language == "Hindi":
        text_message = "आपने हिंदी चुना है। \nआप अपना सवाल अब हिंदी में पूछ सकते हैं।"
    elif preferred_language == "Kannada":
        text_message = "ಕನ್ನಡ ಆಯ್ಕೆ ಮಾಡಿಕೊಂಡಿದ್ದೀರಿ. \nದಯವಿಟ್ಟು ಈಗ ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ನೀಡಿ"

    await bot.send_message(chat_id=update.effective_chat.id, text=text_message)


async def get_query_response(query: str, voice_message_url: str, voice_message_language: str) -> Union[ApiResponse, ApiError]:
    try:
        if voice_message_url is None:
            if voice_message_language == "English":
                query_engine_route = 'query-with-langchain-gpt4'
                params = {
                    'uuid_number': uuid_number,
                    'query_string': query,
                }

                url = f'https://api.jugalbandi.ai/{query_engine_route}?' \
                      + urllib.parse.urlencode(params)
            else:
                params = {
                    'uuid_number': uuid_number,
                    'query_text': query,
                    'audio_url': "",
                    'input_language': voice_message_language,
                    'output_format': 'Text',
                }
                url = 'https://api.jugalbandi.ai/query-using-voice-gpt4?' \
                      + urllib.parse.urlencode(params)
        else:
            params = {
                'uuid_number': uuid_number,
                'audio_url': voice_message_url,
                'input_language': voice_message_language,
                'output_format': 'Voice',
            }
            url = 'https://api.jugalbandi.ai/query-using-voice-gpt4?' \
                  + urllib.parse.urlencode(params)

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return {'error': e}
    except (KeyError, ValueError):
        return {'error': 'Invalid response received from API'}


async def response_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await query_handler(update, context)


async def query_handler(update: Update, context: CallbackContext):
    voice_message_language = context.user_data.get('language')
    voice_message = None
    query = None

    if update.message.text:
        query = update.message.text
    elif update.message.voice:
        voice_message = update.message.voice

    voice_message_url = None
    if voice_message is not None:
        voice_file = await voice_message.get_file()
        voice_message_url = voice_file.file_path

    text_message = ""
    if voice_message_language == "English":
        text_message = "Thank you, allow me to search for the best information to respond to your query."
    elif voice_message_language == "Hindi":
        text_message = "शुक्रीया। मैं आपके प्रश्न के लिए सही जानकरी ढूंढ रही हूं।"
    elif voice_message_language == "Kannada":
        text_message = "ಧನ್ಯವಾದ. ನಾನು ಉತ್ತಮ ಮಾಹಿತಿಯನ್ನು ಕಂಡುಕೊಳ್ಳುವವರೆಗೆ ದಯವಿಟ್ಟು ನಿರೀಕ್ಷಿಸಿ"

    await bot.send_message(chat_id=update.effective_chat.id, text=text_message)
    await handle_query_response(update, query, voice_message_url, voice_message_language)


async def handle_query_response(update: Update, query: str, voice_message_url: str, voice_message_language: str):
    response = await get_query_response(query, voice_message_url, voice_message_language)
    if "error" in response:
        await bot.send_message(chat_id=update.effective_chat.id,
                               text='An error has been encountered. Please try again.')
        print(response)
    else:
        answer = response['answer']
        await bot.send_message(chat_id=update.effective_chat.id, text=answer)

        if 'audio_output_url' in response:
            audio_output_url = response['audio_output_url']
            if audio_output_url != "":
                audio_request = requests.get(audio_output_url)
                audio_data = audio_request.content
                await bot.send_voice(chat_id=update.effective_chat.id,
                                     voice=audio_data)


def main() -> None:
    application = ApplicationBuilder().bot(bot).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler('set_language', language_handler))

    application.add_handler(CallbackQueryHandler(preferred_language_callback, pattern=r'lang_\w*'))

    application.add_handler(MessageHandler(filters.TEXT | filters.VOICE, response_handler))

    application.run_polling()


if __name__ == "__main__":
    main()
