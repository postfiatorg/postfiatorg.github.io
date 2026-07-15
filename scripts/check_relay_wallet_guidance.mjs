// Guards the relay-wallet guidance in the validator sidecar setup guides.
// The guides are executed by coding agents on operator hosts, so wording drift
// directly changes operator behavior: during the community rollout, agents
// steered operators into creating new Task Node wallets because the text made
// creation the default. This check fails pull-request validation whenever the
// guidance stops making the operator's existing Task Node wallet the default,
// lets seed material into agent chat, drops the wallet-separation rules, or
// lets the three published surfaces drift apart.
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

export const GUIDE_FILES = [
  "content/validator-sidecar.md",
  "static/agents/validator-sidecar.md",
  "static/agents/validator-sidecar.txt",
];

const IDENTICAL_AGENT_COPIES = [
  "static/agents/validator-sidecar.md",
  "static/agents/validator-sidecar.txt",
];

export const FALLBACK_MARKER = "Only if you don't want to use your Task Node wallet";

const B2_HEADING = "### B2 —";
const NEXT_SECTION_HEADING = "### B3 —";
const PROMPT_START = "I will provide the relay wallet seed";

const REQUIRED_PATTERNS = [
  {
    id: "reuse-default",
    description: "the wallet active in the operator's Task Node account must be stated as the default relay wallet",
    pattern: /the wallet active in your Task Node account is the default relay wallet/,
  },
  {
    id: "seed-retrieval-page",
    description: "seed retrieval must point at the Task Node wallet page",
    pattern: /tasknode\.postfiat\.org\/#wallet/,
  },
  {
    id: "seed-retrieval-action",
    description: "seed retrieval must name the Back up seed action",
    pattern: /Back up seed/,
  },
  {
    id: "seed-not-in-chat",
    description: "the retrieved wallet secret must be kept out of agent chat",
    pattern: /never into agent chat/,
  },
  {
    id: "seed-not-requested",
    description: "agents must be forbidden from asking for the relay seed in chat",
    pattern: /Never ask for or accept the relay seed/,
  },
  {
    id: "prompt-default",
    description: "the pasted quick-start prompt must default to retrieving the existing Task Node wallet secret",
    pattern: /retrieve the wallet secret of my existing Task Node wallet/,
  },
  {
    id: "fallback-offered",
    description: "creating a new wallet must be offered as the explicit fallback",
    pattern: new RegExp(FALLBACK_MARKER.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")),
  },
  {
    id: "validator-identity-separation",
    description: "the relay wallet must be required to differ from the validator identity",
    pattern: /account from your validator identity/,
  },
  {
    id: "per-sidecar-wallet",
    description: "each sidecar instance must be required to use its own relay wallet",
    pattern: /give each instance its own relay wallet/,
  },
];

const FORBIDDEN_PHRASES = [
  {
    id: "legacy-create-prompt",
    description: "the quick-start prompt presents wallet creation as the default hand-step",
    phrase: "create and fund a Task Node relay wallet",
  },
  {
    id: "legacy-create-heading",
    description: "the relay-wallet section presents wallet creation as the default path",
    phrase: "Get A Funded Relay Wallet (Task Node, default)",
  },
  {
    id: "legacy-create-lede",
    description: "the relay-wallet section leads with obtaining a new funded wallet",
    phrase: "The easiest way to get a funded one is",
  },
];

export function checkGuideText(path, text) {
  const violations = [];

  for (const { id, description, pattern } of REQUIRED_PATTERNS) {
    if (!pattern.test(text)) {
      violations.push(`${path}: missing required guidance [${id}] — ${description}`);
    }
  }

  for (const { id, description, phrase } of FORBIDDEN_PHRASES) {
    if (text.includes(phrase)) {
      violations.push(`${path}: forbidden legacy wording [${id}] — ${description} ("${phrase}")`);
    }
  }

  const fallbackIndex = text.indexOf(FALLBACK_MARKER);
  const creationIndex = text.indexOf("new_wallet");
  if (creationIndex !== -1 && (fallbackIndex === -1 || creationIndex < fallbackIndex)) {
    violations.push(
      `${path}: wallet creation out of place [creation-before-fallback] — new_wallet is mentioned before the fallback marker, presenting creation as more than a fallback`,
    );
  }

  return violations;
}

function relayWalletSection(text) {
  const start = text.indexOf(B2_HEADING);
  const end = text.indexOf(NEXT_SECTION_HEADING);
  if (start === -1 || end === -1 || end <= start) {
    return null;
  }
  return text.slice(start, end);
}

function participationPrompt(text) {
  const start = text.indexOf(PROMPT_START);
  if (start === -1) {
    return null;
  }
  const end = text.indexOf("\n```", start);
  if (end === -1) {
    return null;
  }
  return text.slice(start, end);
}

function compareAcrossSurfaces(files, label, extract) {
  const violations = [];

  const extracted = files.map((f) => ({ path: f.path, part: extract(f.text) }));
  for (const { path, part } of extracted) {
    if (part === null) {
      violations.push(`${path}: ${label} not found`);
    }
  }

  const found = extracted.filter((e) => e.part !== null);
  for (let i = 1; i < found.length; i++) {
    if (found[i].part !== found[0].part) {
      violations.push(
        `${found[i].path}: ${label} differs from ${found[0].path} — the three surfaces have drifted`,
      );
    }
  }

  return violations;
}

export function checkSurfaceSync(files) {
  const violations = [];

  const agentCopies = files.filter((f) => IDENTICAL_AGENT_COPIES.includes(f.path));
  if (agentCopies.length !== 2) {
    violations.push(
      `expected both agent-facing copies (${IDENTICAL_AGENT_COPIES.join(", ")}) in the checked file set, found ${agentCopies.length}`,
    );
  } else if (agentCopies[0].text !== agentCopies[1].text) {
    violations.push(
      `${agentCopies[0].path} and ${agentCopies[1].path}: agent-facing copies are not byte-identical`,
    );
  }

  violations.push(
    ...compareAcrossSurfaces(
      files,
      `relay-wallet section (${B2_HEADING} … ${NEXT_SECTION_HEADING})`,
      relayWalletSection,
    ),
    ...compareAcrossSurfaces(files, "participation prompt", participationPrompt),
  );

  return violations;
}

export function runChecks(repoRoot) {
  const files = GUIDE_FILES.map((path) => ({
    path,
    text: readFileSync(resolve(repoRoot, path), "utf8"),
  }));

  return [
    ...files.flatMap(({ path, text }) => checkGuideText(path, text)),
    ...checkSurfaceSync(files),
  ];
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const repoRoot = resolve(fileURLToPath(import.meta.url), "../..");
  const violations = runChecks(repoRoot);
  if (violations.length > 0) {
    console.error("Relay-wallet guidance check failed:");
    for (const violation of violations) {
      console.error(`  - ${violation}`);
    }
    process.exit(1);
  }
  console.log(`Relay-wallet guidance check passed for ${GUIDE_FILES.length} files.`);
}
