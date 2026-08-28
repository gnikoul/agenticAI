from flask import Flask, Response, request
from .agent import get_response_stream


def server():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return 'hello world'
    
    @app.route("/agent/send_message", methods=['POST'])
    def agent_send_message():
        message = request.form["message"]
        ollama_response = get_response_stream(message)
        return Response(
            ollama_response,
            mimetype="application/x-ndjson"
        )
        # return ""
    return app
