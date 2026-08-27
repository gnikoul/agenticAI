
import requests
import json

def get_response_stream(message: str, model: str = 'mistral:latest'):
    if not message:
        yield '\n'
        return
    payload = {
        "model": model,
        "stream": True,
        "messages": [{"role": "user", "content": message}]
    }
        
    with requests.post('http://localhost:11434/api/chat', json=payload, stream=True) as r:
        for line in r.iter_lines():
            if line:
                data = json.loads(line)
                data = data['message']['content']
                # yield json.dumps(data) + "\n"
                yield data