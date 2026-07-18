const $ = (selector) => document.querySelector(selector);
const escapeHtml = (value = '') => String(value).replace(/[&<>'"]/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));

$('#year').textContent = new Date().getFullYear();
window.addEventListener('scroll', () => $('#navbar').classList.toggle('scrolled', window.scrollY > 30));
$('#navToggle').addEventListener('click', () => $('#navLinks').classList.toggle('open'));
document.querySelectorAll('#navLinks a').forEach((link) => link.addEventListener('click', () => $('#navLinks').classList.remove('open')));

async function loadPortfolio() {
  try {
    const response = await fetch('/api/portfolio');
    if (!response.ok) throw new Error('Data portofolio gagal dimuat.');
    const data = await response.json();
    renderProfile(data.profile || {});
    renderSkills(data.skills || []);
    renderExperiences(data.experiences || []);
    renderProjects(data.projects || []);
  } catch (error) {
    ['#skillsGrid', '#experienceList', '#projectGrid'].forEach((id) => $(id).innerHTML = `<div class="empty-public">${escapeHtml(error.message)}</div>`);
  }
}

function renderProfile(profile) {
  const firstName = (profile.nama_panggilan || profile.nama_lengkap || 'Vanessa').split(' ')[0];
  $('#heroName').textContent = firstName;
  $('#heroStudy').textContent = profile.prodi || 'Sistem Informasi';
  $('#heroSummary').textContent = profile.alamat || 'Mahasiswa Sistem Informasi yang tertarik pada teknologi, desain, dan pengembangan solusi digital.';
  $('#aboutText').textContent = profile.alamat || 'Profil lengkap dapat dikelola melalui halaman admin.';
  $('#factName').textContent = profile.nama_lengkap || 'Vanessa Ruth Walingkas';
  $('#factUniversity').textContent = profile.universitas || 'Belum diisi';
  $('#factSemester').textContent = profile.semester || 'Belum diisi';
  $('#factEmail').textContent = profile.email || 'Belum diisi';
  const emailLink = $('#contactEmail');
  emailLink.textContent = profile.email || 'Email belum diisi';
  emailLink.href = profile.email ? `mailto:${profile.email}` : '#';
  if (profile.foto_url) {
    $('#portrait').src = profile.foto_url;
    $('#portrait').style.display = 'block';
    $('#portraitPlaceholder').style.display = 'none';
  }
}

function renderSkills(items) {
  $('#skillsGrid').innerHTML = items.length ? items.map((item, index) => `
    <article class="skill-card"><span class="skill-index">${String(index + 1).padStart(2, '0')}</span><h3>${escapeHtml(item.nama_skill)}</h3></article>
  `).join('') : '<div class="empty-public"><strong>Skill akan segera ditambahkan.</strong><br>Backend CRUD sudah siap digunakan.</div>';
}

function renderExperiences(items) {
  $('#experienceList').innerHTML = items.length ? items.map((item) => `
    <article class="timeline-item"><div class="duration">${escapeHtml(item.durasi || 'Periode belum diisi')}</div><div><h3>${escapeHtml(item.posisi)}</h3><strong>${escapeHtml(item.perusahaan || '')}</strong></div><p>${escapeHtml(item.deskripsi || '')}</p></article>
  `).join('') : '<div class="empty-public">Pengalaman belum ditambahkan.</div>';
}

function renderProjects(items) {
  $('#projectGrid').innerHTML = items.length ? items.map((item, index) => `
    <article class="project-card"><div class="project-image">${item.gambar_url ? `<img src="${escapeHtml(item.gambar_url)}" alt="${escapeHtml(item.judul)}">` : `PROJECT ${String(index + 1).padStart(2, '0')}`}</div><div class="project-info"><small>PROJECT ${String(index + 1).padStart(2, '0')}</small><h3>${escapeHtml(item.judul)}</h3><p>${escapeHtml(item.deskripsi || '')}</p>${item.link_project ? `<a href="${escapeHtml(item.link_project)}" target="_blank" rel="noopener">Lihat proyek ↗</a>` : ''}</div></article>
  `).join('') : '<div class="empty-public dark-empty">Proyek belum ditambahkan.</div>';
}

$('#contactForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const button = $('#submitButton');
  const status = $('#formStatus');
  button.disabled = true;
  button.textContent = 'Mengirim...';
  status.className = 'form-status';
  status.textContent = '';
  try {
    const payload = Object.fromEntries(new FormData(form).entries());
    const response = await fetch('/api/contact', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Pesan gagal dikirim.');
    status.classList.add('success');
    status.textContent = result.message;
    form.reset();
  } catch (error) {
    status.classList.add('error');
    status.textContent = error.message;
  } finally {
    button.disabled = false;
    button.textContent = 'Kirim Pesan';
  }
});

loadPortfolio();
