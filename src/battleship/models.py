from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


BOAT_SIZE = {
        'portaaviones': 5,
        'acorazado': 4,
        'fragata':3,
        'submarino':3,
        'botepatrulla':2
        }

class Room(models.Model):
    name = models.CharField(max_length=30)
    map_size = models.IntegerField()
    aircraft_carrier = models.IntegerField(default=1)
    battleship = models.IntegerField(default=1)
    frigate = models.IntegerField(default=1)
    submarine = models.IntegerField(default=1)
    patrol_boat = models.IntegerField(default=1)
    start = models.BooleanField(default=False)
    winner = models.IntegerField(default=0)
    admin = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('waiting-room-view', args=[self.id,])

    def get_map_size(self):
        """ Return the map size of room """
        return self.map_size

    def get_amount_aircraft_carrier(self):
        return self.aircraft_carrier

    def get_amount_battleship(self):
        return self.battleship

    def get_amount_frigate(self):
        return self.frigate

    def get_amount_submarine(self):
        return self.submarine

    def get_amount_patrol_boat(self):
        return self.patrol_boat

    def there_is_a_winner(self):
        try:
            Player.objects.get(id=self.winner, room=self)
            return True
        except Player.DoesNotExist:
            return False

    def get_winner(self):
        try:
            player = Player.objects.get(id=self.winner, room=self)
            return player
        except Player.DoesNotExist:
            return None

    def get_admin(self):
        """ Return the user admin """
        try:
            user = User.objects.get(id=self.admin)
            return user
        except User.DoesNotExist:
            return None

    def set_admin(self, user):
        """ Save the id of the user admin """
        self.admin = user.id
        self.save()

    def get_start_game(self):
        """ Return True if the game is running """
        return self.start

    def set_start_game(self, value=False):
        """ Set the start game with the value
        Params:
            value -> Should be True o False
        """
        self.start = value
        self.save()

    def start_game(self):
        """ Gives turn players and decide the first player """
        state, msg = self.check_state()
        if state:
            self.set_start_game(True)
            players = Player.objects.filter(room=self)
            amount_players = len(players)
            turns = [i for i in range(1, amount_players+1)]
            for player in players:
                player.set_number_turn(turns.pop(0))
                player.set_on_game(True)
            first_player = Player.objects.get(room=self, number_turn=1)
            first_player.set_turn(True)
            first_player.set_offensive(True)
            first_player.set_defense(True)

    def check_state(self):
        """ Verify that everything is correct for start the game """
        players = Player.objects.filter(room=self)
        amount_players = len(players)
        if amount_players < 2:
            msg = "Falta al menos un contricante"
            return (False, msg)
        for player in players:
            if not player.ready:
                msg = "Algunos jugadores no estan listos"
                return (False, msg)
        if self.get_start_game():
            return (False, "El juego ya empezo")
        return (True, '')

    def get_table_from_user(self, user):
        """ Return the table of user or None if the user not has a player
        in the Room.
        Params:
            user -> User instance
        """
        try:
            player = Player.objects.get(user=user, room=self)
            table = Table.objects.get(player=player, victim=0)
        except Player.DoesNotExist:
            return None
        return table

    def get_player_from_user(self, user):
        """ Return the player of user in the room or None if the user not has
        a player in the Room.
        Params:
            user -> User instance
        """
        try:
            player = Player.objects.get(user=user, room=self)
            return player
        except Player.DoesNotExist:
            return None

    def get_len_players(self):
        """ Return the number of players """
        return len(Player.objects.filter(room=self))

    def end_shift(self):
        """ A player's turn finishes """
        player = Player.objects.get(room=self, turn=True)
        n = self.get_len_players()
        turn = (player.number_turn % n) + 1
        next_player = Player.objects.get(room=self, turn=False,
                number_turn=turn)
        player.set_turn(False)
        player.set_attack(False)
        player.set_defense(False)

        next_player.set_turn(True)
        next_player.set_attack(True)
        next_player.set_defense(True)

    def attack(self, pos, player, victim):
        """ Attacks a victim specific
        Params:
            pos -> is a tuple (row, column)
            player -> Player instance. The player who attacks
            victim -> Id of victim player
        """
        victim_player = Player.objects.get(id=victim)
        table_victim = Table.objects.get(player=victim_player, victim=0)
        table_player = Table.objects.get(player=player, victim=victim)
        row, col = pos
        tv = table_victim.get_table()
        ocupado = table_victim.get_ocupado()

        boat = Boat.objects.get(table=table_player)
        if tv[row][col] in ocupado:
            b = table_victim.get_boat_from_coord(row, col)
            cv = Cell.objects.get(boat=b, row=row, column=col)
            cv.set_value('T')
            c = Cell.objects.get_or_create(boat=boat, row=row, column=col)[0]
            c.set_value('T')
        else:
            c = Cell.objects.get_or_create(boat=boat, row=row, column=col)[0]
            c.set_value('X')


class Player(models.Model):
    user = models.ForeignKey(User)
    room = models.ForeignKey(Room)
    name = models.CharField(max_length=20)
    on_game = models.BooleanField(default=False)
    number_turn = models.IntegerField(default=0)
    turn = models.BooleanField(default=False)
    ready = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    offensive = models.BooleanField(default=False)
    defense = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def set_offensive(self, value):
        """ Sets offensive attack to value
        Params:
            value -> Should be True o False
        """
        self.offensive = value
        self.save()

    def set_defense(self, value):
        """ Sets defence attack to value
        Params:
            value -> Should be True o False
        """
        self.defense = value
        self.save()

    def is_ready(self):
        return self.ready

    def set_ready(self, value):
        """ Sets the state ready of player to value
        Params:
            value -> Should be True o False
        """
        self.ready = value
        self.save()

    def is_admin(self):
        return self.admin

    def set_admin(self, value):
        """ Sets player admin to value
        Params:
            value -> Should be True o False
        """
        self.admin = value
        self.save()

    def set_number_turn(self, value):
        """ Sets turn number to player
        Params:
            value -> Integer greater than 0
        """
        self.number_turn = value
        self.save()

    def set_on_game(self, value):
        """ Puts to the player on game if value is True
        Params:
            value -> Should be True o False
        """
        self.on_game = value
        self.save()

    def set_turn(self, value):
        """ Gives turn the player if value is True
        Params:
            value -> Should be True o False
        """
        self.turn = value
        self.save()

    def get_or_create_victim_table(self, victim):
        """ Return a table of the victim
        Params:
            victim -> Id of victim's table
        """
        try:
            t = Table.objects.get(player=self, victim=victim)
        except Table.DoesNotExist:
            t = Table.objects.create(player=self, victim=victim)
            Boat.objects.create(table=t, name='bote_aux')
        return t


class Table(models.Model):
    player = models.ForeignKey(Player)
    victim = models.IntegerField(default=0)

    AGUA = 0
    # P: Portaaviones, A: Acorazado, F: Fragata,
    # S: submarino, B: botepatrulla
    OCUPADO = ['P', 'A', 'F', 'S', 'B']

    def __str__(self):
        size = self.get_map_size()
        return self.player.__str__() + '%d x %d' % (size, size)

    def get_absolute_url(self):
        room = Room.objects.get(id=self.player.room.id)
        data = {'room': room.id, 'table': self.id}
        return reverse('my-table-view', kwargs=data)

    def get_map_size(self):
        room = Room.objects.get(id=self.player.room.id)
        return room.map_size

    def get_ocupado(self):
        ret = self.OCUPADO.copy()
        return ret

    def get_boat_from_coord(self, row, col):
        """ Return the boat from the coordinates (row, column)
        Params:
            row -> Positive integer
            col -> Positive integer
        """
        boats = Boat.objects.filter(table=self)
        for boat in boats:
            cells = boat.get_boat()
            for r, c, v in cells:
                if r == row and c == col:
                    return boat

    def add_boat_available(self):
        """ Check if it's possible to add more boat """
        res = self.add_aircraft_carrier_available() or \
                self.add_battleship_available() or \
                self.add_frigate_available() or \
                self.add_submarine_available() or \
                self.add_patrol_boat_available()
        return res

    def add_aircraft_carrier_available(self):
        """ Check if it's possible to add more aircraft carrier """
        room = Room.objects.get(id=self.player.room.id)
        aircraft_carriers = Boat.objects.filter(table=self,
                name='portaaviones')
        return len(aircraft_carriers) < room.get_amount_aircraft_carrier()

    def add_battleship_available(self):
        """ Check if it's possible to add more battleship """
        room = Room.objects.get(id=self.player.room.id)
        battleships = Boat.objects.filter(table=self, name='acorazado')
        return len(battleships) < room.get_amount_battleship()

    def add_frigate_available(self):
        """ Check if it's possible to add more frigate """
        room = Room.objects.get(id=self.player.room.id)
        frigates = Boat.objects.filter(table=self, name='fragata')
        return len(frigates) < room.get_amount_frigate()

    def add_submarine_available(self):
        """ Check if it's possible to add more submarine """
        room = Room.objects.get(id=self.player.room.id)
        submarines = Boat.objects.filter(table=self, name='submarino')
        return len(submarines) < room.get_amount_submarine()

    def add_patrol_boat_available(self):
        """ Check if it's possible to add more patrol boat """
        room = Room.objects.get(id=self.player.room.id)
        patrol_boats = Boat.objects.filter(table=self, name='botepatrulla')
        return len(patrol_boats) < room.get_amount_patrol_boat()

    def set_boat(self, pos, orientation, boat_type):
        """ Puts a boat type in the coordinates (row, column) with some
        orientation
        Params:
            pos -> (row, column) Positive integer
            orientation -> 'H' Horizontal or 'V' Vertical
            boat_type -> String It can be portaaviones, acorazado,
                         fragata, submarino or botepatrulla
        """
        if self.position_is_valid(pos, orientation, boat_type) and \
                self.add_boat_available():
            row, col = pos
            boat_size = BOAT_SIZE[boat_type.lower()]
            v = boat_type.capitalize()[0]
            if orientation.upper() == 'H':
                boat = Boat.objects.create(table=self, name=boat_type.lower())
                for j in range(boat_size):
                    Cell.objects.create(boat=boat, column=col, row=row,
                            value=v)
                    col += 1
            if orientation.upper() == 'V':
                boat = Boat.objects.create(table=self, name=boat_type.lower())
                for i in range(boat_size):
                    Cell.objects.create(boat=boat, column=col, row=row,
                            value=v)
                    row += 1

    def position_is_valid(self, pos, orientation, boat_type):
        """ Check if it position is correct
        Params:
            pos -> (row, column) Positive integer
            orientation -> 'H' Horizontal or 'V' Vertical
            boat_type -> String It can be portaaviones, acorazado,
                         fragata, submarino or botepatrulla
        """
        try:
            row, col = pos
            boat_size = BOAT_SIZE[boat_type.lower()]
            table = self.get_table(extended=True)
            map_size = self.get_map_size()
            row_valid = row >= 0 and row < map_size
            column_valid = col >= 0 and col < map_size
            if not row_valid or not column_valid:
                return False
            if orientation.upper() == 'H':
                if col+boat_size-1 >= map_size:
                    return False
                for i in range(row, row+2):
                    for j in range(col, col+boat_size+1):
                        if table[i][j] in self.OCUPADO:
                            return False
            elif orientation.upper() == 'V':
                if row+boat_size-1 >= map_size:
                    return False
                for i in range(row, row+boat_size+1):
                    for j in range(col, col+2):
                        if table[i][j] in self.OCUPADO:
                            return False
            else:
                return False
            return True
        except (TypeError, KeyError):
            print('Posicion invalida o no existe ese tipo de barco')
            return False

    def get_table(self, extended=False, enumerated=False):
        """ Return a matrix NxN where N is the map size or N+1xN+1 if
        extended is True and with numbers coordinate if enumerated is True
        Params:
            extended -> True o False A table of N+1xN+1 if it is True
            enumerated -> True o False A table with number of rows and columns
                          if it is True
        """
        table_size = self.get_map_size()
        if extended:
            table_size += 1
        table = []
        for i in range(0, table_size):
            row = []
            for j in range(0, table_size):
                row.append(self.AGUA)
            table.append(row)
        boats = Boat.objects.filter(table=self)
        for boat in boats:
            cells = boat.get_boat()
            for row, col, value in cells:
                if extended:
                    table[row+1][col+1] = value
                else:
                    table[row][col] = value
        if enumerated:
            row = [str(j) for j in range(1, table_size+1)]
            table.insert(0, row)
            n = 0
            for r in table:
                r.insert(0, str(n))
                n += 1
            table[0][0] = ''
        return table


class Boat(models.Model):
    table = models.ForeignKey(Table)
    name = models.CharField(max_length=20)

    def __str__(self):
        return str(self.table.id) + '-' + self.name

    def get_boat(self):
        """ Return a list of cells of boat """
        cells = Cell.objects.filter(boat=self)
        res = [(cell.row, cell.column, cell.value) for cell in cells]
        return res

class Cell(models.Model):
    boat = models.ForeignKey(Boat)
    column = models.IntegerField()
    row = models.IntegerField()
    value = models.CharField(max_length=2, default="")

    def __str__(self):
        return "(%s, %d, %s)" % (self.row, self.column, self.value)

    def set_value(self, value):
        self.value = value
        self.save()
