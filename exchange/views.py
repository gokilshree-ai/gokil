from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, Skill, Booking, Review
from .forms import UserRegistrationForm, SkillForm, BookingForm, UserUpdateForm, UserProfileUpdateForm
from django.db.models import Q

def home_view(request):
    trending_skills = Skill.objects.all().order_by('-created_at')[:6]
    categories = [cat[0] for cat in Skill.CATEGORY_CHOICES]
    return render(request, 'home.html', {'trending_skills': trending_skills, 'categories': categories})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Create UserProfile
            UserProfile.objects.create(
                user=user, 
                department=form.cleaned_data.get('department', '')
            )
            login(request, user)
            messages.success(request, 'Registration successful. Welcome to SkillSwap!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
        
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('home')

def marketplace_view(request):
    skills = Skill.objects.all().order_by('-created_at')
    
    # Search and Filter Logic
    query = request.GET.get('q')
    category = request.GET.get('category')
    level = request.GET.get('level')
    
    if query:
        skills = skills.filter(
            Q(skill_name__icontains=query) | 
            Q(description__icontains=query) |
            Q(teacher__username__icontains=query)
        )
    if category:
        skills = skills.filter(category=category)
    if level:
        skills = skills.filter(level=level)
        
    categories = [cat[0] for cat in Skill.CATEGORY_CHOICES]
    levels = [lvl[0] for lvl in Skill.LEVEL_CHOICES]
    
    context = {
        'skills': skills,
        'categories': categories,
        'levels': levels,
        'current_category': category,
        'current_level': level,
        'query': query,
    }
    return render(request, 'marketplace.html', context)

@login_required
def add_skill_view(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.teacher = request.user
            skill.save()
            messages.success(request, 'Your skill has been published successfully!')
            return redirect('marketplace')
    else:
        form = SkillForm()
        
    return render(request, 'add_skill.html', {'form': form})

@login_required
def book_session_view(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    
    # Can't book your own skill
    if skill.teacher == request.user:
        messages.warning(request, "You cannot book your own skill.")
        return redirect('marketplace')
        
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # Check for credits (ensure profile exists)
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            if profile.credits > 0:
                booking = form.save(commit=False)
                booking.student = request.user
                booking.teacher = skill.teacher
                booking.skill = skill
                booking.save()
                
                # Deduct credit
                profile.credits -= 1
                profile.save()
                
                # Add credit to teacher
                teacher_profile = skill.teacher.userprofile
                teacher_profile.credits += 1
                teacher_profile.save()
                
                messages.success(request, f'Successfully booked a session for {skill.skill_name}!')
                return redirect('profile')
            else:
                messages.error(request, 'You do not have enough credits to book a session.')
    else:
        form = BookingForm()
        
    return render(request, 'book_session.html', {'form': form, 'skill': skill})

@login_required
def profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    skills_offered = Skill.objects.filter(teacher=request.user).order_by('-created_at')
    
    # Sessions booked by the student
    learning_sessions = Booking.objects.filter(student=request.user).order_by('-date')
    
    # Sessions where the user is the teacher
    teaching_sessions = Booking.objects.filter(teacher=request.user).order_by('-date')
    
    context = {
        'profile': user_profile,
        'skills_offered': skills_offered,
        'learning_sessions': learning_sessions,
        'teaching_sessions': teaching_sessions,
    }
    return render(request, 'profile.html', context)

@login_required
def edit_profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = UserProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = UserProfileUpdateForm(instance=user_profile)
        
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'edit_profile.html', context)

@login_required
def edit_skill_view(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, teacher=request.user)
    
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your skill has been updated!')
            return redirect('profile')
    else:
        form = SkillForm(instance=skill)
        
    return render(request, 'edit_skill.html', {'form': form, 'skill': skill})
@login_required
def confirm_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, teacher=request.user)
    if booking.status == 'Pending':
        booking.status = 'Confirmed'
        booking.save()
        messages.success(request, f'Session with {booking.student.username} confirmed!')
    return redirect('profile')

@login_required
def decline_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, teacher=request.user)
    if booking.status == 'Pending':
        booking.status = 'Cancelled'
        booking.save()
        
        # Refund credits to the student
        student_profile = booking.student.userprofile
        student_profile.credits += 1
        student_profile.save()
        
        # Take credit back from the teacher (since they didn't teach)
        teacher_profile = booking.teacher.userprofile
        teacher_profile.credits -= 1
        teacher_profile.save()
        
        messages.info(request, f'Session with {booking.student.username} declined. Credit refunded.')
    return redirect('profile')
