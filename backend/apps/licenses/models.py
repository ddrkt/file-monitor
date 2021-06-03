from project import db
from mixins import BaseTokenModel


class License(BaseTokenModel):
    pass


class ViewToken(BaseTokenModel):
    license_id = db.Column(
        db.Integer, db.ForeignKey('license.id', ondelete='CASCADE')
    )
    license = db.relationship('License')
