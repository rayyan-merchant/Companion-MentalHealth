# Companion Project Audit

Date: June 11, 2026

## Executive Verdict

Companion has a strong demonstration concept: a visible evidence trail, a
deterministic rule layer, a usable full-stack interface, and a safety
interceptor placed before generative output. Those are genuinely differentiating
choices.

It is not yet ready for unsupervised public mental-health use. The largest gap
is not visual polish; it is evidence. There is no clinician-reviewed evaluation
set, no measured sensitivity or false-positive rate, no subgroup analysis, and
no calibrated interpretation of the displayed confidence labels.

After the hardening work in this audit, the repository is a more credible
deployable demonstration. A responsible public launch still requires the P0
items below.

## What Is Strong

- The chat experience exposes extracted evidence instead of hiding all logic.
- Crisis interception occurs before ordinary reasoning or LLM phrasing.
- The system has a deterministic template fallback and can now run offline.
- Session ownership is enforced on the main session API.
- The ontology and rule catalog provide a useful foundation for academic work.
- The frontend production build is compact enough for a single-container demo.
- The code is divided into extraction, reasoning, confidence, explanation, and
  persistence concerns.

## Material Findings

### P0: Accuracy Was Not Evaluated

Before this audit, the repository had examples embedded in `__main__` blocks
but no automated test suite and no aggregate evaluation.

This means terms such as "production-grade", "high confidence", and "safe"
were unsupported. A deterministic rule is repeatable, but repeatability is not
the same as correctness.

Required:

- Build a versioned, clinician-reviewed corpus with positive, negative,
  ambiguous, negated, historical, third-person, quoted, slang, and multilingual
  cases.
- Separate extraction, safety detection, state inference, and response-quality
  evaluation.
- Publish confusion matrices, not only accuracy.
- Measure safety-event recall and false-positive rate with predefined thresholds.
- Measure performance by language, gendered phrasing, dialect, and disability
  language where collection and review are ethical and feasible.
- Track every result against a rule-set and model version.

### P0: Negation Produced High-Confidence False Inferences

Observed before the fix:

- "I'm not depressed, just tired" became `DepressiveSpectrum`, high confidence.
- "I am not anxious anymore and I sleep well" became `AnxietyRisk`, high
  confidence.

The extractor recorded a form of negation, but the pipeline still passed every
label into reasoning. Label normalization also meant `depressed` did not match
the normalized label `depression`.

Status: fixed for nearby phrase negation, with offline regression tests.

Remaining:

- Negation scope is still heuristic.
- Contrastive sentences, double negatives, quotations, and long-distance scope
  need a larger test set.
- Historical statements such as "I used to be depressed" need explicit temporal
  semantics rather than a binary present/absent label.

### P0: Medical Red Flags Could Be Labeled as Panic

Observed before the fix:

- "My chest hurts and I can't breathe" became `PanicRisk`, high confidence.

That is unsafe because a support tool should not reassure a user away from
urgent medical assessment.

Status: a narrow chest-pain-plus-breathing red-flag interceptor was added.

Remaining:

- Red-flag coverage must be designed and reviewed by qualified clinicians.
- The app needs region-aware emergency routing.
- The system should distinguish "possible urgent medical concern" from a mental
  health state in its data model, analytics, and audit events.

### P0: Crisis Detection Had Important Coverage Gaps

Observed misses included:

- "I cannot keep myself safe tonight."
- "I have pills beside me and I'm saying goodbye."
- "Sometimes I wish I would not wake up."
- "I want to hurt my boss."

Status: representative patterns were added and tested.

Remaining:

- Regex cannot be the sole public-launch safety mechanism.
- Add a conservative second-stage safety classifier that cannot lower a
  deterministic alert, only raise one or request human review.
- Preserve a fast local baseline for provider outages.
- Add an explicit safety check state for denied, historical, or ambiguous
  suicidal language instead of treating every denial as ordinary conversation.
- Have crisis language and response copy reviewed by local professionals.

### P0: The Production Path Was Not Actually SPARQL-Driven

The active chat path calls `agents/symbolic_reasoner.py`, whose `reason` method
implements Python `if` statements. Its `_build_session_graph` and `_apply_rules`
methods are not called. The more complete modules under `reasoning/` are also
not connected to the chat API.

The previous documentation claimed that the production path constructed RDF
graphs and executed SPARQL rules. That was inaccurate.

Recommendation:

Choose one canonical rule source.

Option A, best for shipping:

- Store rules in a reviewed YAML/JSON schema.
- Compile or interpret that schema in Python.
- Emit RDF-compatible provenance as an output artifact.
- Remove claims that SPARQL executes at runtime.

Option B, best for an ontology-focused research project:

- Route production inference through `reasoning/orchestrator.py`.
- Execute and test the SPARQL rules.
- Remove the duplicate Python rule implementation.
- Add parity tests proving expected RDF triples and selected primary states.

Do not maintain two manually synchronized rule engines.

### P0: Persistence Is Demonstration-Only

Users and sessions are stored in JSON files. Writes are not atomic, there is no
locking, and broad exception handlers silently treat corrupt data as missing.
Concurrent signups or messages can overwrite each other. Multiple application
instances cannot safely share this store.

Required before public deployment:

- PostgreSQL with migrations.
- Transactional message creation and assessment persistence.
- Unique normalized-email constraints.
- Foreign keys and session ownership constraints.
- Encrypted backups and a tested restore procedure.
- Defined retention, deletion, and account-export behavior.
- Separate immutable safety/audit events from mutable user-facing session data.

Suggested core tables:

- `users`
- `sessions`
- `messages`
- `assessments`
- `evidence_items`
- `rule_firings`
- `safety_events`
- `model_runs`
- `consent_records`

### P0: Privacy Claims Exceeded the Implementation

The signup page said data was private, secure, and never shared. When LLM
features are enabled, user input or conversation history can be sent to external
providers. Local JSON files are not encrypted, and there is no privacy policy,
consent record, retention control, or deletion workflow.

Status:

- The absolute privacy claim was removed.
- LLM, embeddings, and vector memory are now explicit opt-ins.

Required:

- A plain-language privacy notice before account creation.
- Separate consent for external model processing.
- Provider-specific data-flow documentation.
- Data minimization and redaction before external calls.
- Account deletion and data export.
- A decision on age eligibility and parental consent.
- Legal review for every intended deployment jurisdiction.

### P1: Confidence Is a Rule Heuristic, Not a Probability

`high`, `medium`, and `low` currently reflect evidence-category counts and
whether a rule fired. They are not calibrated probabilities and do not express
clinical certainty.

Required:

- Rename to labels such as `evidence_strength` unless calibrated.
- Store the factors used to compute the label.
- Test monotonicity and counterexamples.
- Do not map labels to arbitrary frontend numbers such as 0.9, 0.6, and 0.3.
- Avoid showing "high confidence" beside sensitive state names without a clear
  explanation of what confidence means.

### P1: Longitudinal Context Can Accumulate Stale Evidence

The fallback fuses unique signals from the whole session without decay,
resolution, contradiction handling, or temporal scope. A past symptom can
combine with a current message to create a stronger state even after the user
says it has resolved.

Required:

- Represent each signal with source message, timestamp, negation, temporality,
  and status.
- Apply recency weighting or explicit validity windows.
- Handle corrections and contradictions.
- Show users when history, rather than the current message, caused an inference.
- Add a "forget this" control.

### P1: Safety Analytics Are Semantically Weak

Session risk is derived by substring matching the selected state. Once elevated,
it does not reliably de-escalate. Dashboard sentiment is a fixed heuristic based
on whether any session is high or medium. These values can be misleading.

Required:

- Model safety events directly instead of inferring them from display strings.
- Separate current status from historical maximum.
- Remove the unused pseudo-sentiment score or replace it with a defined measure.
- Never label a session "safe"; use "no elevated flag detected".
- Add visible uncertainty and data-window labels to dashboard analytics.

### P1: Authentication and Abuse Controls Need Production Work

Improvements made:

- Production now refuses the default JWT secret.
- CORS is no longer wildcard by default.
- The legacy KRR endpoint now requires authentication and session ownership.
- Request text is bounded.
- The Docker image runs as a non-root user.

Remaining:

- Add rate limits for login, signup, messaging, and insight generation.
- Add account lockout or progressive delay.
- Move browser authentication to secure, HttpOnly, SameSite cookies or document
  the localStorage threat model and deploy a strict CSP.
- Add token rotation/revocation and shorter access-token lifetime.
- Add password reset, email verification, account deletion, and session logout.
- Add CSRF protection if cookie authentication is adopted.
- Scan dependencies and container images in CI.
- Rotate all existing provider credentials because earlier exception logging
  could include credential-bearing request URLs.

### P1: External Provider Reliability Was Coupled to Startup

The extractor previously attempted to embed the whole concept vocabulary during
normal initialization. On a blocked network it made repeated provider calls,
logged large failure streams, and prevented quick startup.

Status:

- Embeddings are opt-in.
- Concept prewarming is an explicit setup action.
- Vector session memory is opt-in.
- Provider logs no longer print raw exception URLs.
- Deterministic template responses are the default.

Remaining:

- Add per-provider timeout, retry budget, and latency metrics.
- Use a background job for prewarming.
- Validate vector dimensions by model instead of truncating or zero-padding
  incompatible embeddings.
- Do not mix embeddings from different models in one collection.
- Add health/readiness checks for optional providers without making the core
  service unhealthy.

### P1: Observability Is Insufficient

The app logs strings and stack traces but has no request IDs, structured events,
latency histograms, safety-event counters, provider metrics, or alerting.

Required:

- Structured JSON logs with redaction.
- Request and session correlation IDs.
- Metrics for p50/p95 latency, error rates, provider fallbacks, rule firing, and
  safety alerts.
- Tracing around extraction, reasoning, storage, and provider calls.
- A readiness endpoint distinct from liveness.
- Alerts for elevated 5xx rate, storage failure, and safety-path failure.
- Audit logs that contain references and hashes, not unnecessary raw message
  content.

### P1: CI and Automated Coverage Are Incomplete

The frontend lint script was initially nonfunctional because ESLint and its
configuration were absent.

Status:

- ESLint is now installed and configured.
- TypeScript, lint, and production build checks pass.
- The npm audit reports zero known vulnerabilities after dependency upgrades.

Remaining:

- There are no backend lint/type-check settings, frontend component tests,
  browser end-to-end tests in CI, or CI workflow.

Required CI gates:

- Python compile check.
- `pytest` or `unittest` safety tests.
- Ruff formatting and linting.
- Mypy or Pyright on critical typed modules.
- Frontend TypeScript check.
- ESLint.
- Vitest component tests.
- Playwright smoke test for signup, chat, crisis alert, and session reload.
- Production frontend build.
- Docker build and non-root startup test.
- Dependency and secret scanning.

### P2: UX and Accessibility

- The explanation panel is hidden on smaller screens with no equivalent mobile
  drawer.
- Internal identifiers such as `DepressiveSpectrum` are shown directly.
- Crisis alerts should remain visible after session reload; metadata persistence
  was added, but this needs an end-to-end test.
- Quick prompts should disappear after the user starts a conversation.
- Errors should offer retry and preserve message state.
- The app needs a clear emergency disclaimer before the first message.
- Add focus management, keyboard testing, reduced-motion support, color-contrast
  checks, and screen-reader labels.
- Add locale selection and region-specific resources instead of hardcoding one
  country for every user.

## Changes Made During This Audit

- Added offline safety and startup regression tests.
- Added phrase-scoped negation and filtered negated evidence from reasoning.
- Added representative crisis coverage for inability to stay safe, method plus
  farewell language, passive death wishes, and named-target threats.
- Added an urgent medical red-flag path for chest pain plus breathing difficulty.
- Changed Pakistan emergency UI from police `15` to official Rescue `1122`.
- Persisted crisis type so alerts can survive session reload.
- Made LLM, embeddings, prewarming, and vector memory explicit opt-ins.
- Prevented credential-bearing provider URLs from being printed in common logs.
- Protected the legacy KRR endpoint with authentication and ownership checks.
- Bounded message length and removed mutable model defaults.
- Restricted default CORS origins.
- Added production JWT-secret enforcement.
- Made backend import/startup work before the frontend is built.
- Changed the Docker build to `npm ci`, removed duplicate Python installation,
  and switched to a non-root runtime user.
- Added a working ESLint gate.
- Upgraded affected frontend dependencies and cleared the npm vulnerability
  audit.
- Added `.env.example`.
- Rewrote the README to match the actual production path.
- Replaced misleading UI labels such as "ML" and "Safe Sessions".

## Verification Performed

- Python compilation: passed.
- Offline unit tests: 11 passed.
- TypeScript check: passed.
- Frontend lint: passed with zero warnings.
- Vite production build: passed.
- NPM dependency audit: zero known vulnerabilities.
- FastAPI health endpoint: HTTP 200.
- Anonymous access to the legacy KRR endpoint: rejected.
- OWL and Turtle parsing: passed for all three ontology/base files checked.
- Git whitespace validation: passed.
- Browser smoke test: login and signup rendered from the FastAPI-served build,
  updated disclosures were visible, and no console errors were recorded.

Not yet verified:

- Docker image build and container smoke test.
- Live Groq, Gemini, Hugging Face, Jina, or Qdrant integrations.
- Browser end-to-end behavior.
- Concurrent database behavior, because the repository still uses JSON files.
- Clinical or real-world accuracy.

## Recommended Delivery Plan

### Phase 1: Credible Demonstration

Target: a stable portfolio and academic demo.

- Keep deterministic offline mode as the default.
- Add CI around the now-working local verification commands.
- Add 100+ synthetic, reviewed regression cases.
- Add Playwright smoke tests.
- Add rule provenance to each response.
- Add a mobile explanation drawer.
- Add demo seed data and screenshots.
- Build and smoke-test the Docker image.

Exit criteria:

- All CI gates pass.
- No external credential is required for the demo.
- Every displayed state includes evidence and rule provenance.
- Crisis alerts work before and after reload.

### Phase 2: Deployable Beta

Target: limited, consented testers.

- Migrate to PostgreSQL.
- Add migrations, backups, deletion, and export.
- Add rate limiting and structured observability.
- Implement secure production authentication.
- Add provider consent and redaction.
- Localize safety resources.
- Run clinician review of rules, content, and synthetic test cases.

Exit criteria:

- Restore test succeeds.
- Load and concurrency tests pass.
- Security review has no unresolved critical findings.
- Privacy and consent flows are complete.
- Safety evaluation report is versioned and published internally.

### Phase 3: Responsible Public Pilot

Target: narrowly scoped institutional pilot, not general clinical care.

- Pre-register intended use, excluded use, and evaluation thresholds.
- Complete prospective human-factors testing.
- Establish incident response and safety escalation ownership.
- Monitor drift and subgroup performance.
- Add rollback and kill-switch procedures.
- Obtain legal, privacy, and clinical governance approval.

Exit criteria:

- Named human owners can respond to safety incidents.
- The release has a model/rule card and data-flow diagram.
- Safety metrics meet predefined thresholds.
- Users can understand limitations, consent, export, and delete data.

## Best Positioning

The strongest honest positioning is:

"An explainable, ontology-informed student wellbeing reflection prototype with
deterministic safety rules and optional generative phrasing."

Avoid:

- "clinical assistant"
- "diagnostic"
- "production-grade mental-health AI"
- "SPARQL-powered inference" until the runtime actually executes SPARQL
- quantified accuracy claims without a reviewed evaluation report

That narrower framing is not less impressive. It makes the project technically
credible, demonstrates judgment, and gives the ontology work a clear path to
becoming the canonical reasoning engine rather than decorative architecture.
