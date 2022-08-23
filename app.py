"""Portfolio Web App"""
import os
from datetime import datetime
from typing import Dict, Literal

from flask import redirect, render_template, request, url_for

from models import Project, app, db


# Make project list available in all view templates using a context processor.
# Context processors run before the template is rendered.
# https://flask.palletsprojects.com/en/2.2.x/templating/#context-processors
@app.context_processor
# Create function that returns a list of all projects in the database.
def inject_projects() -> Dict[str, Project]:
    """Inject projects into all view templates."""
    return dict(projects=Project.query.order_by(Project.date_created.asc()).all())


@app.route('/')
def index():
    """Homepage."""
    return render_template('index.html')


@app.route('/projects/new', methods=['GET', 'POST'])
def add_project():
    """Add a new project."""
    # Create an empty default `project` value since project-form.html requires
    # it to be passed in to the template when editing an existing project.
    empty_project = None
    if request.form:
        new_project = Project(title=request.form['title'],
                              date_created=datetime.strptime(
                                  request.form['date_created'], '%Y-%m-%d'),
                              description=request.form['description'],
                              skills_practiced="|".join(
                                  [str(i).strip() for i in request.form['skills_practiced'].split(',') if i]),
                              github_link=request.form['github_link'])
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('project-create.html', project=empty_project)


@app.route('/projects/<int:project_id>')
def project(project_id: int):
    """View a project."""
    selected_project = Project.query.get_or_404(project_id)
    return render_template("project.html", project=selected_project)


@app.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id: int):
    """Edit a project."""
    project_to_edit = Project.query.get_or_404(project_id)
    if request.form:
        print(request.form)
        project_to_edit.title = request.form["title"]
        project_to_edit.description = request.form["description"]
        project_to_edit.date_created = datetime.strptime(
            request.form['date_created'], '%Y-%m-%d')
        # Split the skills input by comma, strip whitespace from beginning and
        # end of each skill, and join them back together with a pipe character
        # separating each skill to be stored in the database.
        project_to_edit.skills_practiced = "|".join(
            map(str.strip, request.form["skills_practiced"].split(',')))
        project_to_edit.github_link = request.form["github_link"]
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('project-edit.html', project_id=project_id, project=project_to_edit)


@app.route('/projects/<int:project_id>/delete', methods=['GET', 'POST'])
def delete_project(project_id: int):
    """Delete a project."""
    selected_project = Project.query.get_or_404(project_id)
    db.session.delete(selected_project)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')


@app.route('/contact')
def contact():
    """Contact page."""
    return render_template('contact.html')


# Invalid URL
@app.errorhandler(404)
def not_found(error: Exception) -> tuple[str, Literal[404]]:
    """404 error page."""
    return render_template('404.html', msg=error), 404


# Internal server error
@app.errorhandler(500)
def page_not_found(error: Exception):
    """500 error page."""
    return render_template('500.html', msg=error), 500


if __name__ == '__main__':
    db.create_all()
    Project.add_csv_data(db.session)
    app.run(port=os.getenv('PORT'), host=os.getenv('HOST'))  # type: ignore
