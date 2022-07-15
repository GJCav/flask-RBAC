from flask import session
from app.auth.model import Entity
from . import router

from .model import db, Entity

@router.route("/test")
def test():
    return {
        "test": "hello"
    }


@router.route("/login/<name>")
def login(name):
    user = db.session.query(Entity).filter(Entity.name == name).one_or_none()
    if user:
        session["name"] = name
        session.permanent = True
        return {
            "name": "name"
        }
    else:
        session.clear()
        return {
            "name": "null"
        }


@router.route("/profile")
def profile():
    return dict(session)