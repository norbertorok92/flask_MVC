from mpa_admin_app import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = create_app()

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand) 
#command will be python manage.py db and from MigrateCommand we will use three commands:
# 1. init (python manage.py db init) - creates a new migration repository
# 2. migrate (python manage.py db migrate) - autogenerate a migration file
# 3. upgrade (python manage.py db upgrade) - takes the migration and run it


if __name__ == '__main__':
    manager.run()

