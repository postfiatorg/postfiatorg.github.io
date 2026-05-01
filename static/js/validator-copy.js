(function(){
  const root = document.getElementById('pftValidatorCopyTool');
  if (!root) return;

  const sourceUrl = '/agents/validator-setup.md';
  const markdownBox = document.getElementById('pftValidatorMarkdown');
  const status = document.getElementById('pftValidatorCopyStatus');
  const copyButton = root.querySelector('[data-copy-validator-markdown]');
  let markdownText = '';

  function setStatus(message) {
    if (!status) return;
    status.textContent = message;
    if (!message) return;

    window.setTimeout(() => {
      if (status.textContent === message) {
        status.textContent = '';
      }
    }, 2500);
  }

  async function loadMarkdown() {
    if (!markdownBox) return;

    try {
      const response = await fetch(sourceUrl, { cache: 'no-store' });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      markdownText = await response.text();
      markdownBox.value = markdownText;
      setStatus('Official markdown loaded');
    } catch (error) {
      markdownText = '';
      markdownBox.value = `Unable to load ${sourceUrl}. Use the Open raw markdown link above.`;
      setStatus('Could not load markdown');
    }
  }

  async function copyText(text) {
    if (!text || text.startsWith('Loading official validator markdown')) {
      setStatus('Markdown is still loading');
      return;
    }

    try {
      await navigator.clipboard.writeText(text);
    } catch (error) {
      const scratch = document.createElement('textarea');
      scratch.value = text;
      scratch.setAttribute('readonly', '');
      scratch.style.position = 'fixed';
      scratch.style.opacity = '0';
      document.body.appendChild(scratch);
      scratch.select();
      document.execCommand('copy');
      document.body.removeChild(scratch);
    }

    setStatus('Full markdown copied');
  }

  if (copyButton) {
    copyButton.addEventListener('click', () => {
      copyText(markdownText || (markdownBox ? markdownBox.value : ''));
    });
  }

  loadMarkdown();
})();
