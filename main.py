import os
import speech_recognition as sr
import pyttsx3
import spacy
from transformers import pipeline
import datetime
import time
import threading
import requests
from dotenv import load_dotenv
from send_email import send_email

# Load environment variables
load_dotenv()

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")


class VoiceAssistant:
    """A simple voice assistant that performs tasks based on user commands."""

    def __init__(self, name="Jarvis"):
        """Initialize assistant with necessary components."""
        self.name = name
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.api_key = os.getenv("api_key")
        self.reminders = []
        self.classifier = pipeline("zero-shot-classification")

    def speak(self, text):
        """Convert text to speech."""
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Listen for a command and convert it to text."""
        with sr.Microphone() as source:
            audio = self.recognizer.listen(source)
            try:
                return self.recognizer.recognize_google(audio).lower()
            except (sr.UnknownValueError, sr.RequestError):
                self.speak("Sorry, I didn't catch that.")
                return ""

    def nlp_process(self, text):
        """Process the command using spaCy and zero-shot classification."""
        doc = nlp(text)
        entities = [ent.text for ent in doc.ents]
        labels = ["weather", "time", "mail", "reminder"]
        result = self.classifier(text, candidate_labels=labels)
        return result['labels'][0], entities

    def handle_command(self, command):
        """Process and execute the given command."""
        if "stop" in command or "exit" in command or "quit" in command:
            self.speak("Goodbye!")
            return True

        if "reminder" in command or "set reminder" in command:
            self.set_reminder()
            return False

        intent, _ = self.nlp_process(command)

        if intent == "time":
            self.tell_time()
        elif "weather" in command:
            self.get_weather(command)
        elif intent == "mail":
            self.send_mail()
        else:
            self.speak("Sorry, I didn't understand that command.")

    def set_reminder(self):
        """Set a reminder based on user input."""
        self.speak("Please tell me the time for the reminder.")
        reminder_time = self.listen()
        if not reminder_time:
            return

        reminder_time = reminder_time.lower().replace('a.m.', 'am').replace('p.m.', 'pm')

        self.speak("What should the reminder say?")
        reminder_message = self.listen()
        if not reminder_message:
            return

        try:
            reminder_time = datetime.datetime.strptime(reminder_time, "%I:%M %p")
            reminder_time = reminder_time.replace(year=datetime.datetime.now().year,
                                                  month=datetime.datetime.now().month,
                                                  day=datetime.datetime.now().day)
            self.reminders.append((reminder_time, reminder_message))
            self.speak(f"Reminder set for {reminder_time.strftime('%I:%M %p')}. I'll remind you about: {reminder_message}.")
            threading.Thread(target=self.check_reminders, daemon=True).start()
        except ValueError:
            self.speak("Sorry, I couldn't understand the time format. Please try again.")

    def check_reminders(self):
        """Check periodically if any reminders are due."""
        while True:
            now = datetime.datetime.now()
            for reminder_time, reminder_message in list(self.reminders):
                if now >= reminder_time:
                    self.speak(f"Reminder: {reminder_message}")
                    self.reminders.remove((reminder_time, reminder_message))
            time.sleep(30)

    def tell_time(self):
        """Announce the current time."""
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        self.speak(f"The time is {current_time}")

    def get_weather(self, command):
        """Get the weather for a specified city."""
        city_name = self.get_city_from_command(command)
        if city_name:
            api_key = self.api_key
            base_url = "https://api.openweathermap.org/data/2.5/weather?"
            complete_url = f"{base_url}q={city_name}&appid={api_key}&units=metric"
            response = requests.get(complete_url)
            data = response.json()

            if data["cod"] != "404":
                main = data["main"]
                weather = data["weather"][0]
                temperature = main["temp"]
                description = weather["description"]
                self.speak(f"The current temperature in {city_name} is {temperature}°C with {description}.")
            else:
                self.speak("Sorry, I couldn't find that city.")

    def get_city_from_command(self, command):
        """Extract the city name from the user's command."""
        doc = nlp(command)
        cities = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
        return cities[0] if cities else None

    def send_mail(self):
        """Send an email based on user input."""
        receiver_email = self.get_receiver_email()
        if receiver_email:
            subject = self.get_subject()
            message = self.get_message()
            send_email(receiver_email, subject, message)

    def get_receiver_email(self):
        """Prompt for and return the recipient's email address."""
        self.speak("Please type the email of the receiver.")
        email = input("Enter the recipient's email address: ")
        return email if email else None

    def get_subject(self):
        """Prompt for and return the subject of the email."""
        self.speak("Tell the subject.")
        return self.listen()

    def get_message(self):
        """Prompt for and return the message content for the email."""
        self.speak("Tell me the message.")
        return self.listen()

    def start(self):
        """Start the assistant and listen for commands."""
        self.speak(f"Hello, it's {self.name}!")
        while True:
            command = self.listen()
            if command and self.handle_command(command):
                break


# Initialize and start the assistant
assistant = VoiceAssistant()
assistant.start()
