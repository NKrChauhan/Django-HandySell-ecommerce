from django.urls import path,include
from search.views import SearchListView
app_name='search'

urlpatterns = [
    path("",SearchListView.as_view(),name="query"),
]