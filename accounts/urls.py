from django.urls import path
from .views import Profile, get_status_ip, Login, Logout, sync_db, get_logs


urlpatterns = [
    path('', Profile.as_view(), name='profile'),
    path('status/<int:pk>', get_status_ip, name='get_status_ip'),
    path("login/", Login.as_view(), name="login"),
    path("logout/", Logout.as_view(), name="logout"),
    path("sync/", sync_db, name="sync"),
    path("get_logs/<int:count>", get_logs, name='get_logs')
]
