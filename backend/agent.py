import os
from ollama import chat 
from .tools import available_functions, function_registry
import json
from dotenv import load_dotenv
load_dotenv()

def get_response_stream(user_message):
    user_name = os.getenv("USER_NAME")
    agent_name = os.getenv("AGENT_NAME")
    messages = [{'role': 'system','content': f'Your name is {agent_name}. You are my AI assistant. My name is {user_name}.'},
            {'role': 'user', 'content': user_message+'/no_think'}
        ]

    while True:
        stream = chat(
            # model='qwen3:8b',
            # model='qwen3:4b',
            model='qwen3:1.7b',
            # model='qwen3:0.6b',
            # model='gemma4:e2b',
            # model='granite3.1-moe:3b',
            messages=messages,
            tools=available_functions,
            stream=True,
            think=False,
        )

        thinking = ''
        content = ''
        tool_calls = []

        done_thinking = False
        # accumulate the partial fields
        for chunk in stream:
            if chunk.message.thinking:
                thinking += chunk.message.thinking
                print('\033[90m' + chunk.message.thinking + '\033[0m', end='', flush=True)
                yield json.dumps({"message": chunk.message.thinking,"state": "thinking"})
            if chunk.message.content:
                if not done_thinking:
                    done_thinking = True
                    print('\n')
                    # yield json.dumps({"message": "\n","state": "content"})
                content += chunk.message.content
                print(chunk.message.content, end='', flush=True)
                yield json.dumps({"message": chunk.message.content,"state": "content"})
                
            if chunk.message.tool_calls:
                tool_calls.extend(chunk.message.tool_calls)
                print(chunk.message.tool_calls)
                f_string = str(chunk.message.tool_calls)
                yield json.dumps({"message": f_string,"state": "tool_call"})

        # append accumulated fields to the messages
        if thinking or content or tool_calls:
            messages.append({'role': 'assistant', 'thinking': thinking, 'content': content, 'tool_calls': tool_calls})

        if not tool_calls:
            break

        for call in tool_calls:
            f = function_registry.get(call.function.name, None)
            if f:
                result = f(**call.function.arguments)
            else:
                result = 'Unknown tool'
            messages.append({'role': 'tool', 'tool_name': call.function.name, 'content': result})