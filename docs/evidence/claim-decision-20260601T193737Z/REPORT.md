# Claim Decision: Live Verifier-Ready Round Bundle

## Target Criticism

> The most serious weakness is the credibility-undermining mismatch between the document's stated dates and its own cited evidence, combined with reliance on tooling that does not yet exist as described.

## Decision

`MATERIAL_NEW_INPUT_AVAILABLE`

The materially different input is the public testnet round 7 staged bundle exposed by the scoring service. It is not another static benchmark artifact and not another model-card citation. It is a live public round endpoint with:

- `bundle.json`
- `runtime/execution_manifest.json`
- `outputs/verification_hashes.json`
- 14 bundle-listed files retrievable over HTTPS
- all 14 canonical JSON hashes matching the bundle manifest
- all four verifier target hashes matching `outputs/verification_hashes.json`

This supports the narrow claim that live Phase 1 publication now includes verifier-ready artifact structure and hash-checkable public bundle files. It does not prove independent validator reruns, model superiority over deterministic or human baselines, cross-hardware convergence, or Phase 3 authority transfer.

## New Measurement

Command run from `/home/postfiat/repos/postfiatorg.github.io`:

```bash
python3 - <<'PY'
import hashlib, json, urllib.request
base='https://scoring-testnet.postfiat.org/api/scoring/rounds/7/'
def fetch(path):
    with urllib.request.urlopen(base+path, timeout=30) as r:
        return r.status, r.read()
def canon_hash(raw):
    data=json.loads(raw)
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':'), default=str).encode()).hexdigest()
status, raw = fetch('bundle.json')
bundle=json.loads(raw)
print('bundle_status', status)
print('bundle_version', bundle.get('bundle_version'))
print('round_kind', bundle.get('round_kind'))
print('file_count', len(bundle['file_hashes']))
print('bundle_hashes_self', 'bundle.json' in bundle['file_hashes'])
missing=[]; mismatches=[]; checked=0
for path, expected in sorted(bundle['file_hashes'].items()):
    st, b = fetch(path)
    if st != 200:
        missing.append((path, st)); continue
    got=canon_hash(b)
    checked += 1
    if got != expected:
        mismatches.append((path, expected, got))
print('checked', checked)
print('missing', missing)
print('mismatches', mismatches)
st, vh_raw=fetch('outputs/verification_hashes.json')
vh=json.loads(vh_raw)
print('verification_hashes', json.dumps(vh, sort_keys=True))
for key, path in [('model_response_hash','outputs/model_response.json'),('validator_scores_hash','outputs/validator_scores.json'),('selected_unl_hash','outputs/selected_unl.json'),('signed_validator_list_hash','outputs/signed_validator_list.json')]:
    st,b=fetch(path)
    print(key, vh.get(key)==canon_hash(b), vh.get(key))
PY
```

Output:

```text
bundle_status 200
bundle_version 2
round_kind normal
file_count 14
bundle_hashes_self False
checked 14
missing []
mismatches []
verification_hashes {"model_response_hash": "8da0de1e666a6665aa15e4897ab8b120888c21b2bf8d72a6c269f829479f2d40", "selected_unl_hash": "a0922bea53b1cd1f3f4b1cc92dce902a87bcd5a506a9fa578836c83bb8f819fc", "signed_validator_list_hash": "a0983ea17e0ee18a54e9ea78dfcb5c4334c88e36aa5db4673af5c24819ebfd44", "validator_scores_hash": "c96bf06445753b241a6ac4748830bbe542e090eb50caa30e36c7f771c561bf04"}
model_response_hash True 8da0de1e666a6665aa15e4897ab8b120888c21b2bf8d72a6c269f829479f2d40
validator_scores_hash True c96bf06445753b241a6ac4748830bbe542e090eb50caa30e36c7f771c561bf04
selected_unl_hash True a0922bea53b1cd1f3f4b1cc92dce902a87bcd5a506a9fa578836c83bb8f819fc
signed_validator_list_hash True a0983ea17e0ee18a54e9ea78dfcb5c4334c88e36aa5db4673af5c24819ebfd44
```

## Completed Evidence Not Repeated

- `docs/evidence/whitepaper-provenance-20260601T175048Z`: date/provenance packet. It already established that the May 2026 revision is not future-dated, the public validator list is live, and the scoring config is publicly reachable.
- `docs/evidence/claim-decision-20260601T190931Z`: Qwen model-card packet. It established that the active model profile is publicly resolvable on Hugging Face.
- `docs/evidence/claim-decision-20260601T192645Z`: public benchmark-artifact packet. It established that static benchmark reports are publicly retrievable and hash-checkable.
- `static/benchmarks/model-lift-baseline-20260601T154824Z` and `static/benchmarks/model-lift-adjudication-20260601T165516Z`: comparator and adjudication packets. They show repeatable disagreement against a deterministic baseline, not model superiority.

Repeating those artifacts adds no information. The new input here is that the live scoring service round itself exposes verifier-ready files and matching public hashes.

## Safe Sentence For The Document Editor

The live testnet scorer now publishes verifier-ready round bundles: round 7 exposes `bundle.json`, an execution manifest, verification hashes, and 14 hash-checkable files over HTTPS, all of which matched the canonical bundle hashes in a fresh verification run.

## Stronger Claim Not Supported

Do not claim that independent validators have already rerun the bundle, that model-assisted scoring beats deterministic or human baselines, that cross-hardware replay is solved, or that authority has transferred beyond Phase 1.

