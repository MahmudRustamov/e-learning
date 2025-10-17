from django.utils.text import slugify
from rest_framework import serializers

from apps.courses.id_generator import generate_id
from apps.courses.models import Course, Instructor, Category

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

    class Meta:
        model = Course
        fields = ['id', 'category', 'instructor', 'category_id', 'instructor_id', 'title','slug',
                  'description', 'thumbnail', 'trailer_url', 'price', 'discount_percentage',
                  'level','status','duration_hours','requirements','what_you_learn','language',
                  'is_featured','created_at','updated_at',
                  ]
        read_only_fields = ('slug', 'status', 'category', 'instructor')

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


    def validate(self, attrs):
        instructor_id = attrs.get('instructor_id')
        category_id = attrs.get('category_id')
        level = attrs.get('level')

        if not instructor_id:
            raise serializers.ValidationError({"instructor": "Instructor is required."})
        if not Instructor.objects.filter(id=instructor_id, is_verified=True).exists():
            raise serializers.ValidationError({"instructor": "Instructor must be verified."})

        if not category_id:
            raise serializers.ValidationError({"category": "Category is required."})
        if not Category.objects.filter(id=category_id, is_active=True).exists():
            raise serializers.ValidationError({"category": "Category must be active."})

        if level not in dict(Course.LEVEL_CHOICES):
            raise serializers.ValidationError({
                "level": "Invalid level. Choose a valid level option."
            })

        return attrs


    def create(self, validated_data):
        base_slug = slugify(validated_data.get('title'))
        slug = base_slug

        while Course.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{generate_id()}"
        validated_data['slug'] = slug
        validated_data['status'] = 'draft'
        return Course.objects.create(**validated_data)



