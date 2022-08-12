from spell import spell_lookup, capital
from pickle import load, dump
import pathlib
from os import path, listdir, mkdir
STATS = ["Strength", "Dexterity", "Constitution",
         "Intelligence", "Wisdom", "Charisma"]
stats_abbr = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
SKILLS = {"Acrobatics": "Dexterity", "Animal Handling": "Wisdom", "Arcana": "Intelligence", "Athletics": "Strength", "Deception": "Charisma", "History": "Intelligence", "Insight": "Wisdom", "Intimidation": "Charisma", "Investigation": "Intelligence",
          "Medicine": "Wisdom", "Nature": "Intelligence", "Perception": "Wisdom", "Performance": "Charisma", "Persuasion": "Charisma", "Religion": "Intelligence", "Sleight of Hand": "Dexterity", "Stealth": "Dexterity", "Survival": "Wisdom"}
PATH = str(pathlib.Path().resolve())
if not path.isdir('characters'):
    mkdir("characters")


def can_afford(a, b):
    if 100*a[0] + 10*a[1] + a[2] >= 100*b[0] + 10*b[1] + b[2]:
        return True
    return False


def cload(name):
    file = open(
        f'{PATH}/characters/{name.lower().replace(" ", "-")}.chr', "rb")
    return load(file)


def ver_int(prompt):
    a = True
    while a:
        try:
            num = int(input(prompt))
            a = False
        except:
            print("Integers only")
    return num


def menu(options, prompt):
    if len(options) == 0:
        return 'No Options'
    for x in range(len(options)):
        print(f'{x+1}: {options[x]}')
    choice = True
    while choice:
        dec = input(prompt)
        try:
            dec = int(dec)
            if dec in list(range(1, len(options)+1)):
                return options[dec-1]
        except:
            pass
        print("Pick an option\n")


class Character():
    def __init__(self, name, level, stats, ac, prof, money, hp, spellcaster, spellslots, saves, profs):
        self.name = name.lower().replace(" ", "-")
        self.level = level
        self.stats = stats
        self.ac = ac
        self.prof = prof
        self.money = money
        self.inventory = []
        self.hp = hp
        self.max_hp = hp

        self.temp_hp = 0
        if len(spellslots) < 9:
            spellslots += [0 for i in range(9-len(spellslots))]
        self.spellslots = [int(x) for x in spellslots]
        self.max_spellslots = [x for x in self.spellslots]
        self.spellcaster = spellcaster
        self.skill_profs = profs
        self.save_profs = saves
        self.spells = []
        self.abilities = []

        self.sort_options = [1, 0]
        self.keep_logs = True

    def add_money(self, money):
        self.money = [money[ii]+self.money[ii] for ii in range(3)]

    def pay(self, money):
        if can_afford(self.money, money):
            self.money = [self.money[ii]-money[ii] for ii in range(3)]
            if sum([x < 0 for x in self.money]) != 0:
                self.level_money()
            return 1
        else:
            print("\nInsufficient Funds\n")
            return -1

    def cast(self, spellname):
        spell = spell_lookup(spellname)
        if type(spell) == type("eeee"):
            print(spell)
            return -2
        if spell.level == "cantrip":
            print(spell)
            return 1
        elif self.spellslots[int(spell.level)-1] >= 1:
            print(spell)
            if input("Cast Spell?\n>> ").lower() in ["y", "yes"]:
                self.spellslots[int(spell.level)-1] -= 1
                print(
                    f"\nYou have {self.spellslots[int(spell.level)-1]} slots at level {spell.level} remaining")
                return 1
            else:
                print("Spell not cast")
                return -1
        else:
            print(spell)
            print(
                f"\n You do not have enough level {spell.level} spellslots remaining")
            return -1

    def save(self):
        file = open(f"{PATH}/characters/{self.name}.chr", "wb")
        dump(self, file)
        file.close()

    def gp_to_sp(self):
        if self.money[0] < 1:
            return -1
        self.money[0] -= 1
        self.money[1] += 10
        return 1

    def sp_to_bp(self):
        if self.money[1] < 1:
            a = self.gp_to_sp()
            if a == -1:
                return -1
        self.money[1] -= 1
        self.money[2] += 10

    def level_money(self):

        while self.money[0] > 0:
            self.gp_to_sp()
        while self.money[1] > 0:
            self.sp_to_bp()

        for ii in range(2):
            if self.money[2-ii] >= 10:
                start = self.money[2-ii]
                self.money[2-ii] -= 10 * (start // 10)
                self.money[1-ii] += 1 * (start // 10)

    def hit(self, points):
        new_health = self.hp + self.temp_hp - points
        if new_health <= -self.max_hp:
            print(f"Permanently dead at {new_health} hp")
        elif new_health <= 0:
            print(f"Unconscious at {new_health}")
        if self.temp_hp != 0:
            diff = self.temp_hp - points
            if diff < 0:
                self.temp_hp = 0
                points = -1 * diff
            else:
                self.temp_hp = diff
                return
        self.hp -= points

    def heal(self, points):
        if self.hp + points >= self.max_hp:
            self.hp = self.max_hp
        else:
            self.hp += points

    def temp_hp_add(self, points):
        if points > self.temp_hp:
            self.temp_hp = points

    def __str__(self):
        string_ = ''
        br = '\n'
        string_ += f"\nName: {capital(self.name.replace('-', ' '))} (Level {self.level})\n\n"
        string_ += f"AC: {self.ac}\nInitiative: {self.check('Stealth')[0]}\nPassive Perception: {10+self.check('Perception')[0]}\n\n"
        for x in range(6):
            string_ += f'{stats_abbr[x]} : {self.stats[x]} ('
            mod = int((self.stats[x]/2))-5
            if mod >= 0:
                string_ += '+'
            string_ += f'{mod})\n'
        string_ += '\n\n'
        string_ += f"Money: {self.money[0]}GP {self.money[1]}SP {self.money[2]}CP\n"
        if self.temp_hp != 0:
            string_ += f"Health: {self.hp}+{self.temp_hp} points\n\n\n"
        else:
            string_ += f"Health: {self.hp} points\n\n\n"
        if self.spellcaster:
            string_ += f"Spellslots\n\nLevel   Slots (max)\n{br.join(['  '+str(ii+1).ljust(8)+ str(self.spellslots[ii]).ljust(3) + '  (' + str(self.max_spellslots[ii]) + ')' for ii in range(9) if self.max_spellslots[ii]!=0])}"
        if len(self.abilities) != 0:
            string_ += "\n\n\nAbilities\n\n"
            for x in self.abilities:
                if x.increment == -1:
                    string_ += f'{x.name} : {x.counter} uses remaining\n'
                else:
                    string_ += f'{x.name} : Counter at {x.counter}\n'
        if len(self.inventory) != 0:
            string_ += "\n\nInventory\n\n"
            for x in self.inventory:
                string_ += f'{x.quantity} x {x.name}\n'
        return string_

    def check(self, skill):
        stat_used = SKILLS[skill]
        mystat = self.stats[STATS.index(stat_used)]
        return int((mystat/2))-5, self.prof * self.skill_profs[list(SKILLS.keys()).index(skill)]

    def skill_save(self, save):
        mystat = self.stats[STATS.index(save)]
        return int((mystat/2))-5, self.prof * self.save_profs[STATS.index(save)]


class Ability():
    def __init__(self, name, desc, start, increment, rest_condition) -> None:
        self.name = name
        self.desc = desc
        self.start = start
        self.counter = start
        self.increment = increment
        self.reset_condition = rest_condition  # s l c (short long custom)

    def use(self):
        self.counter += self.increment

    def reset(self):
        self.counter = self.start

    def set_custom(self, val):
        self.counter = val

    def change(self, amount):
        self.counter += amount

    def edit(self):
        print("\nLeave blank to keep the same\n")
        name = input("New name\n>> ")
        if name != '':
            self.name = name

        desc = input("New description\n>> ")
        if desc != '':
            self.desc = desc

        start = ver_int("Start Value/Number of uses\n>> ")
        self.start = start
        self.increment = ver_int("Increment (1, -1 etc)\n>> ")
        self.reset_condition = menu(["Short Rest", "Long Rest", "Manually"],
                                    "When does ability uses reset")

    def __str__(self):
        thing = '\n'
        thing += self.name + "\n\n"
        thing += self.desc + "\n\n"
        if self.increment == -1:
            thing += f"{self.counter} uses remaining ({self.start} total)\n\n"
        else:
            thing += f"Counter at {self.counter}\n\n"
        return thing


class Item():
    def __init__(self, name, desc, quantity) -> None:
        self.name = name
        self.desc = desc
        self.quantity = quantity

    def __str__(self):
        string_ = ''
        string_ += f"\n\n{self.quantity} x "+self.name + "\n\n"
        string_ += self.desc + "\n\n"
        return string_
