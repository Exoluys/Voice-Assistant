import speech_recognition as sr  # Library for converting speech to text
import datetime  # Library to get the current time
import pyttsx3  # Library for text-to-speech functionality
import requests  # Library to interact with web APIs


class VoiceAssistant:
    """A simple voice assistant that can tell the time, fetch weather info, and handle basic commands."""

    def __init__(self, name="Jarvis"):
        """
        Initialize the voice assistant with a name, recognizer for speech recognition,
        text-to-speech engine, and API key for weather data.
        """
        self.name = name  # Name of the assistant
        self.recognizer = sr.Recognizer()  # Recognizer object for speech recognition
        self.engine = pyttsx3.init()  # Initialize the text-to-speech engine
        self.api_key = "YOUR_API_KEY"  # Replace with your OpenWeatherMap API key

    def speak(self, text):
        """Convert text to speech and speak it aloud."""
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """
        Listen for a voice command using the microphone and convert the captured audio to text.
        Returns the recognized command as a string or an empty string if recognition fails.
        """
        with sr.Microphone() as source:  # Use the default system microphone as the input source
            print("Listening...")
            audio = self.recognizer.listen(source)  # Capture audio from the microphone
            try:
                # Convert audio to text using Google Web Speech API
                command = self.recognizer.recognize_google(audio).lower()
                print("You said:", command)  # Print the recognized command
                return command
            except sr.UnknownValueError:
                # Handle case when speech was unintelligible
                print("Sorry, I didn't catch that.")
                self.speak("Sorry, I didn't catch that.")
                return ""
            except sr.RequestError:
                # Handle network errors
                print("Network error occurred.")
                self.speak("There was an error with the network.")
                return ""

    def get_city_name(self):
        """
        Prompt the user to say the name of the city for which they want weather information.
        Returns the recognized city name as a string, or an empty string if recognition fails.
        """
        self.speak("Please say the name of the city you want the weather info for.")
        city_name = self.listen()  # Listen for the city name
        if city_name:
            print("City:", city_name)
            return city_name
        else:
            self.speak("Couldn't capture the city name.")
            return ""

    def get_weather(self, city_name):
        """
        Fetch current weather data for the specified city using the OpenWeatherMap API.
        Announce the weather information or error messages if data retrieval fails.
        """
        # Base URL for OpenWeatherMap API
        base_url = "https://api.openweathermap.org/data/2.5/weather?"
        # Parameters for API request
        params = {
            "q": city_name,  # City name
            "appid": self.api_key,  # API key for authentication
            "units": "metric"  # Use Celsius for temperature
        }

        try:
            # Send GET request to the API
            response = requests.get(base_url, params=params)
            if response.status_code == 200:  # Check if the request was successful
                # Parse JSON response and extract weather data
                data = response.json()
                temperature = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]
                weather_description = data['weather'][0]['description']
                wind_speed = data['wind']['speed']

                # Format and announce the weather information
                weather_info = (
                    f"The weather in {city_name} is currently {weather_description}. "
                    f"The temperature is {temperature}°C, feels like {feels_like}°C. "
                    f"Humidity is {humidity}%, and the wind speed is {wind_speed} meters per second."
                )

                print(weather_info)  # Display the weather information
                self.speak(weather_info)  # Announce the weather information
            else:
                # Handle case when the city is not found
                self.speak("City not found.")
        except requests.exceptions.RequestException as e:
            # Handle request errors and notify the user
            print(f"Error fetching weather data: {e}")
            self.speak("There was an error fetching the weather data.")

    def tell_time(self):
        """Announce the current time."""
        current_time = datetime.datetime.now().strftime("%I:%M %p")  # Get the current time in 12-hour format
        print(f"The time is {current_time}")  # Print the time
        self.speak(f"The time is {current_time}")  # Announce the time

    def handle_command(self, command):
        """
        Handle various commands based on recognized voice input.
        Responds to time, weather, and exit commands.
        """
        if "time" in command:
            self.tell_time()  # Announce the current time
        elif "weather" in command:
            # Fetch and announce the weather for a specified city
            city_name = self.get_city_name()
            if city_name:
                self.get_weather(city_name)
        elif any(word in command for word in ["stop", "exit", "quit"]):
            # Handle commands to exit the program
            self.speak("Goodbye!")
            return True  # Return True to signal exiting the loop
        else:
            # Handle unrecognized commands
            self.speak("Sorry, I didn't understand that command.")
        return False  # Return False to continue the loop

    def start(self):
        """Start the assistant and continuously listen for commands."""
        print(f"Hello, it's {self.name}!")  # Greet the user
        self.speak(f"Hello, it's {self.name}!")

        while True:
            command = self.listen()  # Listen for a command
            if command and self.handle_command(command):  # Process the command
                break  # Exit the loop if the user wants to quit


# Initialize and start the assistant
assistant = VoiceAssistant()
assistant.start()
