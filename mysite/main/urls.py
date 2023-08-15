from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("event/<int:id>/", views.event, name="event"),
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("event/create/", views.create_event, name="create_event"),
    path("event/view/", views.view_my_events, name="view_my_events"),
    path('event/<int:id>/modify/', views.modify_event, name='modify_event'),
    path('login/', views.user_login, name='login'),
    path('create_user/', views.create_user, name='create_user'),
    path('event/<int:id>/delete/', views.delete_event, name='delete_event'),
    path('event/<int:id>/approve/', views.approve_event, name='approve_event'),
    path('event/<int:event_id>/buy_ticket/', views.buy_ticket, name='buy_ticket'),
    path('event/<int:event_id>/add_ticket_type/', views.create_ticket_type, name='create_ticket_type'),
    path('event/<int:event_id>/delete_ticket_type/', views.delete_ticket_type, name='delete_ticket_type'),
    path('view_tickets', views.view_tickets, name='view_tickets'),
    path('event/<int:event_id>/refund_ticket/', views.refund_ticket, name='refund_ticket'),
    path('event/search/', views.search_events, name='search_events'),
    path('users', views.user_list, name='user_list'),
    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('user/modify/<int:user_id>/', views.modify_user, name='modify_user'),
    path('event/<int:id>/finish/', views.finish_event, name='finish_event'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

