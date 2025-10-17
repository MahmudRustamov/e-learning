from decimal import Decimal
from django.utils.text import slugify
from rest_framework import serializers
from apps.courses.id_generator import generate_id
from apps.courses.models import Course, Instructor, Category, Enrollment, CourseReview, Lesson, Section


class CategorySerializer(serializers.ModelSerializer):
    sub_count = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'parent', 'sub_count']


    @staticmethod
    def get_sub_count( obj):
        return obj.subcategories.count()


class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = '__all__'


class CourseRegisterSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    instructor = InstructorSerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    instructor_id = serializers.IntegerField(write_only=True)

    final_price = serializers.SerializerMethodField()
    total_lessons = serializers.SerializerMethodField()
    total_duration = serializers.SerializerMethodField()
    students_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'price', 'discount_percentage', 'final_price',
            'category', 'category_id', 'instructor', 'instructor_id',
            'total_lessons', 'total_duration', 'students_count',
            'average_rating', 'reviews_count',
            'language', 'level', 'is_featured', 'duration_hours',
            'requirements', 'what_you_learn', 'thumbnail',
            'status', 'created_at',
        ]
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    @staticmethod
    def get_final_price(obj):
        return round(obj.price * (Decimal(1) - Decimal(obj.discount_percentage) / Decimal(100)), 2)

    @staticmethod
    def get_total_lessons(obj):
        count = 0
        for section in obj.sections.all():
            count += section.lessons.count()
        return count

    @staticmethod
    def get_total_duration(obj):
        total = 0
        for section in obj.sections.all():
            for lesson in section.lessons.all():
                total += lesson.duration_minutes
        return total

    @staticmethod
    def get_students_count(obj):
        return obj.enrollments.count()

    @staticmethod
    def get_average_rating(obj):
        reviews = obj.reviews.all()
        if not reviews.exists():
            return 0
        total = sum(r.rating for r in reviews)
        return round(total / reviews.count(), 1)

    @staticmethod
    def get_reviews_count(obj):
        return obj.reviews.count()


    @staticmethod
    def validate_title(value):
        if value is None or len(value) < 10:
            raise serializers.ValidationError("Title can't be empty and must contain at leat 10 characters")
        return value


    @staticmethod
    def validate_description(value):
        if len(value) <= 50:
            raise serializers.ValidationError("Description must contain at least 50 characters")
        return value


    @staticmethod
    def validate_price(value):
        if not value > 0:
            raise serializers.ValidationError("Price should be greater than 0")
        return value


    @staticmethod
    def validate_discount_percentage(value):
        if not (0 <= value <= 100):
            raise serializers.ValidationError("Discount percentage should between 0-100")
        return value


    @staticmethod
    def validate_duration_hours(value):
        if not value > 0:
            raise serializers.ValidationError("Duration hours must be a positive numbers")
        return value


    @staticmethod
    def validate_language(value):
        if not value or not value.strip():
            raise serializers.ValidationError("Language can't be empty")
        return value


    def create(self, validated_data):
        instructor_id = validated_data.pop('instructor_id')
        category_id = validated_data.pop('category_id')

        instructor = Instructor.objects.get(id=instructor_id)
        category = Category.objects.get(id=category_id)

        title = validated_data.get('title')
        slug_base = slugify(title)
        slug = slug_base

        while Course.objects.filter(slug=slug).exists():
            slug = f"{slug_base}-{generate_id()}"

        validated_data['slug'] = slug
        validated_data['status'] = 'draft'
        validated_data['instructor'] = instructor
        validated_data['category'] = category

        return Course.objects.create(**validated_data)


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'duration_minutes', 'is_preview']


class SectionSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'title', 'order', 'lessons']


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = CourseReview
        fields = ['id', 'user', 'rating', 'comment', 'created_at']


class CourseDetailSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    instructor_id = serializers.IntegerField(write_only=True)
    sections = SectionSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    final_price = serializers.SerializerMethodField()
    total_lessons = serializers.SerializerMethodField()
    total_duration = serializers.SerializerMethodField()
    students_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'price', 'discount_percentage',
            'final_price', 'category', 'category_id', 'instructor', 'instructor_id',
            'language', 'level', 'requirements', 'what_you_learn', 'duration_hours',
            'sections', 'reviews', 'students_count', 'total_lessons', 'total_duration',
            'average_rating', 'is_featured', 'status', 'created_at'
        ]

        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'is_active': {'read_only': True},
        }

    @staticmethod
    def get_final_price(obj):
        return round(obj.price * (Decimal(1) - Decimal(obj.discount_percentage) / Decimal(100)), 2)

    @staticmethod
    def get_total_lessons(obj):
        count = 0
        for section in obj.sections.all():
            count += section.lessons.count()
        return count

    @staticmethod
    def get_total_duration(obj):
        total = 0
        for section in obj.sections.all():
            for lesson in section.lessons.all():
                total += lesson.duration_minutes
        return total

    @staticmethod
    def get_students_count(obj):
        return obj.enrollments.count()

    @staticmethod
    def get_average_rating(obj):
        reviews = obj.reviews.all()
        if not reviews.exists():
            return 0
        total = sum(r.rating for r in reviews)
        return round(total / reviews.count(), 1)

    @staticmethod
    def get_reviews_count(obj):
        return obj.reviews.count()


class CourseUpdateSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True, required=False)
    instructor_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Course
        fields = [
            "title", "description", "instructor_id", "category_id",
            "price", "discount_percentage", "level", "duration_hours",
            "requirements", "what_you_learn", "language", "thumbnail", "status"
        ]

        extra_kwargs = {
            'status': {'required': False},
        }

    @staticmethod
    def validate_title(value):
        if value and len(value) < 10:
            raise serializers.ValidationError("Title must contain at least 10 characters")
        return value

    @staticmethod
    def validate_description(value):
        if value and len(value) < 50:
            raise serializers.ValidationError("Description must contain at least 50 characters")
        return value

    @staticmethod
    def validate_price(value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    @staticmethod
    def validate_discount_percentage(value):
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Discount percentage must be between 0 and 100")
        return value

    @staticmethod
    def validate_duration_hours(value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Duration (hours) must be greater than 0")
        return value

    @staticmethod
    def validate_language(value):
        if value == "":
            raise serializers.ValidationError("Language field cannot be empty")
        return value

    @staticmethod
    def validate_instructor_id(value):
        if value and not Instructor.objects.filter(id=value, is_verified=True).exists():
            raise serializers.ValidationError("Instructor does not exist or is not verified")
        return value

    @staticmethod
    def validate_category_id(value):
        if value and not Category.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Category does not exist or is not active")
        return value

    def update(self, instance, validated_data):
        title = validated_data.get('title')
        if title and title != instance.title:
            slug_base = slugify(title)
            slug = slug_base
            while Course.objects.filter(slug=slug).exclude(id=instance.id).exists():
                slug = f"{slug_base}-{generate_id()}"
            instance.slug = slug

        instructor_id = validated_data.pop('instructor_id', None)
        if instructor_id:
            try:
                instance.instructor = Instructor.objects.get(id=instructor_id)
            except Instructor.DoesNotExist:
                raise serializers.ValidationError("Instructor does not exist.")

        category_id = validated_data.pop('category_id', None)
        if category_id:
            try:
                instance.category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                raise serializers.ValidationError("Category does not exist.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance