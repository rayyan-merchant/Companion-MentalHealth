# Frontend Plan — Mental Health KG Chatbot (Complete & Actionable)

Below is a full, production-ready frontend plan you can hand to an AI builder (or a frontend dev) to generate the entire UI. It describes the visual design, component specs, user flows, data contracts, animations, accessibility, folder structure, and acceptance criteria. The style is calm, modern, and readable — suitable for mental-health tooling.

---

# 1 — Overview & goals

**Primary goal:** a local, single-page app (React + TypeScript + Tailwind) that provides a calming, explainable conversational experience backed by your ontology KG.
**Secondary goals:** analytics/dashboard for instructors, session history, and explanation traces for each inference.

**Tone / visual personality:** warm, gentle, low-contrast, generous spacing, rounded shapes, soft shadows, accessible typography. The interface should feel like a helpful companion — non-clinical, empathetic, and private.

**Tech stack (frontend-only):**

* React + TypeScript
* Tailwind CSS (for rapid, consistent styling)
* headlessui / Radix UI (optional for accessible components)
* react-query (or simple fetch + context) for API data fetching
* react-router (if multi-page) or single-page with tabs
* recharts or chart.js for lightweight charts in dashboard
* framer-motion for subtle micro-interactions
* icons: lucide-react or Heroicons
* localStorage for session persistence (optional)

---

# 2 — Page architecture & routes

This app is a single-page app with the following main screens (routes):

* `/` — Home / Welcome / Quick start
* `/chat` — Continuous Chat (main experience)
* `/session/:id` — Session detail + explanation trace (deep-dive)
* `/dashboard` — Aggregated Trends & Visualizations (team / demo view)
* `/settings` — Preferences (theme, anonymize data toggle, local export)
* `/about` — Project & citations / safety info / contact

You can keep everything in one page with modals, but routes make sharing links and bookmarking easier.

---

# 3 — Layout & responsive grid

Global layout uses a centered max-width container with three possible widths:

* Mobile: full-width single-column
* Tablet: 2-column layout (chat + compact right panel)
* Desktop: 3-column layout (left nav / center chat / right insights)

### Desktop layout (primary)

* **Left column (220–280px)** — vertical nav + quick stats (session count, flagged items)
* **Center column (content, 640–880px)** — Chat pane (conversation) — main focus
* **Right column (300–360px)** — Explanation panel + quick interventions + recent triggers timeline

### Tablet

* Left nav collapses to top/bottom drawer
* Chat remains central
* Right insights collapsible (toggle button)

### Mobile

* Single column: chat occupies full viewport; explanation & interventions accessible by a bottom sheet or sliding drawer.

Spacing: use `px-6` / `md:px-10` / `py-8` paddings. Large comfortable line heights (leading-7/8).

---

# 4 — Visual design system

### Color palette (calming)

* Primary soft blue: `#6AAFE6` (use for CTA accents)
* Secondary teal: `#66C2B6` (for positive actions)
* Muted slate (text): `#334155` (primary text)
* Soft charcoal: `#0F172A` (headers)
* Background off-white: `#F8FAFC`
* Card background: `#FFFFFF`
* Mild warning: `#FBCFOA` (very subtle; prefer amber `#F5D0A9`)
* Error / escalation: `#EF4444` (sparingly)

Use low contrast: avoid pure black; prefer the muted slate.

### Typography

* Headline: Inter / Poppins (600) — `font-sans`
* Body: Roboto / Inter (400) — `text-base`, `leading-7`
* Size scale: h1 28–32px, h2 20–24px, body 16px, captions 13px

### UI tokens (Tailwind-like)

* Border radius: `rounded-2xl` for cards, `rounded-md` for buttons
* Box shadows: soft (`shadow-sm`) for cards, `shadow-lg` for modal
* Elevation: prefer subtle, not deep
* Animation durations: `200ms`–`300ms` for micro-interactions

### Iconography

* Use soft-stroke icons (lucide / heroicons)
* Use unique icon for each intervention (breathing, journaling, counseling)

---

# 5 — Component inventory & specs

Below are components, props, behavior, and accessibility notes. Each component should be modular and testable.

---

## 5.1 Global components

### 1. `TopNav`

* Shows logo, app name, quick help, user initials (local), theme toggle.
* Mobile: hamburger to open nav drawer.
* Props: `title?: string`

### 2. `LeftNav`

* Vertical nav with icons & labels: Home, Chat, Dashboard, Sessions, Settings, About.
* Compact state (icons only).
* Show session status (number of open sessions).

### 3. `FooterBar` (mobile)

* Quick actions: New session, Save, Export.

---

## 5.2 Chat components

### 4. `ChatShell`

Main wrapper for the conversation.

* Props: `sessionId`, `onSendMessage`, `messages`, `onSelectMessage`.
* Behavior: scroll locking to bottom when new messages arrive unless user scrolled up (show 'new messages' indicator).

### 5. `MessageItem`

* Types: `user`, `bot`, `system` (info/warning).
* Fields: `id`, `sender`, `text`, `timestamp`, `metadata` (confidence, extracted concepts).
* UI: user messages on right (rounded bubble), bot messages on left with subtle card. Include small tag for `confidence` when relevant (e.g., "anxiety 0.92").

Accessibility: each message is a `<article>` with `aria-live="polite"` for bot messages.

### 6. `Composer`

* Text input with multi-line support, attachments (optional), quick-buttons (share GAD7 score, add assessment).
* Buttons: Send (primary), QuickStressCheck (secondary).
* Shortcut keys: Enter = new line, Shift+Enter = send OR customizable — choose one and display hint.

### 7. `QuickPrompts`

* Row of chips below composer: "I can't sleep", "Exams", "Feeling hopeless", "Panic". Clicking inserts text to composer.

---

## 5.3 Explanation & Evidence components

### 8. `ExplanationPanel` (right column)

* Shows the latest inference(s) with step-by-step explanation cards.
* Each explanation card:

  * Header: inferred state (e.g., "AnxietyRisk — Moderate (0.72)")
  * Steps: list of steps with icon, source (message id/date), confidence.
  * Causal path visualization: small node-link SVG (simple path: Trigger → Symptom → Condition → Intervention).
  * Buttons: "More evidence", "Save explanation", "Copy text".
* Collapsible timeline: show events that contributed to inference.

### 9. `EvidenceList`

* Expandable list of message snippets that contributed to the reasoning. Clicking a snippet scrolls the chat to that message and highlights it.

---

## 5.4 Interventions + Resources

### 10. `InterventionCard`

* Title, one-line why it's recommended (link to ontology rule), steps (3 bullets), estimated effort (5 min / 15 min), urgency tag (low/medium/high).
* Actions: "Start now" (opens modal with step-by-step), "Add to plan", "Mark as tried".

### 11. `ExerciseModal`

* Guided breathing/journaling UI with timers, animations (framer-motion), and progress.

---

## 5.5 Session management & search

### 12. `SessionList`

* Lists recent sessions (date, summary: top inference, risk level).
* Actions: open session detail, export session TTL, delete (local).

### 13. `SessionDetail`

* Full chat + explanation saved. Option to export as TTL or JSON (anonymize toggle).

---

## 5.6 Dashboard & Insights

### 14. `DashboardGrid`

* Cards: Top Symptoms (bar chart), Risk by Trigger (pie), Weekly Trend (line chart), Recent High-Risk Sessions.
* Filters: date range, department/role tag (if synthetic), anonymize toggle.

### 15. `TrendChart`

* Line chart of aggregate riskScore over time (weekly). Hover shows provenance counts.

---

# 6 — UI flows & user stories

Design every main flow with step-by-step interactions so an AI can implement.

---

## Flow A — Start a continuous session (primary)

1. User clicks **Chat** in left nav or landing page button **Start Conversation**.
2. If no existing session, prompt: `New Session` modal — ask for alias (optional), consent note.
3. ChatShell opens with `Welcome` bot message:

   * "Hi, I'm here to listen..."
   * Offers QuickPrompts below composer.
4. User types message → `Composer.onSend`:

   * POST `/api/message` with payload (see API spec section).
   * Append user message to messages state immediately (optimistic).
5. API returns bot `reply` + `explanation` + `inferredStates`.
6. Append bot message to messages and update ExplanationPanel (render steps).
7. If inference is `HighRisk`/`Escalation` → show explicit escalation modal with counselor contact & emergency instructions per safety policy (always local).

---

## Flow B — Explore Explanation

1. Clicking an explanation card opens `SessionDetail` or expands explanation.
2. Show causal path visualization and clickable evidence steps.
3. Clicking evidence scrolls to that message and briefly highlights it.

---

## Flow C — Try an Intervention

1. In ExplanationPanel, click `Recommended Intervention` card.
2. Modal opens with explanation + actionable steps (e.g., 4-step breathing exercise).
3. User can "Start" – run guided steps with simple animations and timers.
4. After completion, user can mark as helpful; this adds a local note to session data (could be used for similarity later).

---

## Flow D — Export & Save Session

1. Click `Save / Export` on header.
2. Options: Export JSON (raw), Export TTL (RDF), or Print summary (PDF).
3. If TTL, include only anonymized URIs (toggle available).

---

# 7 — API & Data contracts (backend interaction)

Design endpoints and sample payloads to feed to the AI builder.

### POST `/api/message`

Request:

```json
{
  "sessionId":"sess-123",
  "messageId":"m-20251205-01",
  "text":"I haven't slept for 5 nights and exams are stressing me",
  "timestamp":"2025-12-05T14:20:30+05:00"
}
```

Response:

```json
{
  "reply": "I hear that exams are causing sleep trouble...",
  "botMessageId":"b-20251205-02",
  "inferredStates":[
    {
      "id":"inf-001",
      "state":"AnxietyRisk",
      "confidence":0.72,
      "evidence":["m-20251205-01","m-20251130-09"],
      "rule":"R3: Stress+Insomnia+ExamPressure->AnxietyRisk"
    }
  ],
  "explanation": {
    "id":"ex-001",
    "steps":[
      {"text":"Detected Insomnia (confidence 0.9) in message m-20251205-01", "source":"m-20251205-01"},
      {"text":"Detected ExamPressure (confidence 0.85)", "source":"m-20251205-01"},
      {"text":"Rule R3 matched: Insomnia + ExamPressure => AnxietyRisk"}
    ],
    "confidence":0.72
  },
  "suggestedInterventions":[
    {"id":"int-01","title":"3-min breathing","duration":"5 min","urgency":"low"}
  ]
}
```

### GET `/api/session/:id`

Returns session metadata, messages, inferences, and explanation nodes (as JSON). Provide TTL export `/api/session/:id/export.ttl`.

### POST `/api/feedback`

Accepts user feedback about interventions or correctness.

---

# 8 — Data/state management & persistence

* **State slices:**

  * `session` (id, alias, createdAt)
  * `messages` (ordered array)
  * `inferences` (array)
  * `explanations` (map)
  * `ui` (selectedMessageId, panelOpen)
* Use React Context to provide session across components or react-query to fetch session data.
* Persist `messages` and `explanations` to `localStorage` for session resume. Include an optional TTL export button to store on disk.

---

# 9 — Animations & micro-interactions

* Use `framer-motion` for smooth fades and slide-ups.
* Bot typing indicator: 3-dot animated bubble.
* New message arrival: subtle pop + `transform: translateY(6px)` then settle.
* Explanation steps expand/collapse with `height` animation.
* Intervention start: calm breathing animation (circle expansion/contract) synced to a 4-4-4 breathing pattern.

---

# 10 — Accessibility & inclusivity

* All interactive elements `tabindex`-managed and keyboard operable.
* Provide `aria-live="polite"` for bot messages to announce new bot text to screen readers.
* High-contrast alternative theme toggle.
* Font sizes adjustable (accessibility settings).
* Avoid flashing animations; limit animations to opacity and transform.
* Provide text-only fallback for guided exercises (no audio required).

---

# 11 — Assets & icons

* Logo: minimal leaf or soft cloud + “Calm KG” (vector SVG)
* Hero illustration for landing: abstract calm campus or sunrise
* Icons: breathing, journal, counseling, exercise, sleep — use lucide icons
* Animations: Lottie files for breathing circle (optional)

Provide these assets in `/public/assets/`.

---

# 12 — Testing & QA

* Unit tests for key components (Composer, ChatShell, ExplanationPanel) using Jest + React Testing Library.
* E2E tests using Playwright or Cypress for main flows:

  * Start session → send messages → check explanation appears.
  * Open intervention → start exercise → mark as completed.
* Accessibility audit via axe-core / Lighthouse.

---

# 13 — Project folder structure (recommended)

```
frontend/
├─ public/
│  ├─ assets/
│  └─ index.html
├─ src/
│  ├─ api/
│  │  └─ client.ts
│  ├─ components/
│  │  ├─ ChatShell/
│  │  │  ├─ MessageItem.tsx
│  │  │  └─ Composer.tsx
│  │  ├─ ExplanationPanel/
│  │  ├─ InterventionCard/
│  │  └─ Dashboard/
│  ├─ pages/
│  │  ├─ Home.tsx
│  │  ├─ Chat.tsx
│  │  ├─ Session.tsx
│  │  └─ Dashboard.tsx
│  ├─ hooks/
│  │  └─ useSession.ts
│  ├─ styles/
│  │  └─ tailwind.css
│  ├─ utils/
│  └─ App.tsx
├─ package.json
└─ tailwind.config.js
```

---

# 14 — Dev setup & commands (local)

* `npm install`
* `npm run dev` — start React dev server
* `npm run build` — production build (if needed)
* `npm test` — run tests
* `npm run lint` — optional

Provide sample `package.json` dependencies: `react`, `react-dom`, `typescript`, `tailwindcss`, `framer-motion`, `react-query`, `recharts`, `lucide-react`, `jest`, `react-testing-library`.

---

# 15 — Example UI snapshots (descriptive wireframes)

1. **Landing / Welcome**

   * Top: logo + nav
   * Center card: "Hi, I’m your Wellness Assistant" + CTA "Start Chat"
   * Soft illustration

2. **Chat screen (desktop)**

   * Left: Vertical menu (compact)
   * Center: Chat window (scrollable), composer at bottom with quick prompts strip
   * Right: Explanation panel, top shows current inferred state, below list of steps, below suggested interventions

3. **Session detail**

   * Full conversation timeline (left) and a full graph of causal path (center) and interventions (right)

4. **Dashboard**

   * Grid of cards, muted color palette, small charts, filters bar

---

# 16 — Acceptance criteria (what “done” looks like)

* [ ] Chat page accepts user input and displays user and bot messages.
* [ ] Every bot response includes at least one `explanation` object (with steps).
* [ ] ExplanationPanel shows the causal chain with clickable evidence linking to messages.
* [ ] Suggested interventions show reasonable titles and steps.
* [ ] Sessions persist locally and can be exported as TTL/JSON.
* [ ] Mobile layout works and composer is usable.
* [ ] Accessibility basics implemented (aria-live, focus management).
* [ ] Tests exist for the main user flows.

---

# 17 — Deliverable to hand to an AI builder

Provide the AI with:

1. This plan (entire file).
2. Folder structure.
3. Tailwind token file (colors, spacing).
4. Example API stubs (the `/api/message` contract).
5. A set of 10 sample dialogues (we generated those earlier) plus their expected responses & explanation JSON. Use them as seed data in `src/data/sample-sessions.json`.
6. Logos / icons / illustrations or instructions to fetch calm-themed assets.

Prompt suggestion for the AI:

> "Create a React + TypeScript single-page app using Tailwind CSS implementing the Mental Health KG Chatbot UI described in `context.md`. Implement components, styles, routing, mock API using sample data, and basic animations. The chat should be continuous and explanation-driven. Save to a GitHub repo with tests and a README."

---




---

# ❌ **WHAT NOT TO DO (For the AI Generating the Frontend + API Boilerplate)**

When generating the frontend and backend API scaffolding, you must strictly **avoid** doing any of the following:

---

## ❌ 1. **Do NOT build any ontology logic**

* Do **NOT** write OWL files
* Do **NOT** generate RDF triples
* Do **NOT** embed SPARQL queries
* Do **NOT** implement reasoning rules
* Do **NOT** load or parse ontologies

> These parts will be done **manually by our team**, not by the AI.

---

## ❌ 2. **Do NOT generate any NLP or ML logic**

* No symptom extraction
* No emotion detection
* No semantic similarity
* No transformers
* No classifiers
* No keyword matching pipeline

> The AI should only create the frontend UI and the backend endpoints, not the internal intelligence.

---

## ❌ 3. **Do NOT implement chatbot reasoning logic**

* Do not attempt to infer mental states
* Do not hardcode stress → anxiety rules
* Do not create heuristics or logic trees
* Do not write causal reasoners or explanations

> Only create placeholder handlers like:

```js
POST /api/message
→ receives { text: "...user message..." }
→ returns a dummy JSON response
```

We will replace dummy responses with real reasoning later.

---

## ❌ 4. Do NOT build database code

* No MongoDB
* No SQL
* No local storage logic
* No session persistence

> Use only **in-memory mocks** if needed.
> All actual logic will be added later by us.

---

## ❌ 5. Do NOT set up deployment, Docker, CI/CD, or authentication

We are **NOT** deploying the system, so:

* No Dockerfile
* No Kubernetes
* No Firebase/Auth0
* No JWT tokens

Keep the backend simple, local, and minimal.

---

## ❌ 6. Do NOT alter the UI theme or structure we provided

* Do not ignore our color palette
* Do not redesign screens
* Do not change the layout structure
* Do not add new pages

> Only build exactly what is listed in the frontend plan.

---

## ❌ 7. Do NOT create advanced UI functionality

Avoid:

* Recommender systems
* Graph visualizations of KG
* Ontology editors
* Admin dashboards
* Real-time analytics

> These features are out of scope for now.

---

## ❌ 8. Do NOT mix frontend and backend frameworks

The AI must follow:

### ✔ **Frontend:** React + TailwindCSS + Framer Motion

### ✔ **Backend:** Node.js + Express (simple REST API)

Anything else (Angular, Vue, Flask, Next.js, Django, etc.) is not allowed unless we explicitly ask.

---

## ❌ 9. Do NOT generate unnecessary comments, explanations, or tutorials

When generating actual code later:

* Keep code clean
* No long explanations
* No teaching
* No redundant documentation

We only want clean, production-quality code.

---

## ❌ 10. Do NOT assume or hallucinate system logic

If the backend response requires something like:

```
{
  "emotion": ...,
  "symptoms": ...,
  "inferred_state": ...,
  "explanation": ...
}
```

The AI must NOT automatically generate the logic behind it.

Just create placeholders like:

```
{
  "emotion": "placeholder_emotion",
  "symptoms": ["placeholder"],
  "inferred_state": "placeholder_state",
  "explanation": "placeholder_reason"
}
```

We will replace these placeholders with actual ontology/NLP logic later.

---

# ✔ What The AI **IS ALLOWED** To Do

For clarity, the AI **MAY** generate:

### ✔ Full frontend UI (React + Tailwind + Framer Motion)

### ✔ Components, layouts, themes, animations

### ✔ API call functions (fetch/axios)

### ✔ Backend boilerplate (Express.js)

### ✔ API endpoint structure

### ✔ Dummy placeholder responses

### ✔ Instructions for running the frontend/backend locally

Everything else is off-limits.

---

# ⭐ Final Summary 

**When generating code, focus ONLY on:**

* UI
* UX
* Layout
* Components
* Theming
* Animations
* Basic Express.js endpoints with mock JSON

**Do NOT build reasoning, NLP, ontology, ML, or backend logic.**

---


