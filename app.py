from flask import Flask, render_template, jsonify, abort, request
import openai
# from dotenv import load_dotenv
import os
from openai.error import RateLimitError
from tempfile import NamedTemporaryFile

# load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
uri = '/api/'


def generate_prompt(prompt):
    return """Suggest a enginering prompt for créate a beautiful images:
    Prompt: a cute girl halloween
    Prompt engineering: The personification of the Halloween holiday in the form of a cute girl with short hair and a villain's smile, (((cute girl)))cute hats, cute cheeks, unreal engine, highly detailed, artgerm digital illustration, woo tooth, studio ghibli, deviantart, sharp focus, artstation, by Alexei Vinogradov bakery, sweets, emerald eyes
    Prompt: a man Victorinan old
    Prompt engineering: portrait of a rugged 19th century man with mutton chops in a jacket, victorian, concept art, detailed face, fantasy, close up face, highly detailed, cinematic lighting, digital art painting by greg rutkowski
    Prompt: {}
    Prompt engineering:""".format(
        prompt.capitalize()
    )


def completion(p):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"{generate_prompt(p)}",
        max_tokens=200,
        temperature=0.8
    )
    return response.choices[0].text


def chat_completion(words, content):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": content},
                {"role": "user", "content": words}
            ]
        )
        content = response.choices[0].message.content
    except RateLimitError:
        content = "The server is experiencing a high volume of requests. Please try again later."
    return content


def dalle(prompt):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        response['data'][0]['url']
        content = response['data'][0]['url']
    except RateLimitError:
        content = "The server is experiencing a high volume of requests. Please try again later."
    return content


def voice_text(x):
    audio_file = open(x, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]


def translate_text(sentence):
    return chat_completion(sentence, f"Actua como un traductor profesional, experto en varias lenguas. Traduce el siguiente texto a inglés: ")


@app.route("/")
def home():
    return render_template('index.html')


# @app.route(uri+'transcript', methods=['POST'])
# def handler():
#     if not request.files:
#         # If the user didn't submit any files, return a 400 (Bad Request) error.
#         abort(400)

#     # For each file, let's store the results in a list of dictionaries.
#     results = []

#     # Loop over every file that the user submitted.
#     for filename, handle in request.files.items():
#         # Create a temporary file.
#         # The location of the temporary file is available in `temp.name`.
#         temp = NamedTemporaryFile()
#         # Write the user's uploaded file to the temporary file.
#         # The file will get deleted when it drops out of scope.
#         handle.save(temp)
#         # Let's get the transcript of the temporary file.
#         result = openai.Audio.transcribe("whisper-1", temp)
#         # result = model.transcribe(temp.name)
#         # Now we can store the result object for this file.
#         results.append({
#             'filename': filename,
#             'transcript': result['text'],
#         })

#     # This will be automatically converted to JSON.
#     return {'results': results}


# @app.route(uri+'transcript', methods=['GET'])
# def transcript():
#     if request.method == 'GET':
#         content = "Invalid method!"
#     else:
#         if request.json:
#             prompt = request.json.get(
#                 'text') if request.json.get('text') else None
#             print("prompt")
#             translate = translate_text(prompt.capitalize())
#             content = jsonify({'transcript': translate})
#     return content


@app.route(uri+'translate', methods=['GET', 'POST'])
def get_translate():
    if request.method == 'GET':
        content = "Invalid method!"
    else:
        if request.json:
            prompt = request.json.get(
                'text') if request.json.get('text') else None
            translate = translate_text(prompt.capitalize())
            content = jsonify({'translate': translate})
    return content


@app.route(uri+'magic', methods=['GET', 'POST'])
def make_magic():
    if request.method == 'GET':
        content = "Invalid method!"
    else:
        if request.json:
            prompt = request.json.get(
                'text') if request.json.get('text') else None
            prompt_engineering = completion(prompt)
            content = jsonify({'new_prompt': prompt_engineering})
    return content


@app.route(uri+'draw', methods=['GET', 'POST'])
def make_art():
    if request.method == 'GET':
        content = "Invalid method!"
    else:
        if request.json:
            prompt = request.json.get(
                'text') if request.json.get('text') else None
            if prompt:
                image = dalle(prompt)
                content = jsonify({'image': image})
            else:
                content = "No prompt!"
    return content


if __name__ == '__main__':
    app.run(debug=True)
