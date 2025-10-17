from django.urls import path

from apps.courses.views import CourseListAPIView, CourseDetailAPIView, CourseUpdateView, CourseDeleteView

app_name = 'courses'

urlpatterns = [
    path('courses/', CourseListAPIView.as_view(), name='create-list'),
    path('courses/<int:pk>/',CourseDetailAPIView.as_view()),
    path('courses/<int:pk>/',CourseUpdateView.as_view(), name='course-detail'),
    path('courses/<int:pk>/',CourseDeleteView.as_view()),
]