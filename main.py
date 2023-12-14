import openai
import sys
import random
import os
from flask import Flask, render_template, request
from flask import send_file, jsonify
import requests

app = Flask(__name__)


# Load your API key from an environment variable
api_key = os.getenv("OPENAI_API_KEY")  # Use the name of your environment variable here
if api_key is None:
    print("API key not found. Please set the OPENAI_API_KEY environment variable.")
    sys.exit(1)
client = openai.OpenAI()
# Initialize the OpenAI client
openai.api_key = api_key

# Base prompt
base_prompt = "Create a humorous and respectful pick-up line for a BYU student that includes a reference to "

@app.route('/generate_speech', methods=['POST'])
def generate_speech():
    text = request.form.get('text')
    voice = request.form.get('voice')  # Get the selected voice from the form data

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "tts-1",
        "input": text,
        "voice": voice  # Use the selected voice for TTS
    }
    response = requests.post("https://api.openai.com/v1/audio/speech", json=data, headers=headers)

    if response.status_code == 200:
        # Save the response content as an audio file
        with open("speech.mp3", "wb") as audio_file:
            audio_file.write(response.content)
        return send_file("speech.mp3", mimetype="audio/mp3")
    else:
        return jsonify({"error": "Failed to generate speech"}), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    pickup_line = ''
    if request.method == 'POST':
        custom_prompt = request.form.get('custom_prompt')
        if custom_prompt:
            pickup_line = main(custom_prompt)
        else:
            phrase = random_choice(phrase_list)
            pickup_line = main(phrase)
    return render_template('index.html', pickup_line=pickup_line)
# Load phrases from file
phrase_list = []
with open("phrases.txt", "r") as f:
    for line in f:
        phrase_list.append(line.strip())
@app.route('/delete', methods=['POST'])
def delete_pickup_line():
    # delete all pickup lines from static/pickup_lines.txt
    open("static/pickup_lines.txt", "w").close()
    return render_template('index.html', pickup_line="All pickup lines deleted")

@app.route('/rate', methods=['POST'])
def rate_pickup_line():
    pickup_line_to_rate = request.form.get('pickup_line_to_rate')
    rating = request.form.get('rating')
    #save to static/pickup_lines.txt
    # find all lines that start with pickup_line_to_rate
    # replace the rating with the new rating
    with open("static/pickup_lines.txt", "r") as f:
        lines = f.readlines()
    with open("static/pickup_lines.txt", "w") as f:
        for line in lines:
            if line.startswith(pickup_line_to_rate):
                line = pickup_line_to_rate + " " + rating + "\n"
            f.write(line)
    return render_template('index.html', pickup_line=pickup_line_to_rate)

@app.route('/save', methods=['POST'])
def save_pickup_line():
    pickup_line_to_save = request.form.get('pickup_line_to_save')
    #save to static/pickup_lines.txt
    with open("static/pickup_lines.txt", "a") as f:
        f.write(pickup_line_to_save + "\n")
    return render_template('index.html', pickup_line=pickup_line_to_save)

# Function to choose a random phrase
def random_choice(phrase_list):
    return random.choice(phrase_list)

# Main function
def main(phrase=None):
    if phrase is None:
        phrase = random_choice(phrase_list)

    input_prompt = base_prompt + phrase + " use puns and humor to make the pick-up line funny and respectful. Not too desperate but not too cocky. Ignore references to chastity. Careful not to insult other religions or holy places. Keep things non sexual. Don't mention long term relationships."

    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a witty chatbot that creates humorous and respectful pick-up lines for BYU students."
            },
            {
                "role": "user",
                "content": input_prompt,
            }
        ]
    )

    # print(chat_completion)
    response_content = chat_completion.choices[0].message.content if chat_completion.choices else "No response generated."
    return response_content
    


# Example usage
if __name__ == '__main__':
    app.run(debug=True)
    # phrase_input = ""
    # if len(sys.argv) > 1:
    #     for arg in sys.argv[1:]:
    #         phrase_input += arg + " "
    # pickup_line = main(phrase_input)
    # print(pickup_line)
    # should_save = input("Would you like to save this pickup line? (y/n)")
    # if should_save.lower() == "y":
# 
    #     # save to static/pickup_lines.txt
    #     with open("static/pickup_lines.txt", "a") as f:
    #         f.write(pickup_line + "\n")
    # else:
    #     print("Pickup line ignored ):")
