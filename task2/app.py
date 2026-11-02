from flask import Flask, request, jsonify
import secrets
import hmac

app = Flask(__name__)

# Generate 3 unique API keys
API_KEYS = {
    "Consumer 1": secrets.token_urlsafe(32),
    "Consumer 2": secrets.token_urlsafe(32),
    "Consumer 3": secrets.token_urlsafe(32)
}

# Display keys for local testing
print("\n===== API KEYS =====")
for consumer, key in API_KEYS.items():
    print(consumer, ":", key)
print("====================")


@app.route('/process', methods=['POST'])
def process_text():

    supplied_key = request.headers.get('X-API-Key')

    # Validate API key
    valid_key = any(
        hmac.compare_digest(supplied_key, key)
        for key in API_KEYS.values()
    ) if supplied_key else False

    if not valid_key:
        return jsonify({
            "error": "Invalid or missing API key"
        }), 401

    data = request.get_json(silent=True)

    if not data or not isinstance(data.get("text"), str):
        return jsonify({
            "error": "Please provide text as a JSON string"
        }), 400

    processed_text = data["text"].upper()

    return jsonify({
        "message": "Text processed successfully",
        "processed_text": processed_text
    }), 200


if __name__ == '__main__':
    app.run(debug=False, port=5001, use_reloader=False)