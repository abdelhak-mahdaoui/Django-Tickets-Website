from django.db import models
#from django.contrib.auth.models import user
from django.contrib.auth.models import AbstractUser

"""from django.conf import settings
User = settings.AUTH_USER_MODEL"""

from django.conf import settings

User = settings.AUTH_USER_MODEL

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('organizer', 'Organizer'),
        ('user', 'User'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    def is_admin(self):
        return self.user_type == 'admin'

    def is_organizer(self):
        return self.user_type == 'organizer'

    def is_user(self):
        return self.user_type == 'user'

class Event(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('finished', 'Finished'),
    )

    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event", null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.title

"""
class TicketType(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2) 
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f"Ticket Type : {self.name} | Event : {self.event.title}"
"""

class TicketType(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE,
        related_name="ticket_types" 
    )
    num_tickets_issued = models.IntegerField(default=0)

    def __str__(self):
        return f"Ticket Type: {self.name} | Event: {self.event.title}"


class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket #{self.id} | {self.event.title} ({self.ticket_type.name})"


class Attendee(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.user.username} | {self.event.title}"



"""
class TicketType(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name
        

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event", null=True)
    #ticket_price = models.DecimalField(max_digits=8, decimal_places=2)
    ticket_types = models.ManyToManyField(TicketType, through='Ticket')

    def __str__(self):
        return self.title


class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    attendee = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket_code = models.CharField(max_length=100)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.event.title} ({self.ticket_type.name})"

"""

