from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import tempfile

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'asd123jf23\/\/\/1231aa'
app.logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app.logger.handlers[0].setFormatter(formatter)
uri = 'mysql+mysqldb://taskman:taskman@localhost/taskmanager'
app.config['SQLALCHEMY_DATABASE_URI'] = uri
#app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600
db = SQLAlchemy(app)

oid_file = tempfile.mkdtemp()


