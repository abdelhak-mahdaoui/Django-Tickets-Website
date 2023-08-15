from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import Event, TicketType, Ticket, Attendee, CustomUser
from .forms import CreateNewEvent, ModifyEvent, CreateNewTicketType, BuyTicket

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CreateUserForm, BuyTicket, ModifyUserForm
from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from django.db.models import Q

from django.db import transaction

"""
from django.conf import settings
User = settings.AUTH_USER_MODEL
"""

def clear_and_redirect(request, url):
    response = redirect(url)
    response.delete_cookie('cookie_name')
    return response

def clear_and_redirect_1(request, url, parameter=None):
    response = redirect(url)
    response.delete_cookie('cookie_name')
    
    if parameter:
        response['Location'] += f'?parameter={parameter}'
        
    return response

def home(request):
    ev_all = Event.objects.filter(status='approved').order_by('-id')[:10]
    return render(request, "main/home.html", {"ev_all": ev_all})


"""def event(response, id):
    ev = Event.objects.get(id=id)
    ticket_types = ev.ticket_types.all()

    return render(response, "main/event.html", {"ev":ev, "ticket_types":ticket_types, "event_id": id})"""

def event(request, id):
    ev = Event.objects.get(id=id)
    ticket_types = ev.ticket_types.all()

    user_tickets = Ticket.objects.filter(event=ev, owner=request.user) if request.user.is_authenticated else []

    return render(request, "main/event.html", {"ev": ev, "ticket_types": ticket_types, "event_id": id, "user_tickets": user_tickets})

""" @login_required(login_url='login')
def create_event(response):
    if response.user.is_organizer:
        if response.method == "POST":
            form = CreateNewEvent(response.POST)

            if form.is_valid():
                title = form.cleaned_data["title"]
                description = form.cleaned_data["description"]
                start_time = form.cleaned_data["start_time"]
                end_time = form.cleaned_data["end_time"]
                location = form.cleaned_data["location"]
                organizer = response.user

                ev_f = Event(title=title, description=description, start_time=start_time, end_time=end_time, location=location, organizer=organizer)
                ev_f.save()
                response.user.event.add(ev_f)

            return HttpResponseRedirect("/event/%i" %ev_f.id)
        else:
            form = CreateNewEvent()
        return render(response, "main/create_event.html", {"form":form})
    else:
        return redirect("home") """

@login_required(login_url='login')
def create_event(request):
    if request.user.is_organizer:
        if request.method == "POST":
            form = CreateNewEvent(request.POST, request.FILES)  # Include request.FILES to handle file uploads

            if form.is_valid():
                image = form.cleaned_data['image']
                title = form.cleaned_data["title"]
                description = form.cleaned_data["description"]
                start_time = form.cleaned_data["start_time"]
                end_time = form.cleaned_data["end_time"]
                location = form.cleaned_data["location"]
                organizer = request.user

                if start_time < end_time:
                    ev_f = Event(image=image, title=title, description=description, start_time=start_time, end_time=end_time, location=location, organizer=organizer)
                    ev_f.save()
                    request.user.event.add(ev_f)

                    return HttpResponseRedirect("/event/%i" % ev_f.id)
                else:
                    form.add_error('end_time', "End time should be after the start time.")

        else:
            form = CreateNewEvent()
        return render(request, "main/create_event.html", {"form": form})
    else:
        return redirect("home")

@login_required(login_url='login')
def view_my_events(request):
    if request.user.is_superuser or request.user.is_admin or request.user.is_user:
        ev_all = Event.objects.all()
    elif request.user.is_organizer:
        ev_all = Event.objects.filter(organizer=request.user)
    else:
        ev_all = Event.objects.none()

    return render(request, "main/view.html", {"ev_all": ev_all})
    
def modify_event(request, id):
    ev = get_object_or_404(Event, id=id)

    if request.method == "POST":
        form = ModifyEvent(request.POST, request.FILES, instance=ev)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/event/{}".format(id))     
    else:
        form = ModifyEvent(instance=ev)
        
    return render(request, "main/modify_event.html", {"form": form, "ev": ev})


""" @login_required(login_url='login')
def modify_event(request, id):
    event = get_object_or_404(Event, id=id)

    # Check if the logged-in user is the organizer of the event
    if not event.organizer == request.user:
        return clear_and_redirect(request, '/event/view/')

    if request.method == "POST":
        form = ModifyEvent(request.POST, request.FILES, instance=event)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/event/{}".format(id))
    else:
        form = ModifyEvent(instance=event)

    return render(request, "main/modify_event.html", {"form": form, "id": id}) """

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')

def logout(request):
    logout(request)
    return redirect('home')

def create_user(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}. You can now log in.')
            return redirect('login')

    return render(request, 'create_user.html', {'form': form})

def create_user(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            
            # Authenticate and log in the user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Account created for {username}. You are now logged in.')
                return redirect('home') 
            else:
                # Handle authentication error
                messages.error(request, 'Failed to log in after account creation. Please try logging in manually.')
                return redirect('login') 

    return render(request, 'create_user.html', {'form': form})

def delete_event(request, id):
    event = get_object_or_404(Event, id=id)

    if request.method == 'POST':
        event.delete()
        return clear_and_redirect(request, '/event/view/')

    return render(request, 'main/delete_event.html', {'event': event})

@login_required(login_url='login')
def approve_event(request,id):
    # Check if the user is an admin or superuser
    if not request.user.is_admin and not request.user.is_superuser:
        return redirect('home')
    try:
        event = get_object_or_404(Event, id=id)
    except Event.DoesNotExist:
        return clear_and_redirect(request, '/event/view/')

    if event.status == 'approved':
        return clear_and_redirect(request, '/event/view/')

    event.status = 'approved'
    event.save()

    return clear_and_redirect(request, '/event/view/')

""" def addcket(request, event_id):
    event = Event.objects.get(id=event_id)
    
    # Check if the logged-in user is the organizer of the event
    if not event.organizer == request.user:
        return clear_and_redirect(request, '/event/view/')

    if request.method == 'POST':
        form = CreateNewTicket(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.event_id = event_id
            ticket.save()
            return redirect('event', event_id=event_id)
    else:
        form = CreateNewTicket()
    
    return render(request, 'create_ticket.html', {'form': form, 'event_id': event_id}) """

"""def buy_ticket(request, event_id):
    event = Event.objects.get(id=event_id)

    if not request.user.is_authenticated or not request.user.is_user:
        return clear_and_redirect(request, '/event/view/')

    if request.method == 'POST':
        form = BuyTicket(request.POST)
        if form.is_valid():
            ticket_type = form.cleaned_data['ticket_type']
            ticket = Ticket(event=event, ticket_type=ticket_type, owner=request.user)
            ticket.save()
            #return redirect('event', event_id=event_id)
            return clear_and_redirect(request, '/event/view/')
    else:
        form = BuyTicket()

    return render(request, 'buy_ticket.html', {'form': form, 'event_id': event_id})"""

def buy_ticket(request, event_id):
    event = Event.objects.get(id=event_id)

    if not request.user.is_authenticated or not request.user.is_user:
        return clear_and_redirect(request, '/event/view/')

    existing_tickets = Ticket.objects.filter(event=event, owner=request.user)
    if existing_tickets.exists():
        return clear_and_redirect(request, '/event/view/')

    if request.method == 'POST':
        form = BuyTicket(request.POST, event=event)  # Pass the event to the form
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.event = event
            ticket.owner = request.user
            ticket.save()
            return clear_and_redirect(request, '/event/view/')
    else:
        form = BuyTicket(event=event)  # Pass the event to the form

    return render(request, 'buy_ticket.html', {'form': form, 'event_id': event_id})

"""def create_ticket_type(request, event_id):
    if request.method == 'POST':
        form = CreateNewTicketType(request.POST)
        if form.is_valid():
            ticket_type = form.save(commit=False)
            ticket_type.event_id = event_id
            ticket_type.save()
            #return  redirect('view', event_id=event_id)
            return clear_and_redirect(request, '/event/view/')
    else:
        form = CreateNewTicketType()

    return render(request, 'create_ticket_type.html', {'form': form, 'event_id': event_id})"""

def create_ticket_type(request, event_id):
    if request.method == 'POST':
        form = CreateNewTicketType(request.POST)
        if form.is_valid():
            ticket_type = form.save(commit=False)
            ticket_type.event_id = event_id

            # Check if a ticket type with the same name already exists for the event
            if TicketType.objects.filter(event_id=event_id, name=ticket_type.name).exists():
                form.add_error('name', 'A ticket type with this name already exists for the event.')
            else:
                ticket_type.save()
                # return redirect('view', event_id=event_id)
                return clear_and_redirect(request, '/event/view/')
    else:
        form = CreateNewTicketType()

    return render(request, 'create_ticket_type.html', {'form': form, 'event_id': event_id})

def delete_ticket_type(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    ticket_types = TicketType.objects.filter(event=event)

    if request.method == 'POST':
        ticket_type_id = request.POST.get('ticket_type_id')
        ticket_type = get_object_or_404(TicketType, id=ticket_type_id)
        ticket_type.delete()
        return redirect('delete_ticket_type', event_id=event_id)

    return render(request, 'delete_ticket_type.html', {'event': event, 'ticket_types': ticket_types, 'event_id': event_id })

@login_required(login_url='login')
def view_tickets(request):
    user_tickets = Ticket.objects.filter(owner=request.user)

    return render(request, 'view_tickets.html', {'user_tickets': user_tickets})

@login_required(login_url='login')
def refund_ticket(request, event_id):
    event = Event.objects.get(id=event_id)

    if not request.user.is_authenticated or not request.user.is_user:
        return clear_and_redirect(request, '/event/view/')

    ticket = Ticket.objects.filter(event=event, owner=request.user).first()

    if not ticket:
        return clear_and_redirect(request, '/event/view/')

    if request.method == 'POST':
        ticket.delete()
        return clear_and_redirect(request, '/event/view/')

    return render(request, 'refund_ticket.html', {'ticket': ticket})

def search_events(request):
    query = request.GET.get('query')
    events = Event.objects.none()  # Create an empty queryset to hold the search results
    event_ids = []  # Initialize the list to store event IDs
    results_count = 0  # Initialize the search results count

    if query:
        events = Event.objects.filter(
            Q(title__icontains=query) |  # Search by title (case-insensitive)
            Q(description__icontains=query) |  # Search by description (case-insensitive)
            Q(location__icontains=query) |  # Search by location (case-insensitive)
            Q(organizer__username__icontains=query)  # Search by organizer username (case-insensitive)
        ).filter(status='approved')  # Filter by approved status

        event_ids = events.values_list('id', flat=True)  # Get a list of event IDs
        results_count = events.count()  # Get the count of search results

    return render(request, 'search_events.html', {'query': query, 'events': events, 'event_ids': event_ids, 'results_count': results_count})


@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser or not request.user.is_admin:
        messages.error(request, 'You are not authorized to delete users.')
        return redirect('user_list')

    try:
        user = CustomUser.objects.get(pk=user_id)
        if user.is_superuser:
            messages.error(request, 'Deleting a superuser is not allowed.')
        else:
            user.delete()
            messages.success(request, 'User has been deleted successfully.')
    except User.DoesNotExist:
        messages.error(request, 'User does not exist.')

    return redirect('user_list')

@user_passes_test(lambda u: u.is_superuser or u.is_admin, login_url='access_denied')
@login_required(login_url='login')
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'user_list.html', {'users': users})

@user_passes_test(lambda u: u.is_superuser or u.is_admin, login_url='access_denied')
@login_required(login_url='login')
def modify_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    form = ModifyUserForm(request.POST or None, instance=user)

    if request.method == 'POST':
        if form.is_valid():
            with transaction.atomic():
                new_user = form.save(commit=False)
                if user.user_type == 'organizer' and new_user.user_type == 'user':
                    # Delete the events created by the organizer
                    user.event.all().delete()
                new_user.save()
                form.save_m2m()  # Save any many-to-many fields
                messages.success(request, 'User details updated successfully.')
            return redirect('user_list')

    return render(request, 'modify_user.html', {'form': form, 'user_id': user_id})

@login_required(login_url='login')
def finish_event(request,id):
    # Check if the user is an admin or superuser
    if not request.user.is_admin and not request.user.is_superuser:
        return redirect('home')
    try:
        event = get_object_or_404(Event, id=id)
    except Event.DoesNotExist:
        return clear_and_redirect(request, '/event/view/')

    if event.status == 'finished':
        return clear_and_redirect(request, '/event/view/')

    event.status = 'finished'
    event.save()

    return clear_and_redirect(request, '/event/view/')



