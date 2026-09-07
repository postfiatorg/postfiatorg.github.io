(() => {
  'use strict';
  const scenarios = {
    original: { failed: null, verdict: 'Accepted in this illustration', explanation: 'The proof matches the registered run, the public result is unchanged and the registration has not been consumed.' },
    rules: { failed: 'registration', verdict: 'Rejected: different rulebook', explanation: 'The substituted methodology or parameter commitment differs from the registered expectations. A different strategy needs a different explicitly identified run.' },
    input: { failed: 'registration', verdict: 'Rejected: different input collection', explanation: 'Replacing the collection commitment breaks its binding to the registered run. The operator cannot pass a different collection off as the registered one.' },
    target: { failed: 'proof', verdict: 'Rejected: altered target', explanation: 'Changing the target commitment in the public result invalidates the proof binding. The original proof does not certify the substituted output.' },
    duplicate: { failed: 'replay', verdict: 'Rejected: run already consumed', explanation: 'Even a valid proof cannot create a second receipt for the same registration. This is a ledger-state rule in addition to cryptographic proof verification.' }
  };
  document.querySelectorAll('[data-ot-verification]').forEach(panel => {
    const labels = { registration: ['Match', 'Mismatch'], proof: ['Valid', 'Invalid binding'], replay: ['Available', 'Already consumed'] };
    panel.querySelectorAll('[data-scenario]').forEach(button => {
      button.addEventListener('click', () => {
        const selected = scenarios[button.dataset.scenario];
        if (!selected) return;
        panel.querySelectorAll('[data-scenario]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
        panel.querySelectorAll('[data-check]').forEach(check => {
          const failed = check.dataset.check === selected.failed;
          const skipped = selected.failed === 'registration' && check.dataset.check !== 'registration';
          const proofNotNeeded = selected.failed === 'replay' && check.dataset.check === 'proof';
          check.dataset.state = failed ? 'failed' : (skipped || proofNotNeeded ? 'skipped' : 'passed');
          check.querySelector('.ot-check-mark').textContent = failed ? '×' : (skipped || proofNotNeeded ? '—' : '✓');
          check.querySelector('[data-check-text]').textContent = skipped ? 'Not needed after rejection' : (proofNotNeeded ? 'Original proof; no new check needed' : labels[check.dataset.check][failed ? 1 : 0]);
        });
        panel.querySelector('.ot-verdict').dataset.state = selected.failed ? 'failed' : 'passed';
        panel.querySelector('[data-verdict]').textContent = selected.verdict;
        panel.querySelector('[data-explanation]').textContent = selected.explanation;
      });
    });
  });
})();
