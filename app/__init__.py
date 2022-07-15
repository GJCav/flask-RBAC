from flask import Flask
from config import DefaultConfig

app = Flask("toy_RBAC")
app.config.from_object(DefaultConfig)

from . import model
model.init(app)

from . import auth

app.register_blueprint(auth.router)