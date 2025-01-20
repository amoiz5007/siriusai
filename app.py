import requests
from flask import Flask, render_template, request, jsonify
import g4f 
import wikipedia
from functools import lru_cache
import random
import logging

WEATHER_API_KEY = "adf2f772808548e89d0143637250701"

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/voice-command', methods=['POST'])
def voice_command():
    command = request.json.get('command')
    print(f"Received command: {command}")  
    response = process_command(command)
    print(f"Response: {response}") 
    return jsonify({'response': response})

def process_command(command):
    command = command.lower() 
    print(f"Processing command: {command}")  

    if "play number guessing game" in command:
        return start_number_guessing_game()
    elif is_guess_game_active and any(char.isdigit() for char in command):
        return handle_guess(command)
    elif "play rock paper scissors" in command:
        return start_rock_paper_scissors()
    elif is_rock_paper_scissors_active and ("rock" in command or "paper" in command or "scissors" in command):
        return play_rock_paper_scissors(command)
    elif "hello" in command:
        return "Hello, How can I assist you today?"
    elif "name" in command:
        return "My name is Sirius and I am your Personal Voice Assistant"
    elif "show schedule" in command or "schedule of section" in command:
        words = command.split()
        user_section = None
        user_day = None
        for word in words:
            if word.upper() in ['A', 'B', 'C', 'D', 'E', 'F']:
                user_section = word.upper()
            elif word.lower() in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                user_day = word.lower()
        if user_section is None:
             return "Please specify a valid section."
        schedule = get_schedule(user_section)
        if not schedule:
            return "No schedule found for Section " + user_section
        else:
            if user_day is None:
                schedule_message = "Schedule for Section " + user_section + ":\n"
                for entry in schedule:
                    schedule_message += f"{entry['day']}: {entry['time']} - {entry['subject']}\n"
            else:
                schedule_message = f"Schedule for Section {user_section} on {user_day.capitalize()}:\n"
                for entry in schedule:
                    if entry['day'].lower() == user_day:
                        schedule_message += f"{entry['time']} - {entry['subject']}\n"
            return schedule_message
    elif "wikipedia" in command:
        query = command.replace("wikipedia", "").strip()
        return search_wikipedia(query)
    elif "weather" in command:
        location = command.replace("weather", "").strip()
        return get_weather(location)
    elif "open" in command:
        site_name = command.replace("open", "").strip()
        return open_site(site_name)
    else:
        print("No matching command found. Using G4F response.")  
        return get_g4f_response(command)

# Open Sites Code
def open_site(site_name):
    import webbrowser
    site_url = get_site_url(site_name)
    if site_url:
        webbrowser.open(site_url)
        return f"Opening {site_name}..."
    else:
        return f"Sorry, I couldn't find the URL for {site_name}."
def get_site_url(site_name):
    site_urls = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "facebook": "https://www.facebook.com",
        "instagram": "https://www.instagram.com",
        "netflix": "https://www.netflix.com",
        "student portal": "https://edusmartz.ssuet.edu.pk/StudentPortal/login",
        "whatsapp": "https://web.whatsapp.com/",
        "spotify": "https://open.spotify.com/",
    }
    return site_urls.get(site_name)

def get_schedule(section):
    schedules = {
        'A': [
            {'day': 'Monday', 'time': '1:30-2:30', 'subject': 'Introduction to Computing'},
            {'day': 'Monday', 'time': '2:30-4:30', 'subject': 'Linear Algebra'},
            {'day': 'Monday', 'time': '4:30-5:30', 'subject': 'Islamic Studies'},
            {'day': 'Tuesday', 'time': '12:30-1:30', 'subject': 'Islamic Studies'},
            {'day': 'Tuesday', 'time': '1:30-2:30', 'subject': 'Linear Algebra'},
            {'day': 'Tuesday', 'time': '2:30-4:30', 'subject': 'Programming Fundamentals'},
            {'day': 'Tuesday', 'time': '4:30-5:30', 'subject': 'Functional English'},
            {'day': 'Wednesday', 'time': '8:30-11:30', 'subject': 'Programming Fundamentals Lab'},
            {'day': 'Wednesday', 'time': '11:30-2:30', 'subject': 'Introduction to Computing Lab'},
            {'day': 'Thursday', 'time': '1:30-2:30', 'subject': 'Introduction to Computing'},
            {'day': 'Thursday', 'time': '2:30-4:30', 'subject': 'Functional English'},
            {'day': 'Thursday', 'time': '4:30-5:30', 'subject': 'Programming Fundamentals'},
        ],
        'B': [
            {'day': 'Monday', 'time': '8:30-9:30', 'subject': 'Introduction to Computing'},
            {'day': 'Monday', 'time': '9:30-10:30', 'subject': 'Functional English'},
            {'day': 'Monday', 'time': '10:30-11:30', 'subject': 'Islamic Studies'},
            {'day': 'Monday', 'time': '11:30-12:30', 'subject': 'Programming Fundamentals'},
            {'day': 'Tuesday', 'time': '8:30-9:30', 'subject': 'Islamic Studies'},
            {'day': 'Tuesday', 'time': '9:30-10:30', 'subject': 'Introduction to Computing'},
            {'day': 'Tuesday', 'time': '10:30-12:30', 'subject': 'Linear Algebra'},
            {'day': 'Wednesday', 'time': '12:30-2:30', 'subject': 'Functional English'},
            {'day': 'Wednesday', 'time': '2:30-3:30', 'subject': 'Linear Algebra'},
            {'day': 'Wednesday', 'time': '3:30-5:30', 'subject': 'Programming Fundamentals'},
            {'day': 'Thursday', 'time': '11:30-1:30', 'subject': 'Programming Fundamentals Lab'},
            {'day': 'Thursday', 'time': '2:30-5:30', 'subject': 'Introduction to Computing Lab'},
        ],
        'C': [
            {'day': 'Tuesday', 'time': '12:30-1:30', 'subject': 'Introduction to Computing'},
            {'day': 'Tuesday', 'time': '1:30-2:30', 'subject': 'Functional English'},
            {'day': 'Tuesday', 'time': '2:30-5:30', 'subject': 'Programming Fundamentals Lab'},
            {'day': 'Wednesday', 'time': '1:30-3:30', 'subject': 'Linear Algebra'},
            {'day': 'Wednesday', 'time': '3:30-5:30', 'subject': 'Functional English'},
            {'day': 'Thursday', 'time': '1:30-3:30', 'subject': 'Programming Fundamentals'},
            {'day': 'Thursday', 'time': '3:30-4:30', 'subject': 'Islamic Studies'},
            {'day': 'Thursday', 'time': '4:30-5:30', 'subject': 'Introduction to Computing'},
            {'day': 'Friday', 'time': '9:30-12:30', 'subject': 'Introduction to Computing Lab'},
            {'day': 'Friday', 'time': '2:30-3:30', 'subject': 'Linear Algebra'},
            {'day': 'Friday', 'time': '3:30-4:30', 'subject': 'Islamic Studies'},
            {'day': 'Friday', 'time': '4:30-5:30', 'subject': 'Programming Fundamentals'},
        ],
        'D': [
            {'day': 'Monday', 'time': '11:30 - 2:30','subject': 'Introduction to Computing Lab'},
            {'day': 'Monday', 'time': '2:30-5:30', 'subject': 'Programming Fundamentals Lab'},
            {'day': 'Wednesday', 'time': '8:30-9:30', 'subject': 'Islamic Studies'},
            {'day': 'Wednesday', 'time': '9:30-10:30', 'subject': 'Functional English'},
            {'day': 'Wednesday', 'time': '10:30-11:30', 'subject': 'Linear Algebra'},
            {'day': 'Wednesday', 'time': '11:30-12:30', 'subject': 'Introduction to Computing'},
            {'day': 'Thursday', 'time': '8:30-9:30', 'subject': 'Islamic Studies'},
            {'day': 'Thursday', 'time': '9:30-11:30', 'subject': 'Programming Fundamentals'},
            {'day': 'Thursday', 'time': '11:30-12:30', 'subject': 'Functional English'},
            {'day': 'Thursday', 'time': '12:30-1:30', 'subject': 'Linear Algebra'},
            {'day': 'Friday', 'time': '8:30-9:30', 'subject': 'Introduction to Computing'},
            {'day': 'Friday', 'time': '9:30-10:30', 'subject': 'Linear Algebra'},
            {'day': 'Friday', 'time': '10:30-11:30', 'subject': 'Functional English'},
            {'day': 'Friday', 'time': '11:30-12:30', 'subject': 'Programming Fundamentals'},
        ],
        'E': [
            {'day': 'Monday', 'time': '12:30-2:30', 'subject': 'Functional English'},
            {'day': 'Monday', 'time': '2:30-3:30', 'subject': 'Programming Fundamentals'},
            {'day': 'Monday', 'time': '3:30-5:30', 'subject': 'Linear Algebra'},
            {'day': 'Tuesday', 'time': '8:30-9:30', 'subject': 'Functional English'},
            {'day': 'Tuesday', 'time': '9:30-10:30', 'subject': 'Islamic Studies'},
            {'day': 'Tuesday', 'time': '10:30-11:30', 'subject': 'Linear Algebra'},
            {'day': 'Tuesday', 'time': '11:30-2:30', 'subject': 'Introduction to Computing Lab'},
            {'day': 'Wednesday', 'time': '8:30-10:30', 'subject': 'Introduction to Computing'},
            {'day': 'Wednesday', 'time': '10:30-11:30', 'subject': 'Islamic Studies'},
            {'day': 'Wednesday', 'time': '11:30-1:30', 'subject': 'Programming Fundamentals'},
            {'day': 'Friday', 'time': '2:30-5:30', 'subject': 'Programming Fundamentals Lab'},
        ],
        'F': [
            {'day': 'Monday', 'time': '8:30-9:30', 'subject': 'Introduction to Computing'},
            {'day': 'Monday', 'time': '9:30-10:30', 'subject': 'Functional English'},
            {'day': 'Monday', 'time': '10:30-12:30', 'subject': 'Programming Fundamentals'},
            {'day': 'Tuesday', 'time': '8:30-11:30', 'subject': 'Introduction to Computing Lab'},
            {'day': 'Tuesday', 'time': '11:30-12:30', 'subject': 'Programming Fundamentals'},
            {'day': 'Wednesday', 'time': '11:30-12:30', 'subject': 'Linear Algebra'},
            {'day': 'Wednesday', 'time': '12:30-1:30', 'subject': 'Islamic Studies'},
            {'day': 'Wednesday', 'time': '1:30-2:30', 'subject': 'Introduction to Computing'},
            {'day': 'Wednesday', 'time': '2:30-5:30', 'subject': 'Programming Fundamentals Lab'},
            {'day': 'Thursday', 'time': '8:30-10:30', 'subject': 'Linear Algebra'},
            {'day': 'Thursday', 'time': '10:30-11:30', 'subject': 'Islamic Studies'},
            {'day': 'Thursday', 'time': '11:30-1:30', 'subject': 'Functional English'},
        ],
    }

    return schedules.get(section, [])


# Example ```python
user_section = 'A'  # Example
schedule = get_schedule(user_section)

print(f"Schedule for Section {user_section}:")
for entry in schedule:
    print(f"{entry['day']}: {entry['time']} - {entry['subject']}")

# Weather Code
def get_weather(location):
    if not location:
        return "Please specify a location for the weather."

    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={location}"
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()

        city = data["location"]["name"]
        country = data["location"]["country"]
        temp_c = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]

        return f"The weather in {city}, {country} is {temp_c}°C with {condition}."
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching weather data: {e}")
        return "Sorry, I couldn't fetch the weather information at the moment."

#Number Guessing Game Code
target_number = None
is_guess_game_active = False

def start_number_guessing_game():
    global target_number, is_guess_game_active
    target_number = random.randint(1, 10)
    is_guess_game_active = True
    return "I have chosen a number between 1 and 10. Start guessing!"

def handle_guess(command):
    global is_guess_game_active
    try:
        guess = int(''.join(filter(str.isdigit, command)))
        print(f"User   guessed: {guess}")  # Debugging: Log the guess

        if guess < target_number:
            return "Higher."
        elif guess > target_number:
            return "Lower."
        else:
            is_guess_game_active = False
            return "Congratulations! You guessed the correct number."
    except ValueError:
        return "Please say a valid number."

#Rock Paper Scissors Game Code
is_rock_paper_scissors_active = False

def start_rock_paper_scissors():
    global is_rock_paper_scissors_active
    is_rock_paper_scissors_active = True
    return "Say 'rock', 'paper', or 'scissors' to play!"

def play_rock_paper_scissors(command):
    global is_rock_paper_scissors_active
    choices = ["rock", "paper", "scissors"]
    user_choice = command.strip().lower()
    assistant_choice = random.choice(choices)

    if user_choice not in choices:
        return "Please say 'rock', 'paper', or 'scissors'."

    if user_choice == assistant_choice:
        return f"I chose {assistant_choice}. It's a tie!"
    elif (user_choice == "rock" and assistant_choice == "scissors") or \
         (user_choice == "paper" and assistant_choice == "rock") or \
         (user_choice == "scissors" and assistant_choice == "paper"):
        return f"I chose {assistant_choice}. You win!"
    else:
        return f"I chose {assistant_choice}. You lose!"
    is_rock_paper_scissors_active = False

#Response Time Code for Wikipedia
@lru_cache(maxsize=100)  #only 100 queries will be taken
def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=2)  #only to sentences
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found. Please be more specific: {e.options}"
    except wikipedia.exceptions.PageError:
        return f"Sorry, I couldn't find any information on Wikipedia for '{query}'."

def get_g4f_response(prompt):
    try:
        modified_prompt = f"Provide a concise and to-the-point answer in 1-2 lines: {prompt}"
        
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": modified_prompt}],
        )
        return response
    except Exception as e:
        logging.error(f"Error calling G4F API: {e}")  # Log the error
        return "Error occurred while processing your request."


if __name__ == '__main__':
    app.run(debug=False)