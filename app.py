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
from database import add_application, get_all_applications


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
    """Render the dashboard showing all saved job applications."""
    apps = get_all_applications()
    return render_template('applications.html', applications=apps)


if __name__ == '__main__':
    app.run(debug=True)
