# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

# Inisialisasi SQLAlchemy tanpa mengikatnya ke app terlebih dahulu (Pendekatan Modern)
db = SQLAlchemy()

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    headline = db.Column(db.String(200), nullable=False)
    about_text = db.Column(db.Text, nullable=False)
    avatar = db.Column(db.String(150), default='default_avatar.png')

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    technologies = db.Column(db.String(200))  # Disimpan sebagai string, dipisah koma (contoh: HTML, CSS)
    image_file = db.Column(db.String(150), default='default_project.png')
    github_link = db.Column(db.String(250))
    live_link = db.Column(db.String(250))
    # Menggunakan timezone-aware datetime yang modern menggantikan utcnow yang sudah deprecated
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))