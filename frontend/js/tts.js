export async function speak(text, speachVoice = 'af_heart') {
    const response = await fetch("http://localhost:8880/v1/audio/speech", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            model: "kokoro",
            input: cleanTextForTTS(text),
            voice: speachVoice,
            response_format: "mp3",
            speed: 1.0
        })
    });

    if (!response.ok) {
        throw new Error(`TTS request failed: ${response.status}`);
    }

    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);

    const audio = new Audio(audioUrl);

    audio.addEventListener("ended", () => {
        URL.revokeObjectURL(audioUrl);
    });

    await audio.play();
}

function cleanTextForTTS(text) {
    return text
        // Remove code blocks
        .replace(/```[\s\S]*?```/g, " ")

        // Remove inline code markers
        .replace(/`([^`]+)`/g, "$1")

        // Markdown links: [text](url) → text
        .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")

        // Images: ![alt](url) → alt
        .replace(/!\[([^\]]*)\]\([^)]+\)/g, "$1")

        // Headers
        .replace(/^#{1,6}\s+/gm, "")

        // Bold / italic / strikethrough
        .replace(/(\*\*|__)(.*?)\1/g, "$2")
        .replace(/(\*|_)(.*?)\1/g, "$2")
        .replace(/~~(.*?)~~/g, "$1")

        // Bullet points
        .replace(/^\s*[-*+]\s+/gm, "")

        // Numbered lists
        .replace(/^\s*\d+\.\s+/gm, "")

        // Blockquotes
        .replace(/^\s*>\s?/gm, "")

        // Remove emojis
        .replace(/[\p{Extended_Pictographic}\uFE0F]/gu, "")

        // Clean excessive whitespace
        .replace(/\n{3,}/g, "\n\n")
        .trim();
}