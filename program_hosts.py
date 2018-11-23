import datetime
import infrastructure.state as state
import services.data_service as svc
from colorama import Fore
from dateutil import parser

pre_login_commands = ("x", "bye", "exit", "exit()", "c", "l", "?")


def run():
    section_msg("\n**********************  Welcome HOST  **********************\n")

    show_commands()

    while True:
        action = get_action()

        if action == "m":
            return
        elif not state.active_account and action not in pre_login_commands:
            error_msg("You must log in or create account first.")
            continue

        switch(action)()


def switch(action):
    switcher = {
        **dict.fromkeys(["x", "bye", "exit", "exit()"], exit_app),
        "c": lambda: create_account(True),
        "l": lambda: log_into_account(True),
        "r": register_room,
        "y": list_rooms,
        "u": update_availability,
        "v": view_bookings,
        "?": show_commands
    }
    return switcher.get(action, unknown_command)


def show_commands():
    print("What action would you like to take:")
    print("[C]reate an account")
    print("[L]ogin to your account")
    print("[R]egister a room")
    print("List [y]our rooms")
    print("[U]pdate room availability")
    print("[V]iew your bookings")
    print("Change [m]ode (guest or host)")
    print("E[x]it app")
    print("[?] Help (this info)")


def create_account(is_host):
    section_msg("\n**********************  REGISTER  **********************\n")

    name = input("What is your name? ")
    email = input("What is your email? ").strip().lower()

    old_account = svc.find_account_by_email(email)
    if old_account:
        error_msg(f"ERROR: Account with email {email} already exists.")
        return

    state.active_account = svc.create_account(name, email, is_host)
    success_msg(f"Created new account with id {state.active_account.id}.")


def log_into_account(is_host):
    section_msg("\n**********************  LOGIN  **********************\n")

    email = input("What is your email? ").strip().lower()
    account = svc.find_account_by_email(email)

    if not account:
        error_msg(f"Could not find account with email {email}.")
        return

    if is_host != account.is_host:
        error_msg("Sorry, you aren\'t a {}. Change [m]ode to log in.".format("host" if is_host else "guest"))
        return

    state.active_account = account
    success_msg("Logged in successfully.")


def register_room():
    section_msg("\n**********************  REGISTER A ROOM  **********************\n")

    meters = input("How many square meters are your room? ")
    if not meters:
        error_msg("Cancelled.")
        return

    meters = float(meters)
    carpeted = input("Is it carpeted [y, n]? ").lower().startswith("y")
    has_toys = input("Have dog toys [y, n]? ").lower().startswith("y")
    allow_aggressive = input("Can you host aggressive dogs [y, n]? ").lower().startswith("y")
    name = input("Give your room a name: ")
    price = float(input("How much are you charging? "))

    room = svc.register_room(
        state.active_account, name, allow_aggressive, has_toys, carpeted, meters, price
    )

    state.reload_account()
    success_msg(f"Registered new room with id {room.id}.")


def list_rooms(suppress_header=False):
    if not suppress_header:
        section_msg("\n**********************  YOUR ROOMS  **********************\n")

    rooms = svc.find_rooms_for_user(state.active_account)
    print(f"You have {len(rooms)} rooms.")
    for idx, r in enumerate(rooms):
        print(f" {idx+1}. {r.name} is {r.square_meters} meters.")
        for b in r.bookings:
            print(" * Booking: {}, {} days, booked? {}".format(
                b.check_in_date,
                (b.check_out_date - b.check_in_date).days,
                "YES" if b.booked_date is not None else "no"
            ))


def update_availability():
    section_msg("\n**********************  ADD AVAILABLE DATE  **********************\n")

    list_rooms(suppress_header=True)

    room_number = input("\nEnter room number: ")
    if not room_number.strip():
        error_msg("Cancelled.")
        return

    room_number = int(room_number)

    rooms = svc.find_rooms_for_user(state.active_account)
    selected_room = rooms[room_number - 1]

    success_msg("Selected room {}.".format(selected_room.name))

    start_date = parser.parse(
        input("\nEnter available date [yyyy-mm-dd]: ")
    )

    while True:
        try:
            days = int(input("How many days you can host? "))
            break
        except ValueError:
            error_msg("Wrong days format.\n")

    svc.add_available_date(
        selected_room,
        start_date,
        days
    )

    success_msg(f"Date added to room {selected_room.name}.")


def view_bookings():
    section_msg("\n**********************  YOUR BOOKINGS  **********************\n")

    rooms = svc.find_rooms_for_user(state.active_account)

    bookings = [
        (r, b)
        for r in rooms
        for b in r.bookings
        if b.booked_date is not None
    ]

    print("You have {} bookings.".format(len(bookings)))
    for r, b in bookings:
        print(" * room: {}, booked date: {}, from {} for {} days.".format(
            r.name,
            datetime.date(b.booked_date.year, b.booked_date.month, b.booked_date.day),
            datetime.date(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day),
            b.duration_in_days
        ))


def exit_app():
    print("\nbye")
    raise KeyboardInterrupt()


def get_action():
    text = "\n> "
    if state.active_account:
        text = f"\n{state.active_account.name}> "

    action = input(Fore.YELLOW + text + Fore.WHITE)
    return action.strip().lower()


def unknown_command():
    error_msg("Sorry we didn\'t understand that command.")


def error_msg(text):
    print(Fore.LIGHTRED_EX + text + Fore.WHITE)


def success_msg(text):
    print(Fore.LIGHTGREEN_EX + text + Fore.WHITE)


def section_msg(text):
    print(Fore.MAGENTA + text + Fore.WHITE)
