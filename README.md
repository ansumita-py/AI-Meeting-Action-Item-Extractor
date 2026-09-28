# AI Meeting Action-Item Extractor

## Project Overview
This beginner-friendly Python project converts a meeting transcript into structured action items containing:
- Task
- Owner
- Deadline
- Confidence
- Status

## Approach
1. Meeting transcript is entered in a simple Flask web interface.
2. The transcript is cleaned and segmented into sentences.
3. Action-oriented sentences are detected.
4. Python NLP-style extraction rules identify the task, owner and deadline.
5. Validation checks identify missing owners, missing deadlines and duplicate tasks.
6. Results are displayed in a table.

### AI / Transformer Extension
The project is structured so a transformer/LLM extraction layer can be added in `extractor.py`. For a beginner submission, the included extractor works without an API key or model download, making the project easy to run and demonstrate.

## How to Run
1. Install Python 3.10 or newer.
2. Open the project folder in VS Code.
3. Open the terminal.
4. Run:
   `pip install -r requirements.txt`
5. Run:
   `python app.py`
6. Open the local Flask address shown in the terminal, normally:
   `http://127.0.0.1:5000`

## Example
Input:
`Rahul will prepare the project report by Friday.`

Output:
- Task: Rahul will prepare the project report by Friday
- Owner: Rahul
- Deadline: Friday
- Confidence: high percentage
- Status: Open

## Files
- `app.py` - Flask application
- `extractor.py` - extraction and validation logic
- `templates/index.html` - web interface
- `static/style.css` - styling
- `sample_transcript.txt` - sample input
- `requirements.txt` - Python dependency list
- `project_report.pdf` - project report
