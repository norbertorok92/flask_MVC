from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from mpa_admin_app import db
from mpa_admin_app.models import Comment
from mpa_admin_app.comments.forms import CommentForm

comments = Blueprint('comments', __name__)


@comments.route("/comment/<int:post_id>", methods=['GET', 'POST'])
@login_required
def new_comment(post_id):
	comment = Comment(content=request.form['addComment'], post_id=post_id, author=current_user)
	path = request.form['path']
	db.session.add(comment)
	db.session.commit()
	flash('Your comment has been posted!', 'success')
	
	return redirect(path)


# @comments.route("/post/<int:post_id>")
# def post(post_id):
# 	post = Post.query.get_or_404(post_id)
# 	return render_template('post.html', title=post.title, post=post)


# @comments.route("/comment/<int:comment_id>/edit", methods=['GET', 'POST'])
# @login_required
# def edit_comment(comment_id):
# 	comment = Comment.query.get_or_404(comment_id)
# 	if comment.author != current_user:
# 		abort(403)
# 	editComment = CommentForm()
# 	if editComment.validate_on_submit():
# 		comment.content = editComment.content.data
# 		db.session.commit()
# 		flash('Your post has been updated!', 'success')
# 		return redirect(url_for('comments.post', post_id=post.id))
# 	elif request.method == 'GET':
# 		editComment.content.data = comment.content
# 	return render_template('create_post.html', title='Update Post', form=editComment, legend='Update Post')


@comments.route("/<string:page>/comment/<int:comment_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_comment(comment_id, page):
	comment = Comment.query.get_or_404(comment_id)
	
	db.session.delete(comment)
	db.session.commit()
	flash('Your comment has been deleted!', 'success')
	
	if page == 'profile':
		return redirect(page)
	else:
		return redirect(url_for('main.home'))
		

