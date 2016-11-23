from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import (
        login as Login,
        logout as Logout,
        authenticate
    )
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from .models import Room, Table, Player
from .forms import (
        CreateRoomForm, CreatePlayerForm, SetBoatsForm, SelectVictimForm,
        AttackForm,
        )


def signup(request):
    """
    Create a new user
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Se ha registrado correctamente')
        return HttpResponseRedirect('/login/')
    else:
        messages.error(request, form.errors)
    return render(request, 'signup.html', {'form': form})

def login(request):
    """
    Login a session
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    form = AuthenticationForm(data=request.POST or None)
    if form.is_valid():
        user = request.POST['username']
        password = request.POST['password']
        access = authenticate(username=user, password=password)
        if access is not None:
            Login(request, access)
            messages.success(request, 'Bienvenido %s'%request.user)
            return HttpResponseRedirect('/rooms/')
        else:
            msg = 'El usuario y la contraseña no coinciden o el usuario\
                    no existe'
            messages.error(request, msg)
    return render(request, 'login.html', {'form':form})

@login_required
def logout(request):
    Logout(request)
    messages.success(request, '¡Nos vemos pronto!')
    return HttpResponseRedirect('/')

def index(request):
    return render(request, 'index.html')

@login_required
def create_room(request):
    form = CreateRoomForm(request.POST or None)
    if form.is_valid():
        room = form.save(commit=False)
        room.set_admin(request.user)
        return HttpResponseRedirect(reverse('create-player-view',
            args=[room.id]))
    return render(request, 'create_room.html', {'form': form})

@login_required
def join_room(request):
    rooms = Room.objects.all()
    return render(request, 'room_list.html', {'rooms':rooms})

@login_required
def create_player(request, room):
    r = get_object_or_404(Room, id=room)
    try:
        Player.objects.get(user=request.user, room=room)
        messages.error(request, "Ya te encuentras en esta sala")
        return HttpResponseRedirect(r.get_absolute_url())
    except Player.DoesNotExist:
        pass
    if r.start:
        messages.error(request, "La sala ya esta en juego")
        return HttpResponseRedirect('/rooms/')
    form = CreatePlayerForm(request.POST or None)
    if form.is_valid():
        u = r.get_admin()
        player = form.save(commit=False)
        player.user = request.user
        player.room = r
        player.save()
        if u is not None and u == request.user:
            player.set_admin(True)
        table = Table.objects.create(player=player)
        return HttpResponseRedirect(table.get_absolute_url() + '/setboats')
    return render(request, 'create_player.html', {'form':form, 'room':r})

@login_required
def waiting_room(request, room):
    r = get_object_or_404(Room, id=room)
    if r.start and r.get_player_from_user(request.user) is not None:
        return HttpResponseRedirect(reverse('game-room-view', args=[room]))
    u = r.get_admin()
    players = Player.objects.filter(room=r)
    ctx = {'players':players, 'room':r, 'admin':u}
    return render(request, 'waiting_room.html', ctx)

@login_required
def my_table(request, room, table):
    r = get_object_or_404(Room, id=room)
    t = get_object_or_404(Table, id=table)
    mytable = t.get_table(enumerated=True)
    ctx = dict()
    ctx['room'] = r
    ctx['table'] = mytable
    ctx['table_obj'] = t.id
    ctx['coordinate'] = ctx['table'][0]
    return render(request, 'my_table.html', ctx)

@login_required
def set_boats(request, room, table):
    r = get_object_or_404(Room, id=room)
    t = get_object_or_404(Table, id=table)
    player = get_object_or_404(Player, user=request.user, room=r)
    if player.is_ready():
        return HttpResponseRedirect(r.get_absolute_url())
    form = SetBoatsForm(t, request.POST or None)
    if form.is_valid():
        col = int(form.cleaned_data['column'])
        row = int(form.cleaned_data['row'])
        orientation = form.cleaned_data['orientation']
        boat_type = form.cleaned_data['boat_type']
        if t.position_is_valid((row, col), orientation, boat_type):
            t.set_boat((row, col), orientation, boat_type)
            if not t.add_boat_available():
                player.set_ready(True)
                return HttpResponseRedirect(r.get_absolute_url())
            else:
                form = SetBoatsForm(t, None)
        else:
            messages.error(request, 'No se puede ubicar en esta posición')
    ctx = dict()
    ctx['form'] = form
    ctx['room'] = r
    ctx['table'] = t.get_table(enumerated=True)
    ctx['coordinate'] = ctx['table'][0]
    return render(request, 'set_boat.html', ctx)

@login_required
def start_game(request, room):
    r = get_object_or_404(Room, id=room)
    is_ready, msg = r.check_state()
    if not is_ready:
        messages.error(request, msg)
    if is_ready:
        r.start_game()
    return HttpResponseRedirect(r.get_absolute_url())

@login_required
def game_room(request, room):
    r = get_object_or_404(Room, id=room)
    t = r.get_table_from_user(request.user)
    if t is None:
        messages.error(request, "No tienes un jugador en esta sala.")
        return HttpResponseRedirect('/rooms')
    if not r.start:
        messages.error(request, "No esta lista aun la sala")
        return HttpResponseRedirect(r.get_absolute_url())
    table_player = t.get_table(enumerated=True)
    player_turn = Player.objects.get(room=r, turn=True)
    ctx = {'room': r, 'table': table_player,
            'coordinate': table_player[0], 'player': t.player,
            'player_turn': player_turn}
    return render(request, 'game_room.html', ctx)

@login_required
def attack(request, room):
    r = get_object_or_404(Room, id=room)
    p = Player.objects.get(user=request.user, room=r)
    if p.turn:
        return HttpResponseRedirect(reverse('select-victim-view',
            args=[room]))
    else:
        messages.error(request, "Aun no es tu turno")
    return HttpResponseRedirect(reverse('game-room-view', args=[room]))

@login_required
def select_victim(request, room):
    r = get_object_or_404(Room, id=room)
    p = r.get_player_from_user(request.user)
    players = Player.objects.filter(room=r).exclude(id=p.id)
    form = SelectVictimForm(players, request.POST or None)
    if form.is_valid():
        victim = int(form.cleaned_data['victim'])
        p.get_or_create_victim_table(victim)
        return HttpResponseRedirect(reverse('victim-table-view',
            args=[room, victim]))
    return render(request, 'select_victim.html', {'form':form})

@login_required
def victim_table(request, room, victim):
    r = get_object_or_404(Room, id=room)
    p = r.get_player_from_user(request.user)
    victim_table = Table.objects.get(player=p, victim=victim)
    form = AttackForm(r, request.POST or None)
    if form.is_valid():
        row = int(form.cleaned_data['row'])
        col = int(form.cleaned_data['column'])
        r.attack((row, col), p, victim)
    t = victim_table.get_table(enumerated=True)
    return render(request, 'victim_table.html', {'form':form,
        'table': t, 'coordinate': t[0]})
