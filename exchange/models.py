from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    credits = models.IntegerField(default=10) # Give users some initial credits to book sessions
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('Programming', 'Programming'),
        ('Design', 'Design'),
        ('Marketing', 'Marketing'),
        ('Public Speaking', 'Public Speaking'),
        ('Video Editing', 'Video Editing'),
        ('Music', 'Music'),
        ('Languages', 'Languages'),
        ('Other', 'Other'),
    ]

    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Expert', 'Expert'),
    ]

    MODE_CHOICES = [
        ('Online', 'Online'),
        ('Offline', 'Offline'),
        ('Both', 'Both'),
    ]

    skill_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills_taught')
    availability = models.CharField(max_length=255, help_text="E.g., Weekends 10 AM - 12 PM")
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='Online')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.skill_name} by {self.teacher.username}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions_booked')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions_teaching')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} booked {self.skill.skill_name} with {self.teacher.username}"

class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.booking.skill.skill_name} - {self.rating} Stars"

# Signals to automatically create UserProfile
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    else:
        UserProfile.objects.create(user=instance)
