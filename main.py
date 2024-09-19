import telebot
import os
import ffmpeg
from gtts import gTTS
from duckduckgo_search import DDGS
from datetime import datetime
from telebot import types
# from telebot.util import quick_markup
import speech_recognition as sr
from ytmusicapi import YTMusic
from dotenv import load_dotenv
# from pyfiglet import Figlet

# Init
load_dotenv()
BOT = {
    "username": "b_alfredbot",
    "name": "Butler Alfred",
    "token": os.getenv("TOKEN"),
    "architect": {
        "name": "tcitrogg",
        "link": "https://linktr.ee/tcitrogg"
    }
}
bot = telebot.TeleBot(BOT["token"], parse_mode="Markdown")
r = sr.Recognizer()
ytmusic = YTMusic()
# speech_eng = pyttsx4.init()
# f = Figlet(font="graffiti")
AUDIOPATH = "audio"


# - Functions
# AI Chat w/ DuckDuckGo
def chat(text: str) -> str:
    result = DDGS().chat(text)
    return result

# Convert audio from OGG -> WAV
def ogg_to_wav(audiofile:str):
    new_filename = audiofile.split(".ogg")[0] + ".wav"
    ffmpeg.input(audiofile).output(new_filename).run()
    return new_filename

# Audio translation
def audio_to_text(audiopath: str) -> str:
    with sr.AudioFile(audiopath) as source:
        audio_listened = r.record(source)
        # convert to text
        text = r.recognize_google(audio_listened)
    return text

# # Text to speech
# def say_text(text: str):
#     speech_eng.say(text)
#     speech_eng.runAndWait()


# # Text to audio file
# def text_to_audiofile(text) -> str:
#     speech_eng.save_to_file(text)
#     speech_eng.runAndWait


# Welcome
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, chat("How are you!"))


# Handle voice notes
# Download vn, translate to text, send response
@bot.message_handler(content_types=["voice"])
def voice_processing(message):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    timestamp = str(datetime.now().timestamp()).replace(".", "_")
    filename = f"{AUDIOPATH}/{message.from_user.username}-{timestamp}.ogg"
    with open(filename, "wb") as opened_file:
        opened_file.write(downloaded_file)
    wav_audio = ogg_to_wav(filename)
    response = audio_to_text(wav_audio)
    bot.send_message(message.chat.id, chat(response))
    os.remove(filename) # Delete ogg audio
    os.remove(wav_audio) # Delete wav audio


# Sending audio: send text or file
@bot.message_handler(commands=["audio"])
def audio_command(message):
    text = "paraphrase: send me the text you would like to convert to audio: "
    bot.send_message(message.chat.id, chat(text), parse_mode="Markdown")
    bot.register_next_step_handler(message, handle_audio)

def handle_audio(message, lang="en", audiotype="mp3"):
    text = message.text
    text_summary = chat(f"summarise '{text}' in one sentence")
    speech_audio = gTTS(text, lang="en")
    timestamp = str(datetime.now().timestamp()).replace(".", "_")
    filename = f"{AUDIOPATH}/from-{BOT['name']}-to-{message.from_user.username}-{timestamp}.{audiotype}"
    speech_audio.save(filename) # Saving the audio file
    text_summary_prefix = chat("paraphrase: Your audio about: ")
    doc_caption = f"{text_summary_prefix}\n{text_summary}"
    print(f"(+) Sending audio | {doc_caption}")
    bot.send_document(message.chat.id, document=open(filename, 'rb'), caption=doc_caption)
    os.remove(filename) # Delete the audio
    # return filename
    # bot.register_next_step_handler(message, handle_sending_audio, filename)

# def handle_sending_audio(message, filename):
#     # bot.send_document(message.chat.id, document=filename)
#     print("Sending audio...")
#     
#     bot.send_document(message.chat.id, document=open(filename, 'rb'))
#     os.remove(filename) # Delete the audio
#     # return filename


# Loading message
@bot.message_handler(commands=["load"])
def loading_message(message):
    text = "Loading..."
    loading_text = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.edit_message_text("Yeah edited the loading message", loading_text.chat.id, loading_text.message_id, parse_mode="Markdown")


# Search the internet
@bot.message_handler(commands=["search"])
def search_command(message):
    text = "paraphrase: what would you like to search for: "
    bot.send_message(message.chat.id, chat(text), parse_mode="Markdown")
    bot.register_next_step_handler(message, search)

def search(message, max_results=5):
    text = message.text
    results = DDGS().text(keywords=text, max_results=max_results)
    formatted_result = ""
    for each_result in results:
        formatted_result += f"""
**{each_result['title']}**
{each_result['body']}
_Link:_ {each_result['href']}
"""
    bot.send_message(message.chat.id, formatted_result, parse_mode="Markdown")


# YouTube search
@bot.message_handler(commands=["ytsearch"])
def ytsearch_command(message):
    text = chat("paraphrase: what would you like to search for: Video or Music?")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
    markup.row('Video', 'Music')
    markup.row('Cancel')
    bot.send_message(message.chat.id, text, reply_markup=markup)
    # types.ReplyKeyboardRemove()
    # bot.send_message(message.chat.id, chat(text), parse_mode="Markdown")
    if message.text == "Cancel":
        send_welcome()
    else:
        bot.register_next_step_handler(message, ytsearch_getquery)

def ytsearch_getquery(message):
    option = message.text
    text = chat(f"paraphrase: what {option} would you like to search for?")
    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    if option == "Music":
        bot.register_next_step_handler(message, ytmusic_search)
    elif option == "Video":
        bot.register_next_step_handler(message, ytvideo_search)

def ytmusic_search(message):
    query = message.text
    text = f"🎵 Music Searching | for **{query}**..."
    loading_text = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    results = ytmusic.search(query, filter="songs")
    formatted_result = ""
    for index, song in enumerate(results[:5]):
        formatted_result = formatted_result + f"""
{index+1}. {song["title"]} _by_ {song["artists"][0]["name"]}
_Link:_ https://music.youtube.com/watch?v={song["videoId"]}
"""
        
    print(formatted_result)
    bot.edit_message_text(formatted_result, loading_text.chat.id, loading_text.message_id, parse_mode="Markdown")

def ytvideo_search(message):
    query = message.text
    text = f"🎞 Video Searching | for **{query}**..."
    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    # bot.send_message(message.chat.id, "Under construction!!!", parse_mode="Markdown")


# AI chating
@bot.message_handler(func=lambda m:True)
def chat_echo(message):
    response = chat(message.text)
    bot.send_message(message.chat.id, response)


# Running
# print(f.renderText(BOT["name"]))
print(f"(+) Launching {BOT['name']}")
bot.infinity_polling()