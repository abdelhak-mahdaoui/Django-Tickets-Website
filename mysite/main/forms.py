"""
from django import forms
from django.contrib.auth.models import User

class CreateNewEvent(forms.Form):
    title = forms.CharField(label="Title", max_length=100, required=True)
    description = forms.CharField(label="Description", widget=forms.Textarea, required=True)
    start_time = forms.DateField(label="Start Time", widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    end_time = forms.DateField(label="End Time", widget=forms.DateInput(attrs={'type': 'date'}))
    location = forms.CharField(label="Location", max_length=100, required=True)
    organizer = forms.ModelChoiceField(label="Organizer", queryset=User.objects.all(), required=True)
    #ticket_price = forms.DecimalField(label="Ticket Price", required=True)
    ticket_types = forms.ModelMultipleChoiceField(queryset=TicketType.objects.all())
"""

from django import forms
from django.contrib.auth.models import User
from .models import Event, TicketType, Ticket, Attendee, CustomUser
from django.forms import DateTimeInput, DateInput

from django.contrib.auth.forms import UserCreationForm

#from django.forms import formset_factory

"""
from django.conf import settings
User = settings.AUTH_USER_MODEL
"""

class CreateNewTicketType(forms.ModelForm):
    #num_tickets_issued = forms.IntegerField(label='Number of Tickets Issued')

    class Meta:
        model = TicketType
        fields = ['name', 'price']


class CreateNewEvent(forms.ModelForm):
    #ticket_types = formset_factory(CreateNewTicketType, extra=1)
    #ticket_types = formset_factory(CreateNewTicketType, extra=1, can_delete=True)


    class Meta:
        model = Event
        fields = ['image', 'title', 'description', 'start_time', 'end_time', 'location']
        widgets = {
            'start_time': DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_ticket_types(self):
        ticket_types_data = self.cleaned_data.get('ticket_types')
        if ticket_types_data:
            ticket_types = [CreateNewTicketType(data=data) for data in ticket_types_data]
            for ticket_type_form in ticket_types:
                if not ticket_type_form.is_valid():
                    raise forms.ValidationError('Invalid ticket type data')
            return ticket_types
        return []


""" class CreateNewTicket(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['event', 'ticket_type', 'owner'] """

class BuyTicket(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event')  # Get the event from kwargs
        super().__init__(*args, **kwargs)
        self.fields['ticket_type'].queryset = TicketType.objects.filter(event=event)
        self.fields['ticket_type'].empty_label = None  # Remove the empty option

    class Meta:
        model = Ticket
        fields = ['ticket_type']

class CreateNewAttendee(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = ['event', 'user', 'ticket']

class ModifyEvent(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['image', 'title', 'description', 'start_time', 'end_time', 'location']
        widgets = {
            'start_time': DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_ticket_types(self):
        ticket_types_data = self.cleaned_data.get('ticket_types')
        if ticket_types_data:
            ticket_types = [CreateNewTicketType(data=data) for data in ticket_types_data]
            for ticket_type_form in ticket_types:
                if not ticket_type_form.is_valid():
                    raise forms.ValidationError('Invalid ticket type data')
            return ticket_types
        return []

class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class CreateUserForm(UserCreationForm):
    USER_TYPE_CHOICES = (
        ('user', 'Regular User'),
        ('organizer', 'Organizer'),
    )
    user_type = forms.ChoiceField(label='User Type', choices=USER_TYPE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'user_type']   

class ModifyUserForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('password1', 'password2', 'user_type')
