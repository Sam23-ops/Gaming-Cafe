from django.urls import path
from . import views

app_name = 'engagement'

urlpatterns = [
    path('reviews/', views.reviews_list_view, name='reviews'),
    path('reviews/submit/', views.submit_review_view, name='submit_review'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('events/', views.events_list_view, name='events'),
    path('events/<slug:slug>/', views.event_detail_view, name='event_detail'),
]
