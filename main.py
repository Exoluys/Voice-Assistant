import os
import speech_recognition as sr
import pyttsx3
import spacy  # Import spaCy
from transformers import pipeline  # Import transformers pipeline
import datetime
import time
import threading
import requests
from dotenv import load_dotenv

load_dotenv()

# Load spaCy model
nlp = spacy.load("en_core_web_sm")  # Add this line to load the spaCy model


class VoiceAssistant:
    """A simple voice assistant with NLP features for better command recognition."""

    def __init__(self, name="Jarvis"):
        self.name = name
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.api_key = os.getenv("api_key")  # Replace with your OpenWeatherMap API key
        self.reminders = []  # To store reminders

        # Initialize the zero-shot classification model
        self.classifier = pipeline("zero-shot-classification")

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
        doc = nlp(text)  # Using the loaded spaCy model
        entities = [ent.text for ent in doc.ents]
        labels = ["weather", "time", "send email", "greeting", "reminder"]

        # Use zero-shot classification to determine the intent
        result = self.classifier(text, candidate_labels=labels)
        intent = result['labels'][0]  # Get the most likely intent

        # Debugging output
        print(f"Entities: {entities}")
        print(f"Intent: {intent}")
        return intent, entities

    def handle_command(self, command):
        """Handle commands based on recognized intent and entities."""
        # Stop command detection first
        if "stop" in command or "exit" in command or "quit" in command:
            self.speak("Goodbye!")
            print("Goodbye!")
            return True  # Exit the loop and stop the assistant

        # Check if "reminder" or "set reminder" is mentioned and handle separately
        if "reminder" in command or "set reminder" in command:
            self.set_reminder(command)
            return False  # Don't need further processing after setting a reminder

        # Process other intents
        intent, entities = self.nlp_process(command)

        if intent == "time":
            self.tell_time()
        elif "weather" in command:  # Improved weather detection
            self.get_weather(command)
        elif intent == "send email":
            receiver_email = self.get_receiver_email()
            subject = self.get_subject()
            message = self.get_message()
            self.send_email(receiver_email, subject, message)
        elif intent == "greeting":
            self.speak("Hello! How can I assist you?")
        else:
            self.speak("Sorry, I didn't understand that command.")

    def set_reminder(self, command):
        """Set a reminder based on the command."""
        self.speak("Please tell me the time for the reminder.")
        reminder_time = self.listen()  # Get time from the user

        # If no valid time, exit the reminder process
        if not reminder_time:
            self.speak("Sorry, I couldn't understand the time. Please try again.")
            return

        # Normalize the time format to handle 'a.m.' and 'p.m.'
        reminder_time = reminder_time.lower().replace('a.m.', 'am').replace('p.m.', 'pm')

        self.speak("What should the reminder say?")
        reminder_message = self.listen()  # Get message for the reminder

        # If no valid message, exit the reminder process
        if not reminder_message:
            self.speak("Sorry, I couldn't understand the reminder message. Please try again.")
            return

        # Try to parse the time
        try:
            # Use datetime's strptime with a flexible time format
            reminder_time = datetime.datetime.strptime(reminder_time, "%I:%M %p")
            reminder_time = reminder_time.replace(year=datetime.datetime.now().year,
                                                  month=datetime.datetime.now().month,
                                                  day=datetime.datetime.now().day)

            # Store reminder with the time and message
            self.reminders.append((reminder_time, reminder_message))
            self.speak(
                f"Reminder set for {reminder_time.strftime('%I:%M %p')}. I'll remind you about: {reminder_message}.")

            # Start a background thread to check reminders
            threading.Thread(target=self.check_reminders, daemon=True).start()

        except ValueError:
            self.speak("Sorry, I couldn't understand the time format. Please try again.")

    def check_reminders(self):
        """Check if any reminders are due."""
        while True:
            now = datetime.datetime.now()
            for reminder_time, reminder_message in list(self.reminders):
                if now >= reminder_time:
                    self.speak(f"Reminder: {reminder_message}")
                    self.reminders.remove((reminder_time, reminder_message))  # Remove reminder after it's triggered
            time.sleep(30)  # Check every 30 seconds

    def tell_time(self):
        """Announce the current time."""
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        print(f"The time is {current_time}")
        self.speak(f"The time is {current_time}")

    def get_weather(self, command):
        """Fetch weather data from the OpenWeatherMap API."""
        city_name = self.get_city_from_command(command)
        if not city_name:
            self.speak("Sorry, I couldn't understand the city name.")
            return

        api_key = self.api_key  # Replace with your actual API key
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = f"{base_url}q={city_name}&appid={api_key}&units=metric"

        response = requests.get(complete_url)
        data = response.json()

        if data["cod"] == "404":
            self.speak("Sorry, I couldn't find that city.")
            print("City not found.")
        else:
            main = data["main"]
            weather = data["weather"][0]
            temperature = main["temp"]
            description = weather["description"]

            self.speak(f"The current temperature in {city_name} is {temperature}°C with {description}.")
            print(f"The current temperature in {city_name} is {temperature}°C with {description}.")

    def get_city_from_command(self, command):
        """Extract the city from the user's command."""
        doc = nlp(command)
        cities = [ent.text for ent in doc.ents if ent.label_ == "GPE"]  # Geopolitical entity
        return cities[0] if cities else None

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
                if self.handle_command(command):  # Process the command
                    break  # Stop the assistant when the stop command is given


# Initialize and start the assistant
assistant = VoiceAssistant()
assistant.start()
