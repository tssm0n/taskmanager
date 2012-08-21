from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#uri = 'sqlite:////tmp/test.db'
uri = 'mysql+mysqldb://taskman:taskman@localhost/taskmanager'
# mysql+mysqldb://<user>:<password>@<host>[:<port>]/<dbname>

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
db = SQLAlchemy(app)

task_tags = db.Table('task_tags', db.Model.metadata,
    db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    priority = db.Column(db.Integer)
    details = db.Column(db.Text)
    tags = db.relationship("Tag",
                    secondary=task_tags,
                    backref="tasks")
    last_update = db.Column(db.DateTime)

    def __repr__(self):
	return '<Task %s>' % self.id

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))

user_group = db.Table('user_group', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    groups = db.relationship("Group", secondary=user_group, backref="users")


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

class Options(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(20))
    value = db.Column(db.String(20))
    label = db.Column(db.String(50))
    
