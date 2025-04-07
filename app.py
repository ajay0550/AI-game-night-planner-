import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Use your API Key directly
GEMINI_API_KEY = "AIzaSyBKuBNPgbpqBUOIH-nzhxbOGsgeGuj54sg"

def get_game_recommendations(players, hours):
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"""
                        Recommend 5 fun family games for {players} players that last around {hours} hours.
                        Provide:
                        - Name
                        - Duration
                        - Minimum number of players
                        - A short description
                        Return the response in JSON format inside a markdown block like this:
                        ```json
                        {{ "games": [ ... ] }}
                        ```
                        """
                    }
                ]
            }
        ]
    }

    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 200:
        response_json = response.json()
        
        try:
            # Extract the text response from the AI output
            model_response = response_json["candidates"][0]["content"]["parts"][0]["text"]

            # Extract JSON content from markdown format
            json_start = model_response.find("{")
            json_end = model_response.rfind("}") + 1
            json_data = model_response[json_start:json_end]  

            return json.loads(json_data)  # Convert string JSON to actual JSON
        except (json.JSONDecodeError, KeyError, IndexError):
            return {"error": "Failed to parse AI response. Check API output format."}
    else:
        return {"error": f"API request failed with status code {response.status_code}"}

@app.route('/get-game-recommendations', methods=['POST'])
def recommend_games():
    data = request.get_json()
    players = data.get("players")
    hours = data.get("hours")

    recommendations = get_game_recommendations(players, hours)
    
    return jsonify(recommendations)  # Ensure the response matches frontend needs

if __name__ == '__main__':
    app.run(debug=True, port=5000)
