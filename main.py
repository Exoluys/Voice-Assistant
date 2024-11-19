import os
import speech_recognition as sr
import datetime
import pyttsx3
import requests
from send_email import send_email
from dotenv import load_dotenv
import spacy
from transformers import pipeline

# Load environment variables
load_dotenv()

# Load spaCy's pre-trained English model
nlp = spacy.load("en_core_web_sm")

# Initialize the pre-trained transformer model for zero-shot classification
classifier = pipeline("zero-shot-classification")

class VoiceAssistant:
    """A simple voice assistant with NLP features for better command recognition."""

    def __init__(self, name="Jarvis"):
        self.name = name
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.api_key = os.getenv("api_key")  # Replace with your OpenWeatherMap API key

    def speak(self, text):
        """Convert text to speech and speak it aloud."""
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Listen for a voice command and convert it to text."""
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
            try:
                command = self.recognizer.recognize_google(audio).lower()
                print("You said:", command)
                return command
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that.")
                self.speak("Sorry, I didn't catch that.")
                return ""
            except sr.RequestError:
                print("Network error occurred.")
                self.speak("There was an error with the network.")
                return ""

    def nlp_process(self, text):
        """
        Process the command using spaCy and transformers for NLP tasks like entity recognition
        and intent classification.
        """
        # Use spaCy for entity recognition
        doc = nlp(text)
        entities = [ent.text for ent in doc.ents]

        # Use transformers for intent classification
        labels = ["weather", "time", "send email", "greeting"]
        result = classifier(text, candidate_labels=labels)
        intent = result['labels'][0]  # Get the most likely intent

        print(f"Entities: {entities}")
        print(f"Intent: {intent}")
        return intent, entities

    def handle_command(self, command):
        """Handle commands based on recognized intent and entities."""
        intent, entities = self.nlp_process(command)

        if intent == "time":
            self.tell_time()
        elif intent == "weather" and entities:
            city_name = self.get_city_from_command(command)
            if city_name:
                self.get_weather(city_name)
        elif intent == "send email":
            receiver_email = self.get_receiver_email()
            subject = self.get_subject()
            message = self.get_message()
            send_email(receiver_email, subject, message)
        elif intent == "Hello":
            self.speak("Hello! How can I assist you?")
        elif any(word in command for word in ["stop", "exit", "quit"]):
            # If the user says 'exit', 'quit', or 'stop', the assistant will stop.
            self.speak("Goodbye!")
            print("Goodbye!")
            return True  # Exit the loop and stop the assistant
        else:
            self.speak("Sorry, I didn't understand that command.")

    def get_city_from_command(self, command):
        """Extract the city name from the command using NLP."""
        doc = nlp(command)
        cities = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
        return cities[0] if cities else None

    def get_weather(self, city_name):
        """Fetch weather data from the OpenWeatherMap API."""
        base_url = "https://api.openweathermap.org/data/2.5/weather?"
        params = {
            "q": city_name,
            "appid": self.api_key,
            "units": "metric"
        }
        try:
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                temperature = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]
                weather_description = data['weather'][0]['description']
                wind_speed = data['wind']['speed']
                weather_info = (
                    f"The weather in {city_name} is currently {weather_description}. "
                    f"The temperature is {temperature}°C, feels like {feels_like}°C. "
                    f"Humidity is {humidity}%, and the wind speed is {wind_speed} meters per second."
                )
                print(weather_info)
                self.speak(weather_info)
            else:
                self.speak("City not found.")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            self.speak("There was an error fetching the weather data.")

    def tell_time(self):
        """Announce the current time."""
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        print(f"The time is {current_time}")
        self.speak(f"The time is {current_time}")

    def get_receiver_email(self):
        """Prompt the user to say the receiver's email."""
        self.speak("Please say the email of the receiver you want the email to be sent.")
        return self.listen()

    def get_subject(self):
        """Prompt the user to say the email subject."""
        self.speak("Tell the subject.")
        return self.listen()

    def get_message(self):
        """Prompt the user to say the message content for the email."""
        self.speak("Tell me the message.")
        return self.listen()

    def start(self):
        """Start the assistant and listen for commands."""
        print(f"Hello, it's {self.name}!")
        self.speak(f"Hello, it's {self.name}!")

        while True:
            command = self.listen()  # Listen for a command
            if command:
                self.handle_command(command)  # Process the command

# Initialize and start the assistant
assistant = VoiceAssistant()
assistant.start()
