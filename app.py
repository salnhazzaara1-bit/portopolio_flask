# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Profile, Skill, Project, Message

app = Flask(__name__)

# Konfigurasi Aplikasi Modern
app.config['SECRET_KEY'] = 'kunci-rahasia-serigala-alpha-2026' # Ganti dengan key rahasiamu
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # Batasi ukuran upload maksimal 5 MB

# Menghubungkan database ke aplikasi Flask
db.init_app(app)

# ==================== ROUTE HALAMAN PUBLIK ====================

@app.route('/')
def index():
    # Mengambil data profil pertama dari database
    profile = Profile.query.first()
    return render_template('index.html', profile=profile)

@app.route('/about')
def about():
    profile = Profile.query.first()
    skills = Skill.query.all()
    return render_template('about.html', profile=profile, skills=skills)

@app.route('/portfolio')
def portfolio():
    projects = Project.query.all()
    return render_template('portfolio.html', projects=projects)

@app.route('/project/<int:id>')
def project_detail(id):
    project = Project.query.get_or_404(id)
    return render_template('project_detail.html', project=project)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        content = request.form.get('message')
        
        if name and email and content:
            new_message = Message(name=name, email=email, content=content)
            db.session.add(new_message)
            db.session.commit()
            flash('Pesan kamu berhasil dikirim!', 'success')
            return redirect(url_for('contact'))
            
    return render_template('contact.html')

# ==================== ANCHOR JALANKAN APLIKASI ====================

if __name__ == '__main__':
    with app.app_context():
        # Membuat file database portfolio.db otomatis jika belum ada
        db.create_all()
        
        # Mengisi data profil default jika database masih kosong agar tidak error
        if Profile.query.first() is None:
            default_profile = Profile(
                name="Nama Kamu",
                headline="IT Student & Web Developer",
                about_text="Halo! Selamat datang di web portofolio saya."
            )
            db.session.add(default_profile)
            db.session.commit()
            
    app.run(debug=True)