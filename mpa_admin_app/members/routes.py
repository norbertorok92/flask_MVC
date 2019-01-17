from flask import Blueprint, render_template, request
from mpa_admin_app.models import Post, User, Event, Role

members = Blueprint('members', __name__)


@members.route("/members")
def membership():
	users = User.query.all()
	return render_template('members.html', title='Members', users=users)
