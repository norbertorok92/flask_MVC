from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from mpa_admin_app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default='def_profile_pic.jpg')
	subscribedTo = db.Column(db.String(20), nullable=False, default='visitor')
	user_role = db.Column(db.String, db.ForeignKey('role.id'), nullable=False, default='visitor')
	posts = db.relationship('Post', backref='author', uselist=True, cascade="all, delete-orphan")
	comments = db.relationship('Comment', backref='author', uselist=True, cascade="all, delete-orphan")
	events = db.relationship('Event', backref='author', uselist=True, cascade="all, delete-orphan")


	def get_reset_token(self, expires_sec=1800):
		s = Serializer(current_app.app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	# staticmethod because we're just telling python not to expect self as an argument, only to expect token as an arg.
	def verify_reset_token(token):
		s = Serializer(current_app.app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.user_role}')"

	def to_dict(self):
		return dict(id=self.id, username=self.username, user_role=self.user_role)


class Post(db.Model):
	__tablename__ = 'post'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content = db.Column(db.Text, nullable=False)
	code_snippet = db.Column(db.Text)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	comments = db.relationship('Comment', backref='postId', uselist=True, cascade="all, delete-orphan")

	def __repr__(self):
		return f"Post('{self.title}', '{self.date_posted}', '{self.comments}')"


class Comment(db.Model):
	__tablename__ = 'comment'
	id = db.Column(db.Integer, primary_key=True)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content = db.Column(db.Text, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

	def __repr__(self):
		return f"Comment('{self.content}', '{self.date_posted}', '{self.post_id}')"

	def to_dict(self):
		return dict(id=self.id, date_posted=self.date_posted, content=self.content, author=self.author.to_dict(), post_id=self.post_id)


class Event(db.Model):
	__tablename__ = 'event'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	content = db.Column(db.Text, nullable=False)
	event_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
		return f"Event('{self.title}', '{self.event_date}')"


class Role(db.Model):
	__tablename__ = 'role'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	description = db.Column(db.String(1000), nullable=False)
	members = db.relationship('User', backref='role', uselist=True, cascade="all, delete-orphan")

	def __repr__(self):
		return f"Role('{self.id}', '{self.title}', '{self.members}'"
