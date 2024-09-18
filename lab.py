
import pyttsx4
from gtts import gTTS
from datetime import datetime

AUDIOPATH = "audio"
speech_eng = pyttsx4.init()
speech_eng.setProperty("rate", 105)
# speech_eng.setProperty('speaker_wav', './audio/_my_voice.wav')
voices = speech_eng.getProperty("voices")
speech_eng.setProperty("voices", voices[1].id)

def say_text(text: str):
    speech_eng.say(text)
    speech_eng.runAndWait()


# Text to audio file
def text_to_audiofile(text, lang="en", audiotype="mp3") -> str:
    audio = gTTS(text, lang="en")
    timestamp = str(datetime.now().timestamp()).replace(".", "_")
    filename = f"{AUDIOPATH}/test-{timestamp}.{audiotype}"
    audio.save(filename)
    return filename

text_to_audiofile("""
"Dear Church Members, we deeply appreciate your continued support for the Female Fellowship Centre project. We are excited to inform you that the roofing phase has begun! Your generosity has brought us this far, and we look forward to your further support as we complete this important project. God bless you all!"

yours truly
Es.Radiance Thy Teach
""")