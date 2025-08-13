"""
Flask application entry point for the JobApp project.

This version of ``app.py`` eliminates any reliance on Selenium‑based
scrapers from the ``scraper/`` directory.  Instead, it uses a
dedicated API client module to fetch job listings via REST and a
database module to persist application information in MongoDB.

Routes:
    /            – Render the search form.
    /submit      – Handle search form submission and display results.
    /apply       – Persist a selected job application to the database.
    /applications – Display all saved job applications.

To run the application locally install dependencies from
``requirements.txt`` and set up a MongoDB instance.  You can override
the MongoDB URI via the ``MONGO_URI`` environment variable.  When run
with ``debug=True`` changes will be reloaded automatically.
"""

from flask import Flask, render_template, request, redirect, url_for

from api_client import get_jobs
from flask import Flask, jsonify, request
from bson import ObjectId
from database import connect, add_application, list_applications, update_application_status

app = Flask(__name__)


@app.route('/')
def index() -> str:
    """Render the landing page with the job search form."""
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit() -> str:
    """Handle the job search form submission.

    Extracts the job title from the submitted form, calls the REST API
    to fetch matching job postings and renders the result page with the
    returned data.
    """
    job_title = request.form.get('jobTitle', '').strip()
    # Fetch jobs from the external API.  If the API call fails or no
    # results are found ``jobs`` will be an empty list.
    jobs = get_jobs(job_title) if job_title else []
    return render_template('result.html', results=jobs, search_query=job_title)


@app.route('/apply', methods=['POST'])
def apply() -> str:
    """Save a selected job posting as an application in MongoDB.

    This route is expected to receive hidden form fields containing the
    details of the job posting.  After saving the record the user is
    redirected to the applications dashboard.
    """
    application_data = {
        'title': request.form.get('title', ''),
        'company': request.form.get('company', ''),
        'location': request.form.get('location', ''),
        'link': request.form.get('link', ''),
        # Store a default status of 'applied' or use the provided status
        'status': request.form.get('status', 'applied')
    }
    add_application(application_data)
    return redirect(url_for('applications'))


@app.route('/applications')
def applications() -> str:

    return render_template('applications.html')

def _to_json(doc):
    doc["_id"] = str(doc["_id"])
    return doc

@app.get("/api/applications")
def api_list_apps():
    coll = connect()
    apps = list_applications(coll)
    return jsonify([_to_json(a) for a in apps])

@app.post("/api/applications")
def api_add_app():
    data = request.get_json(force=True) or {}
    payload = {
        "company": data.get("company"),
        "title":   data.get("title"),
        "url":     data.get("url"),
        "status":  data.get("status", "wishlist"),
        "date":    data.get("date"),
    }
    coll = connect()
    new_id = add_application(coll, payload)  # should return inserted_id
    payload["_id"] = str(new_id)
    return jsonify(payload), 201

@app.patch("/api/applications/<id>")
def api_update_status(id):
    data = request.get_json(force=True) or {}
    status = data.get("status")
    if not status:
        return jsonify({"error": "status required"}), 400
    coll = connect()
    ok = update_application_status(coll, ObjectId(id), status)
    return jsonify({"ok": bool(ok)})

if __name__ == '__main__':
    app.run(debug=True)
