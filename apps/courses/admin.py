# courses/admin.py

from django.contrib import admin
from .models import (
    Instructor, Category, Course, Section, Lesson,
    Enrollment, LessonProgress, CourseReview,
    Question, Answer, Certificate
)


# --- Inlines for Nested Models in Admin ---

class LessonInline(admin.TabularInline):
    """Allows adding/editing Lessons directly within the Section admin."""
    model = Lesson
    extra = 1
    fields = ('title', 'order', 'duration_minutes', 'is_preview', 'video_url')


class SectionInline(admin.TabularInline):
    """Allows adding/editing Sections directly within the Course admin."""
    model = Section
    extra = 1
    show_change_link = True
    fields = ('title', 'order', 'description')


class AnswerInline(admin.TabularInline):
    """Allows viewing/editing Answers directly within the Question admin."""
    model = Answer
    extra = 0
    fields = ('user', 'content', 'is_instructor_answer')
    readonly_fields = ('user', 'content', 'is_instructor_answer', 'created_at')


# --- Model Admin Classes ---

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('user', 'expertise', 'total_students', 'rating', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'expertise')
    search_fields = ('user__username', 'user__email', 'bio', 'expertise')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'bio', 'profile_image', 'expertise')
        }),
        ('Statistics', {
            'fields': ('total_students', 'rating', 'is_verified'),
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'price', 'level', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'level', 'language', 'is_featured', 'category')
    search_fields = ('title', 'description', 'instructor__user__username')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created_at',)
    inlines = [SectionInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'instructor', 'category')
        }),
        ('Content & Media', {
            'fields': ('thumbnail', 'trailer_url', 'language', 'duration_hours', 'requirements', 'what_you_learn')
        }),
        ('Pricing & Status', {
            'fields': ('price', 'discount_percentage', 'level', 'status', 'is_featured')
        }),
    )


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    ordering = ('course', 'order')
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'order', 'duration_minutes', 'is_preview')
    list_filter = ('section__course', 'is_preview')
    search_fields = ('title', 'section__title', 'content')
    ordering = ('section__course__title', 'section__order', 'order')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'progress_percentage', 'enrolled_at')
    list_filter = ('status', 'course', 'enrolled_at')
    search_fields = ('student__username', 'course__title')
    ordering = ('-enrolled_at',)


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'is_completed', 'watch_time_minutes', 'completed_at')
    list_filter = ('is_completed', 'enrollment__course')
    search_fields = ('enrollment__student__username', 'lesson__title')


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'rating', 'title', 'created_at')
    list_filter = ('rating', 'course')
    search_fields = ('title', 'comment', 'course__title', 'student__username')
    ordering = ('-created_at',)
    readonly_fields = ('student', 'course', 'rating', 'title', 'comment', 'created_at', 'updated_at')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'student', 'created_at')
    list_filter = ('lesson__section__course',)
    search_fields = ('title', 'content', 'student__username', 'lesson__title')
    ordering = ('-created_at',)
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'user', 'is_instructor_answer', 'created_at')
    list_filter = ('is_instructor_answer',)
    search_fields = ('content', 'user__username', 'question__title')
    ordering = ('created_at',)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'certificate_number', 'issued_at', 'certificate_url')
    search_fields = ('certificate_number', 'enrollment__student__username', 'enrollment__course__title')
    ordering = ('-issued_at',)
    readonly_fields = ('issued_at',)