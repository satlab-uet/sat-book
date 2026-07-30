document.addEventListener('DOMContentLoaded', () => {
  const copyBtn = document.getElementById('copy-bibtex-btn');
  const bibtexCode = document.getElementById('bibtex-code');
  const copyToast = document.getElementById('copy-toast');

  if (copyBtn && bibtexCode) {
    copyBtn.addEventListener('click', async () => {
      const textToCopy = bibtexCode.textContent.trim();
      try {
        await navigator.clipboard.writeText(textToCopy);
        if (copyToast) {
          copyToast.textContent = '✓ Đã sao chép BibTeX';
          setTimeout(() => {
            copyToast.textContent = '';
          }, 3000);
        }
      } catch (err) {
        console.error('Lỗi khi sao chép: ', err);
      }
    });
  }
});
