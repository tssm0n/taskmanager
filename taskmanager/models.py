from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import desc

#uri = 'sqlite:////tmp/test.db'
uri = 'mysql+mysqldb://taskman:taskman@localhost/taskmanager'
# mysql+mysqldb://<user>:<password>@<host>[:<port>]/<dbname>

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

task_tags = db.Table('task_tags', db.Model.metadata,
    db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150),nullable=False)
    priority = db.Column(db.Integer,nullable=False)
    details = db.Column(db.Text)
    tags = db.relationship("Tag",
                    secondary=task_tags,
                    backref="tasks")
    last_update = db.Column(db.DateTime)
    complete = db.Column(db.Boolean,nullable=False)
    list = db.Column(db.Integer, db.ForeignKey('list.id'))

    def __repr__(self):
        return '<Task %s>' % self.id
    
    def priority_index(self):
        p = self.priority / 100000
        p = 10 - p
        if p == 0:
            p = 1
        if p > 10:
            p = 10
        return p

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    list = db.Column(db.Integer, db.ForeignKey('list.id'))
    parent = db.Column(db.Integer, db.ForeignKey('tag.id'))

user_list = db.Table('user_list', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('list_id', db.Integer, db.ForeignKey('list.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    lists = db.relationship("List", secondary=user_list, backref="users")
    default_list = db.Column(db.Integer)


class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    tasks = db.relationship("Task",
	primaryjoin="and_(Task.list==List.id, Task.complete==False)",
	order_by=desc(Task.priority))
    tags = db.relationship("Tag")

class Options(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(20))
    value = db.Column(db.String(20))
    label = db.Column(db.String(50))
    
