import datetime
import bson
from typing import List
from mongoengine.queryset.visitor import Q
from entities.bookings import Booking
from entities.rooms import Room
from entities.owners import Owner
from entities.dogs import Dog


def create_account(name: str, email: str, is_host: bool) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email
    owner.is_host = is_host

    owner.save()
    return owner


def find_account_by_email(email: str) -> Owner:
    owner = Owner.objects(email=email).first()
    return owner


def get_host_status(is_host=None) -> bool:
    return Owner.objects(is_host)


def register_room(active_account: Owner,
                  name, allow_aggressive, has_toys,
                  carpeted, meters, price) -> Room:
    room = Room()

    room.name = name
    room.square_meters = meters
    room.is_carpeted = carpeted
    room.has_toys = has_toys
    room.allow_aggressive_dogs = allow_aggressive
    room.price = price

    room.save()

    account = find_account_by_email(active_account.email)
    account.room_ids.append(room.id)
    account.save()

    return room


def find_rooms_for_user(account: Owner) -> List[Room]:
    query = Room.objects(id__in=account.room_ids)
    rooms = list(query)

    return rooms


def add_available_date(room: Room,
                       start_date: datetime.datetime, days: int):
    booking = Booking()
    booking.check_in_date = start_date
    booking.check_out_date = start_date + datetime.timedelta(days=days)

    room = Room.objects(id=room.id).first()
    room.bookings.append(booking)
    room.save()

    # return room


def add_dog(account, name, weight, breed, is_aggressive) -> Dog:
    dog = Dog()
    dog.name = name
    dog.weight = weight
    dog.breed = breed
    dog.is_aggressive = is_aggressive
    dog.save()

    owner = find_account_by_email(account.email)
    owner.dog_ids.append(dog.id)
    owner.save()

    return dog


def get_dogs_for_user(user_id: bson.ObjectId) -> List[Dog]:
    owner = Owner.objects(id=user_id).first()
    dogs = Dog.objects(id__in=owner.dog_ids).all()

    return list(dogs)


def get_available_rooms(checkin: datetime.datetime,
                        checkout: datetime.datetime, dog: Dog) -> List[Room]:
    min_size = dog.weight / 4

    query = Room.objects(Q(square_meters__gte=min_size) &
                         Q(bookings__check_in_date__lte=checkin) &
                         Q(bookings__check_out_date__gte=checkout))

    if dog.is_aggressive:
        query = query.filter(allow_aggressive_dogs=True)

    rooms = query.order_by("price", "-square_meters")

    return rooms


def book_room(account, dog, room, checkin, checkout):
    booking: Booking = None

    for b in room.bookings:
        if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_dog_id is None:
            booking = b
            break

    booking.guest_owner_id = account.id
    booking.guest_dog_id = dog.id
    booking.booked_date = datetime.datetime.now()

    room.save()


def get_bookings_for_user(email: str) -> List[Booking]:
    account = find_account_by_email(email)

    booked_rooms = Room.objects() \
        .filter(bookings__guest_owner_id=account.id) \
        .only("bookings", "name")

    def map_room_for_booking(room, booking):
        booking.room = room
        return booking

    bookings = [
        map_room_for_booking(room, booking)
        for room in booked_rooms
        for booking in room.bookings
        if booking.guest_owner_id == account.id
    ]

    return bookings
