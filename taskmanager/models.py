from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import desc
from sqlalchemy.orm import column_property, object_session
from sqlalchemy import *
from sqlalchemy import event
from datetime import datetime
import config

db = config.db

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

    @property
    def task_count(self):
	return object_session(self).\
	    scalar(
		select([func.count(Task.id)]).\
		    where(Task.complete==False).\
		    where(Task.tags.contains(self)))

user_list = db.Table('user_list', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('list_id', db.Integer, db.ForeignKey('list.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    lists = db.relationship("List", secondary=user_list, backref="users", cascade="delete")
    openid = db.Column(db.String(255))
    default_list = db.Column(db.Integer)
    created = db.Column(db.DateTime)

class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    tasks = db.relationship("Task",
	primaryjoin="and_(Task.list==List.id, Task.complete==False)",
	order_by=desc(Task.priority))
    tags = db.relationship("Tag", order_by="Tag.name")

class Options(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(20))
    value = db.Column(db.String(20))
    label = db.Column(db.String(50))
    

def update_task_timestamp(mapper, connection, target):
    target.last_update = datetime.now()

event.listen(Task, 'before_insert', update_task_timestamp)
event.listen(Task, 'before_update', update_task_timestamp)
