from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.courses.models import Course, Enrollment
from apps.courses.serializers import CourseRegisterSerializer


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
    serializer_class = CourseRegisterSerializer

    def get(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        if course.status == "archived":
            return Response({"error": "Course is archived"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(course)
        return Response(serializer.data, status=status.HTTP_200_OK)