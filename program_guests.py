import datetime
import program_hosts as hosts
import services.data_service as svc
import infrastructure.state as state
from dateutil import parser
from program_hosts import error_msg, success_msg, section_msg


def run():
    section_msg("\n**********************  WELCOME GUEST  **********************\n")
    show_commands()

    while True:
        action = hosts.get_action()

        if action == "s":
            state.active_account = None
            return
        elif not state.active_account and action not in hosts.pre_login_commands:
            error_msg("You must log in or create account first.")
            continue

        switch(action)()


def switch(action):
    switcher = {
        **dict.fromkeys(["x", "bye", "exit", "exit()"], hosts.exit_app),
        "c": lambda: hosts.create_account(False),
        "l": lambda: hosts.log_into_account(False),
        "a": add_a_dog,
        "y": view_your_dogs,
        "b": book_a_room,
        "v": view_bookings,
        "?": show_commands
    }
    return switcher.get(action, hosts.unknown_command)


def show_commands():
    print("What action would you like to take:")
    print("[C]reate an account")
    print("[L]ogin to your account")
    print("[A]dd a dog")
    print("View [y]our dogs")
    print("[B]ook a room")
    print("[V]iew your bookings")
    print("[S]witch user")
    print("e[X]it app")
    print("[?] Help (this info)")


def add_a_dog():
    section_msg("\n**********************  ADD A DOG  **********************\n")

    name = input("What is your dog\'s name? ")
    if not name:
        error_msg("Cancelled.")
        return

    length = float(input("How big is your dog (in kilos)? "))
    species = input("What breed? ")
    is_aggressive = input("Is your dog aggressive [y]es, [n]o? ").lower().startswith("y")

    dog = svc.add_dog(state.active_account, name, length, species, is_aggressive)

    state.reload_account()
    success_msg("Created {} with id {}".format(dog.name, dog.id))


def view_your_dogs():
    section_msg("\n**********************  YOUR DOGS  **********************\n")

    dogs = svc.get_dogs_for_user(state.active_account.id)
    print("You have {} dogs.".format(len(dogs)))
    for d in dogs:
        print(" * {} is a {} that weights {}kg and is {}aggressive.".format(
            d.name,
            d.breed,
            d.weight,
            "" if d.is_aggressive else "not "
        ))


def book_a_room():
    if state.active_account.is_host:
        error_msg("You have to [l]ogin to guest account to book a room.")
        return

    section_msg("\n**********************  BOOK A ROOM  **********************\n")

    dogs = svc.get_dogs_for_user(state.active_account.id)
    if not dogs:
        error_msg("You must first [a]dd a dog before you can book a room.")
        return

    print("Let\'s start by finding available rooms.")
    checkin_date = input("Check-in date [yyyy-mm-dd]: ")
    if not checkin_date:
        error_msg("Cancelled.")
        return

    checkin = parser.parse(
        checkin_date
    )
    checkout = parser.parse(
        input("Check-out date [yyyy-mm-dd]: ")
    )
    if checkin >= checkout:
        error_msg("Check-in must be before check-out.")
        return

    print()
    for idx, d in enumerate(dogs):
        print("{}. {} (weight: {}kg, aggressive: {})".format(
            idx + 1,
            d.name,
            d.weight,
            "yes" if d.is_aggressive else "no"
        ))

    dog = dogs[int(input("Which dog do you want to book (number)? ")) - 1]

    rooms = svc.get_available_rooms(checkin, checkout, dog)

    print("\nThere are {} rooms available in that time:".format(len(rooms)))
    for idx, r in enumerate(rooms):
        print(" {}. {} with {}m carpeted: {}, has toys: {}.".format(
            idx + 1,
            r.name,
            r.square_meters,
            "yes" if r.is_carpeted else "no",
            "yes" if r.has_toys else "no"))

    if not rooms:
        error_msg("Sorry, no rooms are available for that date.")
        return

    room = rooms[int(input("\nWhich room do you want to book (number)? ")) - 1]
    svc.book_room(state.active_account, dog, room, checkin, checkout)

    success_msg("Successfully booked {} for {} at ${}/night.".format(room.name, dog.name, room.price))


def view_bookings():
    section_msg("\n**********************  YOUR BOOKINGS  **********************\n")

    dogs = {d.id: d for d in svc.get_dogs_for_user(
        state.active_account.id)}

    bookings = svc.get_bookings_for_user(state.active_account.email)

    print("You have {} bookings.".format(len(bookings)))
    for b in bookings:
        print(" * dog: {} is booked at {} from {} for {} days.".format(
            dogs.get(b.guest_dog_id).name,
            b.room.name,
            datetime.date(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day),
            (b.check_out_date - b.check_in_date).days
        ))
