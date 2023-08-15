from django.contrib import admin
from .models import Event, TicketType, Ticket, Attendee, CustomUser

# Register your models here.

admin.site.register(Event)
admin.site.register(TicketType)
admin.site.register(Ticket)
admin.site.register(Attendee)
admin.site.register(CustomUser)




