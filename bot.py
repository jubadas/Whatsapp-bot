from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import re

app = Flask(__name__)

# --- In-memory user language preference ---
user_language = {}  # {sender: "english" / "swahili"}

# --- Normalize slang function ---
def normalize_text(text):
    slang_map = {
        "sasa": "hello",
        "niaje": "hello",
        "poa": "fine",
        "freshi": "fine",
        "vipi": "how are you",
        "mambo": "hello",
        "uko aje": "how are you",
    }
    text = text.lower()
    for slang, meaning in slang_map.items():
        text = re.sub(rf"\b{slang}\b", meaning, text)
    return text

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").strip().lower()
    sender = request.values.get("From")

    # Normalize slang
    incoming_msg = normalize_text(incoming_msg)

    resp = MessagingResponse()
    msg = resp.message()

    # --- Language switching ---
    if "swahili" in incoming_msg:
        user_language[sender] = "swahili"
        reply = "Umechagua Kiswahili ✅. Karibu kwenye huduma yetu ya biashara!"
    elif "english" in incoming_msg:
        user_language[sender] = "english"
        reply = "You have switched to English ✅. Welcome to our business service!"
    else:
        lang = user_language.get(sender, "english")  # default English

        # --- Bot responses ---
        if lang == "english":
            if "hello" in incoming_msg or "hi" in incoming_msg:
                reply = "Hello 👋! Welcome to *Your Business Name*. We offer top-quality safari & tour services. Type 'info' to learn more."
            elif "info" in incoming_msg:
                reply = "🌍 *Your Business Name*:\n- Safari Packages 🐘\n- Luxury Camps 🏕️\n- Guided Tours 🚙\nVisit our website: https://uni.tech.oloshobotours.co.ke/"
            elif "bye" in incoming_msg:
                reply = "Goodbye! 👋 We look forward to serving you again."
            else:
                reply = "Sorry, I didn’t understand. Type 'info' for business details or 'swahili' to switch language."
        else:  # Swahili Mode
            if "hello" in incoming_msg or "hi" in incoming_msg:
                reply = "Habari 👋! Karibu *Huduma za Biashara Yetu*. Tunatoa huduma bora za safari na utalii. Andika 'maelezo' ujifunze zaidi."
            elif "maelezo" in incoming_msg or "info" in incoming_msg:
                reply = "🌍 *Biashara Yetu*:\n- Safari Packages 🐘\n- Luxury Camps 🏕️\n- Guided Tours 🚙\nTembelea tovuti yetu: https://uni.tech.oloshobotours.co.ke/"
            elif "bye" in incoming_msg:
                reply = "Kwaheri! 👋 Tunatarajia kukuhudumia tena."
            else:
                reply = "Samahani, sijaelewa. Andika 'maelezo' kupata huduma zaidi au 'english' kubadilisha lugha."

    msg.body(reply)
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

