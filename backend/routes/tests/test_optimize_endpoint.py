import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from routes import views
from routes.services.google_maps import (
    MAX_STOPS,
    GoogleMapsConfigurationError,
    GoogleMapsError,
    LatLng,
    OptimizedRoute,
    RouteLeg,
    RouteNotFoundError,
    RouteStop,
)

STOPS = ["1 Depot Way", "10 Elm St", "20 Oak Ave"]

ROUTE = OptimizedRoute(
    stops=[
        RouteStop(1, 0, "1 Depot Way", "1 Depot Way, Springfield, IL", LatLng(40.0, -89.6)),
        RouteStop(2, 2, "20 Oak Ave", "20 Oak Ave, Springfield, IL", LatLng(40.05, -89.55)),
        RouteStop(3, 1, "10 Elm St", "10 Elm St, Springfield, IL", LatLng(39.95, -89.65)),
    ],
    legs=[RouteLeg(1, 2, 3000, 300), RouteLeg(2, 3, 5000, 480)],
    total_distance_meters=8000,
    total_duration_seconds=780,
    polyline="abc123",
    bounds={"northeast": {"lat": 40.1, "lng": -89.5}, "southwest": {"lat": 39.9, "lng": -89.7}},
)


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def url():
    return reverse("routes:optimize")


@pytest.fixture
def optimizer(monkeypatch):
    """Replace the Google Maps service; tests can set .result or .error."""

    class Stub:
        result = ROUTE
        error = None
        calls = []

        def __call__(self, stops):
            self.calls.append(stops)
            if self.error:
                raise self.error
            return self.result

    stub = Stub()
    monkeypatch.setattr(views, "optimize_route", stub)
    return stub


def test_returns_optimized_route(client, url, optimizer):
    response = client.post(url, {"stops": STOPS}, format="json")

    assert response.status_code == 200
    assert optimizer.calls == [STOPS]
    body = response.json()
    assert [s["position"] for s in body["stops"]] == [1, 2, 3]
    assert [s["original_index"] for s in body["stops"]] == [0, 2, 1]
    assert body["stops"][1] == {
        "position": 2,
        "original_index": 2,
        "address": "20 Oak Ave",
        "formatted_address": "20 Oak Ave, Springfield, IL",
        "location": {"lat": 40.05, "lng": -89.55},
    }
    assert body["legs"][1] == {
        "from_position": 2,
        "to_position": 3,
        "distance_meters": 5000,
        "duration_seconds": 480,
    }
    assert body["total_distance_meters"] == 8000
    assert body["total_distance_km"] == 8.0
    assert body["total_distance_miles"] == 4.97
    assert body["total_duration_seconds"] == 780
    assert body["total_duration_minutes"] == 13
    assert body["polyline"] == "abc123"
    assert body["bounds"]["southwest"] == {"lat": 39.9, "lng": -89.7}


def test_strips_whitespace_from_addresses(client, url, optimizer):
    client.post(url, {"stops": ["  1 Depot Way ", "10 Elm St\n"]}, format="json")

    assert optimizer.calls == [["1 Depot Way", "10 Elm St"]]


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({}, id="missing-stops"),
        pytest.param({"stops": "1 Depot Way"}, id="stops-not-a-list"),
        pytest.param({"stops": ["only one"]}, id="too-few"),
        pytest.param({"stops": [f"stop {i}" for i in range(MAX_STOPS + 1)]}, id="too-many"),
        pytest.param({"stops": ["1 Depot Way", ""]}, id="blank-address"),
        pytest.param({"stops": ["1 Depot Way", "   "]}, id="whitespace-address"),
        pytest.param({"stops": ["1 Depot Way", None]}, id="null-address"),
        pytest.param({"stops": ["1 Depot Way", "x" * 256]}, id="address-too-long"),
    ],
)
def test_rejects_invalid_payloads_without_calling_google(client, url, optimizer, payload):
    response = client.post(url, payload, format="json")

    assert response.status_code == 400
    assert "stops" in response.json()
    assert optimizer.calls == []


def test_rejects_non_json_body(client, url, optimizer):
    response = client.post(url, "stops=a&stops=b", content_type="application/x-www-form-urlencoded")

    assert response.status_code == 415
    assert optimizer.calls == []


@pytest.mark.parametrize(
    ("error", "expected_status", "expected_body"),
    [
        pytest.param(
            RouteNotFoundError("Could not locate address: 10 Elm St", "NOT_FOUND", address="10 Elm St"),
            422,
            {"detail": "Could not locate address: 10 Elm St", "code": "route_not_found", "address": "10 Elm St"},
            id="address-not-found",
        ),
        pytest.param(
            RouteNotFoundError("No drivable route could be found between the provided stops", "ZERO_RESULTS"),
            422,
            {"detail": "No drivable route could be found between the provided stops", "code": "route_not_found"},
            id="no-route",
        ),
        pytest.param(
            GoogleMapsConfigurationError("GOOGLE_MAPS_API_KEY is not configured"),
            503,
            {"detail": "Route optimization is not configured on the server", "code": "not_configured"},
            id="not-configured",
        ),
        pytest.param(
            GoogleMapsError("The provided API key is invalid.", "REQUEST_DENIED"),
            502,
            {"detail": "The provided API key is invalid.", "code": "upstream_error"},
            id="upstream-error",
        ),
    ],
)
def test_maps_service_errors_to_http_responses(client, url, optimizer, error, expected_status, expected_body):
    optimizer.error = error

    response = client.post(url, {"stops": STOPS}, format="json")

    assert response.status_code == expected_status
    assert response.json() == expected_body


def test_get_is_not_allowed(client, url, optimizer):
    response = client.get(url)

    assert response.status_code == 405
    assert optimizer.calls == []
