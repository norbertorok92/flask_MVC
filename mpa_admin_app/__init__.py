from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from mpa_admin_app.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

mail = Mail()


def create_app(config_class=Config):
  app = Flask(__name__)
  app.config.from_object(Config)

  db.init_app(app)
  bcrypt.init_app(app)
  login_manager.init_app(app)
  mail.init_app(app)

  from mpa_admin_app.main.routes import main
  from mpa_admin_app.users.routes import users
  from mpa_admin_app.posts.routes import posts
  from mpa_admin_app.events.routes import events
  from mpa_admin_app.members.routes import members
  from mpa_admin_app.api.routes import api
  from mpa_admin_app.errors.handlers import errors
  app.register_blueprint(main)
  app.register_blueprint(users)
  app.register_blueprint(posts)
  app.register_blueprint(events)
  app.register_blueprint(members)
  app.register_blueprint(api)
  app.register_blueprint(errors)

  return app