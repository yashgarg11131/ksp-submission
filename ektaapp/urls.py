from django.urls import path, include
from .views import *
urlpatterns = [
    path("",LoginView.as_view(),name="login"),
    path("home/",HomeView.as_view(),name="home"),
    path("pdf/download/", DownloadPDF.as_view(), name="pdf-download"),
    path("linkedin/data/api/", LinkedInDATAAPI.as_view(), name="linkedin-api"),
    path("image/search",ImageSearchView.as_view(), name="image-search")
]

