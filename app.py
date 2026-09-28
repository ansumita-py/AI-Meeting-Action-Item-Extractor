from flask import Flask, render_template, request
from extractor import extract_action_items

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    results = []
    error = ""

    if request.method == "POST":
        transcript = request.form.get("transcript", "").strip()

        if not transcript:
            error = "Please enter or upload a meeting transcript."
        else:
            results = extract_action_items(transcript)

    return render_template(
        "index.html",
        transcript=transcript,
        results=results,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)
