import $ from 'jquery';
import { getUserMessage, clearInput, appendMessageToHistory, StreamAgentMessage } from './dom.js';
import { getAgentStreamResponse } from '../agent/main.js'
import { speak } from '../tts.js'
import { sttRun } from '../stt.js'


$('#userInput').on('keydown', async function(e){
    if (e.which == 13) {
        dispatch_message();
    }
});


$("#micButton").on("click", async () => {
    
    const inputArea = {write: text => $('#userInput').val(text)};
    const user_input = await sttRun(inputArea);
    $('#userInput').val(user_input);
    dispatch_message();
});

async function dispatch_message() {
    const userMessage = getUserMessage();
    clearInput();
    appendMessageToHistory(userMessage, 'User');
    const agentMessageId = appendMessageToHistory('', 'Agent');
    const response = await getAgentStreamResponse(userMessage);
    StreamAgentMessage(response, agentMessageId)
        .then(async text => {
            // const response = await getAgentStreamResponse(
            //     'Create a natural speaking text from the below text. This will be used in a text-to-speech model: ' + text
            // );
            // const reader = response.body.getReader();
            // const decoder = new TextDecoder();
            // let textToBeSpoken = '';
            // while (true) {
            //     const { value, done } = await reader.read();

            //     if (done) {
            //         break;
            //     }
            //     const chunk = JSON.parse(decoder.decode(value, { stream: true }));
            //     const message = chunk.message;
            //     textToBeSpoken+=message;
            // }

            speak(text);
        });
}