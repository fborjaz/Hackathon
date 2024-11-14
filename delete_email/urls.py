from django.urls import path
from .views import EmailSelectionView, DeleteEmailsView, DeleteAllEmailsView

urlpatterns = [
    path('email/', EmailSelectionView.as_view(), name='name-view'),
    path('delete/', DeleteEmailsView.as_view(), name='delete-emails'),
    path('delete-all/', DeleteAllEmailsView.as_view(), name='delete-all-emails'),
]