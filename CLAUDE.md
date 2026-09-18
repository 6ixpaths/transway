# CLAUDE.md - Transway (Delivery & Logistics Route Optimizer)

## Project Overview
Transway is a high-performance Minimum Viable Product (MVP) delivery and logistics route optimization application. Its core mission is to accept an $X$ number of delivery stops and leverage Google Maps APIs to calculate the most time- and fuel-efficient route.

## Repository Architecture (Monorepo)
Transway is structured as a single repository containing both the frontend and backend applications to ensure unified version control, streamlined full-stack commits, and shared context:

```text
transway/
├── backend/                  # Django REST API service
│   ├── manage.py
│   ├── requirements.txt
│   └── ...
├── frontend/                 # Vue 3 application (Webpack, SASS, Bootstrap)
│   ├── package.json
│   ├── src/
│   └── ...
├── CLAUDE.md
└── README.md
```

## Tech Stack & Frameworks
- **Frontend:** Vue.js 3 (Composition API, `<script setup>`)
- **Backend:** Django (Python 3.11+, Django REST Framework)
- **UI Framework:** Bootstrap 5 (compiled via SASS/SCSS)
- **Design System:** Material Design principles applied over Bootstrap components
- **Styling Architecture:** BEM (Block Element Modifier) methodology written in SCSS

---

## Coding Standards & Architectural Guidelines

### 1. Styling & CSS (BEM + Bootstrap + SASS)
- All custom styles must reside in SASS/SCSS files located in `frontend/src/assets/scss/`.
- Strictly follow **BEM naming conventions**:
  - `block`
  - `block__element`
  - `block--modifier`
  - `block__element--modifier`
- Integrate **Material Design** principles over Bootstrap structural components:
  - Soft surface elevations (`box-shadow`), floating form controls, and rounded action buttons.
  - Standardized Material color roles (Primary, Surface, On-Surface).
  - Avoid inline CSS styles or unorganized utility classes.

### 2. Vue 3 Standards
- Use clean Composition API syntax with `<script setup>`.
- Maintain modular component boundaries:
  - `StopInputForm.vue` (Handles dynamic entry, additions, deletions, and ordering of stops)
  - `RouteSummary.vue` (Displays total distance, duration, and efficiency metrics)
  - `OptimizedMap.vue` (Handles Google Maps JS SDK initialization, polyline rendering, and numbered markers)
- Always provide active UI handling for loading states, address validation errors, and empty route states.

### 3. Django Standards
- Isolate external integrations inside dedicated service modules (e.g., `backend/routes/services/google_maps.py`).
- Store sensitive configuration keys (Google Maps API Key) strictly inside `.env` files.
- Use Django REST Framework (DRF) serializers to validate incoming request payloads before calling Google APIs.

---

## Phased Development & Git Commit Instructions

> **Execution Rule for Claude Code:**
> Execute work strictly **one phase and one step at a time**. Do NOT jump ahead or build multiple components simultaneously. 
> At the completion of each sub-component or task, verify functional correctness and **execute a clean Git commit** using conventional commit formatting before moving to the next task.

### Phase 1: Monorepo & Environment Setup
1. **Backend Initialization (`/backend`):**
   - Initialize Django project and `routes` app.
   - Configure DRF, CORS policies, `.env` loading, and basic settings.
   - *Git Commit:* `feat(backend): initialize django REST framework setup in monorepo`
2. **Frontend & SCSS Architecture (`/frontend`):**
   - Initialize Vue 3 project using Webpack and install Bootstrap 5 + SASS dependencies.
   - Establish BEM file structure (`assets/scss/components/_card.scss`, `_form.scss`, etc.) and Material overrides.
   - *Git Commit:* `feat(frontend): setup vue 3 app with bootstrap scss bem architecture`

### Phase 2: Route Optimization Endpoint
1. **Google Maps Integration Service:**
   - Create `services/google_maps.py` to interface with Google Route Optimization / Directions API (`optimizeWaypoints=true`).
   - Extract and format: ordered stop array, total distance (km/miles), duration (mins), and polyline path string.
   - *Git Commit:* `feat(backend): implement google maps route optimization service`
2. **REST API Endpoint & Serializer:**
   - Create `POST /api/v1/routes/optimize/` view and DRF request/response serializers.
   - *Git Commit:* `feat(backend): create route optimization POST endpoint`

### Phase 3: Frontend MVP Components (Step-by-Step)
1. **Stop Entry Component (`StopInputForm.vue`):**
   - Implement address input list, dynamic row addition/removal, and BEM/Material styled controls.
   - *Git Commit:* `feat(frontend): create stop input form component with bem styling`
2. **Summary Metrics Display (`RouteSummary.vue`):**
   - Create Material-style summary card for displaying total distance, time, and fuel savings estimates.
   - *Git Commit:* `feat(frontend): build route summary metrics component`
3. **Map Integration (`OptimizedMap.vue`):**
   - Integrate Google Maps JS SDK. Render route polylines and numbered markers for each ordered stop.
   - *Git Commit:* `feat(frontend): integrate google maps SDK for path rendering`

### Phase 4: Integration & Verification
1. Connect Vue state to Django backend API via `axios`/`fetch`.
2. Add global loading overlay, error notifications, and input validation bounds.
3. Perform end-to-end routing test for an $X$-stop delivery scenario.
4. *Git Commit:* `feat(app): complete end-to-end route optimization workflow for transway`

---

## Future Roadmap (Do Not Build Yet)
- Multi-driver dispatch management & Vehicle Routing Problem (VRP) constraints.
- Real-time driver GPS tracking and turn-by-turn navigation view.
- Delivery time-window constraints and vehicle capacity limits.
- Automated SMS notifications for customers upon stop arrival.