from django.urls import path
from .views import HomePageView, EmailSelectionView, DeleteEmailsView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('email/', EmailSelectionView.as_view(), name='select_email'),
    path('delete/', DeleteEmailsView.as_view(), name='delete-emails'),
]