import datetime
import os


UNIX_USER = "jcav"
DB_SOCK = r"/run/mysqld/mysqld.sock"

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=3)
    SCHEDULER_TIMEZONE = "Asia/Shanghai"


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://%s@/PBAC_dev?unix_socket=%s&charset=utf8mb4"
        % (UNIX_USER, DB_SOCK)
    )
    SECRET_KEY = b"dev -------"



class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://%s@/PBAC?unix_socket=%s&charset=utf8mb4"
        % (UNIX_USER, DB_SOCK)
    )

    SECRET_KEY = os.urandom(32)


DefaultConfig = DevelopmentConfig