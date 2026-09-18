from rest_framework import serializers

from routes.services.google_maps import MAX_STOPS, MIN_STOPS

MAX_ADDRESS_LENGTH = 255


class RouteOptimizationRequestSerializer(serializers.Serializer):
    stops = serializers.ListField(
        child=serializers.CharField(max_length=MAX_ADDRESS_LENGTH),
        min_length=MIN_STOPS,
        max_length=MAX_STOPS,
    )


class LatLngSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()


class RouteStopSerializer(serializers.Serializer):
    position = serializers.IntegerField()
    original_index = serializers.IntegerField()
    address = serializers.CharField()
    formatted_address = serializers.CharField()
    location = LatLngSerializer()


class RouteLegSerializer(serializers.Serializer):
    from_position = serializers.IntegerField()
    to_position = serializers.IntegerField()
    distance_meters = serializers.IntegerField()
    duration_seconds = serializers.IntegerField()


class OptimizedRouteSerializer(serializers.Serializer):
    stops = RouteStopSerializer(many=True)
    legs = RouteLegSerializer(many=True)
    total_distance_meters = serializers.IntegerField()
    total_distance_km = serializers.FloatField()
    total_distance_miles = serializers.FloatField()
    total_duration_seconds = serializers.IntegerField()
    total_duration_minutes = serializers.IntegerField()
    polyline = serializers.CharField()
    bounds = serializers.DictField()
