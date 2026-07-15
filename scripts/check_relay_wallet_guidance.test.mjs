import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  GUIDE_FILES,
  FALLBACK_MARKER,
  checkGuideText,
  checkSurfaceSync,
  runChecks,
} from "./check_relay_wallet_guidance.mjs";

const repoRoot = resolve(fileURLToPath(import.meta.url), "../..");

function readGuides() {
  return GUIDE_FILES.map((path) => ({
    path,
    text: readFileSync(resolve(repoRoot, path), "utf8"),
  }));
}

function violationIds(violations) {
  return violations.map((v) => (v.match(/\[([a-z-]+)\]/) || [])[1]).filter(Boolean);
}

test("the published guides pass every check", () => {
  assert.deepEqual(runChecks(repoRoot), []);
});

test("rejects guidance that stops making the Task Node wallet the default", () => {
  const { path, text } = readGuides()[0];
  const reversed = text.replace(
    "the wallet active in your Task Node account is the default relay wallet",
    "the easiest path is a fresh wallet",
  );
  assert.ok(violationIds(checkGuideText(path, reversed)).includes("reuse-default"));
});

test("rejects guidance that reverts to the legacy creation-as-default wording", () => {
  const { path, text } = readGuides()[0];
  const legacy = text.replace(
    "retrieve the wallet secret of my existing Task Node wallet",
    "create and fund a Task Node relay wallet",
  );
  const ids = violationIds(checkGuideText(path, legacy));
  assert.ok(ids.includes("legacy-create-prompt"));
  assert.ok(ids.includes("prompt-default"));
});

test("rejects guidance that presents wallet creation as more than a fallback", () => {
  const { path, text } = readGuides()[0];
  const creationFirst = text.replace(FALLBACK_MARKER, "If you want a wallet");
  const ids = violationIds(checkGuideText(path, creationFirst));
  assert.ok(ids.includes("fallback-offered"));
  assert.ok(ids.includes("creation-before-fallback"));
});

test("rejects guidance that moves wallet creation ahead of the fallback", () => {
  const { path, text } = readGuides()[0];
  const creationEarly = text.replace("## Scope", "Reply `new_wallet` to begin.\n\n## Scope");
  assert.ok(violationIds(checkGuideText(path, creationEarly)).includes("creation-before-fallback"));
});

test("rejects guidance that loses the seed-retrieval path", () => {
  const { path, text } = readGuides()[0];
  const noRetrieval = text.replaceAll("Back up seed", "your records");
  assert.ok(violationIds(checkGuideText(path, noRetrieval)).includes("seed-retrieval-action"));
});

test("rejects guidance that lets the seed into agent chat", () => {
  const { path, text } = readGuides()[0];
  const seedInChat = text
    .replace("never into agent chat", "or paste it into agent chat")
    .replace("Never ask for or accept the relay seed", "The agent may collect the relay seed");
  const ids = violationIds(checkGuideText(path, seedInChat));
  assert.ok(ids.includes("seed-not-in-chat"));
  assert.ok(ids.includes("seed-not-requested"));
});

test("rejects guidance that omits the wallet-separation rules", () => {
  const { path, text } = readGuides()[0];
  const noSeparation = text
    .replaceAll("account from your validator identity", "account of your choosing")
    .replaceAll("give each instance its own relay wallet", "wallets can be shared freely");
  const ids = violationIds(checkGuideText(path, noSeparation));
  assert.ok(ids.includes("validator-identity-separation"));
  assert.ok(ids.includes("per-sidecar-wallet"));
});

test("rejects agent-facing copies that are not byte-identical", () => {
  const files = readGuides();
  const mutated = files.map((f) =>
    f.path === "static/agents/validator-sidecar.txt" ? { ...f, text: `${f.text}\ndrifted` } : f,
  );
  const violations = checkSurfaceSync(mutated);
  assert.ok(violations.some((v) => v.includes("not byte-identical")));
});

test("rejects a relay-wallet section that drifts between surfaces", () => {
  const files = readGuides();
  const mutated = files.map((f) =>
    f.path === "content/validator-sidecar.md"
      ? { ...f, text: f.text.replace("pays the small per-round fees", "pays the fees") }
      : f,
  );
  const violations = checkSurfaceSync(mutated);
  assert.ok(violations.some((v) => v.includes("relay-wallet section") && v.includes("drifted")));
});

test("rejects a participation prompt that drifts between surfaces", () => {
  const files = readGuides();
  const mutated = files.map((f) =>
    f.path === "content/validator-sidecar.md"
      ? {
          ...f,
          text: f.text.replace(
            "retrieve the wallet secret of my existing Task Node wallet",
            "retrieve the wallet secret of my current Task Node wallet",
          ),
        }
      : f,
  );
  const violations = checkSurfaceSync(mutated);
  assert.ok(violations.some((v) => v.includes("participation prompt") && v.includes("drifted")));
});

test("rejects a surface whose relay-wallet section disappears", () => {
  const files = readGuides();
  const mutated = files.map((f) =>
    f.path === "content/validator-sidecar.md"
      ? { ...f, text: f.text.replace("### B2 —", "### Wallets —") }
      : f,
  );
  const violations = checkSurfaceSync(mutated);
  assert.ok(violations.some((v) => v.includes("relay-wallet section") && v.includes("not found")));
});
