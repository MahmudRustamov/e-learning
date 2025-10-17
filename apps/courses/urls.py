from django.urls import path

from apps.courses.views import CourseListAPIView, CourseDetailAPIView

app_name = 'courses'

urlpatterns = [
    path('courses/', CourseListAPIView.as_view(), name='create-list'),
    path('courses/<int:pk>/', CourseDetailAPIView.as_view(), name='course-detail'),
]