CREATE DATABASE IF NOT EXISTS portfolio_vanessa
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE portfolio_vanessa;

CREATE TABLE IF NOT EXISTS users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(10) NOT NULL DEFAULT 'admin',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT users_username_uk UNIQUE (username)
);

CREATE TABLE IF NOT EXISTS profiles (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  nama_lengkap VARCHAR(100) NOT NULL,
  nama_panggilan VARCHAR(50),
  tempat_lahir VARCHAR(50),
  tanggal_lahir DATE,
  email VARCHAR(100),
  telepon VARCHAR(20),
  universitas VARCHAR(100),
  fakultas VARCHAR(100),
  prodi VARCHAR(100),
  semester VARCHAR(20),
  alamat VARCHAR(4000),
  foto_url VARCHAR(255),
  CONSTRAINT profiles_user_uk UNIQUE (user_id),
  CONSTRAINT profiles_users_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS skills (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  nama_skill VARCHAR(50) NOT NULL,
  icon_class VARCHAR(50),
  CONSTRAINT skills_users_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS experiences (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  posisi VARCHAR(100) NOT NULL,
  perusahaan VARCHAR(100) NOT NULL,
  durasi VARCHAR(50),
  deskripsi VARCHAR(4000),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT experiences_users_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS projects (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  judul VARCHAR(100) NOT NULL,
  deskripsi VARCHAR(4000),
  gambar_url VARCHAR(255),
  link_project VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT projects_users_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabel tambahan untuk kebutuhan fitur Kontak pada instruksi tugas.
CREATE TABLE IF NOT EXISTS contact_messages (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  nama VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  subjek VARCHAR(150),
  pesan VARCHAR(4000) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'baru',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Akun admin dibuat otomatis oleh app.py dengan password yang di-hash.
-- Default development: username admin, password admin123.
