# Web Portofolio — Vanessa Ruth Walingkas

Aplikasi portofolio full-stack menggunakan **Python Flask**, **HTML/CSS/JavaScript**, **TiDB Cloud**, **Cloudinary**, dan **Resend**. Data awal profil sudah disesuaikan menjadi:

- Nama: Vanessa Ruth Walingkas
- Program studi: Sistem Informasi
- Skill: sengaja belum diisi; dapat ditambahkan kemudian melalui menu Admin → Skills.

## Fitur

- Halaman utama dinamis melalui endpoint `GET /api/portfolio`
- Login admin dengan session dan password hash
- CRUD profil, skill, pengalaman, proyek, serta pesan kontak
- Upload foto profil dan gambar proyek ke Cloudinary
- Form kontak: simpan ke database dan kirim email menggunakan Resend
- TiDB/MySQL untuk pengumpulan dan SQLite sebagai fallback demo lokal
- Validasi file gambar, CSRF untuk halaman admin, honeypot form kontak, dan responsive layout

## Struktur database

Tabel mengikuti ERD: `users`, `profiles`, `skills`, `experiences`, dan `projects`. Tabel `contact_messages` ditambahkan karena instruksi tugas juga mewajibkan pengelolaan kontak.

## Menjalankan di Windows / VS Code

1. Ekstrak ZIP lalu buka folder proyek di VS Code.
2. Buka terminal:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

3. Edit `.env`.
   - Untuk mencoba cepat tanpa TiDB: ubah `DB_DRIVER=sqlite`.
   - Untuk tugas akhir: gunakan `DB_DRIVER=tidb` dan isi kredensial TiDB.
4. Jalankan:

```powershell
python app.py
```

5. Buka:
   - Website: `http://127.0.0.1:5000`
   - Admin: `http://127.0.0.1:5000/admin/login`
   - Login awal: `admin` / `admin123`

## Konfigurasi TiDB dan CA Path

Secara default aplikasi memakai CA bundle dari `certifi`. Jika TiDB mewajibkan file CA khusus,
isi absolute path pada `.env`:

```env
DB_CA_PATH=C:/Users/Nama/Downloads/isrgrootx1.pem
```

Gunakan garis miring `/` di Windows agar tidak bermasalah dengan escape character. Jangan beri tanda kutip kecuali path mengandung karakter khusus.

## Cloudinary

Isi tiga variabel Cloudinary. Upload tersedia pada:

- Admin → Profil → Upload foto
- Admin → Proyek → Upload gambar

URL aman (`secure_url`) hasil Cloudinary disimpan ke kolom `foto_url` atau `gambar_url`.

## Resend

Isi `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, dan `RESEND_TO_EMAIL`. Pada akun Resend baru, `onboarding@resend.dev` biasanya hanya dapat digunakan sesuai aturan testing akun. Untuk produksi, verifikasi domain pengirim.

## File SQL

File disediakan sebagai:

`DB_682024101_VANESSA_RUTH_WALINGKAS.sql`

## Screenshot pengumpulan

Folder `screenshots` berisi screenshot halaman yang dapat dibuat tanpa kredensial layanan. Setelah mengisi Cloudinary dan Resend, tambahkan screenshot full screen:

1. Halaman Admin
2. Halaman Login
3. Halaman Utama
4. Hasil upload pada Media Library Cloudinary
5. Bukti email pada dashboard/log Resend atau inbox tujuan

## Catatan keamanan

- Jangan mengumpulkan atau mengunggah file `.env` yang berisi API key ke GitHub.
- `.env.example` aman karena hanya berisi placeholder.
- Segera ganti password admin setelah login pertama.
