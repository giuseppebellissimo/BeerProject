from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='root'),
    path('login/', views.login_user, name='login'),
    path('signup/', views.signup, name='signup'),
]
