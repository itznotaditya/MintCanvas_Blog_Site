# blog/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Comment
from .models import Profile
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'bio', 'email', 'location', 'profile_photo']

    def clean_profile_photo(self):
        photo = self.cleaned_data.get('profile_photo')
        if photo:
            if not photo.name.endswith(('.jpg', '.jpeg', '.png')):
                raise ValidationError(_('Only .jpg, .jpeg, and .png images are allowed.'))
        return photo