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


@comments.route("/comment/<int:comment_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_comment(comment_id):
	path = request.form['path']

	comment = Comment.query.get_or_404(comment_id)
	
	db.session.delete(comment)
	db.session.commit()
	flash('Your comment has been deleted!', 'success')
	
	return redirect(path)
		

