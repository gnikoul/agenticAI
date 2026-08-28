import $ from "jquery";
import { marked } from "marked";

export function getUserMessage() {
    return $('#userInput').val();
}

export function clearInput() {
    $('#userInput').val('');
}

let currentID=0;
export function appendMessageToHistory(message, role){
    currentID++;
    let newMessage = $('<div>')
        .attr('id', currentID)
        .attr('data-role', role.toLocaleLowerCase())
        .html(message);
    newMessage.appendTo('#chatHistory');
    return currentID;
}

export async function StreamAgentMessage(stream, messageId){
    const reader = stream.body.getReader();
    const decoder = new TextDecoder();

    const $chatHistory = $('#chatHistory');
    const $messageEl = $(`#chatHistory #${messageId}`)
    let current_state = '';
    let stateId=0;
    let $current_div = undefined;
    let markdown = "";
    while (true) {
        const { value, done } = await reader.read();

        if (done) {
            break;
        }

        const chunk = JSON.parse(decoder.decode(value, { stream: true }));
        const message = chunk.message;
        const state = chunk.state;
        if (state!==current_state){
            markdown='';
            current_state = state
            stateId++;
            const toAppend = $('<div>')
                .attr('data-state', state)
                .attr('data-state-id', stateId)
            $messageEl.append(toAppend);
            $current_div = $messageEl.find(`div[data-state-id=${stateId}]`);
        }
        markdown += message;
        console.log(state);
        const toPrint = state==='content'?marked.parse(markdown):markdown;

        $current_div.html(toPrint);
        $chatHistory.scrollTop($chatHistory[0].scrollHeight);
    }
}