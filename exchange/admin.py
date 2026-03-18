from django.contrib import admin
from .models import UserProfile, Skill, Booking, Review

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'credits')
    search_fields = ('user__username', 'department')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('skill_name', 'teacher', 'category', 'level', 'mode', 'created_at')
    list_filter = ('category', 'level', 'mode')
    search_fields = ('skill_name', 'description', 'teacher__username')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('skill', 'student', 'teacher', 'date', 'status', 'created_at')
    list_filter = ('status', 'date')
    search_fields = ('student__username', 'teacher__username', 'skill__skill_name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'rating', 'created_at')
    list_filter = ('rating',)
