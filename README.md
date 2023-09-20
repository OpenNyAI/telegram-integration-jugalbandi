# Jugalbandi-Accelerator-Telegram-Bot

This is an accelerator pack for deploying a telegram bot which uses Jugalbandi APIs.

### Steps to install, run and deploy

1. After creating a telegram bot using BotFather in Telegram, copy the token of the newly created bot and replace it with this text <b>TELEGRAM_BOT_TOKEN_KEY</b> in telegram_bot.py
2. Replace the text <b>UUID_NUMBER</b> with the uuid number of your document set to be queried in telegram_bot.py
3. Currently the bot has configurations for 3 languages (English, Hindi, Kannada). The same can be updated for other Indian languages as well in the respective places.
4. The bot commands (start, set_language) can be customized by using BotFather in Telegram. In order to do that, go to BotFather and choose the bot to edit its command and paste the follow lines.
```
start - Start the bot
set_language - To choose language of your choice
```
5. Install the necessary python packages for this bot by running this command `pip install -r requirements.txt`
6. [OPTIONAL] Edit the url in get_query_response function in telegram.py to use other [Jugalbandi](https://api.jugalbandi.ai/docs) endpoints of your choice.
7. For running the bot in the local environment, run this command `python3 telegram_bot.py` and open the bot in Telegram to start querying.
8. To start querying the bot in Telegram, type `/start` to start the bot and choose the language from the given options. Then type the query in the language of your choice and the bot will respond with the answer.
9. [OPTIONAL] For deploying the bot as a service in cloud (eg: Compute Engine in GCP), <b>bot.service</b> file can be used as a template file.