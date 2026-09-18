"""Google Maps Directions API integration for delivery route optimization."""

from dataclasses import asdict, dataclass

import requests
from django.conf import settings

DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"
REQUEST_TIMEOUT_SECONDS = 10

# Directions API accepts at most 25 intermediate waypoints per request.
MAX_WAYPOINTS = 25
MIN_STOPS = 2
MAX_STOPS = MAX_WAYPOINTS + 2

METERS_PER_KM = 1000
METERS_PER_MILE = 1609.344


class GoogleMapsError(Exception):
    """Base error for failures talking to Google Maps."""

    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


class GoogleMapsConfigurationError(GoogleMapsError):
    """Raised when the integration is not configured (e.g. missing API key)."""


class RouteNotFoundError(GoogleMapsError):
    """Raised when Google cannot geocode a stop or find a route between stops."""


@dataclass(frozen=True)
class LatLng:
    lat: float
    lng: float


@dataclass(frozen=True)
class RouteStop:
    position: int
    original_index: int
    address: str
    formatted_address: str
    location: LatLng


@dataclass(frozen=True)
class RouteLeg:
    from_position: int
    to_position: int
    distance_meters: int
    duration_seconds: int


@dataclass(frozen=True)
class OptimizedRoute:
    stops: list[RouteStop]
    legs: list[RouteLeg]
    total_distance_meters: int
    total_duration_seconds: int
    polyline: str
    bounds: dict

    @property
    def total_distance_km(self) -> float:
        return round(self.total_distance_meters / METERS_PER_KM, 2)

    @property
    def total_distance_miles(self) -> float:
        return round(self.total_distance_meters / METERS_PER_MILE, 2)

    @property
    def total_duration_minutes(self) -> int:
        return round(self.total_duration_seconds / 60)

    def to_dict(self) -> dict:
        data = asdict(self)
        data.update(
            total_distance_km=self.total_distance_km,
            total_distance_miles=self.total_distance_miles,
            total_duration_minutes=self.total_duration_minutes,
        )
        return data


def optimize_route(stops: list[str]) -> OptimizedRoute:
    """Return the most efficient visiting order for the given stops.

    The first stop is treated as the origin and the last as the destination;
    every stop in between is reordered by Google to minimise travel time.
    """
    if not MIN_STOPS <= len(stops) <= MAX_STOPS:
        raise ValueError(f"Expected between {MIN_STOPS} and {MAX_STOPS} stops, got {len(stops)}")

    api_key = settings.GOOGLE_MAPS_API_KEY
    if not api_key:
        raise GoogleMapsConfigurationError("GOOGLE_MAPS_API_KEY is not configured")

    origin, destination, waypoints = stops[0], stops[-1], stops[1:-1]
    params = {
        "origin": origin,
        "destination": destination,
        "units": "metric",
        "key": api_key,
    }
    if waypoints:
        params["waypoints"] = "optimize:true|" + "|".join(waypoints)

    try:
        response = requests.get(DIRECTIONS_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise GoogleMapsError(f"Directions request failed: {exc}") from exc

    status = payload.get("status")
    if status != "OK":
        _raise_for_status(status, payload, stops)

    return _parse_route(payload["routes"][0], stops)


def _raise_for_status(status, payload, stops):
    message = payload.get("error_message") or f"Directions API returned {status}"

    if status == "NOT_FOUND":
        # geocoded_waypoints mirrors request order: origin, waypoints..., destination
        unresolved = [
            stops[i]
            for i, wp in enumerate(payload.get("geocoded_waypoints", []))
            if wp.get("geocoder_status") != "OK"
        ]
        if unresolved:
            message = f"Could not locate address: {unresolved[0]}"
        raise RouteNotFoundError(message, status)

    if status == "ZERO_RESULTS":
        raise RouteNotFoundError("No drivable route could be found between the provided stops", status)

    raise GoogleMapsError(message, status)


def _parse_route(route, stops):
    last_index = len(stops) - 1
    waypoint_order = route.get("waypoint_order", [])
    visit_order = [0] + [i + 1 for i in waypoint_order] + [last_index]

    legs = route["legs"]
    route_stops = []
    for position, original_index in enumerate(visit_order, start=1):
        leg_index = position - 1
        if leg_index < len(legs):
            formatted, location = legs[leg_index]["start_address"], legs[leg_index]["start_location"]
        else:
            formatted, location = legs[-1]["end_address"], legs[-1]["end_location"]
        route_stops.append(
            RouteStop(
                position=position,
                original_index=original_index,
                address=stops[original_index],
                formatted_address=formatted,
                location=LatLng(lat=location["lat"], lng=location["lng"]),
            )
        )

    route_legs = [
        RouteLeg(
            from_position=i + 1,
            to_position=i + 2,
            distance_meters=leg["distance"]["value"],
            duration_seconds=leg["duration"]["value"],
        )
        for i, leg in enumerate(legs)
    ]

    return OptimizedRoute(
        stops=route_stops,
        legs=route_legs,
        total_distance_meters=sum(leg.distance_meters for leg in route_legs),
        total_duration_seconds=sum(leg.duration_seconds for leg in route_legs),
        polyline=route["overview_polyline"]["points"],
        bounds=route["bounds"],
    )
