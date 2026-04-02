"""
pokemon_game.py

A terminal-based Pokemon battle simulator featuring:
- Type-effectiveness damage calculations
- Player and CPU teams with switchable Pokemon
- Items: Potions (healing) and Pokeballs (catching)
- Turn-based combat with random first-turn selection
"""

import random


# ---------------------------------------------------------------------------
# Type Chart
# ---------------------------------------------------------------------------

# Nested dictionary mapping attacking type -> defending type -> damage multiplier.
# 2.0 = super effective, 0.5 = not very effective, 1.0 = neutral.
TYPE_CHART = {
    "fire":     {"grass": 2.0, "water": 0.5, "fire": 1.0, "electric": 1.0, "flying": 1.0, "rock": 0.5, "normal": 1.0},
    "grass":    {"water": 2.0, "fire": 0.5, "grass": 1.0, "electric": 1.0, "flying": 0.5, "rock": 2.0, "normal": 1.0},
    "water":    {"fire": 2.0, "grass": 0.5, "water": 1.0, "electric": 1.0, "flying": 1.0, "rock": 2.0, "normal": 1.0},
    "electric": {"water": 2.0, "flying": 2.0, "grass": 0.5, "electric": 1.0, "fire": 1.0, "rock": 1.0, "normal": 1.0},
    "flying":   {"grass": 2.0, "electric": 0.5, "rock": 0.5, "water": 1.0, "fire": 1.0, "flying": 1.0, "normal": 1.0},
    "rock":     {"flying": 2.0, "fire": 2.0, "grass": 1.0, "electric": 1.0, "water": 1.0, "rock": 1.0, "normal": 1.0},
    "normal":   {"rock": 0.5, "fire": 1.0, "water": 1.0, "grass": 1.0, "electric": 1.0, "flying": 1.0, "normal": 1.0},
}


def type_multiplier(attacking_type, defending_type):
    """
    Return the damage multiplier for an attacking type vs. a defending type.
    Falls back to 1.0 (neutral) if the matchup is not found in TYPE_CHART.
    """
    atk = attacking_type.lower()
    dfn = defending_type.lower()

    if atk in TYPE_CHART and dfn in TYPE_CHART[atk]:
        return TYPE_CHART[atk][dfn]

    return 1.0


# ---------------------------------------------------------------------------
# Move
# ---------------------------------------------------------------------------

class Move:
    """
    Represents a single attack a Pokemon can use in battle.

    Attributes:
        name   (str): Display name of the move (e.g. "Ember").
        mtype  (str): Elemental type of the move (e.g. "fire").
        damage (int): Base damage value before stats and type modifiers.
    """

    def __init__(self, name, mtype, damage):
        self.name   = name
        self.mtype  = mtype
        self.damage = damage


# ---------------------------------------------------------------------------
# Pokemon
# ---------------------------------------------------------------------------

class Pokemon:
    """
    Represents a single Pokemon with stats, HP, and a moveset.

    Attributes:
        name       (str):   Pokemon's name.
        ptype      (str):   Pokemon's elemental type.
        health     (int):   Current HP.
        max_health (int):   Maximum HP.
        attack     (int):   Attack stat used in damage calculations.
        defense    (int):   Defense stat used to reduce incoming damage.
        moves      (list):  List of Move objects (max 4).
    """

    def __init__(self, name, ptype, health, attack, defense):
        self.name       = name
        self.ptype      = ptype
        self.health     = health
        self.max_health = health
        self.attack     = attack
        self.defense    = defense
        self.moves      = []

    def can_be_caught(self, threshold):
        """Return True if this Pokemon's HP is at or below the catch threshold."""
        return self.health <= threshold

    def heal(self, amount):
        """
        Heal this Pokemon by 'amount' HP, capped at max_health.
        Returns False if the Pokemon is fainted (HP == 0); True otherwise.
        """
        if self.health == 0:
            return False

        self.health = min(self.health + amount, self.max_health)
        return True

    def is_fainted(self):
        """Return True if this Pokemon has 0 HP."""
        return self.health == 0

    def add_move(self, move):
        """
        Add a Move to this Pokemon's moveset.
        A Pokemon can hold at most 4 moves.
        Returns True if the move was added, False if the moveset is already full.
        """
        if len(self.moves) >= 4:
            print(f"{self.name} already has 4 moves.")
            return False

        self.moves.append(move)
        return True

    def attack_target(self, target, move):
        """
        Attack 'target' using 'move'.

        Damage formula:
            base   = move.damage + self.attack - target.defense  (min 0)
            total  = round(base * type_multiplier)

        Prints a battle message showing damage dealt and effectiveness.
        """
        base = max(0, (move.damage + self.attack) - target.defense)
        mult = type_multiplier(move.mtype, target.ptype)
        total = int(round(base * mult))

        note = ""
        if mult > 1.0:
            note = " It's super effective!"
        elif mult < 1.0:
            note = " It's not very effective..."

        target.health = max(0, target.health - total)

        print(
            f"{self.name} used {move.name} on {target.name}! "
            f"Damage: {total}.{note} {target.name} HP: {target.health}"
        )


# ---------------------------------------------------------------------------
# Team
# ---------------------------------------------------------------------------

class Team:
    """
    Represents a team of Pokemon.

    Attributes:
        pokemon_list (list): All Pokemon on the team.
        active_index (int):  Index of the currently active Pokemon.
    """

    def __init__(self):
        self.pokemon_list = []
        self.active_index = 0

    def add_pokemon(self, pokemon):
        """
        Add a Pokemon to the team.
        If this is the first Pokemon added, it automatically becomes active.
        """
        self.pokemon_list.append(pokemon)
        if len(self.pokemon_list) == 1:
            self.active_index = 0

    def all_fainted(self):
        """Return True if every Pokemon on the team has 0 HP."""
        for pokemon in self.pokemon_list:
            if pokemon.health > 0:
                return False
        return True

    def switch_to(self, index):
        """
        Switch the active Pokemon to the one at 'index'.
        Returns False if the index is out of range or the target Pokemon is fainted.
        """
        if index < 0 or index >= len(self.pokemon_list):
            return False

        if self.pokemon_list[index].health == 0:
            return False

        self.active_index = index
        return True

    def __str__(self):
        """Return a formatted string showing each Pokemon's index, HP, and moves."""
        result = "Team:\n"
        for i, pokemon in enumerate(self.pokemon_list):
            label = "  (Active)  " if i == self.active_index else "  "
            result += f"[{i}]{label}{pokemon.name} - HP: {pokemon.health}/{pokemon.max_health}\n"

            if pokemon.moves:
                move_names = ", ".join(move.name for move in pokemon.moves)
                result += f"            Moves: {move_names}\n"
            else:
                result += "            Moves: (none)\n"

            result += "\n"
        return result


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------

class Item:
    """
    Base class for all in-battle items.

    Attributes:
        name     (str): Item name.
        quantity (int): How many of this item remain.
    """

    def __init__(self, itemName, quantity):
        self.name     = itemName
        self.quantity = quantity

    def is_available(self):
        """Return True if at least one of this item is available."""
        return self.quantity > 0


class Potion(Item):
    """
    A healing item that restores HP to a Pokemon.

    Attributes:
        heal_amount (int): HP restored per use.
    """

    def __init__(self, name, quantity, heal_amount):
        super().__init__(name, quantity)
        self.heal_amount = heal_amount

    def use(self, pokemon):
        """
        Use this potion on 'pokemon'.
        Raises Exception if no potions remain or the Pokemon is fainted.
        Returns True on success.
        """
        if not self.is_available():
            raise Exception("No potions left!")

        if pokemon.is_fainted():
            raise Exception("Cannot heal a fainted Pokemon.")

        pokemon.heal(self.heal_amount)
        self.quantity -= 1
        return True

    def __str__(self):
        return f"{self.name} (heals {self.heal_amount} HP) - Quantity: {self.quantity}"


class Pokeball(Item):
    """
    An item used to catch wild or enemy Pokemon.

    Attributes:
        catch_threshold (int): Maximum HP a Pokemon can have to be catchable.
    """

    def __init__(self, name, quantity, catch_threshold):
        super().__init__(name, quantity)
        self.catch_threshold = catch_threshold

    def use(self, pokemon, team):
        """
        Attempt to catch 'pokemon' and add it to 'team'.
        Raises Exception if no balls remain, the Pokemon is fainted, or its HP is too high.
        Returns True on a successful catch.
        """
        if not self.is_available():
            raise Exception("No Pokeballs left!")

        if pokemon.is_fainted():
            raise Exception("Cannot catch a fainted Pokemon.")

        if not pokemon.can_be_caught(self.catch_threshold):
            raise Exception("The Pokemon broke free! Its HP is too high to catch.")

        team.add_pokemon(pokemon)
        self.quantity -= 1
        return True

    def __str__(self):
        return f"{self.name} - Quantity: {self.quantity}, Catch threshold: {self.catch_threshold} HP"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def choose_user_move(pokemon):
    """
    Prompt the player to select one of 'pokemon's moves.
    Loops until a valid choice is entered. Returns the chosen Move object.
    """
    print(f"\nChoose a move for {pokemon.name}:")
    for i, mv in enumerate(pokemon.moves, start=1):
        print(f"  {i}) {mv.name} ({mv.mtype}) dmg:{mv.damage}")

    while True:
        choice = input("Enter number: ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(pokemon.moves):
                return pokemon.moves[idx]
        print("Invalid choice, try again.")


def choose_cpu_move(pokemon):
    """Return a randomly selected move from 'pokemon's moveset."""
    return random.choice(pokemon.moves)


# ---------------------------------------------------------------------------
# Battle loop
# ---------------------------------------------------------------------------

def battle(p1, p2, my_team, cpu_team):
    """
    Run the main battle loop between the player and the CPU.

    Parameters:
        p1       (Pokemon): Player's starting active Pokemon.
        p2       (Pokemon): CPU's starting active Pokemon.
        my_team  (Team):    Player's full team.
        cpu_team (Team):    CPU's full team.

    The battle ends when all Pokemon on one side have fainted (or been caught).
    """
    print("\n===== BATTLE START =====")
    print(f"{p1.name} vs {p2.name}")

    user_turn = random.choice([True, False])
    round_num = 1

    while not my_team.all_fainted() and not cpu_team.all_fainted():
        print(f"\nRound {round_num}!")

        # --- Player's turn ---
        if user_turn:
            while True:
                try:
                    action_choice = int(input("Please pick 1(Move), 2(Potion), 3(Pokeball): ").strip())
                    if action_choice in (1, 2, 3):
                        break
                    else:
                        print("Please enter 1, 2, or 3.")
                except ValueError:
                    print("Please enter a number: 1, 2, or 3.")

            # Option 1: Attack
            if action_choice == 1:
                mv = choose_user_move(p1)
                p1.attack_target(p2, mv)

                if p2.health == 0:
                    print(f"{p2.name} fainted!")

                    if cpu_team.all_fainted():
                        print("All enemy Pokemon fainted! You win!")
                        break
                    else:
                        alive = [i for i, poke in enumerate(cpu_team.pokemon_list) if poke.health > 0]
                        new_index = random.choice(alive)
                        cpu_team.active_index = new_index
                        p2 = cpu_team.pokemon_list[new_index]
                        print(f"CPU sends out {p2.name}!")

            # Option 2: Use a Potion
            elif action_choice == 2:
                try:
                    super_potion.use(p1)
                    print("You used a potion!")
                except Exception as e:
                    print(e)

            # Option 3: Throw a Pokeball
            elif action_choice == 3:
                try:
                    standard_ball.use(p2, my_team)
                    print("You caught the Pokemon!")

                    if p2 in cpu_team.pokemon_list:
                        cpu_team.pokemon_list.remove(p2)

                    if len(cpu_team.pokemon_list) == 0 or cpu_team.all_fainted():
                        print("All enemy Pokemon are gone! You win!")
                        break
                    else:
                        alive_indexes = [
                            i for i, poke in enumerate(cpu_team.pokemon_list)
                            if poke.health > 0
                        ]
                        if alive_indexes:
                            cpu_team.active_index = random.choice(alive_indexes)
                            p2 = cpu_team.pokemon_list[cpu_team.active_index]
                            print(f"CPU sends out {p2.name}!")
                        else:
                            print("All enemy Pokemon fainted! You win!")
                            break

                except Exception as e:
                    print(e)

        # --- CPU's turn ---
        else:
            mv = choose_cpu_move(p2)
            print(f"\nCPU chooses {mv.name} for {p2.name}...")
            p2.attack_target(p1, mv)

            if p1.health == 0:
                print(f"{p1.name} fainted!")

                if my_team.all_fainted():
                    print("All your Pokemon fainted! You lose!")
                    break
                else:
                    print(my_team)
                    while True:
                        try:
                            index = int(input("Pick a Pokemon by index: "))
                            if my_team.switch_to(index):
                                p1 = my_team.pokemon_list[my_team.active_index]
                                print(f"You sent out {p1.name}!")
                                break
                            else:
                                print("That Pokemon is unavailable. Try again.")
                        except ValueError:
                            print("Please enter a valid number (e.g. 0, 1, or 2).")

        user_turn = not user_turn
        round_num += 1


# ---------------------------------------------------------------------------
# Game setup
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    # --- Define Moves ---
    ember         = Move("Ember",         "fire",     20)
    scratch       = Move("Scratch",       "normal",   10)
    water_gun     = Move("Water Gun",     "water",    20)
    thunder_shock = Move("Thunder Shock", "electric", 20)
    quick_attack  = Move("Quick Attack",  "normal",   15)
    vine_whip     = Move("Vine Whip",     "grass",    20)
    tackle        = Move("Tackle",        "normal",   10)
    rock_throw    = Move("Rock Throw",    "rock",     20)
    gust          = Move("Gust",          "flying",   20)

    # --- Define Pokemon ---
    charmander = Pokemon("Charmander", "fire",     39, 52, 43)
    charmander.add_move(ember)
    charmander.add_move(scratch)

    squirtle = Pokemon("Squirtle", "water", 44, 48, 65)
    squirtle.add_move(water_gun)
    squirtle.add_move(scratch)

    pikachu = Pokemon("Pikachu", "electric", 35, 50, 40)
    pikachu.add_move(thunder_shock)
    pikachu.add_move(quick_attack)

    bulbasaur = Pokemon("Bulbasaur", "grass", 45, 49, 49)
    bulbasaur.add_move(vine_whip)
    bulbasaur.add_move(tackle)

    geodude = Pokemon("Geodude", "rock", 40, 45, 50)
    geodude.add_move(rock_throw)
    geodude.add_move(tackle)

    pidgey = Pokemon("Pidgey", "flying", 40, 45, 40)
    pidgey.add_move(gust)
    pidgey.add_move(tackle)

    # --- Define Items ---
    super_potion  = Potion("Crazy Juice", 2, 30)   # heals 30 HP, 2 uses
    standard_ball = Pokeball("Pokeball",  3, 35)   # catches at ≤35 HP, 3 uses

    # --- Build Teams ---
    my_team = Team()
    my_team.add_pokemon(pikachu)
    my_team.add_pokemon(geodude)
    my_team.add_pokemon(charmander)

    cpu_team = Team()
    cpu_team.add_pokemon(pidgey)
    cpu_team.add_pokemon(squirtle)
    cpu_team.add_pokemon(bulbasaur)

    # --- Team Preview ---
    print("Player Team:")
    print(my_team)
    print("CPU Team:")
    print(cpu_team)

    # --- Start Battle ---
    player_active = my_team.pokemon_list[my_team.active_index]
    cpu_active    = cpu_team.pokemon_list[cpu_team.active_index]
    battle(player_active, cpu_active, my_team, cpu_team)
