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
        image = None
        if image_file:
            image = image_file.read()
        ollama_response = get_response_stream(message, image)
        stop = time.perf_counter()
        return Response(
            ollama_response,
            mimetype="application/x-ndjson"
        )
        # return ""
    return app
