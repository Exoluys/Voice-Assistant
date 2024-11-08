from http.client import responses
import speech_recognition as sr
import datetime
import pyttsx3
import requests

# Initialize recognizer and engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()


# Function to make the assistant speak
def speak(text):
    engine.say(text)
    engine.runAndWait()


# Function to listen for the user's command
def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio).lower()
            print("You said:", command)
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            speak("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            print("Network error occurred.")
            speak("There was an error with the network.")
            return ""
        return command


# Function to get city name from the user
def get_city_name():
    print("Please say the name of the city you want the weather info for.")
    speak("Please say the name of the city you want the weather info for.")
    city_name = listen()
    if city_name:
        print("City: ", city_name)
        return city_name
    else:
        print("Couldn't capture the city name.")
        speak("Couldn't capture the city name.")
        return ""


# Function to fetch weather information from the API
def weather_api(city_name):
    api_key = "2d2c7a2e9545edda6c41c22e33ccdc5c"  # Add your API key here
    base_url = "https://api.openweathermap.org/data/2.5/weather?"

    params = {
        "q": city_name,
        "appid": api_key,
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
            speak(weather_info)
        else:
            error_message = "City not found"
            print(error_message)
            speak(error_message)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        speak("There was an error fetching the weather data.")


# Function to handle various commands
def handle_command(command):
    if "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        print(f"The time is {current_time}")
        speak(f"The time is {current_time}")

    elif "weather" in command:
        city_name = get_city_name()
        if city_name:
            weather_api(city_name)

    elif "stop" in command or "exit" in command or "quit" in command:
        print("Goodbye!")
        speak("Goodbye!")
        return True  # Signal to exit the loop

    else:
        print("Sorry, I didn't understand that command.")
        speak("Sorry, I didn't understand that command.")
    return False


# Initial greeting
print("Hello, I am your assistant!")
speak("Hello, I am your assistant!")

# Main loop for continuous listening
while True:
    command = listen()
    if command:
        if handle_command(command):
            break
