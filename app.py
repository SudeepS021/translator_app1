from flask import Flask, render_template, request, jsonify
from googletrans import Translator
from gtts import gTTS
import os
import speech_recognition as sr

app = Flask(__name__)
translator = Translator()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/text')
def text_page():
    return render_template('text.html')


@app.route('/voice')
def voice_page():
    return render_template('voice.html')


@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.json
    from_lang = data.get("from")
    to_lang = data.get("to")
    text = data.get("text")

    translated = translator.translate(text, src=from_lang, dest=to_lang)
    translated_text = translated.text

   
    tts = gTTS(text=translated_text, lang=to_lang, slow=False)
    filename = "static/speech.mp3"
    tts.save(filename)

    return jsonify({
        "translated": translated_text,
        "audio_url": "/" + filename
    })


@app.route('/voice_translate', methods=['POST'])
def voice_translate():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎤 Listening...")
        audio = recognizer.listen(source)

    try:
       
        text = recognizer.recognize_google(audio)
        print("You said:", text)

        to_lang = request.json.get("to")
        translated = translator.translate(text, src="en", dest=to_lang)
        translated_text = translated.text

        
        tts = gTTS(text=translated_text, lang=to_lang, slow=False)
        filename = "static/speech.mp3"
        tts.save(filename)

        return jsonify({
            "original": text,
            "translated": translated_text,
            "audio_url": "/" + filename
        })
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand your voice"}), 400
    except sr.RequestError:
        return jsonify({"error": "Speech recognition service error"}), 500


if __name__ == '__main__':
    if not os.path.exists("static"):
        os.makedirs("static")
    app.run(debug=True)