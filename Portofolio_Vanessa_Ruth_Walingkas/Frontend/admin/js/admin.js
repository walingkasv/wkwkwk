const menuButton = document.getElementById('menuButton');
const sidebar = document.getElementById('sidebar');
if (menuButton && sidebar) {
  menuButton.addEventListener('click', () => sidebar.classList.toggle('open'));
}
document.querySelectorAll('form[data-confirm]').forEach((form) => {
  form.addEventListener('submit', (event) => {
    if (!confirm(form.dataset.confirm || 'Lanjutkan tindakan ini?')) event.preventDefault();
  });
});
setTimeout(() => document.querySelectorAll('.alert').forEach((el) => el.remove()), 5000);
