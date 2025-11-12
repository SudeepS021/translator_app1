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

    # Convert translated text to speech
    tts = gTTS(text=translated_text, lang=to_lang, slow=False)
    filename = "static/speech.mp3"
    tts.save(filename)

    return jsonify({
        "translated": translated_text,
        "audio_url": "/" + filename
    })


# ✅ Multilingual Voice Translation Route
@app.route('/voice_translate', methods=['POST'])
def voice_translate():
    recognizer = sr.Recognizer()
    data = request.json
    from_lang = data.get("from")
    to_lang = data.get("to")

    # Mapping of simple language codes to Google Speech Recognition codes
    language_map = {
        "en": "en-IN", "hi": "hi-IN", "kn": "kn-IN", "ta": "ta-IN", "te": "te-IN",
        "ml": "ml-IN", "mr": "mr-IN", "gu": "gu-IN", "bn": "bn-IN", "ur": "ur-IN",
    }
    recognize_lang = language_map.get(from_lang, "en-IN")

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print(f"🎤 Listening in {recognize_lang} ...")
        audio = recognizer.listen(source)

    try:
        # Recognize speech in selected input language
        text = recognizer.recognize_google(audio, language=recognize_lang)
        print("You said:", text)

        # Translate from input language to target language
        translated = translator.translate(text, src=from_lang, dest=to_lang)
        translated_text = translated.text

        # Convert translated text to speech
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