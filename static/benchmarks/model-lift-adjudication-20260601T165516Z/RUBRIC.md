# Adjudication Rubric

This packet adjudicates only what is visible in the prior model-lift benchmark
packet. It does not invent ground-truth labels, committee labels, operator
identities, or off-snapshot facts.

Categories:

- `model-only`: selected by the model top-20 set and not by the deterministic
  baseline top-20 set.
- `baseline-only`: selected by the deterministic baseline top-20 set and not by
  the model top-20 set.
- `policy_tradeoff_from_existing_fields`: the disagreement is explainable by
  different weighting of fields already present in the snapshot.
- `not_proven_without_external_label_or_policy_choice`: existing evidence shows
  divergence but does not establish which side is correct.

Allowed evidence:

- 1h, 24h, and 30d agreement scores.
- domain presence and domain verification.
- UNL status.
- server version and base fee.
- country/asn/geolocation when present.
- identity status when present.
- model reasoning text from the saved scoring output.

Forbidden evidence:

- inferred operator identity,
- inferred entity continuity,
- inferred legal or reputational facts,
- human committee preference,
- later manual labels.
