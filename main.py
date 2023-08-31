import requests
import logging
import telegram
from typing import Final
import datetime as dt
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler


# API base address and key
BASE_URL : Final = "http://api.openweathermap.org/data/2.5/weather?appid="
API_KEY : Final = ""
# Bot token
BOT_TOKEN : Final = ""

# Recieving data from OpenWeather.com and organizing it for easier use
def weather_data(city: str):
    logger.info("Get request is being sent to OpenWeather ...")
    url = BASE_URL + API_KEY + "&q=" + city
    resp = requests.get(url).json()
    
    if resp['cod'] == 200:
        city_name = resp['name']
        country = resp['sys']['country']
        weather = resp['weather'][0]['description']
        temperature = round(resp['main']['temp'] -273.15, 0)
        temp_min = round(resp['main']['temp_min'] - 273.15, 0)
        temp_max = round(resp['main']['temp_max'] - 273.15, 0)
        feels_like = round(resp['main']['feels_like'] - 273.15, 0)
        pressure = resp['main']['pressure']
        humidity = resp['main']['humidity']
        wind_speed = resp['wind']['speed']
        timezone = resp['timezone']
        datetime = resp['dt'] + timezone
        sunrise = resp['sys']['sunrise'] + timezone
        sunset = resp['sys']['sunset'] + timezone
        cod = resp['cod']
        
        # Changing datatime to a readable version
        local_time = dt.datetime.utcfromtimestamp(datetime)
        local_sunrise = dt.datetime.utcfromtimestamp(sunrise)
        local_sunset = dt.datetime.utcfromtimestamp(sunset)
        
        # Calculating the day of the week
        num2weekday = {0:"Monday", 1:"Tuesday", 2:"Wednesday", 3:"Thursday", 4:"Friday",
                    5:"Saturday", 6:"Sunday"}
        weekday: str = num2weekday[local_time.weekday()]
        
        data = {}
        var_list = ["city_name", "country", "weather", "temperature", "temp_min",
                    "temp_max", "feels_like", "pressure", "humidity", "wind_speed",
                    "local_time", "local_sunrise", "local_sunset", "weekday", "cod"]
        
        # Generating a dictionary to work with variables easier
        for i in var_list:
            data[i] = eval(i)
        
        return data
    
    else:
        return "Wrong Input"


# Generating log
logging.basicConfig(format='%(levelname)s - (%(asctime)s) - %(message)s - (Line: %(lineno)d) - [%(filename)s]',
                    datefmt='%H:%M:%S',
                    encoding='utf-8',
                    level=logging.WARNING)

logger = logging.getLogger(__name__)



WEATHER, CLOSE, HELP = range(3)
INIT_ROUTES, ERROR, BRIEF_CITY, DETAILED_CITY, ALL_CITY = range(5)
BRIEF, DETAILED, ALL = range(3)


# Handles start message
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("App is started by user %s", update.effective_user)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to *WEATHER & TIME INFO* Bot\n\n"
             "If you want to see weather, time, humidity and so much more information "
             "about a city, select the *🌤 Weather* buttom.\n\n"
             "If you need more info about the bot, select the *❔Help* button.\n\n"
             "If you want say goodbye, select *👋🏼 Close* button.",
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🌤 Weather", callback_data="WEATHER")],
                [InlineKeyboardButton(text="❔Help", callback_data="HELP")],
                [InlineKeyboardButton(text="👋🏼 Close", callback_data="CLOSE")],
            ]
        )
    )
    return INIT_ROUTES


# Handles Weather option
async def weather_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("User selected the weather option")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Choose one of the options below:\n\n"
             "*Brief:* Shortest version. Just Time and Temperature.\n"
             "*Detailed:* More detailed than Brief. Includes Pressure and Humidity.\n"
             "*All:* All the info which is available at the moment.\n"
             "*👋🏼 Close:* Closing the bot.",
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
        reply_to_message_id=update.effective_message.id,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Brief", callback_data= "BRIEF")],
                [InlineKeyboardButton(text="Detailed", callback_data= "DETAILED")],
                [InlineKeyboardButton(text="All", callback_data= "ALL")],
                [InlineKeyboardButton(text="👋🏼 Close", callback_data="CLOSE")]
        ],
        ),
    )
    return INIT_ROUTES


async def brief_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("User requested brief option")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_to_message_id=update.effective_message.id,
        text="Awsome! You choosed *Brief* option. Now type the name of the city which you want."
             " For example Tokyo, Berlin, London, Toronto, ...",
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
    )
    return BRIEF_CITY


async def detailed_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("User requested detailed option")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_to_message_id=update.effective_message.id,
        text="Awsome! You choosed *Detailed* option. Now type the name of the city which you want."
             " For example Tokyo, Berlin, London, Toronto, ...",
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
    )
    return DETAILED_CITY


async def all_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("User requested all option")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_to_message_id=update.effective_message.id,
        text="Awsome! You choosed *All* option. Now type the name of the city which you want."
             " For example Tokyo, Berlin, London, Toronto, ...",
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
    )
    return ALL_CITY


async def brief_city_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("City is choosen ...")
    brief_city = str(update.message.text).lower().strip()
    city_data = weather_data(brief_city)
    
    if city_data == "Wrong Input":
        logger.warning("Error happened. Handling the error ...")
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Something went wrong ...\n"
             "It is most likely because you entered the name of your city WRONG!\n\n"
             "Please choose any of the options below to procced ...",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🌤 Weather", callback_data="WEATHER")],
                [InlineKeyboardButton(text="❔Help", callback_data="HELP")],
                [InlineKeyboardButton(text="👋🏼 Close", callback_data="CLOSE")],
                ]
            ),
        )
        return INIT_ROUTES
    
    elif city_data['cod'] == 200:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.effective_message.id,
            
            text=f"🌤 *{city_data['city_name']} - {city_data['country']}*\n\n"
                f"*📅 Local Date:* {city_data['weekday']} - {city_data['local_time'].date()}\n"
                f"*⏰ Local Time:* {str(city_data['local_time'].time())[:5]}\n\n"
                f"*☀️ Description:* {city_data['weather']}\n"
                f"*🌡 Temperature:* {city_data['temperature']} C\n",
                
            parse_mode=telegram.constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🌤 Weather Again!", callback_data="WEATHER")],
                    [InlineKeyboardButton(text="👋🏼 Close", callback_data="CLOSE")]
                ]
            ),
        )
        return INIT_ROUTES
    
    else:
        logger.warning("Some unmatched error happened. Handling the error")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Something went wrong ...\n"
                 "Please start the bot again."
        ),
        ConversationHandler.END 
  


async def detailed_city_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("City is choosen ...")
    detailed_city = str(update.message.text).lower().strip()
    city_data = weather_data(detailed_city)
    
    if city_data == "Wrong Input":
        logger.warning("Error happened. Handling the error ...")
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Something went wrong ...\n"
             "It is most likely because you entered the name of your city WRONG!\n\n"
             "Please choose any of the options below to procced ...",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🌤 Weather", callback_data="WEATHER")],
                [InlineKeyboardButton(text="❔Help", callback_data="HELP")],
                [InlineKeyboardButton(text="👋🏼 Close", callback_data="CLOSE")],
                ]
            ),
        )
        return INIT_ROUTES
        
    elif city_data['cod'] == 200:    
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.effective_message.id,
            
            text=f"🌤 *{city_data['city_name']} - {city_data['country']}*\n\n"
                f"*📅 Local Date:* {city_data['weekday']} - {city_data['local_time'].date()}\n"
                f"*⏰ Local Time:* {str(city_data['local_time'].time())[:5]}\n\n"
                f"*☀️ Description:* {city_data['weather']}\n"
                f"*🌡 Temperature:* {city_data['temperature']} C\n"
                f"*🌡 Feels Like:* {city_data['feels_like']} C\n"
                f"*💧 Humidity:* {city_data['humidity']}%\n"
                f"*🌬 Wind Speed:* {city_data['wind_speed']} m/s\n",
                
            parse_mode=telegram.constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🌤 Weather Again!", callback_data="WEATHER")],
                    [InlineKeyboardButton(text="👋🏼 Close", callback_data="CLOSE")]
                ]
            ),
        )
        return INIT_ROUTES

    else:
        logger.warning("Some unmatched error happened. Handling the error")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Something went wrong ...\n"
                 "Please start the bot again."
        ),
        ConversationHandler.END 
          
    


async def all_city_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("City is choosen ...")
    all_city = str(update.message.text).lower().strip()
    city_data = weather_data(all_city)
    
    if city_data == "Wrong Input":
        logger.warning("Error happened. Handling the error ...")
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Something went wrong ...\n"
             "It is most likely because you entered the name of your city WRONG!\n\n"
             "Please choose any of the options below to procced ...",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🌤 Weather", callback_data="WEATHER")],
                [InlineKeyboardButton(text="❔Help", callback_data="HELP")],
                [InlineKeyboardButton(text="👋🏼 Close", callback_data="CLOSE")],
                ]
            ),
        )
        return INIT_ROUTES
        
    elif city_data['cod'] == 200:    
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.effective_message.id,
            
            text=f"🌤 *{city_data['city_name']} - {city_data['country']}*\n\n"
                f"*📅 Local Date:* {city_data['weekday']} - {city_data['local_time'].date()}\n"
                f"*⏰ Local Time:* {str(city_data['local_time'].time())[:5]}\n"
                f"*🌄 Sunrise Time:* {str(city_data['local_sunrise'].time())[:5]}\n"
                f"*🌇 Sunset Time:* {str(city_data['local_sunset'].time())[:5]}\n\n"
                f"*☀️ Description:* {city_data['weather']}\n"
                f"*🌡 Temperature:* {city_data['temperature']} C\n"
                f"*🌡 Feels Like:* {city_data['feels_like']} C\n"
                f"*🌡 Max Temperature:* {city_data['temp_max']} C\n"
                f"*🌡 Min Temperature:* {city_data['temp_min']} C\n"
                f"*💧 Humidity:* {city_data['humidity']}%\n"
                f"*🌬 Wind Speed:* {city_data['wind_speed']} m/s\n"
                f"*🅿️ Pressure:* {city_data['pressure']} kPa\n",
                
            parse_mode=telegram.constants.ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🌤 Weather Again!", callback_data="WEATHER")],
                    [InlineKeyboardButton(text="👋🏼 Close", callback_data="CLOSE")]
                ]
            ),
        )
        return INIT_ROUTES  
    
    else:
        logger.warning("Some unmatched error happened. Handling the error")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Something went wrong ...\n"
                 "Please start the bot again."
        ),
        ConversationHandler.END   
    
     

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("User selected Help option ...")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="*WEATHER AND TIME INFO* Bot is created by μohammad as the final "
        "project for Quera LevelUp course for developing a Telegram bot.\n\n"
        "With selecting the * 🌤 Weather* bottom you can type any major city "
        "and receive useful information or filter the info which you want.\n\n"
        "Choose *👋🏼 Close* button to exit the bot.",
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
        reply_to_message_id=update.effective_message.id,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🌤 Weather", callback_data="WEATHER")],
                [InlineKeyboardButton(text="👋🏼 Close", callback_data="CLOSE")],
            ],
        ),
    )
    return INIT_ROUTES


async def close_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Closing ...")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Thank you and goodbye!",
    )
    return ConversationHandler.END


if __name__ == "__main__":
    logger.warning("Bot Starting ...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("start", start_handler)],
            states={
                INIT_ROUTES: [
                    CallbackQueryHandler(weather_handler, pattern=f"^WEATHER$"),
                    CallbackQueryHandler(help_handler, pattern=f"^HELP$"),
                    CallbackQueryHandler(close_handler, pattern=f"^CLOSE$"),
                    CallbackQueryHandler(brief_handler, pattern=f"^BRIEF$"),
                    CallbackQueryHandler(detailed_handler, pattern=f"^DETAILED$"),
                    CallbackQueryHandler(all_handler, pattern=f"^ALL$"),
                ],
                BRIEF_CITY: [
                    MessageHandler(filters.TEXT, brief_city_handler)
                ],
                DETAILED_CITY: [
                    MessageHandler(filters.TEXT, detailed_city_handler)
                ],
                ALL_CITY: [
                    MessageHandler(filters.TEXT, all_city_handler)
                ],
                ERROR: []
            },
            fallbacks=[CallbackQueryHandler(close_handler)],
            allow_reentry=True,
        ),
    )
    
    logger.warning("Pooling Started ...")
    app.run_polling()
