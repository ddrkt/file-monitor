from project import db
from sqlalchemy.ext.declarative import declared_attr
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property


class DefaultTableNameMixin(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class BaseModel(DefaultTableNameMixin, db.Model):
    """
    Basic model that contains default methods and fields
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,
                              default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())

    def get_pk(self):
        return self.id


class BaseTokenModel(BaseModel):
    """
    Basic model with encoded token field
    """
    __abstract__ = True

    token_hash = db.Column(db.String(255), nullable=False, unique=True)

    @hybrid_property
    def token(self):
        return self.token_hash

    @token.setter
    def token(self, token):
        self.token_hash = generate_password_hash(token)

    def verify_token(self, token):
        return check_password_hash(self.token, token)
