from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from mpa_admin_app import db
from mpa_admin_app.models import Post, Comment
from mpa_admin_app.posts.forms import PostForm

posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
	postForm = PostForm()
	if postForm.validate_on_submit():
		path = request.form['path']
		post = Post(title = postForm.title.data, content = postForm.content.data, code_snippet = postForm.code_snippet.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post has been created!', 'success')
		
		return redirect(path)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	updatePost = PostForm()
	if updatePost.validate_on_submit():
		post.title = updatePost.title.data
		post.content = updatePost.content.data
		post.code_snippet = updatePost.code_snippet.data
		db.session.commit()
		flash('Your post has been updated!', 'success')
		return redirect(url_for('main.home', post_id=post.id))
	elif request.method == 'GET':
		updatePost.title.data = post.title
		updatePost.content.data = post.content
		updatePost.code_snippet.data = post.code_snippet
	return render_template('create_post.html', title='Update Post', form=updatePost, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
	path = request.form['path']

	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted!', 'success')
	return redirect(path)

