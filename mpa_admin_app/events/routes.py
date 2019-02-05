from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from mpa_admin_app import db
from mpa_admin_app.models import Event
from mpa_admin_app.events.forms import EventForm

events = Blueprint('events', __name__)


@events.route("/event/new", methods=['GET', 'POST'])
@login_required
def new_event():
	eventForm = EventForm()
	if eventForm.validate_on_submit():
		path = request.form['path']
		event = Event(title = eventForm.title.data, content = eventForm.content.data, author=current_user, event_date = eventForm.event_date.data)
		db.session.add(event)
		db.session.commit()
		flash('Your event has been created!', 'success')
		
		return redirect(path)


@events.route("/event/<int:event_id>/update", methods=['GET', 'POST'])
@login_required
def update_event(event_id):
	event = Event.query.get_or_404(event_id)
	if event.author != current_user:
		abort(403)
	updateEvent = EventForm()
	if updateEvent.validate_on_submit():
		event.title = updateEvent.title.data
		event.content = updateEvent.content.data
		event.event_date = updateEvent.event_date.data
		db.session.commit()
		flash('Your event has been updated!', 'success')
		return redirect(url_for('events.event', event_id=event.id))
	elif request.method == 'GET':
		updateEvent.title.data = event.title
		updateEvent.content.data = event.content
		updateEvent.event_date.data = event.event_date
	return render_template('create_event.html', title='Update Event', form=updateEvent, legend='Update Event')


@events.route("/event/<int:event_id>/delete", methods=['POST'])
@login_required
def delete_event(event_id):
	path = request.form['path']

	event = Event.query.get_or_404(event_id)
	if event.author != current_user:
		abort(403)
	db.session.delete(event)
	db.session.commit()
	flash('Your event has been deleted!', 'success')
	return redirect(path)

