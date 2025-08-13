"""
database.py
This module abstracts access to a MongoDB collection used to persist
information about job applications.  Encapsulating database calls in a
separate module makes it easy to swap out the underlying storage
technology or add additional operations without cluttering the Flask
application code.
"""

from typing import Dict, List
import os

from pymongo import MongoClient
from pymongo.collection import Collection

# Connection settings.  The MongoDB URI can be overridden via the
# ``MONGO_URI`` environment variable to point at a different
# deployment (for example a production cluster).  For local
# development the default points at localhost.
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

# Database and collection names.  Adjust these names as appropriate
# for your environment.  Keeping names in variables instead of inline
# strings makes them easier to update and reuse.
DB_NAME = os.environ.get("JOBAPP_DB_NAME", "job_app")
COLLECTION_NAME = os.environ.get("JOBAPP_COLLECTION", "applications")

# Establish the client and collection once at import time.  In a
# real‑world application you may want to handle connection errors
# gracefully or lazily connect on first use.  Here we assume that
# MongoDB is available when the module is imported.
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection: Collection = db[COLLECTION_NAME]


def add_application(application_data: Dict[str, str]) -> str:
    """Insert a new job application document into MongoDB.

    Args:
        application_data: A dictionary containing details about the job
            application.  Expected keys include ``title``, ``company``,
            ``location``, ``link`` and optionally ``status``.

    Returns:
        The string representation of the inserted document's ObjectId.
    """
    result = collection.insert_one(application_data)
    return str(result.inserted_id)


def get_all_applications() -> List[Dict[str, str]]:
    """Retrieve all job application documents from MongoDB.

    Returns:
        A list of dictionaries representing the stored job
        applications.  MongoDB returns documents with an ``_id`` field
        of type ``ObjectId``; we convert these IDs to strings for
        easier rendering in templates.
    """
    docs = []
    for doc in collection.find():
        # Convert ObjectId to string and remove the internal field
        doc["_id"] = str(doc["_id"])
        docs.append(doc)
    return docs
