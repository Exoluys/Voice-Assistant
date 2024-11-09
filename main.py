from http.client import responses  # Import HTTP response status codes (not used in current code, could be omitted)
import speech_recognition as sr  # Import speech recognition library for converting speech to text
import datetime  # Import datetime to get the current time
import pyttsx3  # Import pyttsx3 for text-to-speech functionality
import requests  # Import requests to interact with the weather API


# Initialize recognizer for speech recognition and engine for text-to-speech
recognizer = sr.Recognizer()
engine = pyttsx3.init()


# Function to make the assistant speak the text passed to it
def speak(text):
    engine.say(text)
    engine.runAndWait()


# Function to listen for the user's voice command
def listen():
    with sr.Microphone() as source:
        print("Listening...")  # Prompt indicating the assistant is listening
        audio = recognizer.listen(source)  # Listen to the user's speech
        try:
            # Convert speech to text using Google Web Speech API
            command = recognizer.recognize_google(audio).lower()
            print("You said:", command)
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")  # In case the speech was not recognized
            speak("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            print("Network error occurred.")  # In case there is a network issue
            speak("There was an error with the network.")
            return ""
        return command


# Function to ask for and retrieve the city name for weather information
def get_city_name():
    print("Please say the name of the city you want the weather info for.")
    speak("Please say the name of the city you want the weather info for.")
    city_name = listen()  # Listen to the city name
    if city_name:
        print("City: ", city_name)
        return city_name
    else:
        print("Couldn't capture the city name.")  # If the city name wasn't captured correctly
        speak("Couldn't capture the city name.")
        return ""


# Function to fetch weather data for a specific city using OpenWeatherMap API
def weather_api(city_name):
    api_key = "YOUR_API_KEY"  # Add your OpenWeatherMap API key here
    base_url = "https://api.openweathermap.org/data/2.5/weather?"  # API endpoint for current weather

    # Parameters for the API request
    params = {
        "q": city_name,  # City name
        "appid": api_key,  # API key for authentication
        "units": "metric"  # Unit of measurement for temperature (metric = Celsius)
    }

    try:
        # Send a GET request to the API with the parameters
        response = requests.get(base_url, params=params)

        # Check if the response was successful (HTTP status code 200)
        if response.status_code == 200:
            data = response.json()  # Parse the JSON data from the response
            # Extract relevant weather data from the JSON response
            temperature = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            weather_description = data['weather'][0]['description']
            wind_speed = data['wind']['speed']

            # Format the weather information
            weather_info = (
                f"The weather in {city_name} is currently {weather_description}. "
                f"The temperature is {temperature}°C, feels like {feels_like}°C. "
                f"Humidity is {humidity}%, and the wind speed is {wind_speed} meters per second."
            )

            print(weather_info)  # Display the weather information
            speak(weather_info)  # Announce the weather information

        else:
            error_message = "City not found"  # If city is not found
            print(error_message)
            speak(error_message)

    except requests.exceptions.RequestException as e:
        # Catch any request-related errors and notify the user
        print(f"Error fetching weather data: {e}")
        speak("There was an error fetching the weather data.")


# Function to handle the process of sending an email
def handle_send_email():
    print("To whom should I send the email?")
    speak("To whom should I send the email?")
    recipient = listen()  # Listen for the recipient's email address

    print("What is the subject of the email?")
    speak("What is the subject of the email?")
    subject = listen()  # Listen for the subject of the email

    print("What should I say in the email?")
    speak("What should I say in the email?")
    message = listen()  # Listen for the email's message body

    #Calling the send_email function
    response = send_email(recipient, subject, message)
    print(response)
    speak(response)


# Function to handle various voice commands
def handle_command(command):
    if "time" in command:  # If the command contains "time"
        current_time = datetime.datetime.now().strftime("%I:%M %p")  # Get the current time
        print(f"The time is {current_time}")
        speak(f"The time is {current_time}")

    elif "weather" in command:  # If the command contains "weather"
        city_name = get_city_name()  # Get the city name from the user
        if city_name:
            weather_api(city_name)  # Fetch the weather data for the city

    elif "send email" in command:  # If the command contains "send email"
        handle_send_email()  # Handle the process of sending an email

    elif "stop" in command or "exit" in command or "quit" in command:  # If the user wants to quit
        print("Goodbye!")
        speak("Goodbye!")
        return True  # Signal to exit the loop

    else:
        print("Sorry, I didn't understand that command.")  # For unrecognized commands
        speak("Sorry, I didn't understand that command.")
    return False


# Initial greeting to the user
print("Hello, I am your assistant!")
speak("Hello, I am your assistant!")

# Main loop for continuous listening and handling commands
while True:
    command = listen()  # Listen for the user's command
    if command:  # If a command is received
        if handle_command(command):  # Handle the command
            break  # Exit the loop if the "exit" command is detected
