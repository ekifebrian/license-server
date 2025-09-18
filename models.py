from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


class License(db.Model):
__tablename__ = "licenses"
id = db.Column(db.Integer, primary_key=True)
token_hash = db.Column(db.String(64), unique=True, nullable=False) # sha256 hex
description = db.Column(db.String(255))
bound_hwid = db.Column(db.String(255), nullable=True) # HWID yang diklaim
created_at = db.Column(db.DateTime, default=datetime.utcnow)
used = db.Column(db.Boolean, default=False) # apakah sudah diklaim
active = db.Column(db.Boolean, default=True) # aktif/nonaktif
expires_at = db.Column(db.DateTime, nullable=True) # optional expiration datetime (UTC)
