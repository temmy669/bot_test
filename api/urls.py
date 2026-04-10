from django.urls import path
from .views import ClassifyNameView

urlpatterns = [
    path('classify/', ClassifyNameView.as_view(), name='classify-name'),
]