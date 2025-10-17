from django.utils.text import slugify
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.courses.id_generator import generate_id
from apps.courses.models import Course
from apps.courses.serializers import CourseRegisterSerializer, CourseDetailSerializer, CourseUpdateSerializer


class CourseListAPIView(APIView):
    serializer_class = CourseRegisterSerializer

    @staticmethod
    def get_query_set(request):
        courses = Course.objects.all().order_by('-created_at')
        return courses

    def post(self, request):
       serializer = self.serializer_class(data=request.data)
       if serializer.is_valid():
           serializer.save()
           return Response(data=serializer.data, status=status.HTTP_201_CREATED)
       return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):
        courses = self.get_query_set(request=request)
        serializer = self.serializer_class(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class CourseDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return None

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsAuthenticated()]
        return [AllowAny()]

    @staticmethod
    def get(request, pk):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        if course.status == 'archived':
            return Response({"detail": "Course not available"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseDetailSerializer(course)
        data = serializer.data

        data['instructor']['courses_count'] = course.instructor.courses.count()

        if request.user.is_authenticated:
            data['is_enrolled'] = course.enrollments.filter(user=request.user).exists()
        else:
            data['is_enrolled'] = False

        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        return self.update_course(request, pk, partial=False)

    def patch(self, request, pk):
        return self.update_course(request, pk, partial=True)

    def update_course(self, request, pk, partial=False):
        course = self.get_object(pk)
        if not course:
            return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        if not hasattr(request.user, 'instructor_profile') and not request.user.is_superuser:
            return Response({"detail": "You are not an instructor"}, status=status.HTTP_403_FORBIDDEN)
        if not request.user.is_superuser and course.instructor != request.user.instructor_profile:
            return Response({"detail": "You are not the owner of this course"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()

        if 'title' in data and data['title'] != course.title:
            slug_base = slugify(data['title'])
            slug = slug_base
            while Course.objects.filter(slug=slug).exclude(pk=course.pk).exists():
                slug = f"{slug_base}-{generate_id()}"
            data['slug'] = slug

        serializer = CourseUpdateSerializer(course, data=data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        course = self.get_object(pk)
        if not course:
            return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        if not hasattr(request.user, 'instructor_profile') and not request.user.is_superuser:
            return Response({"detail": "You are not an instructor"}, status=status.HTTP_403_FORBIDDEN)
        if not request.user.is_superuser and course.instructor != request.user.instructor_profile:
            return Response({"detail": "You are not the owner of this course"}, status=status.HTTP_403_FORBIDDEN)

        course.delete()
        return Response({"detail": "Course deleted"}, status=status.HTTP_204_NO_CONTENT)
