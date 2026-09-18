from django.urls import path

from routes.views import RouteOptimizeView

app_name = 'routes'

urlpatterns = [
    path('optimize/', RouteOptimizeView.as_view(), name='optimize'),
]
