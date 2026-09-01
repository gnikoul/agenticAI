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
        start = time.perf_counter()
        print('in agent endpoint now', start)
        message = request.form["message"]
        ollama_response = get_response_stream(message)
        stop = time.perf_counter()
        print(f'returning from agent endpoint now {stop-start}')
        return Response(
            ollama_response,
            mimetype="application/x-ndjson"
        )
        # return ""
    return app
