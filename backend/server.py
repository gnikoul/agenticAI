from flask import Flask, Response, request
from .agent import get_response_stream
import time


def server():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return 'hello world'
    
    @app.route("/agent/send_message", methods=['POST'])
    def agent_send_message():
        message = request.form["message"]
        image_file = request.files.get("image")
        photo_file = request.files.get("photo")
        image = None
        photo = None
        if image_file:
            image = image_file.read()
        if photo_file:
            print(photo_file)
            photo = photo_file.read()
        ollama_response = get_response_stream(message, [image, photo])
        stop = time.perf_counter()
        return Response(
            ollama_response,
            mimetype="application/x-ndjson"
        )
        # return ""
    return app
