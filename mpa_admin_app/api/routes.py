from flask import Blueprint, render_template, request, jsonify
from flask_cors import CORS, cross_origin
from mpa_admin_app.models import User, Post, Event, Role, Comment
from mpa_admin_app import db, bcrypt
from mpa_admin_app.users.utils import save_picture
from datetime import datetime
from sqlalchemy import exc

api = Blueprint('api', __name__)
CORS(api, resources={r"/api/*": {"origins": "*"}})

# # ======================== REGISTER =====================
@api.route('/api/register', methods = ['POST'])
@cross_origin() # allow all origins all methods.
def register():
	data = request.get_json(force=True)
	username = data['username']
	password = data['password']
	email = data['email']
	print(password)
	if not username or not password:
		return jsonify({'message': 'Missing argument', 'success' : False}), 400 # missing arguments
	hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
	new_user = User(username = username, email = email, password = hashed_password)
	db.session.add(new_user)
	try:
		db.session.commit()
		return jsonify({'message' : 'New user created!', 'success' : True, 'userID': new_user.id, 'userRole': new_user.user_role }), 201
	except exc.IntegrityError:
		return jsonify({'message': 'User or email already exists', 'success' : False}), 409 # existing user
	except:
		return jsonify({'message': 'Something went terribly wrong', 'success' : False}), 500

# # ======================== LOGIN =====================
@api.route('/api/login', methods = ['POST'])
@cross_origin() # allow all origins all methods.
def login():
	data = request.get_json(force=True)
	username = data['username']
	password = data['password']
	user = User.query.filter_by(username = username).first()
	if user and bcrypt.check_password_hash(user.password, password):
		return jsonify({'message': 'Logged in as {}'.format(user.username), 'success' : True, 'userID': user.id, 'userRole': user.user_role }), 200
	else:
		return jsonify({'success' : False, 'message': 'Wrong credentials'}), 401

# ===============================================================
# USER API
# ===============================================================

# # ======================== GET ALL USERS =====================
@api.route("/api/users", methods=['GET'])
def get_all_users():

	users = User.query.all()

	output = []

	for user in users:
		user_data = {}
		user_data['id'] = user.id
		user_data['username'] = user.username
		user_data['email'] = user.email
		user_data['user_role'] = user.user_role
		user_data['subscribedTo'] = user.subscribedTo
		
		output.append(user_data)

	return jsonify({'users': output, 'success' : True})


# # ======================== GET ONE USER =====================
@api.route("/api/users/<int:user_id>", methods=['GET'])
def get_one_user(user_id):

	user = User.query.filter_by(id=user_id).first()

	posts_list = []
	events_list = []

	if not user:
		return jsonify({'message': 'No user found', 'success' : False})

	user_data = {}
	user_data['username'] = user.username
	user_data['email'] = user.email
	user_data['image_file'] = user.image_file
	user_data['user_role'] = user.user_role
	user_data['subscribedTo'] = user.subscribedTo
	user_data['id'] = user.id

	posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).all()
	for post in posts:
		comments_list = []
		
		comments = Comment.query.filter_by(post_id=post.id).all()
		for comment in comments:
			comments_list.append(comment.to_dict())
		
		user_post = dict(
			id=post.id,
			title=post.title,
			content=post.content,
			code_snippet=post.code_snippet,
			date_posted=post.date_posted,
			author=post.author.to_dict(),
			comments=comments_list
		)
		
		posts_list.append(user_post)

	events = Event.query.filter_by(author=user).all()

	for event in events:
		user_event = dict(
			title=event.title,
			content=event.content,
			event_date=event.event_date,
			author=event.author.to_dict()
		)
		
		events_list.append(user_event)

	user_data['posts'] = posts_list
	user_data['events'] = events_list

	return jsonify({'user': user_data, 'success' : True})


# # ======================== UPDATE USER =====================
@api.route("/api/users/<int:user_id>", methods=['PUT'])
def update_user(user_id):
	data = request.get_json(force=True)
	user = User.query.filter_by(id=user_id).first()

	if not user:
		return jsonify({'message': 'No user found', 'success' : False})

	user.username = data['username']
	user.email = data['email']

	db.session.commit()

	return jsonify({'message' : 'The user has been updated!', 'success' : True})


# # ======================== SUBSCRIBE TO ROLE =====================
@api.route("/api/users/<int:user_id>/subscribe", methods=['PUT'])
def sbuscribe_user(user_id):
	user = User.query.filter_by(id=user_id).first()

	if not user:
		return jsonify({'message': 'No user found', 'success' : False})

	if user.user_role == 'visitor':
		subscribeTo = 'member'
	else:
		subscribeTo = 'admin'
	
	user.subscribedTo = subscribeTo
	
	db.session.commit()

	return jsonify(
		{
			'message' : 'User subscribed!',
			'success' : True
		}
	)


# # ======================== PROMOTE USER =====================
@api.route("/api/users/<int:user_id>/promote", methods=['PUT'])
def promote_user(user_id):
	user = User.query.filter_by(id=user_id).first()

	if not user:
		return jsonify({'message': 'No user found', 'success' : False})

	if user.user_role == 'visitor':
		promoteToValue = 'member'
	elif user.user_role == 'member':
		promoteToValue = 'admin'
	else:
		promoteToValue = 'visitor'
	
	user.user_role = promoteToValue
	user.subscribedTo = promoteToValue
	
	db.session.commit()

	return jsonify(
		{
			'message' : 'The user has been promoted!',
			'success' : True
		}
	)


# # ======================== DEMOTE USER =====================
@api.route("/api/users/<int:user_id>/demote", methods=['PUT'])
def demote_user(user_id):
	user = User.query.filter_by(id=user_id).first()

	if not user:
		return jsonify({'message': 'No user found', 'success' : False})

	if user.user_role == 'admin':
		demoteToValue = 'member'
	elif user.user_role == 'member':
		demoteToValue = 'visitor'
	else:
		demoteToValue = 'visitor'

	user.user_role = demoteToValue
	user.subscribedTo = demoteToValue

	db.session.commit()

	return jsonify(
		{
			'message' : 'The user has been demoted!',
			'success' : True
		}
	)


# # ======================== DELETE USER =====================
@api.route("/api/users/<int:user_id>", methods=['DELETE'])
def delete_user(user_id):
	user = User.query.filter_by(id=user_id).first()

	if not user:
		return jsonify({'message': 'No user found', 'success' : False})

	db.session.delete(user)
	db.session.commit()

	return jsonify({'message' : 'The user has been deleted!', 'success' : True})


# # ===============================================================
# # POST API
# # ===============================================================

# # ======================== GET ALL POSTS ========================
@api.route("/api/posts", methods=['GET'])
def get_all_posts():

	posts = Post.query.order_by(Post.date_posted.desc()).all()

	output = []

	for post in posts:
		comments_list = []
		post_data = {}
		post_data['id'] = post.id
		post_data['title'] = post.title
		post_data['date_posted'] = post.date_posted
		post_data['content'] = post.content
		post_data['code_snippet'] = post.code_snippet
		post_data['author'] = post.author.to_dict()

		comments = Comment.query.filter_by(post_id=post.id).all()
		for comment in comments:
			comments_list.append(comment.to_dict())

		post_data['comments'] = comments_list
		
		output.append(post_data)

	return jsonify({'posts': output, 'success' : True})


# # ======================== GET ONE POST =========================
@api.route("/api/posts/<int:post_id>", methods=['GET'])
def get_one_post(post_id):
	post = Post.query.filter_by(id=post_id).first()

	comments_list = []

	if not post:
		return jsonify({'message': 'No post found', 'success' : False})

	post_data = {}
	post_data['title'] = post.title
	post_data['date_posted'] = post.date_posted
	post_data['content'] = post.content
	post_data['code_snippet'] = post.code_snippet
	post_data['author'] = post.user_id

	comments = Comment.query.filter_by(post_id=post_id).all()
	for comment in comments:
		comments_list.append(comment.to_dict())

	post_data['comments'] = comments_list

	return jsonify({'post': post_data, 'success' : True})


# # ======================== CREATE POST =========================
@api.route("/api/posts/<int:user_id>", methods=['POST'])
def create_post(user_id):
	user = User.query.filter_by(id=user_id).first()
	data = request.get_json(force=True)
	new_post = Post(title = data['title'], content = data['content'], code_snippet = data['code_snippet'], author=user)
	db.session.add(new_post)
	db.session.commit()

	return jsonify({'message' : 'New post created!', 'success' : True})


# # ======================== UPDATE POST =========================
@api.route("/api/posts/<int:post_id>", methods=['PUT'])
def update_post(post_id):
	data = request.get_json(force=True)
	post = Post.query.filter_by(id=post_id).first()

	if not post:
		return jsonify({'message': 'No post found', 'success' : False})

	post.title = data['title']
	post.content = data['content']
	post.code_snippet = data['code_snippet']

	db.session.commit()

	return jsonify({'message' : 'The post has been updated!', 'success' : True})


# # ======================== DELETE POST =========================
@api.route("/api/posts/<int:post_id>", methods=['DELETE'])
def delete_post(post_id):
	post = Post.query.filter_by(id=post_id).first()

	if not post:
		return jsonify({'message': 'No post found', 'success' : False})

	db.session.delete(post)
	db.session.commit()

	return jsonify({'message' : 'The post has been deleted!', 'success' : True})


# ===============================================================
# COMMENT API
# ===============================================================

# # ======================== POST COMMENT =======================
@api.route("/api/comment/<int:post_id>/<int:user_id>", methods=['POST'])
def post_comment(post_id, user_id):
	user = User.query.filter_by(id=user_id).first()
	data = request.get_json(force=True)
	comment = Comment(content = data['content'], post_id=post_id, author=user)
	db.session.add(comment)
	db.session.commit()

	return jsonify({'message' : 'Your comment has been posted!', 'success' : True})


# # ======================== DELETE COMMENT =======================
@api.route("/api/comment/<int:comment_id>", methods=['DELETE'])
def delete_comment(comment_id):
	comment = Comment.query.filter_by(id=comment_id).first()

	if not comment:
		return jsonify({'message': 'No comment found', 'success' : False})

	db.session.delete(comment)
	db.session.commit()

	return jsonify({'message' : 'The comment has been deleted!', 'success' : True})

# ===============================================================
# EVENT API
# ===============================================================

# # ======================== GET ALL EVENTS =====================
@api.route("/api/events", methods=['GET'])
def get_all_events():
	
	events = Event.query.order_by(Event.event_date.desc()).all()

	output = []

	for event in events:
		event_data = {}
		event_data['id'] = event.id
		event_data['title'] = event.title
		event_data['content'] = event.content
		event_data['event_date'] = event.event_date
		event_data['author'] = event.author.to_dict()
		
		output.append(event_data)

	return jsonify({'events': output, 'success' : True})


# # ======================== GET ONE EVENT =====================
@api.route("/api/events/<int:events_id>", methods=['GET'])
def get_one_event(events_id):
	event = Event.query.filter_by(id=events_id).first()

	if not event:
		return jsonify({'message': 'No event found', 'success' : False})

	event_data = {}
	event_data['title'] = event.title
	event_data['content'] = event.content
	event_data['event_date'] = event.event_date
	event_data['author'] = event.user_id

	return jsonify({'event': event_data, 'success' : True})


# # ======================== CREATE EVENT =====================
@api.route("/api/events/<int:user_id>", methods=['POST'])
def create_event(user_id):
	user = User.query.filter_by(id=user_id).first()
	data = request.get_json(force=True)

	datetime_object = datetime.strptime(data['event_date'], '%Y-%m-%d')
	new_event = Event(title = data['title'], content = data['content'], event_date = datetime_object, author=user)
	db.session.add(new_event)
	db.session.commit()

	return jsonify({'message' : 'New event created!', 'success' : True})


# # ======================== UPDATE EVENT =====================
@api.route("/api/events/<int:events_id>", methods=['PUT'])
def update_event(events_id):
	data = request.get_json(force=True)
	event = Event.query.filter_by(id=events_id).first()

	if not event:
		return jsonify({'message': 'No event found', 'success' : False})

	event.title = data['title']
	event.content = data['content']
	event.event_date = data['event_date']

	db.session.commit()

	return jsonify({'message' : 'The event has been updated!', 'success' : True})


# # ======================== DELETE EVENT =====================
@api.route("/api/events/<int:events_id>", methods=['DELETE'])
def delete_event(events_id):
	event = Event.query.filter_by(id=events_id).first()

	if not event:
		return jsonify({'message': 'No event found', 'success' : False})

	db.session.delete(event)
	db.session.commit()

	return jsonify({'message' : 'The event has been deleted!', 'success' : True})


# ===============================================================
# ROLE API
# ===============================================================

# # ======================== GET ALL ROLES =====================
@api.route("/api/roles", methods=['GET'])
def get_all_roles():
	
	roles = Role.query.all()

	output = []

	for role in roles:
		role_data = {}
		role_data['id'] = role.id
		role_data['title'] = role.title
		role_data['description'] = role.description
		
		output.append(role_data)

	return jsonify({'roles': output, 'success' : True})


# # ======================== UPDATE ROLE =====================
@api.route("/api/roles/<int:role_id>", methods=['PUT'])
def update_role(role_id):
	data = request.get_json(force=True)
	role = Role.query.filter_by(id=role_id).first()

	if not role:
		return jsonify({'message': 'No role found', 'success' : False})

	role.title = data['title']
	role.description = data['description']

	db.session.commit()

	return jsonify({'message' : 'The role has been updated!', 'success' : True})


# # ======================== DELETE ROLE =====================
@api.route("/api/roles/<int:role_id>", methods=['DELETE'])
def delete_role(role_id):
	role = Role.query.filter_by(id=role_id).first()

	if not role:
		return jsonify({'message': 'No role found', 'success' : False})

	db.session.delete(role)
	db.session.commit()

	return jsonify({'message' : 'The role has been deleted!', 'success' : True})