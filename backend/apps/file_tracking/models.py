from project import db
from mixins import BaseModel

STAT_ATTRIBUTES = (
    {
        'label': 'File permissions',
        'name': 'mode'
    },
    {
        'label': 'Number of hard links',
        'name': 'nlink'
    },
    {
        'label': 'File owner User',
        'name': 'user'
    },
    {
        'label': 'File owner Group',
        'name': 'group'
    },
    {
        'label': 'Size of file',
        'name': 'size'
    },
    {
        'label': 'Time of most recent content modification',
        'name': 'mtime'
    },
    {
        'label': 'Time of most recent metadata change',
        'name': 'ctime'
    },
    {
        'label': 'User defined flags for file',
        'name': 'flags'
    }
)


class File(BaseModel):
    file_path = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(15), nullable=False, default='Active')
    license_id = db.Column(
        db.Integer, db.ForeignKey('license.id', ondelete='CASCADE')
    )
    license = db.relationship('License', backref='files')


class FileStats(BaseModel):
    file_id = db.Column(
        db.Integer, db.ForeignKey('file.id', ondelete='CASCADE')
    )
    file = db.relationship('File', backref='stats')
    mode = db.Column(db.String(255), nullable=True, index=False)
    nlink = db.Column(db.String(255), nullable=True, index=False)
    user = db.Column(db.String(255), nullable=True, index=False)
    group = db.Column(db.String(255), nullable=True, index=False)
    size = db.Column(db.String(255), nullable=True, index=False)
    mtime = db.Column(db.String(255), nullable=True, index=False)
    ctime = db.Column(db.String(255), nullable=True, index=False)
    flags = db.Column(db.String(255), nullable=True, index=False)
