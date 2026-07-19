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
        
        
class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    institution = db.Column(db.String(100), nullable=False) # Nama Sekolah/Kampus
    degree = db.Column(db.String(100), nullable=False)      # Jurusan/Gelar
    duration = db.Column(db.String(50), nullable=False)     # Tahun (Contoh: "2025 - Sekarang")
    description = db.Column(db.Text, nullable=True)         # Keterangan tambahan

class Skill(db.Model):
    # Tambahkan baris ini tepat di bawah nama class (perhatikan indentasi spasi/tab-nya)
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

# 2. Update Route Halaman About
@app.route('/about')
def about():
    # Deskripsi diri lengkap
    profile_desc = (
        "Halo! Nama saya Salsabila Nurmardiyah Az'Zahra. Saat ini saya sedang menempuh "
        "perjalanan akademis sebagai mahasiswa di bidang Teknologi Informasi. Fokus utama saya "
        "adalah mengeksplorasi dunia pemrograman dan pengembangan web (web development). "
        "Saya memiliki ketertarikan yang besar dalam membangun antarmuka web yang interaktif, "
        "estetik, dan responsif."
    )
    
    # Mengambil data dari database secara dinamis
    education_history = Education.query.order_by(Education.id.desc()).all()
    skills_list = Skill.query.all()
    
    # Kirim data ke file HTML
    return render_template('about.html', 
                           description=profile_desc, 
                           educations=education_history, 
                           skills=skills_list)
    
if __name__ == '__main__':
    # Membuka konteks aplikasi Flask agar db.create_all() bisa berjalan aman
            with app.app_context():
               db.create_all() # Ini akan otomatis membuat tabel education & skill jika belum ada
        
            app.run(debug=True)        
    