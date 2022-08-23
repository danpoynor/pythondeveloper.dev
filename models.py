"""Project model"""
import csv
import os
from datetime import datetime

from dotenv import load_dotenv  # type: ignore
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


# Load environment variables into the os environment
load_dotenv()

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config["TEMPLATES_AUTO_RELOAD"] = True

# To disable FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS set it to False.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv(
    'SQLALCHEMY_DATABASE_URI')


# This next line takes care of session and declarative base.
db = SQLAlchemy(app)


def clean_date(date_str: str) -> datetime:
    """Clean date string from user input.

    Split date values from format mm/dd/yyyy into separate variables,
    then convert to datetime object format year, month, day

    Args:
        date_str (str): String to interpret as a date.

    Returns:
        datetime.datetime: Date in datetime object format.
    """
    split_date = date_str.split('/')
    date = datetime(int(split_date[2]), int(split_date[0]), int(split_date[1]))
    return date


def check_project_exists(title_to_check: str) -> bool:
    """Check if project already exists in database.

    Note: I moved this outside the class to avoid pylint(not-callable) warning.
    """
    if Project.query.filter_by(title=title_to_check).one_or_none():
        return True
    return False


class Project(db.Model):
    """Project class"""
    # __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    date_created = db.Column(db.DateTime, nullable=False,
                             default=datetime.now)
    description = db.Column(db.String(500), nullable=False)
    skills_practiced = db.Column(db.String(100), nullable=False)
    github_link = db.Column(db.String(100), nullable=False)

    def add_csv_data(self):
        """Add projects from a csv file."""
        with open('projects.csv', encoding='UTF-8') as csvfile:
            # Using csv.DictReader to read the csv file and use the first row
            # as fieldnames and as the dictionary keys used to assign values with.
            # REF: https://docs.python.org/3.8/library/csv.html#csv.DictReader
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Check if project already exists in the database
                if check_project_exists(row['title']) is False:
                    new_project = Project(
                        # Use the dictionary keys to assign values to the
                        # corresponding columns in the database.
                        title=row['title'],
                        description=row['description'],
                        skills_practiced=row['skills_practiced'],
                        github_link=row['github_link'],
                        date_created=clean_date(row['date_created']))
                    self.add(new_project)
        self.commit()

    def __repr__(self):
        return f'''<Project: {self.title: str}
        Date Updated: {self.date_created: date}
        Description: {self.description: str}
        Skills Practiced: {self.skills: str}
        GitHub Link: {self.github_link: str}>'''
