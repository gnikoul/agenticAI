from .server import server
from flask_cors import CORS

app = server()

CORS(app, origins=["http://localhost:5173"])
app.run(port=5000)
