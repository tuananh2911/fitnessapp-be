
from django.contrib import admin
from django.urls import path
from myapp.views import calo_to_goal

urlpatterns = [
    path('admin/', admin.site.urls),
    path('goal-calo/', calo_to_goal),
]
