import os
import secrets
from flask import url_for, current_app
from flask_mail import Message
from mpa_admin_app import mail


def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	# os.path.splitext return us back two values, the f_name and f_ext, but we don't use f_name variable so we replace f_name with _
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_filename = random_hex + f_ext
	picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_filename)
	form_picture.save(picture_path)
	
	return picture_filename


def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender='noreply@mpademo.com', recipients=[user.email])
	msg.body = f'''To reset your password visit your following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made
'''
	mail.send(msg)