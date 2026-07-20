import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from functools import wraps
from models import db, Profile, Skill, Project, Message

app = Flask(__name__)

# Konfigurasi Aplikasi Modern
app.config['SECRET_KEY'] = 'kunci-rahasia-serigala-alpha-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # Batasi ukuran upload maksimal 5 MB

# Menghubungkan database ke aplikasi Flask
db.init_app(app)

# Konfigurasi Ekstensi Gambar yang Diperbolehkan
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# DECORATOR: PROTEKSI LOGIN DASHBOARD 
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Silakan login terlebih dahulu untuk mengakses dashboard.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ADDITIONAL DATABASE MODELS 
class Education(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    institution = db.Column(db.String(100), nullable=False) # Nama Sekolah/Kampus
    degree = db.Column(db.String(100), nullable=False)      # Jurusan/Gelar
    duration = db.Column(db.String(50), nullable=False)     # Tahun 
    description = db.Column(db.Text, nullable=True)         # Keterangan tambahan


# ROUTE HALAMAN PUBLIK

@app.route('/')
def index():
    profile = Profile.query.first()
    return render_template('index.html', profile=profile)

@app.route('/about')
def about():
    profile_desc = (
        "Halo! Nama saya Salsabila Nurmardiyah Az'Zahra. Saat ini saya sedang menempuh "
        "perjalanan akademis sebagai mahasiswa di bidang Teknologi Informasi. Fokus utama saya "
        "adalah mengeksplorasi dunia pemrograman dan pengembangan web (web development). "
        "Saya memiliki ketertarikan yang besar dalam membangun antarmuka web yang interaktif, "
        "estetik, dan responsif."
    )
    education_history = Education.query.order_by(Education.id.desc()).all()
    skills_list = Skill.query.all()
    
    return render_template('about.html', 
                           description=profile_desc, 
                           educations=education_history, 
                           skills=skills_list)

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


# BACKEND: HALAMAN DASHBOARD ADMIN 

#  Login & Logout
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Akun Admin Default (Silakan disesuaikan)
        if username == 'moonwolf' and password == 'senja15':
            session['logged_in'] = True
            session['username'] = username
            flash('Selamat datang kembali, Admin!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah.', 'danger')
            
    return render_template('dashboard/login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Anda telah berhasil keluar.', 'success')
    return redirect(url_for('login'))

# Ringkasan Dashboard Utama
@app.route('/dashboard')
@login_required
def dashboard():
    total_projects = Project.query.count()
    # Menghitung pesan masuk (bisa disesuaikan dengan field model Message kamu, misal is_read)
    unread_messages = Message.query.filter_by(is_read=False).count() if hasattr(Message, 'is_read') else Message.query.count()
    return render_template('dashboard/index.html', total_projects=total_projects, unread_messages=unread_messages)

# CRUD Manajemen Proyek & Upload Gambar
@app.route('/dashboard/projects')
@login_required
def manage_projects():
    projects = Project.query.all()
    return render_template('dashboard/projects.html', projects=projects)

@app.route('/dashboard/projects/add', methods=['GET', 'POST'])
@login_required
def add_project():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        technology = request.form.get('technology')
        link = request.form.get('link')
        file = request.files.get('image')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            new_project = Project(title=title, description=description, technology=technology, link=link, image=filename)
            db.session.add(new_project)
            db.session.commit()
            flash('Proyek berhasil ditambahkan!', 'success')
            return redirect(url_for('manage_projects'))
        else:
            flash('Gagal! Pastikan file gambar valid (PNG, JPG, JPEG, GIF, WEBP) dan di bawah 5MB.', 'danger')
            
    return render_template('dashboard/project_form.html', action="Tambah")

@app.route('/dashboard/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    project = Project.query.get_or_404(id)
    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.technology = request.form.get('technology')
        project.link = request.form.get('link')
        
        file = request.files.get('image')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            project.image = filename
            
        db.session.commit()
        flash('Proyek berhasil diperbarui!', 'success')
        return redirect(url_for('manage_projects'))
        
    return render_template('dashboard/project_form.html', project=project, action="Edit")

@app.route('/dashboard/projects/delete/<int:id>', methods=['POST'])
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Proyek berhasil dihapus.', 'success')
    return redirect(url_for('manage_projects'))


# Manajemen Profil & Skill Dinamis
@app.route('/dashboard/profile', methods=['GET', 'POST'])
@login_required
def manage_profile():
    profile = Profile.query.first()
    skills = Skill.query.all()
    
    if request.method == 'POST':
        # Jalankan proses update jika tombol update_profile ditekan
        if 'update_profile' in request.form:
            if not profile:
                profile = Profile()
                db.session.add(profile)
            
            # Amankan input dengan memberikan nilai fallback string kosong ('') 
            profile.name = request.form.get('name') or "Nama Default"
            profile.headline = request.form.get('headline') or "IT Student & Web Developer"
            profile.about_text = request.form.get('about_text') or ""
            
            # Sinkronisasi Input Skill dari Tag HTML 
            skills_input = request.form.get('skills')
            if skills_input:
                
                if hasattr(profile, 'skills'):
                    profile.skills = skills_input
            
            file = request.files.get('avatar')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                if hasattr(profile, 'avatar'):
                    profile.avatar = filename
                elif hasattr(profile, 'image'):
                    profile.image = filename
                
            db.session.commit()
            flash('Profil berhasil diperbarui!', 'success')
            return redirect(url_for('manage_profile'))
            
        # Proses Tambah Skill Baru secara independen
        elif 'add_skill' in request.form:
            skill_name = request.form.get('skill_name')
            if skill_name:
                new_skill = Skill(name=skill_name)
                db.session.add(new_skill)
                db.session.commit()
                flash('Skill berhasil ditambahkan!', 'success')
                return redirect(url_for('manage_profile'))

    return render_template('dashboard/profile.html', profile=profile, skills=skills)



# Kotak Masuk Pesan
@app.route('/dashboard/messages')
@login_required
def manage_messages():
    messages = Message.query.order_by(Message.id.desc()).all()
    return render_template('dashboard/messages.html', messages=messages)

@app.route('/dashboard/messages/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_message_status(id):
    message = Message.query.get_or_404(id)
    # Membalikkan status: jika True jadi False, jika False jadi True
    message.is_read = not message.is_read 
    db.session.commit()
    
    status_text = "sudah dibaca" if message.is_read else "belum dibaca"
    flash(f'Pesan dari {message.name} ditandai sebagai {status_text}.', 'success')
    return redirect(url_for('manage_messages'))

@app.route('/dashboard/messages/read/<int:id>')
@login_required
def read_message(id):
    msg = Message.query.get_or_404(id)
    if hasattr(msg, 'is_read'):
        msg.is_read = True
        db.session.commit()
    flash('Pesan ditandai sebagai sudah dibaca.', 'success')
    return redirect(url_for('manage_messages'))

@app.route('/dashboard/messages/delete/<int:id>', methods=['POST'])
@login_required
def delete_message(id):
    msg = Message.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    flash('Pesan berhasil dihapus.', 'success')
    return redirect(url_for('manage_messages'))


# JALANKAN APLIKASI 
if __name__ == '__main__':
    with app.app_context():
        # Membuat database otomatis secara aman
        db.create_all()
        
        # Membuat data profil default jika kosong
        if Profile.query.first() is None:
            default_profile = Profile(
                name="NAMA KAMU",
                headline="IT Student & Web Developer",
                about_text="Halo! Selamat datang di web portofolio saya."
            )
            db.session.add(default_profile)
            db.session.commit()
            
    app.run(debug=True)
    with app.app_context():
    # Membuat database otomatis secara aman
            db.create_all()
    
    # Membuat data profil default jika kosong
    if Profile.query.first() is None:
        default_profile = Profile(
            name="NAMA KAMU",
            headline="IT Student & Web Developer",
            about_text="Halo! Selamat datang di web portofolio saya."
        )
        db.session.add(default_profile)
        db.session.commit()