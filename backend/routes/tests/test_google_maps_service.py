import json

import pytest
import requests

from routes.services import google_maps
from routes.services.google_maps import (
    GoogleMapsConfigurationError,
    GoogleMapsError,
    RouteNotFoundError,
    optimize_route,
)

STOPS = [
    "1 Depot Way, Springfield",
    "10 Elm St, Springfield",
    "20 Oak Ave, Springfield",
    "30 Pine Rd, Springfield",
]


def _leg(start, end, start_loc, end_loc, meters, seconds):
    return {
        "start_address": start,
        "end_address": end,
        "start_location": {"lat": start_loc[0], "lng": start_loc[1]},
        "end_location": {"lat": end_loc[0], "lng": end_loc[1]},
        "distance": {"text": f"{meters / 1000} km", "value": meters},
        "duration": {"text": f"{seconds // 60} mins", "value": seconds},
    }


# Google reorders the two intermediate waypoints: visit Oak (index 1) before Elm (index 0).
DIRECTIONS_OK = {
    "status": "OK",
    "geocoded_waypoints": [{"geocoder_status": "OK"}] * 4,
    "routes": [
        {
            "waypoint_order": [1, 0],
            "overview_polyline": {"points": "abc123polyline"},
            "bounds": {
                "northeast": {"lat": 40.1, "lng": -89.5},
                "southwest": {"lat": 39.9, "lng": -89.7},
            },
            "legs": [
                _leg("1 Depot Way, Springfield, IL", "20 Oak Ave, Springfield, IL",
                     (40.0, -89.6), (40.05, -89.55), 3000, 300),
                _leg("20 Oak Ave, Springfield, IL", "10 Elm St, Springfield, IL",
                     (40.05, -89.55), (39.95, -89.65), 5000, 480),
                _leg("10 Elm St, Springfield, IL", "30 Pine Rd, Springfield, IL",
                     (39.95, -89.65), (40.1, -89.7), 2500, 240),
            ],
        }
    ],
}


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")

    def json(self):
        return self._payload


class DirectionsStub:
    """Stands in for requests.get; tests can swap the payload or force a failure."""

    def __init__(self):
        self.payload = DIRECTIONS_OK
        self.status_code = 200
        self.error = None
        self.call = None

    def respond(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def fail(self, error):
        self.error = error

    def __call__(self, url, **kwargs):
        self.call = (url, kwargs)
        if self.error:
            raise self.error
        return FakeResponse(self.payload, self.status_code)


@pytest.fixture(autouse=True)
def api_key(settings):
    settings.GOOGLE_MAPS_API_KEY = "test-key"


@pytest.fixture
def directions(monkeypatch):
    stub = DirectionsStub()
    monkeypatch.setattr(google_maps.requests, "get", stub)
    return stub


def test_sends_optimized_waypoints_request(directions):
    optimize_route(STOPS)

    url, kwargs = directions.call
    assert url == google_maps.DIRECTIONS_URL
    assert kwargs["timeout"] == google_maps.REQUEST_TIMEOUT_SECONDS
    assert kwargs["params"] == {
        "origin": STOPS[0],
        "destination": STOPS[-1],
        "waypoints": f"optimize:true|{STOPS[1]}|{STOPS[2]}",
        "units": "metric",
        "key": "test-key",
    }


def test_orders_stops_by_waypoint_order(directions):
    route = optimize_route(STOPS)

    assert [s.original_index for s in route.stops] == [0, 2, 1, 3]
    assert [s.position for s in route.stops] == [1, 2, 3, 4]
    assert [s.address for s in route.stops] == [STOPS[0], STOPS[2], STOPS[1], STOPS[3]]
    assert route.stops[1].formatted_address == "20 Oak Ave, Springfield, IL"
    assert route.stops[3].formatted_address == "30 Pine Rd, Springfield, IL"
    assert (route.stops[3].location.lat, route.stops[3].location.lng) == (40.1, -89.7)


def test_aggregates_totals_polyline_and_bounds(directions):
    route = optimize_route(STOPS)

    assert route.total_distance_meters == 10500
    assert route.total_distance_km == 10.5
    assert route.total_distance_miles == 6.52
    assert route.total_duration_seconds == 1020
    assert route.total_duration_minutes == 17
    assert route.polyline == "abc123polyline"
    assert route.bounds["northeast"] == {"lat": 40.1, "lng": -89.5}
    assert len(route.legs) == 3
    assert (route.legs[1].from_position, route.legs[1].to_position) == (2, 3)
    assert route.legs[1].distance_meters == 5000


def test_to_dict_is_json_serialisable(directions):
    data = optimize_route(STOPS).to_dict()

    json.dumps(data)
    assert data["total_distance_km"] == 10.5
    assert data["total_duration_minutes"] == 17
    assert data["stops"][1]["location"] == {"lat": 40.05, "lng": -89.55}


def test_two_stops_sends_no_waypoints(directions):
    directions.respond({
        "status": "OK",
        "routes": [{
            "overview_polyline": {"points": "xy"},
            "bounds": DIRECTIONS_OK["routes"][0]["bounds"],
            "legs": [_leg("A, IL", "B, IL", (1, 2), (3, 4), 1000, 60)],
        }],
    })

    route = optimize_route(["A", "B"])

    assert "waypoints" not in directions.call[1]["params"]
    assert [s.original_index for s in route.stops] == [0, 1]
    assert route.stops[1].formatted_address == "B, IL"


@pytest.mark.parametrize(
    "stops",
    [
        pytest.param(["only one"], id="too-few"),
        pytest.param([f"stop {i}" for i in range(google_maps.MAX_STOPS + 1)], id="too-many"),
    ],
)
def test_rejects_out_of_range_stop_count(directions, stops):
    with pytest.raises(ValueError):
        optimize_route(stops)

    assert directions.call is None


def test_missing_api_key_raises_configuration_error(directions, settings):
    settings.GOOGLE_MAPS_API_KEY = ""

    with pytest.raises(GoogleMapsConfigurationError):
        optimize_route(STOPS)

    assert directions.call is None


def test_not_found_reports_unresolved_address(directions):
    directions.respond({
        "status": "NOT_FOUND",
        "geocoded_waypoints": [
            {"geocoder_status": "OK"},
            {"geocoder_status": "OK"},
            {"geocoder_status": "ZERO_RESULTS"},
            {"geocoder_status": "OK"},
        ],
        "routes": [],
    })

    with pytest.raises(RouteNotFoundError) as excinfo:
        optimize_route(STOPS)

    assert STOPS[2] in str(excinfo.value)
    assert excinfo.value.status == "NOT_FOUND"
    assert excinfo.value.address == STOPS[2]


def test_zero_results_raises_route_not_found(directions):
    directions.respond({"status": "ZERO_RESULTS", "routes": []})

    with pytest.raises(RouteNotFoundError) as excinfo:
        optimize_route(STOPS)

    assert excinfo.value.status == "ZERO_RESULTS"


def test_request_denied_surfaces_google_error_message(directions):
    directions.respond({"status": "REQUEST_DENIED", "error_message": "The provided API key is invalid."})

    with pytest.raises(GoogleMapsError) as excinfo:
        optimize_route(STOPS)

    assert str(excinfo.value) == "The provided API key is invalid."
    assert excinfo.value.status == "REQUEST_DENIED"


@pytest.mark.parametrize(
    "break_transport",
    [
        pytest.param(lambda d: d.respond({}, status_code=503), id="http-503"),
        pytest.param(lambda d: d.fail(requests.ConnectionError("boom")), id="connection-error"),
        pytest.param(lambda d: d.fail(requests.Timeout("slow")), id="timeout"),
    ],
)
def test_transport_failures_wrap_requests_errors(directions, break_transport):
    break_transport(directions)

    with pytest.raises(GoogleMapsError):
        optimize_route(STOPS)


