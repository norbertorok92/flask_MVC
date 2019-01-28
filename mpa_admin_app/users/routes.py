from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify, abort
from flask_login import login_user, current_user, logout_user, login_required
from mpa_admin_app import db, bcrypt
from mpa_admin_app.models import User, Post, Comment, Event
from mpa_admin_app.posts.forms import PostForm
from mpa_admin_app.events.forms import EventForm
from mpa_admin_app.users.forms import (RegistrationForm, LoginForm, UpdateProfileForm,
                                   RequestResetForm, ResetPasswordForm)
from mpa_admin_app.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	registrationForm = RegistrationForm()
	if registrationForm.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(registrationForm.password.data).decode('utf-8')
		user = User(username=registrationForm.username.data, email=registrationForm.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! You are now able to log in', 'success')
		return redirect(url_for('users.login'))
	return render_template('register.html', title='Register', form=registrationForm)


@users.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	loginForm = LoginForm()
	if loginForm.validate_on_submit():
		user = User.query.filter_by(username=loginForm.username.data).first()
		if user and bcrypt.check_password_hash(user.password, loginForm.password.data):
			login_user(user, remember=loginForm.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('main.home'))
		else:
			flash('Login Unsuccessful. Please check username and password', 'danger')
	return render_template('login.html', title='Login', form=loginForm)


@users.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('main.home'))


@users.route("/profile/<int:id>", methods=['GET', 'POST'])
@login_required
def profile(id):
	postForm = PostForm()
	eventForm = EventForm()
	user = User.query.filter_by(id=id).first()
	posts = Post.query.order_by(Post.date_posted.desc()).filter_by(author=user).all()
	comments = Comment.query.all()
	events = Event.query.order_by(Event.event_date.desc()).all()
	updateForm = UpdateProfileForm()
	if updateForm.validate_on_submit():
		if updateForm.picture.data:
			picture_file = save_picture(updateForm.picture.data)
			current_user.image_file = picture_file
		current_user.username = updateForm.username.data
		current_user.email = updateForm.email.data
		db.session.commit()
		flash('Your profile has been updated!', 'success')
		return redirect(url_for('users.profile', id=id))
	elif request.method == 'GET':
		updateForm.username.data = user.username
		updateForm.email.data = user.email
	return render_template('profile.html', title='Profile', form=updateForm, postForm=postForm, eventForm=eventForm, user=user, posts=posts, comments=comments, events=events)


@users.route("/user/<string:username>/promote", methods=['POST'])
@login_required
def promote_user(username):
	user = User.query.filter_by(username=username).first()

	if not user:
		return jsonify({'message': 'No user found', 'success' : False})

	if user.user_role == 'visitor':
		promoteToValue = 'member'
	elif user.user_role == 'member':
		promoteToValue = 'admin'
	else:
		promoteToValue = 'visitor'
	
	user.user_role = promoteToValue
	
	db.session.commit()

	flash('User has been promoted!', 'success')
	return redirect(url_for('members.membership'))


@users.route("/user/<string:username>/demote", methods=['POST'])
@login_required
def demote_user(username):
	user = User.query.filter_by(username=username).first()

	if not user:
		return jsonify({'message': 'No user found', 'success' : False})

	if user.user_role == 'admin':
		demoteToValue = 'member'
	elif user.user_role == 'member':
		demoteToValue = 'visitor'
	else:
		demoteToValue = 'visitor'

	user.user_role = demoteToValue

	db.session.commit()

	flash('User has been demoted!', 'success')
	return redirect(url_for('members.membership'))


@users.route("/user/<string:username>/delete", methods=['POST'])
def delete_user(username):
	user = User.query.filter_by(username=username).first()

	if not user:
		return jsonify({'message': 'No user found', 'success' : False})

	db.session.delete(user)
	db.session.commit()

	flash('User has been deleted!', 'success')
	return redirect(url_for('members.membership'))


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	reqPassWForm = RequestResetForm()
	if reqPassWForm.validate_on_submit():
		user = User.query.filter_by(email=reqPassWForm.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instruction to reset your password', 'info')
		return redirect(url_for('users.login'))
	return render_template('reset_request.html', title='Reset Password', form=reqPassWForm)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('users.reset_request'))
	resetForm = ResetPasswordForm()
	if resetForm.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(resetForm.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Your password has been updated! You are now able to log in', 'success')
		return redirect(url_for('users.login'))
	return render_template('reset_token.html', title='Reset Password', form=resetForm)