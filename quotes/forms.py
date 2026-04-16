"""
quotes/forms.py — CJ Web Studio
Client-facing quote request form with validation.
"""

from django import forms
from .models import QuoteRequest


class QuoteRequestForm(forms.ModelForm):

    class Meta:
        model  = QuoteRequest
        fields = ['name', 'email', 'phone', 'business_name', 'project_type', 'budget', 'message']
        widgets = {
            'name':          forms.TextInput(attrs={'class':'form-input','placeholder':'Your full name','autocomplete':'name'}),
            'email':         forms.EmailInput(attrs={'class':'form-input','placeholder':'your@email.com','autocomplete':'email'}),
            'phone':         forms.TextInput(attrs={'class':'form-input','placeholder':'+27 ...','autocomplete':'tel'}),
            'business_name': forms.TextInput(attrs={'class':'form-input','placeholder':'Your business or company name'}),
            'project_type':  forms.Select(attrs={'class':'form-input'}),
            'budget':        forms.Select(attrs={'class':'form-input'}),
            'message':       forms.Textarea(attrs={'class':'form-input','rows':5,'placeholder':'Tell us about your project, goals, and any features you need...','style':'resize:none'}),
        }
        labels = {
            'name':          'Full Name *',
            'email':         'Email Address *',
            'phone':         'Phone / WhatsApp',
            'business_name': 'Business Name',
            'project_type':  'What are you building? *',
            'budget':        'Budget Range',
            'message':       'Project Details *',
        }
        error_messages = {
            'name':    {'required': 'Please enter your name.'},
            'email':   {'required': 'We need your email to reply.', 'invalid': 'Enter a valid email address.'},
            'message': {'required': 'Please describe your project.'},
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError('Name must be at least 2 characters.')
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            digits = ''.join(c for c in phone if c.isdigit())
            if len(digits) < 7:
                raise forms.ValidationError('Please enter a valid phone number.')
        return phone

    def clean_message(self):
        msg = self.cleaned_data.get('message', '').strip()
        if len(msg) < 10:
            raise forms.ValidationError('Please give us a bit more detail about your project.')
        return msg
