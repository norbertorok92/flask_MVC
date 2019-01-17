from flask import Blueprint, render_template, request, jsonify
from mpa_admin_app.models import User, Post, Event
from mpa_admin_app import db, bcrypt
from mpa_admin_app.users.utils import save_picture

api = Blueprint('api', __name__)

# USER API
# ===============================================================
# GET ALL USERS
@api.route("/api/users", methods=['GET'])
def get_all_users():

	users = User.query.all()

	output = []

	for user in users:
		user_data = {}
		user_data['username'] = user.username
		user_data['email'] = user.email
		
		output.append(user_data)

	return jsonify({'users': output})

# GET ONE SPECIFIC USER
@api.route("/api/users/<string:username>", methods=['GET'])
def get_one_user(username):

	user = User.query.filter_by(username=username).first()

	posts_list = []
	events_list = []

	if not user:
		return jsonify({'message': 'No user found'})

	user_data = {}
	user_data['username'] = user.username
	user_data['email'] = user.email
	user_data['image_file'] = user.image_file

	posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).all()
	for post in posts:
		user_post = dict(
			title=post.title,
			content=post.content,
			code_snippet=post.code_snippet,
			date_posted=post.date_posted,
			author=post.user_id
		)
		
		posts_list.append(user_post)

	events = Event.query.filter_by(author=user).all()
	print(events)
	for event in events:
		user_event = dict(
			title=event.title,
			content=event.content,
			event_date=event.event_date,
			author=event.user_id
		)
		
		events_list.append(user_event)

	user_data['posts'] = posts_list
	user_data['events'] = events_list

	return jsonify({'user': user_data})

# CREATE A USER
@api.route("/api/users", methods=['POST'])
def create_user():
	data = request.get_json(force=True)

	hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

	new_user = User(username=data['username'], email=data['email'], password=hashed_password)

	db.session.add(new_user)
	db.session.commit()

	return jsonify({'message' : 'New user created!'})

# UPDATE A USER
@api.route("/api/users/<string:username>", methods=['PUT'])
def update_user(username):
	data = request.get_json(force=True)
	user = User.query.filter_by(username=username).first()

	if not user:
		return jsonify({'message': 'No user found'})

	user.username = data['username']
	user.email = data['email']

	db.session.commit()

	return jsonify({'message' : 'The user has been updated!'})

# DELETE A USER
@api.route("/api/users/<string:username>", methods=['DELETE'])
def delete_user(username):
	user = User.query.filter_by(username=username).first()

	if not user:
		return jsonify({'message': 'No user found'})

	db.session.delete(user)
	db.session.commit()

	return jsonify({'message' : 'The user has been deleted!'})

# # POST API
# # ===============================================================

# @api.route("/api/post", methods=['GET'])
# def get_all_posts():
# 	return ''

# @api.route("/api/post/<int:post_id>", methods=['GET'])
# def get_one_post(post_id):
# 	return ''

# @api.route("/api/post", methods=['POST'])
# def create_post():
# 	return ''

# @api.route("/api/post/<int:post_id>", methods=['PUT'])
# def update_post(post_id):
# 	return ''

# @api.route("/api/post/<int:post_id>", methods=['DELETE'])
# def delete_user(post_id):
# 	return ''