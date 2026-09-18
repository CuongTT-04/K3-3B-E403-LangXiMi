const cards = [...document.querySelectorAll('.question-card')];
const progressText = document.querySelector('#progressText');
const progressBar = document.querySelector('#progressBar');
const toast = document.querySelector('#toast');

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2200);
}

document.querySelectorAll('.explain-toggle').forEach(button => {
  button.addEventListener('click', () => {
    const expanded = button.getAttribute('aria-expanded') === 'true';
    button.setAttribute('aria-expanded', String(!expanded));
    button.nextElementSibling.classList.toggle('open', !expanded);
    button.childNodes[0].textContent = !expanded ? '✦ Ẩn phần giải thích ' : '✦ Xem AI giải thích lỗi sai ';
  });
});

document.querySelectorAll('.reviewed-btn').forEach(button => {
  button.addEventListener('click', () => {
    const card = button.closest('.question-card');
    const reviewed = card.classList.toggle('reviewed');
    card.querySelector('.status').textContent = reviewed ? '✓ Đã xem lại' : 'Chưa xem lại';
    button.textContent = reviewed ? 'Đã hiểu ✓' : 'Đánh dấu đã hiểu ✓';
    const count = document.querySelectorAll('.question-card.reviewed').length;
    progressText.textContent = `${count}/3`;
    progressBar.style.width = `${count / 3 * 100}%`;
    showToast(reviewed ? '✓ Đã lưu tiến độ của bạn' : 'Đã bỏ đánh dấu');
  });
});

document.querySelectorAll('.topic').forEach(button => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.topic').forEach(item => item.classList.remove('active'));
    button.classList.add('active');
    const filter = button.dataset.filter;
    cards.forEach(card => card.classList.toggle('hidden', filter !== 'all' && card.dataset.topic !== filter));
  });
});

const modal = document.querySelector('#practiceModal');
document.querySelector('#startPractice').addEventListener('click', () => {
  modal.classList.add('open');
  modal.setAttribute('aria-hidden', 'false');
});
function closeModal() { modal.classList.remove('open'); modal.setAttribute('aria-hidden', 'true'); }
document.querySelector('.modal-close').addEventListener('click', closeModal);
modal.addEventListener('click', event => { if (event.target === modal) closeModal(); });
document.addEventListener('keydown', event => { if (event.key === 'Escape') closeModal(); });
document.querySelectorAll('.options button').forEach(option => option.addEventListener('click', () => {
  document.querySelectorAll('.options button').forEach(item => item.classList.remove('selected-correct'));
  if (option.classList.contains('correct-option')) {
    option.classList.add('selected-correct');
    document.querySelector('.modal-hint').textContent = '✓ Chính xác! Query được so sánh với Key.';
  } else {
    document.querySelector('.modal-hint').textContent = 'Chưa đúng. Hãy nhớ ví dụ tìm sách trong thư viện nhé!';
  }
}));
document.querySelector('#finishBtn').addEventListener('click', () => showToast('Bài học đã được lưu. Hẹn gặp lại!'));
