document.addEventListener('DOMContentLoaded', () => {
  const detailPoster = document.getElementById('detailPoster');
  const posterModal = document.getElementById('posterModal');
  const closeModal = document.getElementById('closeModal');
  const fullPoster = document.getElementById('fullPoster');

  if (detailPoster) {
    detailPoster.addEventListener('click', () => {
      fullPoster.src = detailPoster.src;  // or bigger image URL if you want
      posterModal.style.display = 'flex';
    });
  }

  closeModal.addEventListener('click', () => {
    posterModal.style.display = 'none';
  });

  posterModal.addEventListener('click', (event) => {
    if (event.target === posterModal) {
      posterModal.style.display = 'none';
    }
  });
});