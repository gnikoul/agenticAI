from ollama import chat 
from .tools import available_functions, function_registry
import json


def get_response_stream(user_message):
    messages = [{'role': 'user', 'content': user_message}]

    while True:
        stream = chat(
            model='qwen3:8b',
            messages=messages,
            tools=available_functions,
            stream=True,
            think=True,
        )

        thinking = ''
        content = ''
        tool_calls = []

        done_thinking = False
        # accumulate the partial fields
        for chunk in stream:
            if chunk.message.thinking:
                thinking += chunk.message.thinking
                # print(chunk.message.thinking, end='', flush=True)
                yield json.dumps({"message": chunk.message.thinking,"state": "thinking"})
            if chunk.message.content:
                if not done_thinking:
                    done_thinking = True
                    # print('\n')
                    # yield json.dumps({"message": "\n","state": "content"})
                content += chunk.message.content
                # print(chunk.message.content, end='', flush=True)
                yield json.dumps({"message": chunk.message.content,"state": "content"})
                
            if chunk.message.tool_calls:
                tool_calls.extend(chunk.message.tool_calls)
                # print(chunk.message.tool_calls)
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