from flask import Blueprint
from app import app

router = Blueprint("auth", __name__)

from . import header_session
header_session.patch_session(app)

from . import model
from . import api