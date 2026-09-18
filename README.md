# Transway 🚚📍

**Transway** is a high-performance Minimum Viable Product (MVP) for delivery and logistics route optimization. Optimize your delivery routes in seconds using advanced routing algorithms powered by Google Maps APIs.

## 🎯 Features

- **Smart Route Optimization** – Accept multiple delivery stops and automatically calculate the most time- and fuel-efficient route
- **Google Maps Integration** – Powered by Google Route Optimization and Directions APIs with `optimizeWaypoints=true`
- **Interactive Map Visualization** – See your optimized route with numbered markers and polylines
- **Real-time Metrics** – Display total distance, duration, and fuel savings estimates
- **Responsive Design** – Mobile-friendly interface built with Vue 3 and Bootstrap 5

## 🏗️ Repository Structure

Transway is a **monorepo** containing both frontend and backend applications:

```
transway/
├── backend/                    # Django REST API Service
│   ├── manage.py
│   ├── requirements.txt
│   ├── routes/
│   │   ├── services/          # Google Maps integration
│   │   └── ...
│   └── ...
├── frontend/                   # Vue 3 Single Page Application
│   ├── package.json
│   ├── webpack.config.js
│   ├── src/
│   │   ├── components/        # Vue components
│   │   ├── assets/scss/       # BEM-styled SCSS
│   │   └── ...
│   └── ...
├── CLAUDE.md                   # Development guidelines
└── README.md                   # This file
```

## 🛠️ Tech Stack

### Frontend
- **Vue.js 3** – Composition API with `<script setup>` syntax
- **Bootstrap 5** – Responsive UI framework
- **SASS/SCSS** – BEM methodology for styling
- **Webpack** – Module bundler
- **Material Design** – Design system principles

### Backend
- **Django** – Python 3.11+ web framework
- **Django REST Framework (DRF)** – RESTful API
- **Google Maps APIs** – Route Optimization & Directions
- **Python-dotenv** – Environment configuration management

## 🚀 Getting Started

### Prerequisites
- **Node.js** 18+ and npm/yarn (for frontend)
- **Python** 3.11+ and pip (for backend)
- **Google Maps API Key** (with Route Optimization and Directions APIs enabled)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the `backend/` directory with the variables listed below:
   ```env
   DEBUG=True
   SECRET_KEY=your-super-secret-key-change-in-production
   GOOGLE_MAPS_API_KEY=your-google-maps-api-key
   ALLOWED_HOSTS=localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
   ```

5. Run Django system checks:
   ```bash
   python manage.py check
   ```

6. Run migrations:
   ```bash
   python manage.py migrate
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

   The backend API will be available at `http://localhost:8000`

8. Run the test suite (requires `pytest` and `pytest-django`):
   ```bash
   pytest
   ```

   All tests should pass. The test suite includes:
   - Google Maps service integration tests
   - Route optimization endpoint tests
   - Request/response serializer validation tests

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file in the `frontend/` directory:
   ```env
   API_BASE_URL=http://localhost:8000
   GOOGLE_MAPS_API_KEY=your-browser-restricted-maps-js-api-key
   GOOGLE_MAPS_MAP_ID=your-optional-map-id
   ```

   **Note:** The `GOOGLE_MAPS_API_KEY` for the frontend should be a browser-restricted API key (different from the backend key) with the **Maps JavaScript API** enabled.

4. Start the development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:8080` (or the port shown in terminal)

### Environment Variables Reference

#### Backend (`backend/.env`)
| Variable | Purpose | Example |
|----------|---------|---------|
| `DEBUG` | Django debug mode (set to `False` in production) | `True` |
| `SECRET_KEY` | Django secret key for session/CSRF protection | `your-super-secret-key-change-in-production` |
| `GOOGLE_MAPS_API_KEY` | Server-side API key for Route Optimization & Directions APIs | `AIza...` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hostnames | `localhost,127.0.0.1,yourdomain.com` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated list of allowed frontend origins for CORS | `http://localhost:8080,https://yourdomain.com` |

#### Frontend (`frontend/.env`)
| Variable | Purpose | Example |
|----------|---------|---------|
| `API_BASE_URL` | Backend API server URL | `http://localhost:8000` |
| `GOOGLE_MAPS_API_KEY` | Browser-restricted API key for Maps JS SDK | `AIza...` |
| `GOOGLE_MAPS_MAP_ID` | Optional Map ID for advanced styling (can be left empty) | `map-id-123` |

### Verifying the Setup

1. **Backend Running:**
   ```bash
   curl http://localhost:8000/admin/login/
   ```
   Should return a 200 response.

2. **Frontend Running:**
   Open `http://localhost:8080` in your browser. You should see the Transway app with a Stop Input Form on the left and a Map placeholder on the right.

3. **API Connectivity:**
   - Enter 2–27 delivery addresses in the form
   - Click "Optimize Route"
   - If your `GOOGLE_MAPS_API_KEY` is configured, the optimized route will appear on the map with metrics

## 📖 Usage

1. **Enter Delivery Stops** – Use the Stop Input Form to add multiple delivery addresses
2. **Optimize Route** – Click "Optimize Route" to send stops to the backend
3. **View Results** – See the optimized route on the map with:
   - Numbered stop markers
   - Route polyline
   - Total distance and duration
   - Efficiency metrics

## 🔄 Development Phases

### Phase 1: Monorepo & Environment Setup ✓
- Initialize Django project with DRF configuration
- Set up Vue 3 with Webpack and Bootstrap 5
- Establish BEM SCSS architecture

### Phase 2: Route Optimization Endpoint ✓
- Implement Google Maps route optimization service
- Create REST API endpoint for route calculation
- Build DRF request/response serializers

### Phase 3: Frontend MVP Components ✓
- `StopInputForm.vue` – Dynamic address entry with add/remove functionality
- `RouteSummary.vue` – Metrics display card with Material Design
- `OptimizedMap.vue` – Google Maps JS SDK integration with polylines and markers

### Phase 4: Integration & Verification ✓
- Connect frontend to backend API
- Add global loading overlay and error notifications
- Perform end-to-end testing

## 🗺️ Roadmap (Future Features)

- **Multi-Driver Dispatch** – Manage multiple drivers with Vehicle Routing Problem (VRP) constraints
- **Real-time Tracking** – GPS tracking with turn-by-turn navigation
- **Delivery Constraints** – Time windows and vehicle capacity limits
- **Customer Notifications** – Automated SMS/email upon stop arrival
- **Analytics Dashboard** – Historical route performance and fuel consumption analysis

## 🤝 Contributing

This project follows conventional commit formatting:
- `feat(module): description` – New features
- `fix(module): description` – Bug fixes
- `refactor(module): description` – Code refactoring
- `docs: description` – Documentation updates

See `CLAUDE.md` for detailed coding standards and architectural guidelines.

## 📝 Coding Standards

### Styling (BEM + SCSS)
- All styles in `frontend/src/assets/scss/`
- Follow BEM naming: `block`, `block__element`, `block--modifier`
- Apply Material Design principles over Bootstrap

### Vue 3 Components
- Use Composition API with `<script setup>`
- Keep components modular and focused
- Handle loading states and error cases

### Django Backend
- Isolate external integrations (e.g., Google Maps) in service modules
- Use `.env` for sensitive configuration
- Validate payloads with DRF serializers before external API calls

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👤 Author

**Ram Raja** – transway project creator

---

**Last Updated:** September 2026

For development guidelines and standards, see [CLAUDE.md](CLAUDE.md).
