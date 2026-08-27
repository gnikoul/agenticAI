import $ from "jquery";

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
        .html(role + ': ' + message);
    newMessage.appendTo('#chatHistory');
    return currentID;
}

export async function StreamAgentMessage(stream, messageId){
    const reader = stream.body.getReader();
    const decoder = new TextDecoder();

    const $messageEl = $(`#chatHistory #${messageId}`)
    while (true) {
        const { value, done } = await reader.read();

        if (done) {
            break;
        }

        const chunk = decoder.decode(value, { stream: true });

        $messageEl.html($messageEl.html()+chunk);
    }
}