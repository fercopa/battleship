from django import forms
from .models import Room, Player

class CreateRoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'map_size',]


class CreatePlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name',]


class SetBoatsForm(forms.Form):
    ORIENTATION = (('H', 'Horizontal'), ('V', 'Vertical'))
    row = forms.ChoiceField()
    column = forms.ChoiceField()
    orientation = forms.ChoiceField(choices=ORIENTATION)
    boat_type = forms.ChoiceField()

    def __init__(self, table, *args, **kwargs):
        super(SetBoatsForm, self).__init__(*args, **kwargs)
        room = Room.objects.get(id=table.player.room.id)
        n = room.get_map_size()
        BOATS = []
        if table.add_aircraft_carrier_available():
            BOATS.append(('portaaviones', 'Porta avion'))
        if table.add_battleship_available():
            BOATS.append(('acorazado', 'Acorazado'))
        if table.add_frigate_available():
            BOATS.append(('fragata', 'Fragata'))
        if table.add_submarine_available():
            BOATS.append(('submarino', 'Submarino'))
        if table.add_patrol_boat_available():
            BOATS.append(('botepatrulla', 'Bote patrulla'))
        BOATS = tuple(BOATS)
        V = [(str(num-1), num) for num in range(1, n+1)]
        self.fields['row'] = forms.ChoiceField(choices=V, label='fila')
        self.fields['column'] = forms.ChoiceField(choices=V, label='columna')
        self.fields['boat_type'] = forms.ChoiceField(choices=BOATS)

class SelectVictimForm(forms.Form):
    victim = forms.ChoiceField()

    def __init__(self, players, *args, **kwargs):
        super(SelectVictimForm, self).__init__(*args, **kwargs)
        PLAYERS = [(p.id, p.name) for p in players]
        self.fields['victim'] = forms.ChoiceField(choices=PLAYERS)


class AttackForm(forms.Form):
    row = forms.ChoiceField()
    column = forms.ChoiceField()

    def __init__(self, room, *args, **kwargs):
        super(AttackForm, self).__init__(*args, **kwargs)
        n = room.get_map_size()
        VALUES = [(str(num-1), num) for num in range(1, n+1)]
        self.fields['row'] = forms.ChoiceField(choices=VALUES, label='fila')
        self.fields['column'] = forms.ChoiceField(choices=VALUES,
                label='columna')
