from django.urls import path
from .views import NameView, DeleteEmailsView

urlpatterns = [
    path('email/', NameView.as_view(), name='name-view'),
    path('delete/', DeleteEmailsView.as_view(), name='delete-emails'),
]