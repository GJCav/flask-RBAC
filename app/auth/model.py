# from flask.sessions import SecureCookieSessionInterface # 留给未来，考虑把session放在cookie之外？或者单独把token放在cookie之外

import enum
from app.model import db
from sqlalchemy import BigInteger, Enum, Integer, String, ForeignKey, Column, Table, and_, or_
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app import app
import app.timetools as T

BaseModel = db.Model

EntityAssociation = Table(
    "entity_association", BaseModel.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("group_id", ForeignKey("entity.id")),
    Column("member_id", ForeignKey("entity.id")),
    Column("expire_at", BigInteger, default=0)
)


Permission = Table(
    "permission", BaseModel.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("entity_id", ForeignKey("entity.id")),
    Column("resource_name", ForeignKey("resource.name")),
    Column("expire_at", BigInteger, default=0)
)


class EntityType(enum.Enum):
    Role = 0
    Group = 1


class Entity(BaseModel):
    __tablename__ = "entity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), unique=True)
    type = Column(Enum(EntityType), default=EntityType.Role)
    expire_at = Column(BigInteger, default=0)       # 超时自动失效

    members = relationship(
        lambda: Entity, 
        secondary = EntityAssociation, 
        primaryjoin = and_(
            id == EntityAssociation.c.group_id,
            or_(
                EntityAssociation.c.expire_at == 0,
                EntityAssociation.c.expire_at > func.unix_timestamp() * 1000
            )
        ),
        secondaryjoin = and_(
            id == EntityAssociation.c.member_id,
            or_(
                EntityAssociation.c.expire_at == 0, 
                EntityAssociation.c.expire_at > func.unix_timestamp() * 1000
            )
        ),
        backref="groups"
    )
    # groups, see members
    resources = relationship(
        lambda: Resource,
        secondary = Permission,
        primaryjoin = and_(
            id == Permission.c.entity_id,
            or_(
                Permission.c.expire_at == 0,
                Permission.c.expire_at > func.unix_timestamp() * 1000
            )
        ),
        secondaryjoin = lambda: and_(
            Permission.c.resource_name == Resource.name,
            or_(
                Permission.c.expire_at == 0,
                Permission.c.expire_at > func.unix_timestamp() * 1000
            )
        ),
        backref="entities"
    )


    def __str__(self):
        return f"{self.name}"


class Resource(BaseModel):
    __tablename__ = "resource"
    
    name = Column(String(128), primary_key=True)
    create_time = Column(BigInteger, default=lambda: T.now())

    # entities, see Entity.resources

    @staticmethod
    def find(name):
        return db.session.query(Resource).filter(Resource.name == name).one_or_none()

    
    @staticmethod
    def define(name, suppress_warning=False):
        exist = Resource.find(name)
        if exist and not suppress_warning:
            from app.color_console import Yellow
            print(f"{Yellow('Warning: ')} duplicate resource name: {name}")
        
        r = Resource(name=name)
        db.session.add(r)
        db.session.commit()

        return r


with app.app_context():
    db.create_all()

    rst = db.session.query(Entity).filter(Entity.name == "u1").one_or_none()

    if not rst:
        u1 = Entity(name="u1")
        u2 = Entity(name="u2")

        g1 = Entity(name="g1", type=EntityType.Group)
        g2 = Entity(name="g2", type=EntityType.Group)
        g3 = Entity(name="g3", type=EntityType.Group)
        
        db.session.add(u1)
        db.session.add(u2)

        db.session.add(g1)
        db.session.add(g1)
        db.session.add(g1)

        db.session.commit()

        u1.groups.append(g1)
        u2.groups.append(g2)

        u1.groups.append(g3)
        u2.groups.append(g3)

        db.session.commit()

        r_login = Resource.define("login")
        r_profile = Resource.define("profile")
        
        u1.resources.append(r_login)
        u2.resources.append(r_login)
        u2.resources.append(r_profile)
        db.session.commit()

        print("------ initial data -------")


with app.app_context():
    for u in db.session.query(Entity).all():
        print(f"{u} {u.groups} {u.members} {u.resources}")

    for r in db.session.query(Resource).all():
        print(f"{r.name} {r.entities}")

    for r in db.session.query(Resource).all():
        r.entities.clear()
    db.session.commit()

    print("------ after -------")
    for u in db.session.query(Entity).all():
        print(f"{u} {u.groups} {u.members} {u.resources}")

    for r in db.session.query(Resource).all():
        print(f"{r.name} {r.entities}")
