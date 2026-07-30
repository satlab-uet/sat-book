(() => {
  const copyButton = document.querySelector("[data-copy-target]");
  if (!copyButton) {
    return;
  }

  const status = copyButton.parentElement.querySelector("[role='status']");
  const target = document.getElementById(copyButton.dataset.copyTarget);

  copyButton.addEventListener("click", async () => {
    if (!target) {
      return;
    }

    const text = target.innerText.replace(/\s+/g, " ").trim();

    try {
      await navigator.clipboard.writeText(text);
      copyButton.textContent = "Đã sao chép";
      status.textContent = "Trích dẫn đã được lưu vào bộ nhớ tạm.";
    } catch {
      const range = document.createRange();
      range.selectNodeContents(target);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      status.textContent = "Đã chọn trích dẫn; nhấn Ctrl+C hoặc ⌘C để sao chép.";
    }

    window.setTimeout(() => {
      copyButton.textContent = "Sao chép trích dẫn";
      status.textContent = "";
    }, 3000);
  });
})();
