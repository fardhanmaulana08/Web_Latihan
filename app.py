from email.utils import format_datetime

from flask import (
   Flask, request, redirect, url_for,
   session, flash, render_template_string
)
from functools import wraps
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta
import os

from db import get_db

app = Flask(__name__)
app.secret_key = "rahasia-ganti-sendiri"

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =====================================================================
# BASE TEMPLATE HTML
# =====================================================================
BASE_HTML = """
<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<title>{{ title or "Pelaporan Security" }}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">

<!-- Font Inter -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<!-- Bootstrap -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

<style>
  body {
    background: #f5f6f8;
    font-family: "Inter", sans-serif;
  }

  /* ================= NAVBAR ================= */
  .navbar {
    height: 64px;
    background: #1e40af !important; /* corporate blue */
    border-bottom: 1px solid rgba(255,255,255,0.1);
  }

  .navbar-brand {
    font-weight: 600;
    letter-spacing: .3px;
  }

  /* ================= SIDEBAR ================= */
  .sidebar {
    background: #ffffff;
    min-height: calc(100vh - 64px);
    border-right: 1px solid #e2e8f0;
    padding: 1.8rem 1rem;
  }

  .sidebar .nav-link {
    color: #475569;
    padding: .65rem 1rem;
    border-radius: .6rem;
    font-size: .95rem;
    font-weight: 500;
    margin-bottom: .25rem;
    transition: .2s ease;
  }

  .sidebar .nav-link:hover {
    background: #eff6ff;
    color: #1d4ed8;
  }

  .sidebar .nav-link.active {
    background: #1d4ed8;
    color: #fff !important;
    box-shadow: 0 2px 8px rgba(29,78,216,0.25);
  }

  /* ================= CARD ================= */
  .card {
    border: 1px solid #e5e7eb;
    border-radius: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  }

  .card:hover {
    border-color: #d1d5db;
  }

  /* ================= BUTTONS ================= */
  .btn {
    font-weight: 500;
    border-radius: .5rem;
    letter-spacing: .2px;
  }

  .btn-primary {
    background-color: #2563eb;
    border-color: #2563eb;
  }

  .btn-primary:hover {
    background-color: #1d4ed8;
    border-color: #1d4ed8;
  }

  .btn-outline-primary {
    color: #2563eb;
    border-color: #2563eb;
  }

  .btn-outline-primary:hover {
    background-color: #2563eb;
    color: #fff;
  }

  /* ================= TABLE ================= */
  table thead th {
    background: #f1f5f9;
    color: #334155;
    font-weight: 600;
  }

  table tbody tr:hover {
    background: #f8fafc !important;
  }

  /* ================= FLASH ================= */
  .alert {
    border-radius: .6rem;
  }
</style>
</head>

<body>

<!-- ================= NAVBAR ================= -->
<nav class="navbar navbar-expand-lg navbar-dark px-3">
 <a class="navbar-brand" href="{{ url_for('index') }}">Security Guard Report</a>

 <div class="ms-auto d-flex align-items-center">
   {% if session.get('user_id') %}
     <span class="text-light small me-3">
       {{ session.get('username') }} ({{ session.get('role') }})
     </span>
     <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm px-3">Logout</a>
   {% endif %}
 </div>
</nav>


<!-- ================= MAIN LAYOUT ================= -->
<div class="container-fluid">
 <div class="row">

   <!-- SIDEBAR -->
   <aside class="col-lg-2 d-none d-lg-block sidebar">
     {% if session.get('user_id') %}

       <div class="mb-3">
         <div class="small text-muted mb-1">Login sebagai</div>
         <div class="fw-semibold">{{ session.get('username') }}</div>
         <div class="small text-muted">{{ session.get('role') }}</div>
         <hr>
       </div>

       <ul class="nav flex-column">

         {% if session.get('role') == 'security' %}
           <li><a class="nav-link {% if request.endpoint=='list_laporan_saya' %}active{% endif %}" href="{{ url_for('list_laporan_saya') }}">📄 Laporan Saya</a></li>
           <li><a class="nav-link {% if request.endpoint=='tambah_laporan' %}active{% endif %}" href="{{ url_for('tambah_laporan') }}">➕ Tambah Laporan</a></li>

         {% elif session.get('role') == 'supervisor' %}
           <li><a class="nav-link {% if request.endpoint=='dashboard' %}active{% endif %}" href="{{ url_for('dashboard') }}">📊 Dashboard</a></li>
           <li><a class="nav-link {% if request.endpoint in ['list_laporan_supervisor','detail_laporan'] %}active{% endif %}" href="{{ url_for('list_laporan_supervisor') }}">📁 Semua Laporan</a></li>

         {% elif session.get('role') == 'admin' %}
           <li><a class="nav-link {% if request.endpoint=='admin_dashboard' %}active{% endif %}" href="{{ url_for('admin_dashboard') }}">🛠 Admin Dashboard</a></li>
           <li><a class="nav-link {% if request.endpoint in ['admin_users','admin_edit_user','admin_add_user'] %}active{% endif %}" href="{{ url_for('admin_users') }}">👤 User Management</a></li>
         {% endif %}

         <li class="mt-3"><a class="nav-link" href="{{ url_for('logout') }}">🚪 Logout</a></li>
       </ul>

     {% endif %}
   </aside>


   <!-- MAIN CONTENT -->
   <main class="col-lg-10 ms-auto mt-4">
     <div class="container">

       <!-- Flash -->
       {% with messages = get_flashed_messages(with_categories=true) %}
         {% for cat, msg in messages %}
           <div class="alert alert-{{ cat }} shadow-sm">
             {{ msg }}
           </div>
         {% endfor %}
       {% endwith %}

       {{ content|safe }}

     </div>
   </main>

 </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>

"""


# =====================================================================
# FIX: RENDER INNER TEMPLATE + BASE TEMPLATE
# =====================================================================
def render_page(title, inner_html, **context):
   # Render inner HTML terlebih dahulu agar {{ var }} dan {% for %} berjalan
   rendered_inner = render_template_string(inner_html, **context)

   # Baru inject ke base template
   return render_template_string(
       BASE_HTML,
       title=title,
       content=rendered_inner,
       **context
   )


# =====================================================================
# AUTH HELPERS
# =====================================================================
def login_required(f):
   @wraps(f)
   def wrapped(*a, **kw):
       if "user_id" not in session:
           return redirect(url_for("login"))
       return f(*a, **kw)
   return wrapped


def role_required(role):
   def decorator(f):
       @wraps(f)
       def wrapped(*a, **kw):
           if "user_id" not in session:
               return redirect(url_for("login"))
           if session.get("role") != role:
               flash("Anda tidak memiliki akses.", "danger")
               if session.get("role") == "security":
                   return redirect(url_for("list_laporan_saya"))
               return redirect(url_for("dashboard"))
           return f(*a, **kw)
       return wrapped
   return decorator


# =====================================================================
# INDEX
# =====================================================================
@app.route("/")
def index():
   if session.get("user_id"):
       return redirect(url_for("list_laporan_saya") if session.get("role") == "security" else url_for("dashboard"))

   inner = """
<div class="row justify-content-center">
  <div class="col-lg-6 col-md-8 col-10">
    <div class="card border-0 shadow-xl p-5 hero-card text-center">

      <div class="icon-wrapper mb-4">
        <i class="bi bi-shield-lock-fill hero-icon"></i>
      </div>

      <h1 class="fw-bold mb-3 hero-title">
        Laporan Security
      </h1>

      <p class="hero-sub mb-4">
        Sistem Pelaporan Kegiatan Security PeTIK II Jombang.<br>
        Cepat • Mudah • Terstruktur
      </p>

      <a href="{{ url_for('login') }}" 
         class="btn btn-primary btn-lg hero-btn px-5 py-3">
         Mulai Login
      </a>

    </div>
  </div>
</div>

<style>
  /* Card container */
  .hero-card {
    border-radius: 1.6rem !important;
    background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
    transition: all .4s ease;
    box-shadow: 0 4px 10px rgba(0,0,0,.1);
  }

  /* Hover effect for card */
  .hero-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 14px 30px rgba(0,0,0,.1);
  }

  /* Icon wrapper */
  .icon-wrapper {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #2563eb;
    padding: 20px;
    border-radius: 50%;
    box-shadow: 0 4px 12px rgba(37,99,235,.2);
  }

  /* Icon styling */
  .hero-icon {
    font-size: 3.5rem;
    color: #ffffff;
  }

  /* Title */
  .hero-title {
    font-size: 2.4rem;
    color: #1e293b;
    letter-spacing: 1px;
    font-weight: 700;
  }

  /* Subtitle */
  .hero-sub {
    font-size: 1.1rem;
    color: #475569;
    line-height: 1.6;
    margin-bottom: 1.5rem;
  }

  /* Button styling */
  .hero-btn {
    font-weight: 600;
    font-size: 1.1rem;
    border-radius: 45px;
    letter-spacing: .5px;
    box-shadow: 0 6px 18px rgba(37,99,235,.3);
    transition: all .3s ease;
  }

  .hero-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 22px rgba(37,99,235,.4);
    background-color: #1d4ed8;
  }

  .hero-btn:active {
    transform: translateY(1px);
    box-shadow: 0 6px 12px rgba(37,99,235,.2);
  }

  /* Add responsiveness */
  @media (max-width: 576px) {
    .hero-title {
      font-size: 1.8rem;
    }

    .hero-btn {
      font-size: 1rem;
      padding: 1rem 3rem;
    }

    .icon-wrapper {
      padding: 16px;
    }
  }
</style>

<!-- Bootstrap Icons -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">

   """

   return render_page("Beranda", inner)


# =====================================================================
# LOGIN
# =====================================================================
@app.route("/login", methods=["GET", "POST"])
def login():
   if request.method == "POST":
       u = request.form["username"].strip()
       p = request.form["password"].strip()

       conn = get_db()
       cur = conn.cursor()

       cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (u, p))
       user = cur.fetchone()
       conn.close()

       if user:
           session["user_id"] = user["id"]
           session["username"] = user["username"]
           session["role"] = user["role"]

           flash("Login berhasil.", "success")
           return redirect(url_for("list_laporan_saya") if user["role"] == "security" else url_for("dashboard"))

       flash("Username atau password salah.", "danger")

   inner = """
<div class="row justify-content-center">
  <div class="col-md-6 col-lg-5">

    <div class="card login-card border-0 shadow-xl p-5 text-center">

      <div class="icon-wrapper mb-4">
        <i class="bi bi-person-lock login-icon"></i>
      </div>

      <h2 class="fw-bold mb-4 login-title">
        Login Akun
      </h2>

      <form method="post">

        <div class="mb-4 text-start">
          <label class="form-label fw-semibold">Username</label>
          <input 
            class="form-control form-control-lg login-input" 
            name="username" 
            required 
            autofocus>
        </div>

        <div class="mb-4 text-start">
          <label class="form-label fw-semibold">Password</label>
          <input 
            type="password" 
            class="form-control form-control-lg login-input" 
            name="password" 
            required>
        </div>

        <button class="btn btn-primary btn-lg login-btn w-100 mt-3">
          Login
        </button>

      </form>

    </div>

  </div>
</div>

<style>
  /* Card style */
  .login-card {
    border-radius: 1.5rem;
    background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
    transition: all .3s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .login-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 16px 32px rgba(0, 0, 0, 0.15);
  }

  /* Icon */
  .login-icon {
    font-size: 3.5rem;
    color: #2563eb;
  }

  .icon-wrapper {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #dbeafe;
    padding: 18px;
    border-radius: 50%;
    box-shadow: 0 6px 18px rgba(37,99,235,.2);
  }

  /* Title */
  .login-title {
    font-size: 2rem;
    color: #0f172a;
    letter-spacing: 1px;
  }

  /* Modern Input */
  .login-input {
    border-radius: .8rem !important;
    padding: .9rem 1.2rem !important;
    border: 1px solid #cbd5e1;
    transition: all .25s ease;
    font-size: 1.05rem;
  }

  .login-input:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37,99,235,.2);
    outline: none;
  }

  /* Button */
  .login-btn {
    font-weight: 600;
    letter-spacing: .4px;
    border-radius: 50px;
    padding: .9rem 0;
    box-shadow: 0 4px 12px rgba(37,99,235,.28);
    transition: all .25s ease;
  }

  .login-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(37,99,235,.35);
  }

  .login-btn:active {
    transform: translateY(1px);
    box-shadow: 0 4px 12px rgba(37,99,235,.25);
  }

  /* Responsiveness for small screens */
  @media (max-width: 576px) {
    .login-card {
      padding: 3rem 2rem;
    }

    .login-title {
      font-size: 1.75rem;
    }

    .login-btn {
      font-size: 1.05rem;
      padding: .8rem 0;
    }

    .login-input {
      padding: .8rem 1rem;
    }
  }
</style>

<!-- Bootstrap Icons -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">

   """

   return render_page("Login", inner)


@app.route("/logout")
def logout():
   session.clear()
   flash("Anda telah logout.", "info")
   return redirect(url_for("login"))


# =====================================================================
# LAPORAN SECURITY: LIST
# =====================================================================
@app.route("/laporan/saya")
@login_required
@role_required("security")
def list_laporan_saya():
   conn = get_db()
   cur = conn.cursor()

   cur.execute("""
       SELECT l.*, u.username AS nama_security
       FROM laporan l
       JOIN users u ON u.id = l.security_id
       WHERE l.security_id = %s
       ORDER BY l.created_at DESC
   """, (session["user_id"],))
   laporan = cur.fetchall()
   conn.close()

   inner = """
<div class="page-header d-flex justify-content-between align-items-center mb-4">
  <h2 class="fw-bold page-title">
    Laporan Saya
  </h2>

  <a href="{{ url_for('tambah_laporan') }}" 
     class="btn btn-primary add-btn px-4 py-2">
    + Buat Laporan
  </a>
</div>

<div class="card laporan-card border-0 shadow-sm">
  <div class="card-body table-responsive">

    <table class="table table-hover align-middle laporan-table">
      <thead class="table-light">
        <tr>
          <th>ID</th>
          <th>Tanggal</th>
          <th>Judul</th>
          <th>Tingkat</th>
          <th>Status</th>
          <th>Dibuat</th>
          <th class="text-center">Aksi</th>
        </tr>
      </thead>

      <tbody>

      {% for row in laporan %}
        <tr>
          <td class="fw-semibold text-dark">#{{ row.id }}</td>
          <td>{{ row.tanggal }}</td>
          <td class="fw-semibold text-primary">{{ row.judul }}</td>

          <td>
            {% if row.tingkat_perhatian == 'merah' %}
              <span class="badge badge-red">Merah</span>
            {% elif row.tingkat_perhatian == 'kuning' %}
              <span class="badge badge-yellow">Kuning</span>
            {% else %}
              <span class="badge badge-green">Hijau</span>
            {% endif %}
          </td>

          <td>
            {% if row.status_dibaca %}
              <span class="badge badge-green-light">Dibaca</span>
            {% else %}
              <span class="badge badge-gray">Belum</span>
            {% endif %}
          </td>

          <td>{{ row.created_at }}</td>

          <td class="text-center">
            <a href="{{ url_for('edit_laporan', laporan_id=row.id) }}" 
               class="btn btn-sm btn-edit">
               Edit
            </a>

            <a href="{{ url_for('hapus_laporan', laporan_id=row.id) }}" 
               class="btn btn-sm btn-delete ms-1"
               onclick="return confirm('Yakin ingin menghapus?')">
               Hapus
            </a>
          </td>
        </tr>

      {% else %}
        <tr>
          <td colspan="7" class="text-center py-5 text-muted empty-row">
            Belum ada laporan yang dibuat.
          </td>
        </tr>
      {% endfor %}

      </tbody>
    </table>

  </div>
</div>

<style>
  /* Page title */
  .page-title {
    color: #0f172a;
    font-size: 1.8rem;
    letter-spacing: .35px;
  }

  /* Button Buat Laporan */
  .add-btn {
    font-weight: 600;
    letter-spacing: .4px;
    border-radius: 50px !important;
    box-shadow: 0 4px 14px rgba(37,99,235,.3);
    transition: .25s ease;
  }

  .add-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(37,99,235,.4);
  }

  /* Card style */
  .laporan-card {
    border-radius: 1rem;
    transition: .3s ease;
  }

  .laporan-card:hover {
    box-shadow: 0 14px 32px rgba(0,0,0,.07);
    transform: translateY(-3px);
  }

  /* Table */
  .laporan-table {
    font-size: .95rem;
  }

  .laporan-table tbody tr {
    transition: .25s ease;
  }

  .laporan-table tbody tr:hover {
    background: #f1f5f9;
  }

  /* Badge */
  .badge {
    padding: .45rem 1rem;
    border-radius: 50px;
    font-size: .78rem;
    font-weight: 600;
  }

  .badge-red {
    background: #ef4444;
    color: white;
  }

  .badge-yellow {
    background: #facc15;
    color: #1e293b;
  }

  .badge-green {
    background: #10b981;
    color: white;
  }

  .badge-green-light {
    background: #bbf7d0;
    color: #065f46;
  }

  .badge-gray {
    background: #cbd5e1;
    color: #334155;
  }

  /* Buttons */
  .btn-edit, .btn-delete {
    border-radius: 50px !important;
    padding: .35rem 1rem;
    font-weight: 600;
    font-size: .78rem;
    letter-spacing: .3px;
    transition: .25s ease;
  }

  .btn-edit {
    border: 1px solid #f59e0b;
    color: #b45309;
    background: #fff7ed;
  }

  .btn-edit:hover {
    background: #fef3c7;
    border-color: #d97706;
  }

  .btn-delete {
    border: 1px solid #ef4444;
    color: #991b1b;
    background: #fef2f2;
  }

  .btn-delete:hover {
    background: #fee2e2;
    border-color: #dc2626;
  }

  .empty-row {
    font-size: 1rem;
    color: #64748b;
  }
</style>

   """

   return render_page("Laporan Saya", inner, laporan=laporan)


# =====================================================================
# TAMBAH LAPORAN SECURITY
# =====================================================================
@app.route("/laporan/tambah", methods=["GET", "POST"])
@login_required
@role_required("security")
def tambah_laporan():
    today = date.today()

    if request.method == "POST":
        # ... (Logika POST sudah benar)
        tanggal = date.fromisoformat(request.form["tanggal"])
        if tanggal != today:
            flash("Laporan hanya untuk tanggal hari ini.", "danger")
            return redirect(url_for("tambah_laporan"))

        judul = request.form["judul"].strip()
        detail = request.form["detail"].strip()
        catatan = request.form.get("catatan_khusus", "").strip()
        tingkat = request.form["tingkat_perhatian"]

        foto = None
        foto_file = request.files.get("foto")
        if foto_file and foto_file.filename:
            # FIX: Cek apakah ekstensi file diperbolehkan
            allowed_ext = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' in foto_file.filename and foto_file.filename.rsplit('.', 1)[1].lower() in allowed_ext:
                filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{foto_file.filename}")
                foto_file.save(os.path.join(UPLOAD_FOLDER, filename))
                foto = filename
            else:
                flash("Tipe file foto tidak didukung.", "warning")

        # app.py: Perbaikan di sekitar baris 445
        conn = get_db()
        cur = conn.cursor()

        # app.py: Pastikan blok ini di fungsi tambah_laporan() sudah benar

        # ... (Baris 461: try:)
        try:
            # Data yang akan dimasukkan:
            data_insert = (
                tanggal,
                session["user_id"],
                judul,
                detail,
                catatan,
                foto,  # <-- Variabel Python
                tingkat,
                0,  # status_dibaca
                None,  # supervisor_id
                None,  # feedback
                datetime.now()  # created_at
            )

            cur.execute("""
                        INSERT INTO laporan(tanggal, security_id, judul, detail, catatan_khusus, foto_nama,
                                            tingkat_perhatian, status_dibaca, supervisor_id, feedback, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, data_insert)  # <-- Column name di SQL harus 'foto_nama'

            conn.commit()
            # ... (lanjut ke flash dan finally)
            flash("Laporan berhasil dibuat.", "success")
            return redirect(url_for("list_laporan_saya"))
        except Exception as e:
            conn.rollback()
            flash(f"Error saat membuat laporan: {str(e)}", "danger")
            return redirect(url_for("tambah_laporan"))
        finally:
            conn.close()

    # --- PERBAIKAN: GANTI TEMPLATE INI DENGAN FORMULIR ---
    inner = """
<h2 class="fw-bold mb-4 edit-title">➕ Buat Laporan Baru</h2>

<div class="card edit-card border-0 shadow-sm">
  <div class="card-body p-4">

    <form method="post" class="row g-4" enctype="multipart/form-data">

      <div class="col-md-4">
        <label class="form-label fw-semibold">Tanggal Kejadian</label>
        <input 
          type="date"
          class="form-control form-control-lg input-soft" 
          name="tanggal"
          value="{{ today }}"
          readonly>
        <div class="form-text">Laporan hanya bisa dibuat untuk hari ini ({{ today }}).</div>
      </div>

      <div class="col-12">
        <label class="form-label fw-semibold">Judul/Ringkasan Kejadian</label>
        <input 
          class="form-control form-control-lg input-soft" 
          name="judul" 
          placeholder="Contoh: Lampu Rusak di Pos 1"
          required>
      </div>

      <div class="col-12">
        <label class="form-label fw-semibold">Detail Kejadian</label>
        <textarea 
          class="form-control form-control-lg input-soft" 
          rows="4" 
          name="detail"
          placeholder="Jelaskan secara rinci apa yang terjadi, kapan, dan bagaimana penanganannya."
          required></textarea>
      </div>

      <div class="col-12">
        <label class="form-label fw-semibold">Foto Bukti (Opsional)</label>
        <input
          type="file"
          class="form-control form-control-lg input-soft"
          name="foto"
          accept="image/*">
        <div class="form-text">Maksimal 2MB. Format: JPG, PNG.</div>
      </div>


      <div class="col-12">
        <label class="form-label fw-semibold">Catatan Khusus (Opsional)</label>
        <textarea 
          class="form-control form-control-lg input-soft" 
          rows="3" 
          name="catatan_khusus"
          placeholder="Tambahkan informasi penting lain jika ada."></textarea>
      </div>

      <div class="col-md-4">
        <label class="form-label fw-semibold">Tingkat Perhatian</label>
        <select 
          class="form-select form-select-lg input-soft" 
          name="tingkat_perhatian"
          required>
          <option value="hijau" selected>🟢 Hijau — Aman</option>
          <option value="kuning">🟡 Kuning — Perlu Perhatian</option>
          <option value="merah">🔴 Merah — Bahaya Serius</option>
        </select>
      </div>

      <div class="col-12 mt-2">
        <button 
          class="btn btn-primary btn-lg save-btn px-4">
          ✅ Kirim Laporan
        </button>

        <a 
          href="{{ url_for('list_laporan_saya') }}" 
          class="btn btn-outline-secondary btn-lg cancel-btn px-4 ms-2">
          Batal
        </a>
      </div>

    </form>

  </div>
</div>

<style>
  /* Menggunakan styling yang sudah ada dari edit_laporan */
  /* Judul */
  .edit-title {
    color: #1e293b;
    font-size: 1.9rem;
    letter-spacing: .3px;
  }

  /* Card utama */
  .edit-card {
    border-radius: 1rem;
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    transition: .3s ease;
  }

  .edit-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 14px 30px rgba(0,0,0,.07);
  }

  /* Input premium */
  .input-soft {
    border-radius: .7rem !important;
    padding: .9rem 1rem !important;
    border: 1px solid #cbd5e1;
    background: #ffffff;
    transition: .25s ease;
    font-size: 1.05rem;
  }

  .input-soft:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59,130,246,.25);
  }

  /* Tombol */
  .save-btn {
    font-weight: 600;
    border-radius: 50px !important;
    box-shadow: 0 4px 14px rgba(59,130,246,.3);
    transition: .25s ease;
  }

  .save-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(59,130,246,.45);
  }

  .cancel-btn {
    font-weight: 500;
    border-radius: 50px !important;
    padding-left: 2rem;
    padding-right: 2rem;
  }

  .cancel-btn:hover {
    background: #f1f5f9;
  }
</style>

   """

    return render_page("Tambah Laporan", inner, today=today.isoformat())


# =====================================================================
# EDIT LAPORAN SECURITY
# =====================================================================
@app.route("/laporan/edit/<int:laporan_id>", methods=["GET", "POST"])
@login_required
@role_required("security")
def edit_laporan(laporan_id):
   conn = get_db()
   cur = conn.cursor()

   cur.execute("SELECT * FROM laporan WHERE id=%s AND security_id=%s", (laporan_id, session["user_id"]))
   laporan = cur.fetchone()

   if not laporan:
       flash("Laporan tidak ditemukan.", "danger")
       return redirect(url_for("list_laporan_saya"))

   if request.method == "POST":
       judul = request.form["judul"].strip()
       detail = request.form["detail"].strip()
       catatan = request.form.get("catatan_khusus", "").strip()
       tingkat = request.form["tingkat_perhatian"]

       cur.execute("""
           UPDATE laporan
           SET judul=%s, detail=%s, catatan_khusus=%s, tingkat_perhatian=%s
           WHERE id=%s
       """, (judul, detail, catatan, tingkat, laporan_id))
       conn.commit()
       conn.close()

       flash("Laporan berhasil diupdate.", "success")
       return redirect(url_for("list_laporan_saya"))

   conn.close()

   inner = """
<h2 class="fw-bold mb-4 edit-title">✏️ Edit Laporan</h2>

<div class="card edit-card border-0 shadow-sm">
  <div class="card-body p-4">

    <form method="post" class="row g-4">

      <!-- Tanggal -->
      <div class="col-md-4">
        <label class="form-label fw-semibold">Tanggal</label>
        <input 
          class="form-control form-control-lg input-soft" 
          value="{{ laporan.tanggal }}" 
          readonly>
      </div>

      <!-- Judul -->
      <div class="col-12">
        <label class="form-label fw-semibold">Judul</label>
        <input 
          class="form-control form-control-lg input-soft" 
          name="judul" 
          value="{{ laporan.judul }}" 
          required>
      </div>

      <!-- Detail -->
      <div class="col-12">
        <label class="form-label fw-semibold">Detail Kejadian</label>
        <textarea 
          class="form-control form-control-lg input-soft" 
          rows="4" 
          name="detail">{{ laporan.detail }}</textarea>
      </div>

      <!-- Catatan Khusus -->
      <div class="col-12">
        <label class="form-label fw-semibold">Catatan Khusus</label>
        <textarea 
          class="form-control form-control-lg input-soft" 
          rows="3" 
          name="catatan_khusus">{{ laporan.catatan_khusus or '' }}</textarea>
      </div>

      <!-- Tingkat Perhatian -->
      <div class="col-md-4">
        <label class="form-label fw-semibold">Tingkat Perhatian</label>
        <select 
          class="form-select form-select-lg input-soft" 
          name="tingkat_perhatian">
          <option value="merah"  {{ 'selected' if laporan.tingkat_perhatian=='merah' else '' }}>🔴 Merah — Bahaya Serius</option>
          <option value="kuning" {{ 'selected' if laporan.tingkat_perhatian=='kuning' else '' }}>🟡 Kuning — Perlu Perhatian</option>
          <option value="hijau"  {{ 'selected' if laporan.tingkat_perhatian=='hijau' else '' }}>🟢 Hijau — Aman</option>
        </select>
      </div>

      <!-- Tombol -->
      <div class="col-12 mt-2">
        <button 
          class="btn btn-primary btn-lg save-btn px-4">
          💾 Simpan Perubahan
        </button>

        <a 
          href="{{ url_for('list_laporan_saya') }}" 
          class="btn btn-outline-secondary btn-lg cancel-btn px-4 ms-2">
          Batal
        </a>
      </div>

    </form>

  </div>
</div>

<style>
  /* Judul */
  .edit-title {
    color: #1e293b;
    font-size: 1.9rem;
    letter-spacing: .3px;
  }

  /* Card utama */
  .edit-card {
    border-radius: 1rem;
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    transition: .3s ease;
  }

  .edit-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 14px 30px rgba(0,0,0,.07);
  }

  /* Input premium */
  .input-soft {
    border-radius: .7rem !important;
    padding: .9rem 1rem !important;
    border: 1px solid #cbd5e1;
    background: #ffffff;
    transition: .25s ease;
    font-size: 1.05rem;
  }

  .input-soft:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59,130,246,.25);
  }

  /* Tombol */
  .save-btn {
    font-weight: 600;
    border-radius: 50px !important;
    box-shadow: 0 4px 14px rgba(59,130,246,.3);
    transition: .25s ease;
  }

  .save-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(59,130,246,.45);
  }

  .cancel-btn {
    font-weight: 500;
    border-radius: 50px !important;
    padding-left: 2rem;
    padding-right: 2rem;
  }

  .cancel-btn:hover {
    background: #f1f5f9;
  }
</style>

   """

   return render_page("Edit Laporan", inner, laporan=laporan)


# =====================================================================
# HAPUS LAPORAN SECURITY
# =====================================================================
@app.route("/laporan/hapus/<int:laporan_id>")
@login_required
@role_required("security")
def hapus_laporan(laporan_id):
   conn = get_db()
   cur = conn.cursor()
   cur.execute("DELETE FROM laporan WHERE id=%s AND security_id=%s", (laporan_id, session["user_id"]))
   conn.commit()
   conn.close()

   flash("Laporan dihapus.", "info")
   return redirect(url_for("list_laporan_saya"))


# =====================================================================
# SUPERVISOR LIST LAPORAN
# =====================================================================
@app.route("/laporan")
@login_required
@role_required("supervisor")
def list_laporan_supervisor():
   conn = get_db()
   cur = conn.cursor()

   cur.execute("""
       SELECT l.*, u.username AS nama_security
       FROM laporan l
       JOIN users u ON u.id = l.security_id
       ORDER BY l.created_at DESC
   """)
   laporan = cur.fetchall()
   conn.close()

   inner = """
<h2 class="fw-bold mb-4" style="color:#1e293b;">📑 Semua Laporan</h2>

<div class="card border-0 shadow-sm" style="border-radius: 1rem;">
  <div class="card-body table-responsive p-4">

    <table class="table align-middle" style="font-size: .95rem;">
      <thead style="background:#f1f5f9;">
        <tr class="fw-semibold text-center" style="color:#334155;">
          <th>ID</th>
          <th>Tanggal</th>
          <th>Petugas</th>
          <th class="text-start">Judul</th>
          <th>Tingkat</th>
          <th>Status</th>
          <th>Dibuat</th>
          <th>Aksi</th>
        </tr>
      </thead>

      <tbody class="border-top-0">

      {% for row in laporan %}
        <tr class="text-center" style="transition:0.15s;">
          
          <!-- ID -->
          <td class="fw-bold text-primary">#{{ row.id }}</td>

          <!-- Tanggal -->
          <td>{{ row.tanggal }}</td>

          <!-- Petugas -->
          <td class="fw-semibold">{{ row.nama_security }}</td>

          <!-- Judul -->
          <td class="text-start fw-semibold" style="color:#1e293b;">{{ row.judul }}</td>

          <!-- Tingkat -->
          <td>
            {% if row.tingkat_perhatian == 'merah' %}
              <span class="badge px-3 py-2" style="background:#dc2626;border-radius:50rem;">🔴 Merah</span>
            {% elif row.tingkat_perhatian == 'kuning' %}
              <span class="badge px-3 py-2" style="background:#facc15;color:#1e293b;border-radius:50rem;">🟡 Kuning</span>
            {% else %}
              <span class="badge px-3 py-2" style="background:#16a34a;border-radius:50rem;">🟢 Hijau</span>
            {% endif %}
          </td>

          <!-- Status -->
          <td>
            {% if row.status_dibaca %}
              <span class="badge px-3 py-2" style="background:#22c55e;border-radius:50rem;">Dibaca</span>
            {% else %}
              <span class="badge px-3 py-2" style="background:#94a3b8;border-radius:50rem;">Belum</span>
            {% endif %}
          </td>

          <!-- Dibuat -->
          <td style="color:#64748b;">{{ row.created_at }}</td>

          <!-- Tombol -->
          <td>
            <a 
              href="{{ url_for('detail_laporan', laporan_id=row.id) }}" 
              class="btn btn-sm rounded-pill px-3"
              style="font-weight:600;border:1px solid #6366f1;color:#4f46e5;background:white;">
              Detail
            </a>
          </td>

        </tr>

      {% else %}
        <tr>
          <td colspan="8" class="text-center py-4 text-muted">
            Belum ada laporan.
          </td>
        </tr>
      {% endfor %}

      </tbody>
    </table>

  </div>
</div>

<style>
  /* Efek hover baris tabel */
  table tbody tr:hover {
    background:#f8fafc;
  }
</style>

   """

   return render_page("Semua Laporan", inner, laporan=laporan)


# app.py: Ganti seluruh fungsi detail_laporan() dengan kode ini
# =====================================================================
# DETAIL LAPORAN + FEEDBACK SUPERVISOR
# =====================================================================
@app.route("/laporan/detail/<int:laporan_id>", methods=["GET", "POST"])
@login_required
@role_required("supervisor")
def detail_laporan(laporan_id):

    conn = get_db()
    cur = conn.cursor()

    # Ambil data laporan
    cur.execute("""
        SELECT l.*, u.username AS nama_security
        FROM laporan l
        JOIN users u ON u.id = l.security_id
        WHERE l.id=%s
    """, (laporan_id,))
    laporan = cur.fetchone()

    if not laporan:
        flash("Laporan tidak ditemukan.", "danger")
        conn.close()
        return redirect(url_for("list_laporan_supervisor"))

    # POST = Supervisor memberi feedback
    if request.method == "POST":
        feedback = request.form.get("feedback", "").strip()
        now = datetime.now()

        try:
            cur.execute("""
                UPDATE laporan
                SET feedback=%s, supervisor_id=%s, waktu_feedback=%s
                WHERE id=%s
            """, (feedback, session["user_id"], now, laporan_id))
            conn.commit()
            flash("Feedback disimpan.", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error: {str(e)}", "danger")

    # Tandai sebagai dibaca
    if laporan["status_dibaca"] == 0:
        now = datetime.now()
        try:
            cur.execute("""
                UPDATE laporan
                SET status_dibaca=1, supervisor_id=%s, waktu_dibaca=%s
                WHERE id=%s
            """, (session["user_id"], now, laporan_id))
            conn.commit()
        except:
            pass

    # Refresh data terbaru
    cur.execute("""
        SELECT l.*, u.username AS nama_security
        FROM laporan l
        JOIN users u ON u.id = l.security_id
        WHERE l.id=%s
    """, (laporan_id,))
    laporan = cur.fetchone()

    conn.close()

    # ================= TEMPLATE DETAIL LAPORAN ================
    inner = """
<h2 class="fw-bold mb-4">📝 Detail Laporan #{{ laporan.id }}</h2>

<div class="card border-0 shadow-sm rounded-4 mb-4">
  <div class="card-body p-4">

    <table class="table table-borderless">
      <tr>
        <th class="text-muted w-25">Tanggal</th>
        <td>{{ laporan.tanggal }}</td>
      </tr>

      <tr>
        <th class="text-muted">Petugas</th>
        <td>{{ laporan.nama_security }}</td>
      </tr>

      <tr>
        <th class="text-muted">Judul</th>
        <td class="fw-semibold">{{ laporan.judul }}</td>
      </tr>

      <tr>
        <th class="text-muted">Detail Kejadian</th>
        <td>{{ laporan.detail }}</td>
      </tr>

      <tr>
        <th class="text-muted">Catatan Khusus</th>
        <td>{{ laporan.catatan_khusus or '-' }}</td>
      </tr>

      <tr>
        <th class="text-muted">Tingkat</th>
        <td>
          {% if laporan.tingkat_perhatian == 'merah' %}
            <span class="badge bg-danger px-3 py-2 rounded-pill">🔴 Merah</span>
          {% elif laporan.tingkat_perhatian == 'kuning' %}
            <span class="badge bg-warning text-dark px-3 py-2 rounded-pill">🟡 Kuning</span>
          {% else %}
            <span class="badge bg-success px-3 py-2 rounded-pill">🟢 Hijau</span>
          {% endif %}
        </td>
      </tr>

      <tr>
        <th class="text-muted">Foto</th>
        <td>
          {% if laporan.foto_nama %}
            <img src="{{ url_for('static', filename='uploads/' ~ laporan.foto_nama) }}" 
                 class="img-fluid rounded shadow-sm" style="max-width:260px;">
          {% else %}
            <span class="text-muted fst-italic">Tidak ada foto</span>
          {% endif %}
        </td>
      </tr>

      <tr>
        <th class="text-muted">Status Dibaca</th>
        <td>
          {% if laporan.status_dibaca %}
            <span class="badge bg-success rounded-pill px-3 py-2">Dibaca</span>
          {% else %}
            <span class="badge bg-secondary rounded-pill px-3 py-2">Belum</span>
          {% endif %}
        </td>
      </tr>

      <tr>
        <th class="text-muted">Feedback Sebelumnya</th>
        <td>{{ laporan.feedback or '-' }}</td>
      </tr>
    </table>

  </div>
</div>

<!-- FORM FEEDBACK -->
<div class="card border-0 shadow-sm rounded-4">
  <div class="card-body p-4">
    <h5 class="fw-bold mb-3">💬 Beri Feedback</h5>

    <form method="post">
      <textarea 
        class="form-control form-control-lg mb-3 rounded-3" 
        name="feedback" 
        rows="3"
        placeholder="Tulis feedback supervisor...">{{ laporan.feedback or '' }}</textarea>

      <button class="btn btn-primary btn-lg rounded-pill px-4">💾 Simpan</button>

      <a href="{{ url_for('list_laporan_supervisor') }}" 
         class="btn btn-outline-secondary btn-lg rounded-pill px-4 ms-2">
         Kembali
      </a>
    </form>
  </div>
</div>
    """

    return render_page(
        f"Detail Laporan #{laporan['id']}",
        inner,
        laporan=laporan
    )



# =====================================================================
# DASHBOARD SUPERVISOR
# =====================================================================
@app.route("/dashboard")
@login_required
@role_required("supervisor")
def dashboard():

   today = date.today()
   start = request.args.get("start") or (today - timedelta(days=7)).isoformat()
   end   = request.args.get("end") or today.isoformat()

   conn = get_db()
   cur = conn.cursor()


   # Total laporan
   cur.execute("SELECT COUNT(*) AS total FROM laporan WHERE tanggal BETWEEN %s AND %s", (start, end))
   total = cur.fetchone()["total"]

   # Rekap tingkat perhatian
   cur.execute("""
       SELECT tingkat_perhatian, COUNT(*) AS jumlah
       FROM laporan
       WHERE tanggal BETWEEN %s AND %s
       GROUP BY tingkat_perhatian
   """, (start, end))
   rows = cur.fetchall()

   merah = kuning = hijau = 0
   for r in rows:
       if r["tingkat_perhatian"] == "merah": merah = r["jumlah"]
       elif r["tingkat_perhatian"] == "kuning": kuning = r["jumlah"]
       elif r["tingkat_perhatian"] == "hijau":  hijau = r["jumlah"]

   # Laporan terlambat
   cur.execute("""
       SELECT tanggal AS tgl_kejadian, DATE(created_at) AS tgl_buat, COUNT(*) AS jumlah
       FROM laporan
       WHERE tanggal BETWEEN %s AND %s
       AND DATE(created_at) <> tanggal
       GROUP BY tanggal, DATE(created_at)
       ORDER BY tanggal DESC
   """, (start, end))
   terlambat = cur.fetchall()

   # Rata-rata respon
   cur.execute("""
       SELECT AVG(TIMESTAMPDIFF(MINUTE, created_at, waktu_dibaca)) AS rata
       FROM laporan
       WHERE waktu_dibaca IS NOT NULL AND tanggal BETWEEN %s AND %s
   """, (start, end))
   avg_respon = cur.fetchone()["rata"]

   conn.close()

   inner = """
<h2 class="fw-bold mb-4" style="color:#1e293b;">📊 Dashboard</h2>

<!-- ================= FILTER TANGGAL ================= -->
<div class="card shadow-sm border-0 rounded-4 mb-4">
  <div class="card-body p-4">

    <form method="get" class="row g-3">
      <div class="col-md-3">
        <label class="fw-semibold text-slate-700">Dari</label>
        <input 
          type="date" 
          name="start" 
          class="form-control form-control-lg rounded-3"
          value="{{ start }}">
      </div>

      <div class="col-md-3">
        <label class="fw-semibold text-slate-700">Sampai</label>
        <input 
          type="date" 
          name="end" 
          class="form-control form-control-lg rounded-3"
          value="{{ end }}">
      </div>

      <div class="col-md-3 align-self-end">
        <button 
          class="btn btn-primary btn-lg px-4 fw-semibold rounded-pill shadow-sm"
        >
          Terapkan
        </button>
      </div>
    </form>

  </div>
</div>


<!-- ================= KARTU STATISTIK ================= -->
<div class="row g-3 mb-4">

  <!-- Total Laporan -->
  <div class="col-md-3">
    <div class="card shadow-sm border-0 rounded-4" style="background:#4f46e5;">
      <div class="card-body py-4 px-4">
        <h6 class="fw-semibold text-white-50 mb-1">Total Laporan</h6>
        <p class="display-5 fw-bold text-white mb-0">{{ total }}</p>
      </div>
    </div>
  </div>

  <!-- Tingkat Perhatian -->
  <div class=
   """

   return render_page(
       "Dashboard", inner,
       start=start, end=end,
       total=total,
       merah=merah, kuning=kuning, hijau=hijau,
       avg_respon=avg_respon,
       terlambat=terlambat
   )



# =====================================================================
# MAIN
# =====================================================================
if __name__ == "__main__":
   app.run(debug=True)
