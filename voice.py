import speech_recognition as sr

def listen_for_audio():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Please speak now...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Processing speech...")
        text = recognizer.recognize_google(audio)
        print(f"Recognized Speech: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand the audio.")
        return None
    except sr.RequestError:
        print("Sorry, the speech service is unavailable.")
        return None

if __name__ == "__main__":
    result = listen_for_audio()
    if result:
        print("Final recognized text:", result)
