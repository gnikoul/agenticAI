const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

const recognition = new SpeechRecognition();

recognition.lang = "en-US";
recognition.continuous = false;
recognition.interimResults = true;

export function sttRun(output) {
    return new Promise((resolve, reject) => {
        recognition.onresult = (event) => {
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const message = event.results[i][0].transcript;
                if (output) {
                    output.write(message);
                }
                if (event.results[i].isFinal) {
                    resolve(message);
                }
            }
        };

        recognition.onerror = (event) => {
            reject(event.error);
        };

        recognition.onend = () => {
            // Don't resolve here
        };

        recognition.start();
    });
}