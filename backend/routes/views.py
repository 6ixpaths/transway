from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from routes.serializers import OptimizedRouteSerializer, RouteOptimizationRequestSerializer
from routes.services.google_maps import (
    GoogleMapsConfigurationError,
    GoogleMapsError,
    RouteNotFoundError,
    optimize_route,
)


class RouteOptimizeView(APIView):
    def post(self, request):
        serializer = RouteOptimizationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            route = optimize_route(serializer.validated_data["stops"])
        except RouteNotFoundError as exc:
            return _error(str(exc), "route_not_found", status.HTTP_422_UNPROCESSABLE_ENTITY)
        except GoogleMapsConfigurationError:
            return _error(
                "Route optimization is not configured on the server",
                "not_configured",
                status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except GoogleMapsError as exc:
            return _error(str(exc), "upstream_error", status.HTTP_502_BAD_GATEWAY)

        return Response(OptimizedRouteSerializer(route).data)


def _error(detail, code, http_status):
    return Response({"detail": detail, "code": code}, status=http_status)
