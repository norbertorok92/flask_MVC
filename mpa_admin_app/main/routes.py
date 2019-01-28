from flask import Blueprint, render_template, request
from mpa_admin_app.models import Post, User, Event, Role, Comment
from mpa_admin_app.posts.forms import PostForm
from mpa_admin_app.events.forms import EventForm

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home", methods=['GET', 'POST'])
def home():
	# import ipdb; ipdb.set_trace()
	postForm = PostForm()
	eventForm = EventForm()
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
	users = User.query.all()
	events = Event.query.order_by(Event.event_date.desc()).all()
	comments = Comment.query.all()
	return render_template('home.html', title='Home', postForm=postForm, eventForm=eventForm, posts=posts, users=users, events=events, comments=comments)

