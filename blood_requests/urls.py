from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('submit-request/', views.submit_blood_request, name='submit_blood_request'),
    path('blood-requests/', views.blood_requests_list, name='blood_requests_list'),
    path('blood-requests/<int:request_id>/respond/', views.respond_to_request, name='respond_to_request'),
    path('compatibility/', views.compatibility_guide, name='compatibility_guide'),
    path('hospitals/', views.hospital_directory, name='hospital_directory'),
    path('faq/', views.faq, name='faq'),
    path('awareness/', views.awareness_list, name='awareness_list'),
    path('awareness/<slug:slug>/', views.awareness_detail, name='awareness_detail'),
    path('offline/', views.offline_page, name='offline_page'),
    path('request/close/<int:request_id>/', views.close_blood_request, name='close_blood_request'),
    
]
