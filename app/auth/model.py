# from flask.sessions import SecureCookieSessionInterface # 留给未来，考虑把session放在cookie之外？或者单独把token放在cookie之外

from email.policy import default
import enum
from app.model import db
from sqlalchemy import BigInteger, Enum, Integer, String, ForeignKey, Column
from sqlalchemy.orm import relationship
from app import app

BaseModel = db.Model


class Entity(BaseModel):
    __tablename__ = "entity"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), unique=True)
    expire_at = Column(BigInteger, default=0)

    groups = relationship("GroupAssociation", back_populates="member")


class Group(BaseModel):
    __tablename__ = "group"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), unique=True)
    expire_at = Column(BigInteger, default=0)

    members = relationship("GroupAssociation", back_populates="group")


class GroupAssociation(BaseModel):
    __tablename__ = "group_association"
    group_id = Column(ForeignKey(Group.id), primary_key=True)
    member_id = Column(ForeignKey(Entity.id), primary_key=True)
    expire_at = Column(BigInteger, default=0) # 临时加入组，但实现可能比较复杂，得手动写SQL查询了

    member = relationship(Entity, back_populates="groups")
    group = relationship(Group, back_populates="members")



print("----------- hello world")


with app.app_context():
    db.create_all()

    rst = db.session.query(Entity).filter(Entity.name == "u1").one_or_none()
    if not rst:
        print("add user and association")

        u1 = Entity(name="u1")
        u2 = Entity(name="u2")

        g1 = Group(name="g1")
        g2 = Group(name="g2")
        g3 = Group(name="g3")

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(g1)
        db.session.add(g2)
        db.session.add(g3)

        db.session.commit()

        a1 = GroupAssociation(group_id = g1.id, member_id = u1.id)
        a2 = GroupAssociation(group_id = g2.id, member_id = u2.id)
        a3 = GroupAssociation(group_id = g3.id, member_id = u1.id)
        a4 = GroupAssociation(group_id = g3.id, member_id = u2.id)

        db.session.add(a1)
        db.session.add(a2)
        db.session.add(a3)
        db.session.add(a4)
        db.session.commit()

with app.app_context():
    users = db.session.query(Entity).filter(Group.expire_at > 10).all()
    for u in users:
        print(f"{u.name}: {u.groups}")