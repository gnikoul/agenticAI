// import $ from 'jquery';
import { BACKEND_URL } from '../config.js'

export async function getAgentStreamResponse(message){
    const response = await fetch(
        BACKEND_URL + "/agent/send_message",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                message: message
            })
        }
    );
    return response;
}