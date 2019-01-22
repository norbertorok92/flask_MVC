from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from mpa_admin_app import db
from mpa_admin_app.models import Role, User
from mpa_admin_app.roles.forms import RoleForm

roles = Blueprint('roles', __name__)


@roles.route("/role/new", methods=['GET', 'POST'])
@login_required
def new_role():
	roleForm = RoleForm()
	if roleForm.validate_on_submit():
		role = Role(title = roleForm.title.data, description = roleForm.description.data)
		db.session.add(role)
		db.session.commit()
		flash('Role has been created!', 'success')
		return redirect(url_for('members.membership'))
	return render_template('create_role.html', title='Create New Role', form=roleForm, legend='New Role')


@roles.route("/role/<int:role_id>")
def role_page(role_id):
	role = Role.query.get_or_404(role_id)
	print(current_user.user_role)
	return render_template('role.html', title=role.title, role=role, user=current_user)


@roles.route("/role/<int:role_id>/update", methods=['GET', 'POST'])
@login_required
def update_role(role_id):
	role = Role.query.get_or_404(role_id)
	if current_user.user_role != 1:
		abort(403)
	updateRole = RoleForm()
	if updateRole.validate_on_submit():
		role.title = updateRole.title.data
		role.description = updateRole.description.data
		role.permissions = updateRole.permissions.data
		db.session.commit()
		flash('Your role has been updated!', 'success')
		return redirect(url_for('roles.role_page', role_id=role.id))
	elif request.method == 'GET':
		updateRole.title.data = role.title
		updateRole.description.data = role.description
		updateRole.permissions.data = role.permissions
	return render_template('create_role.html', title='Update Role', form=updateRole, legend='Update Role')


@roles.route("/role/<int:role_id>/delete", methods=['POST'])
@login_required
def delete_role(role_id):
	role = Role.query.get_or_404(role_id)
	if current_user.user_role != 1:
		abort(403)
	if role.title == 'admin' or role.title == 'visitor':
		flash('You cannot delete ADMIN or VISITOR role!', 'danger')
	db.session.delete(role)
	db.session.commit()
	flash('Your role has been deleted!', 'success')
	return redirect(url_for('members.membership'))