from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home_view, name='home'),
    path('survey/', views.survey_list_view, name='survey_list'),
    path('survey/<str:survey_slug>', views.survey_view, name='survey'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)