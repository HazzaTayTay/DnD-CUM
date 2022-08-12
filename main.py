from character import Character, Ability, Item, cload, ver_int, menu, STATS, SKILLS
from spell import *
from consolemenu import *
from consolemenu.items import *
from datetime import datetime
from time import time
import pathlib
from os import listdir
from pickle import dump, load
PATH = str(pathlib.Path().resolve())


def log(char, desc):
    if char.keep_logs:
        try:
            file = open("log.txt", "r")
            logs = file.readlines()
        except:
            file = open("log.txt", "w")
            logs = []
        file.close()
        logs.append(f'{datetime.now()} {char.name} {desc}\n')
        file = open("log.txt", "w")
        file.writelines(logs)
        file.close()


def stats(char):
    print(char)
    input("\nPress Enter to continue\n")


def spell_sorter(char, spell_list):
    '''
    input: list of spells
    output: sorted list by option
    0 - order added
    1 - spell level
    2 - alphabetical order
    '''
    sort_option = char.sort_options[0]
    spell_list = [spell_lookup(x) for x in spell_list]
    if sort_option == 0:
        return [x.name for x in spell_list]
    elif sort_option == 1:
        def key(x):
            return 0 if x.level == "cantrip" else int(x.level)
        return [x.name for x in sorted(spell_list, key=key)]
    elif sort_option == 2:
        return [x.name for x in sorted(spell_list, key=lambda x: x.name)]


def inv_sorter(char, inv):
    sort_option = char.sort_options[1]
    if sort_option == 0:
        return inv
    elif sort_option == 1:
        return list(sorted(inv, key=lambda x: x.quantity, reverse=True))
    elif sort_option == 2:
        return list(sorted(inv, key=lambda x: x.name))


def create_character():
    # self, name, stats, prof, money, hp, spellcaster, spellslots, saves, profs
    name = input("Name \n>> ")
    level = ver_int("Level \n>> ")
    print("\nFor the following, the raw stat is required (13 rather than +1)\n")

    stats = [ver_int(x+" > ") for x in STATS]

    ac = ver_int("Armour Class\n>> ")
    prof = ver_int("Proficiency modifier\n>> ")

    a = True
    while a:
        try:
            money = [int(x) for x in input(
                "Money (gp, sp, cp)\n>> ").replace(" ", "").split(",")]
            if len(money) == 3:
                a = False
            else:
                print("Integers only, seperated by commas")
        except:
            print("Integers only, seperated by commas")

    hp = ver_int("Max HP\n>> ")
    spellslots = []
    spellcaster = input(
        "Spellcaster (y/n)\n>> ").lower() in ["yes", "y", "true"]
    if spellcaster:
        for x in range(9):
            num = ver_int(f"Level {x+1} spellslots > ")
            if num == 0:
                break
            spellslots.append(num)

    print("Skill Proficiencies (y/n/dp)\n")
    skill_profs = []
    for ii in SKILLS.keys():
        ans = input(f'{ii} >> ').lower()
        if ans in ("y", "yes", "1"):
            skill_profs.append(1)
        elif ans in ("dp", "2"):
            skill_profs.append(2)
        else:
            skill_profs.append(0)

    print("Saving Throw Proficiencies (y/n/dp)\n")
    saving_profs = []
    for ii in STATS:
        ans = input(f'{ii} >> ')
        if ans in ("y", "yes", "1"):
            saving_profs.append(1)
        elif ans in ("dp", "2"):
            saving_profs.append(2)
        else:
            saving_profs.append(0)

    return Character(name, level, stats, ac, prof, money, hp, spellcaster, spellslots, saving_profs, skill_profs)


# Character selection
def select_character():
    characters = listdir(PATH+'\\characters\\')
    if len(characters) == 0:
        char = create_character()
        char.save()
    else:
        choice = menu([x[:-4].capitalize() for x in characters] +
                      ["New Character"], "Pick a character > ")
        if choice == "New Character":
            char = create_character()
        else:
            char = cload(choice)
    return char


def checkmenu(char):
    '''results
    -1: Check not found
    1: Check completed
    '''
    checked = input("Which skill/save? > ")
    if checked.lower() == "sleight of hand":
        checked2 = "Sleight of Hand"
    else:
        checked2 = checked.strip().capitalize()
    if checked2 in STATS:
        check = 0
        mod, prof = char.skill_save(checked2)
        print(f"Saving throw {checked2}: {mod} + {prof} = {mod+prof}\n")
        input("Press enter to continue\n")
        result = 1
    elif checked2 in SKILLS.keys():
        mod, prof = char.check(checked2)
        print(f"Skill check {checked2}: {mod} + {prof} = {mod+prof}\n")
        input("Press enter to continue\n")
        result = 1
    else:
        print("Check not found")
        result = -1
    log(char, f"check {result}")


char = select_character()
####################################################################
#                                                                  #
#                           Spell Menus                            #
#                                                                  #
####################################################################


def spell_usespell(char):
    print("")
    spellchoice = menu(spell_sorter(char, char.spells) +
                       ["Other"], "\nPick a spell\n>> ")
    if spellchoice == "Other":
        result = char.cast(input("Input spell name\n>> "))
    else:
        result = char.cast(spellchoice)
    log(char, f"spell cast {result}")
    char.save()
    input("Press enter to continue\n")


def spell_searchspell(char):
    result = spell_lookup(input("\nSpell name\n>> "))
    print(result)
    try:
        log(char, f"spell search {result.name}")
    except:
        log(char, f"spell search {result}".replace("\n", ''))
    input("Press enter to continue\n")


def spell_addspell(char):
    spellchoice = spell_lookup(
        input("\nEnter spell name\n>> "))
    if type(spellchoice) == type("Hello"):
        result = -2
    else:
        print(spellchoice)
        yesorno = input("\nAdd spell to library? \n>> ").lower()
        if yesorno in ["yes", "y"]:
            char.spells.append(spellchoice.name)
            result = 1
        else:
            result = -1
    log(char, f"Add spell {result}")
    char.save()


def spell_editlib(char):
    print()
    choice2 = menu(spell_sorter(char, char.spells)+["Back"],
                   "\nPick spell to remove from the spell list\n>> ")
    if choice2 == "Back":
        log(char, f"Edit library -1")
    else:
        char.spells.remove(choice2)
        log(char, f"Edit library 1 {choice2}")
    char.save()


def spell_resetslots(char):
    char.spellslots = [x for x in char.max_spellslots]
    char.save()
    log(char, f"Replenished spell slots")


def spell_viewslots(char):
    for x in range(1, 10):
        print(f"{x} ({char.max_spellslots[x-1]}) : {char.spellslots[x-1]}")
    input("\nPress enter to continue\n")


def spell_create(char):
    print("To create new spell follow the format or examples found in homebrew spell upload")
    name = input("Spellname\n>> ")
    spell = Spell(name, False)
    spell.save()
    print(spell)
    input("Press enter to continue\n")


def spell_download(char):
    answer = input(
        "Are you sure you want to redownload all spells? It may take 3m (more dependant on wifi strength)\n>> ").lower() in ["y", "yes"]
    if answer:
        start = time()
        download_all()
        duration = time() - start
        log(char, f"Downloaded all spells in {duration}s")
        input("Press enter to continue\n")


spell_menu = ConsoleMenu("Spell Menu", clear_screen=True)
spelloptions = ["Use Spell", "Spell Search", "Add Spell to Library",
                "Edit Library", "Replenish Spell Slots", "View Spell Slots", "Create new homebrew spell", "Download all spells"]
spellfunctions = [spell_usespell, spell_searchspell,
                  spell_addspell, spell_editlib, spell_resetslots, spell_viewslots, spell_create, spell_download
                  ]
[spell_menu.append_item(FunctionItem(x, y, [char]))
 for x, y in zip(spelloptions, spellfunctions)]


####################################################################
#                                                                  #
#                          Health Menu                             #
#                                                                  #
####################################################################

def hp_add(char):
    points = ver_int("Health gained\n>> ")
    char.heal(points)
    print(f"Now on {char.hp} + ({char.temp_hp}) hitpoints")
    char.save()
    log(char, f"Gained {points} hp")
    input("Press enter to continue\n")


def hp_tempadd(char):
    points = ver_int("Temporary hp given\n>> ")
    char.temp_hp_add(points)
    print(f"Now on {char.hp} + ({char.temp_hp}) hitpoints")
    char.save()
    log(char, f"Gained {points} temp hp")
    input("Press enter to continue\n")


def hp_hit(char):
    points = ver_int("Points of damage\n>> ")
    char.hit(points)
    print(f"Now on {char.hp} + ({char.temp_hp}) hitpoints")
    char.save()
    log(char, f"Hit for {points} hp")
    input("Press enter to continue\n")


hp_menu = ConsoleMenu("Health Menu")
hpoptions = ["Heal", "Take Damage", "Add Temporary Hit Points"]
hpfunctions = [hp_add, hp_hit, hp_tempadd]
[hp_menu.append_item(FunctionItem(x, y, [char]))
 for x, y in zip(hpoptions, hpfunctions)]


####################################################################
#                                                                  #
#                           Money Menus                            #
#                                                                  #
####################################################################

def money_add(char):
    money_gained = [ver_int(f"\n{x} pieces\n>> ")
                    for x in ["gold", "silver", "copper"]]
    char.add_money(money_gained)
    print(f"Now on {char.money[0]}gp {char.money[1]}sp {char.money[2]}bp")
    char.save()
    log(char, f"Gained {money_gained} money")
    input("Press enter to continue\n")


def money_spend(char):
    money_spent = [ver_int(f"\n{x} pieces\n>> ")
                   for x in ["gold", "silver", "copper"]]
    result = char.pay(money_spent)
    print(f"Now on {char.money[0]}gp {char.money[1]}sp {char.money[2]}bp")
    char.save()
    log(char, f"Spent {money_spent} money {result}")
    input("Press enter to continue\n")


def money_edit(char):
    print("Enter new total money\n")
    money_spent = [ver_int(f"\n{x} pieces\n>> ")
                   for x in ["gold", "silver", "copper"]]
    print(f"Now on {char.money[0]}gp {char.money[1]}sp {char.money[2]}bp")
    char.save()
    log(char, f"Money edited")
    input("Press enter to continue\n")


def money_change(char):
    char.level_money()
    print(f"Now on {char.money[0]}gp {char.money[1]}sp {char.money[2]}bp")
    char.save()
    log(char, f"Converted money")
    input("Press enter to continue\n")


money_menu = ConsoleMenu("Money Menu")
money_options = ["Gain Money", "Spend Money",
                 "Edit Money", "Convert into nicest change"]
money_functions = [money_add, money_spend, money_edit, money_change]
[money_menu.append_item(FunctionItem(x, y, [char]))
 for x, y in zip(money_options, money_functions)]


####################################################################
#                                                                  #
#                          Ability Menu                            #
#                                                                  #
####################################################################


def ability_new(char):
    name = input("\nAbility name\n>> ")
    description = input("\nAbility Description\n>> ")
    counter = ver_int("\nNumber of uses/start number\n>> ")
    increment = ver_int("Increment (1, -1 etc)\n>> ")
    reset = menu(["Short Rest", "Long Rest", "Manually"],
                 "When does ability uses reset\n>> ")
    try:
        char.abilities.append(
            Ability(name, description, counter, increment, reset))
    except:
        char.abilities = [
            Ability(name, description, counter, increment, reset)]
    char.save()
    log(char, f"created ability {name}")


def ability_use(char):
    choice = menu([x.name for x in char.abilities] +
                  ["Return"], "Pick an ability\n>> ")
    if choice == "Return":
        return
    actual = [x for x in char.abilities if x.name == choice][0]
    print(actual)

    use = input("Use ability?\n>> ").lower()
    if use in ["y", "yes"]:
        actual.use()
        log(char, f"Ability {choice} Used")
    char.save()
    input("Press Enter to continue\n")


def ability_reset(char):
    choice = menu([x.name for x in char.abilities] +
                  ["Return"], "Pick an ability\n>> ")
    if choice == "Return":
        return
    actual = [x for x in char.abilities if x.name == choice][0]
    actual.reset()
    char.save()
    log(char, f"Reset {choice} to {actual.start}")


def ability_setcustom(char):
    choice = menu([x.name for x in char.abilities] +
                  ["Return"], "Pick an ability\n>> ")
    if choice == "Return":
        return
    actual = [x for x in char.abilities if x.name == choice][0]
    newscore = ver_int("New value\n>> ")
    actual.set_custom(newscore)

    print(actual)
    char.save()
    log(char, f"Set {choice} to {newscore}")
    input("Press Enter to continue\n")


def ability_view(char):
    choice = menu([x.name for x in char.abilities] +
                  ["Return"], "Pick an ability\n>> ")
    if choice == "Return":
        return
    actual = [x for x in char.abilities if x.name == choice][0]
    print(actual)
    input("\nPress enter to continue\n")


def ability_edit(char):
    choice = menu([x.name for x in char.abilities] +
                  ["Return"], "Pick an ability\n>> ")
    if choice == "Return":
        return
    actual = [x for x in char.abilities if x.name == choice][0]
    print(actual)
    actual.edit()
    print()
    print(actual)
    char.save()
    log(char, f"Ability {choice} edited")
    input("Press enter to continue\n")


ability_menu = ConsoleMenu("Ability Menu")
ability_options = ["Use Ability", "View Ability",
                   "Reset Ability Counter", "Set Ability Counter", "Edit Ability", "New Ability"]
ability_functions = [ability_use, ability_view,
                     ability_reset, ability_setcustom, ability_edit, ability_new]
[ability_menu.append_item(FunctionItem(x, y, [char]))
 for x, y in zip(ability_options, ability_functions)]


####################################################################
#                                                                  #
#                            Item Menu                             #
#                                                                  #
####################################################################


def item_new(char):
    name = input("Item Name\n>> ")
    desc = input("Item Description (if applicable)\n>> ")
    quantity = ver_int("Quantity\n>> ")
    char.inventory.append(Item(name, desc, quantity))
    char.save()


def item_lose(char):
    lostname = menu([x.name for x in inv_sorter(char, char.inventory)] +
                    ["Return"], "Pick an item\n>> ")
    if lostname == "Return":
        return
    lost = [x for x in char.inventory if x.name == lostname][0]
    amount = ver_int(f"Quantity lost ({lost.quantity} max)\n>> ")
    if amount >= lost.quantity:
        # some kind of save for later feature
        char.inventory.remove(lost)
        log(char, f"{lostname} removed")
    else:
        lost.quantity -= amount
        log(char, f"lost {amount} {lostname}")
    char.save()


def item_gain(char):
    lostname = menu([x.name for x in inv_sorter(char, char.inventory)] +
                    ["Return"], "Pick an item\n>> ")
    if lostname == "Return":
        return
    lost = [x for x in char.inventory if x.name == lostname][0]
    amount = ver_int("Amount gained\n>> ")
    lost.quantity += amount
    char.save()
    log(char, f"Gained {amount} {lostname}")


def item_view(char):
    lostname = menu([x.name for x in inv_sorter(char, char.inventory)] +
                    ["Return"], "Pick an item\n>> ")
    if lostname == "Return":
        return
    lost = [x for x in char.inventory if x.name == lostname][0]
    print(lost)
    input("Press enter to continue\n")


item_menu = ConsoleMenu("Inventory menu", clear_screen=True)
item_options = ["View Item", "Lose Items", "Gain Items", "Add new Item"]
item_functions = [item_view, item_lose, item_gain, item_new]
[item_menu.append_item(FunctionItem(x, y, [char]))
 for x, y in zip(item_options, item_functions)]

####################################################################
#                                                                  #
#                            Edit Menu                             #
#                                                                  #
####################################################################


def edit_health(char):
    new_hp = ver_int(f"New max hp ({char.max_hp})\n>> ")
    char.max_hp = new_hp
    char.save()

    log(char, f"edit hp->{new_hp}")


def edit_ac(char):
    ac = ver_int(f"New Armour Class (current {char.ac})\n>> ")
    char.ac = ac
    char.save()
    log(char, f"edit AC->{ac}")


def edit_spellslots(char):
    print("Enter new spellslots")
    spellslots = []
    for x in range(9):
        num = ver_int(
            f"Level {x+1} spellslots (current {char.max_spellslots[x]}) > ")
        if num == 0:
            break
        spellslots.append(num)
    if len(spellslots) < 9:
        spellslots += [0 for i in range(9-len(spellslots))]
    char.max_spellslots = spellslots
    char.save()
    log(char, "edit spellslots")


def edit_profs(char):
    print("Skill Proficiencies (y/n/dp)\n")
    skill_profs = []
    for ii in SKILLS.keys():
        ans = input(
            f'{ii} ({["no","yes","dp"][int(char.check(ii)[1]/char.prof)]}) >> ').lower()
        if ans in ("y", "yes", "1"):
            skill_profs.append(1)
        elif ans in ("dp", "2"):
            skill_profs.append(2)
        else:
            skill_profs.append(0)

    print("Saving Throw Proficiencies (y/n/dp)\n")
    saving_profs = []
    for ii in STATS:
        ans = input(
            f'{ii} ({["no","yes","dp"][int(char.skill_save(ii)[1]/char.prof)]}) >> ')
        if ans in ("y", "yes", "1"):
            saving_profs.append(1)
        elif ans in ("dp", "2"):
            saving_profs.append(2)
        else:
            saving_profs.append(0)
    char.save_profs = saving_profs
    char.skill_profs = skill_profs
    char.save()
    log(char, "edit")


def edit_stats(char):
    print("Enter new stats, raw stat required (13 not +1")
    stats = [ver_int(x+" > ") for x in STATS]
    char.stats = stats
    char.save()

    log(char, f"edit stats")


def edit_level_up(char):
    log(char, "Initiate level up")
    new_level = ver_int(f"New level (current {char.level})\n>> ")
    edit_health(char)
    if input("Was there an ASI?\n>> ").lower() in ["y", "yes"]:
        edit_stats(char)
        edit_ac(char)
    if char.spellcaster:
        edit_spellslots(char)
    char.save()
    log(char, f"End level up lvl->{new_level}")
    stats(char)


edit_menu = ConsoleMenu("Edit Menu")
edit_options = ["Level Up", "Edit Health",
                "Edit Armour Class", "Edit Stats", "Edit Proficiencies", "Edit Spellslots"]
edit_functions = [edit_level_up, edit_health,
                  edit_ac, edit_stats, edit_profs, edit_spellslots]
[edit_menu.append_item(FunctionItem(x, y, [char]))
 for x, y in zip(edit_options, edit_functions)]
####################################################################
#                                                                  #
#                          Option Menu                             #
#                                                                  #
####################################################################


def option_spellsort(char):
    spell_options = ["By order added", "By level", "By name"]
    spell_options[char.sort_options[0]] += " (current)"
    choice = menu(spell_options, "Spell list display order\n>> ")
    char.sort_options[0] = spell_options.index(choice)
    char.save()
    log(char, f"Spell sort now {choice}")


def option_inventory_sort(char):
    inv_options = ["By order added", "By quantity", "By name"]
    inv_options[char.sort_options[1]] += " (current)"
    choice = menu(inv_options, "Inventory display order\n>> ")
    char.sort_options[1] = inv_options.index(choice)
    char.save()
    log(char, f"Inv sort now {choice}")


def option_logs(char):
    if char.keep_logs:
        prompt = "Turn off logs\n>> "
    else:
        prompt = "Turn on logs\n>> "
    char.keep_logs = (input(prompt).lower() in ["y", "yes"]) ^ char.keep_logs
    char.save()
    log(char, "Logs ON")


opt_menu = ConsoleMenu("Options", clear_screen=True)
opt_opt = ["Spell Sort", "Inventory Sort", "Toggle Logging"]
opt_funcs = [option_spellsort, option_inventory_sort, option_logs]
[opt_menu.append_item(FunctionItem(x, y, [char]))
 for x, y in zip(opt_opt, opt_funcs)]
####################################################################
#                                                                  #
#                            Main Menu                             #
#                                                                  #
####################################################################
menu_items = ["Abilities",
              "Checks", "Health", "Money", "Inventory", "Edit Character", "Spells"]


mainmenu = ConsoleMenu("Main Menu", clear_screen=True)
mainmenu.append_item(SubmenuItem("Spells", spell_menu, mainmenu))
mainmenu.append_item(FunctionItem("Checks", checkmenu, [char]))
mainmenu.append_item(SubmenuItem("Health", hp_menu, mainmenu))
mainmenu.append_item(SubmenuItem("Money", money_menu, mainmenu))
mainmenu.append_item(SubmenuItem("Abilities", ability_menu, mainmenu))
mainmenu.append_item(SubmenuItem("Inventory", item_menu, mainmenu))
mainmenu.append_item(FunctionItem("Show Stats", stats, [char]))
mainmenu.append_item(SubmenuItem("Options", opt_menu, mainmenu))
mainmenu.append_item(SubmenuItem("Edit Character", edit_menu, mainmenu))
mainmenu.show()
