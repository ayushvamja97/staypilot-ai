from datetime import date, timedelta

from fastapi import FastAPI

app = FastAPI(
    title="StayPilot AI API",
    description="Hotel operations and intelligent search platform",
    version="0.2.0",
)

today = date.today()

reservations = [
    {
        "id": "SP-1001",
        "guest_name": "Jordan Lee",
        "room_number": "1410",
        "room_type": "KNPX",
        "arrival_date": today.isoformat(),
        "departure_date": (today + timedelta(days=2)).isoformat(),
        "status": "reserved",
    },
    {
        "id": "SP-1002",
        "guest_name": "Taylor Morgan",
        "room_number": "403",
        "room_type": "QND2",
        "arrival_date": today.isoformat(),
        "departure_date": (today + timedelta(days=3)).isoformat(),
        "status": "reserved",
    },
    {
        "id": "SP-1003",
        "guest_name": "Alex Rivera",
        "room_number": "1411",
        "room_type": "KNPX",
        "arrival_date": (today - timedelta(days=2)).isoformat(),
        "departure_date": today.isoformat(),
        "status": "checked_in",
    },
    {
        "id": "SP-1004",
        "guest_name": "Sam Patel",
        "room_number": "407",
        "room_type": "QND2",
        "arrival_date": (today - timedelta(days=1)).isoformat(),
        "departure_date": (today + timedelta(days=2)).isoformat(),
        "status": "checked_in",
    },
]


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "staypilot-backend"}


@app.get("/api/reservations")
def list_reservations():
    return {"reservations": reservations, "total": len(reservations)}


@app.get("/api/dashboard")
def dashboard():
    return {
        "date": today.isoformat(),
        "total_reservations": len(reservations),
        "arrivals_today": sum(
            r["arrival_date"] == today.isoformat()
            and r["status"] == "reserved"
            for r in reservations
        ),
        "departures_today": sum(
            r["departure_date"] == today.isoformat()
            and r["status"] == "checked_in"
            for r in reservations
        ),
        "occupied_rooms": sum(
            r["status"] == "checked_in" for r in reservations
        ),
    }

from hotel_config import HOTEL


@app.get("/api/hotel")
def get_hotel():
    return HOTEL


@app.get("/api/room-types")
def get_room_types():
    return {
        "total_rooms": HOTEL["total_rooms"],
        "room_types": HOTEL["room_types"]
    }


@app.get("/api/loyalty-levels")
def get_loyalty_levels():
    return {
        "loyalty_levels": HOTEL["loyalty_levels"]
    }


from room_inventory import ROOMS


@app.get("/api/rooms")
def list_rooms(
    floor: int | None = None,
    room_type: str | None = None,
):
    results = ROOMS

    if floor is not None:
        results = [
            room for room in results
            if room["floor"] == floor
        ]

    if room_type is not None:
        results = [
            room for room in results
            if room["room_type"] == room_type.upper()
        ]

    return {
        "rooms": results,
        "total": len(results),
        "hotel_capacity": HOTEL["total_rooms"],
        "inventory_complete": len(ROOMS) == HOTEL["total_rooms"],
    }

from copilot_api import router as copilot_router
app.include_router(copilot_router)
