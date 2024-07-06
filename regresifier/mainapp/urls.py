from django.urls import path
from . import views


urlpatterns = [
    path("",views.index, name="home"),
    path("api/uploadCSV", views.upload_csv, name="upload_csv"),
    path("api/runRegression",views.run_linear_regression)
]