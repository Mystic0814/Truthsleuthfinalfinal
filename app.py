from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json
import re

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze_news():
    try:
        data = request.json
        if not data or "text" not in data:
            return jsonify({"error": "No text provided"}), 400

        news_text = data["text"].strip()
        if len(news_text) < 10:
            return jsonify({"error": "Please enter a longer text for analysis"}), 400

        prompt = f"""
You are TruthSleuth, an advanced fact-checking AI.
Your job is to determine the credibility of the following news or claim.

You have access to known internet knowledge and sources. You should reason step-by-step as if verifying from multiple references.

If you find 3 or more major credible sources confirming the news (e.g. Reuters, BBC, AP, NYT, etc.), 
set the credibility score to **100** and list those sources explicitly.

If fewer than 3 sources verify it, analyze possible misinformation, partial truth, or bias.
Give a score between 0–100 and explain your reasoning.

News Text:
{news_text}

Return ONLY valid JSON with this structure:
{{
  "score": <number 0-100>,
  "classification": "<Credible | Questionable | Likely Fake>",
  "sources": ["<source 1>", "<source 2>", ...],
  "reasoning": "<clear explanation of why you reached that score>"
}}
        """

        print(f"🔍 Received request for analysis: {news_text[:60]}...")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            messages=[
                {
                    "role": "system",
                    "content": "You are a media analyst AI that verifies factual accuracy based on known reputable data. Always respond with valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=700,
        )

        raw_text = response.choices[0].message.content.strip()
        print("🧩 Raw model response:", raw_text[:200])

        if raw_text.startswith("```"):
            raw_text = re.sub(r"^```(?:json)?|```$", "", raw_text, flags=re.MULTILINE).strip()

        try:
            result = json.loads(raw_text)
        except Exception:
            result = {
                "score": 50,
                "classification": "Questionable",
                "sources": [],
                "reasoning": "AI response format was invalid. Please retry.",
            }

        print("✅ Final structured result:", result)
        return jsonify(result)

    except Exception as e:
        print("❌ Backend error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
