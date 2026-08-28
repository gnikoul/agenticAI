import $ from 'jquery';
import { getUserMessage, clearInput, appendMessageToHistory, StreamAgentMessage } from './dom.js';
import { getAgentStreamResponse } from '../agent/main.js'


$('#userInput').on('keydown', async function(e){
    if (e.which == 13) {
        const userMessage = getUserMessage();
        clearInput();
        appendMessageToHistory(userMessage, 'User');
        const agentMessageId = appendMessageToHistory('', 'Agent');
        const response = await getAgentStreamResponse(userMessage);
        StreamAgentMessage(response, agentMessageId);
    }
});