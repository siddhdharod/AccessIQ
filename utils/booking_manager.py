import os
import json
import hashlib
import uuid
import datetime
from datetime import timedelta
from pathlib import Path
import pandas as pd
from utils.helpers import load_dataset

# Resolve data folder path relative to project root
_BASE_DIR = Path(__file__).resolve().parent.parent
USERS_FILE = _BASE_DIR / "data" / "users.json"
BOOKINGS_FILE = _BASE_DIR / "data" / "bookings.json"

# Pricing structure in Indian Rupees (₹)
PRICING_TABLE = {
    "Wheelchair Booking": {
        "30 Mins": 30,
        "1 Hour": 50,
        "2 Hours": 90,
        "3 Hours": 130,
        "4 Hours": 170,
        "6 Hours": 240,
        "8 Hours": 300,
        "12 Hours": 420,
        "Full Day (24h)": 600
    },
    "Accessible Parking Booking": {
        "30 Mins": 20,
        "1 Hour": 40,
        "2 Hours": 70,
        "3 Hours": 100,
        "4 Hours": 130,
        "6 Hours": 180,
        "8 Hours": 230,
        "12 Hours": 320,
        "Full Day (24h)": 450
    }
}

DURATION_MINUTES = {
    "30 Mins": 30,
    "1 Hour": 60,
    "2 Hours": 120,
    "3 Hours": 180,
    "4 Hours": 240,
    "6 Hours": 360,
    "8 Hours": 480,
    "12 Hours": 720,
    "Full Day (24h)": 1440
}

TOTAL_WHEELCHAIR_SLOTS = 20  # W01 - W20
TOTAL_PARKING_SLOTS = 30     # P01 - P30

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# ─────────────────────────────────────────────────────────────
# JSON STORAGE HELPERS
# ─────────────────────────────────────────────────────────────

def load_users() -> list:
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_users(users: list):
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def load_bookings() -> list:
    if BOOKINGS_FILE.exists():
        try:
            with open(BOOKINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_bookings(bookings: list):
    BOOKINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(BOOKINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(bookings, f, indent=2)

# ─────────────────────────────────────────────────────────────
# USER AUTHENTICATION & MANAGEMENT
# ─────────────────────────────────────────────────────────────

def register_user(username: str, email: str, password: str, full_name: str, phone: str = "") -> tuple[bool, str]:
    username = username.strip()
    email = email.strip().lower()
    if not username or not email or not password:
        return False, "Username, email, and password are required."
    
    users = load_users()
    for u in users:
        if u.get("username", "").lower() == username.lower():
            return False, "Username already exists. Please choose another."
        if u.get("email", "").lower() == email:
            return False, "Email already registered."
    
    new_user = {
        "user_id": f"USR-{uuid.uuid4().hex[:6].upper()}",
        "username": username,
        "email": email,
        "password_hash": _hash_password(password),
        "full_name": full_name,
        "phone": phone,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    users.append(new_user)
    save_users(users)
    return True, "Account created successfully! You can now log in."

def authenticate_user(username: str, password: str) -> dict | None:
    username = username.strip()
    if not username or not password:
        return None
    users = load_users()
    pwd_hash = _hash_password(password)
    for u in users:
        if u.get("username", "").lower() == username.lower() and u.get("password_hash") == pwd_hash:
            return {
                "user_id": u.get("user_id"),
                "username": u.get("username"),
                "email": u.get("email"),
                "full_name": u.get("full_name"),
                "phone": u.get("phone")
            }
    return None

def update_user_profile(username: str, full_name: str, phone: str, email: str) -> tuple[bool, str]:
    users = load_users()
    updated = False
    for u in users:
        if u.get("username", "").lower() == username.lower():
            u["full_name"] = full_name
            u["phone"] = phone
            u["email"] = email
            updated = True
            break
    if updated:
        save_users(users)
        return True, "Profile updated successfully!"
    return False, "User not found."

# ─────────────────────────────────────────────────────────────
# LOCATIONS & SLOTS HELPERS
# ─────────────────────────────────────────────────────────────

def get_available_locations() -> list:
    """Retrieve locations from accessiq_dataset or load_dataset."""
    try:
        raw_path = _BASE_DIR / "data" / "accessiq_dataset.csv"
        if raw_path.exists():
            df_raw = pd.read_csv(raw_path)
            if "Location_Name" in df_raw.columns:
                locs = df_raw["Location_Name"].dropna().unique().tolist()
                if locs:
                    return sorted(locs)
    except Exception:
        pass

    df = load_dataset()
    if not df.empty and "Location_Name" in df.columns:
        locs = df["Location_Name"].dropna().unique().tolist()
        if locs:
            return sorted(locs)

    # Fallback locations if dataset is empty
    return [
        "Central Metro Station",
        "City General Hospital",
        "Civic Tech Park",
        "Delhi Plaza Mall",
        "Hyderabad Central Station",
        "Indore General Hospital",
        "Kochi Central Station",
        "Lucknow International Airport",
        "Mumbai City Transit Hub",
        "Patna Medical Center"
    ]

def get_slots_for_service(service_type: str) -> list:
    """Return slot IDs for specified service type."""
    if "wheelchair" in service_type.lower():
        return [f"W{i:02d}" for i in range(1, TOTAL_WHEELCHAIR_SLOTS + 1)]
    else:
        return [f"P{i:02d}" for i in range(1, TOTAL_PARKING_SLOTS + 1)]

def get_price(service_type: str, duration_str: str) -> float:
    service_key = "Wheelchair Booking" if "wheelchair" in service_type.lower() else "Accessible Parking Booking"
    return PRICING_TABLE.get(service_key, {}).get(duration_str, 50)

# ─────────────────────────────────────────────────────────────
# REAL-TIME AVAILABILITY & OVERLAP PREVENTION
# ─────────────────────────────────────────────────────────────

def parse_booking_times(date_obj: datetime.date, start_time_str: str, duration_str: str) -> tuple[datetime.datetime, datetime.datetime]:
    """Parse date, start time string ('10:00'), and duration into start and end datetimes."""
    hour, minute = map(int, start_time_str.split(":"))
    start_dt = datetime.datetime.combine(date_obj, datetime.time(hour, minute))
    duration_mins = DURATION_MINUTES.get(duration_str, 60)
    end_dt = start_dt + timedelta(minutes=duration_mins)
    return start_dt, end_dt

def is_slot_available(location_name: str, service_type: str, slot_id: str, start_dt: datetime.datetime, end_dt: datetime.datetime) -> bool:
    """
    Check if a specific slot is free for the given location, service, and time range.
    Two intervals [A_start, A_end) and [B_start, B_end) overlap if max(A_start, B_start) < min(A_end, B_end).
    """
    bookings = load_bookings()
    for b in bookings:
        if b.get("status") == "Active" and b.get("location_name") == location_name and b.get("slot_id") == slot_id:
            # Check service compatibility
            b_service = b.get("service_type", "")
            is_same_service = ("wheelchair" in service_type.lower() and "wheelchair" in b_service.lower()) or \
                              ("parking" in service_type.lower() and "parking" in b_service.lower())
            if is_same_service:
                b_start = datetime.datetime.strptime(b["start_datetime"], "%Y-%m-%d %H:%M:%S")
                b_end = datetime.datetime.strptime(b["end_datetime"], "%Y-%m-%d %H:%M:%S")
                if max(start_dt, b_start) < min(end_dt, b_end):
                    return False
    return True

def get_slot_availability_map(location_name: str, service_type: str, date_obj: datetime.date, start_time_str: str, duration_str: str) -> dict:
    """Return dictionary of slot_id -> is_available (True/False)."""
    slots = get_slots_for_service(service_type)
    start_dt, end_dt = parse_booking_times(date_obj, start_time_str, duration_str)
    availability = {}
    for slot in slots:
        availability[slot] = is_slot_available(location_name, service_type, slot, start_dt, end_dt)
    return availability

def get_realtime_counts_for_location(location_name: str, date_obj: datetime.date = None, start_time_str: str = None) -> tuple[int, int]:
    """
    Returns (available_wheelchairs, available_parking) for given location right now or specified time.
    """
    if date_obj is None:
        now = datetime.datetime.now()
        date_obj = now.date()
        start_time_str = now.strftime("%H:%M")
    if start_time_str is None:
        start_time_str = "12:00"

    w_avail = get_slot_availability_map(location_name, "Wheelchair Booking", date_obj, start_time_str, "1 Hour")
    p_avail = get_slot_availability_map(location_name, "Accessible Parking Booking", date_obj, start_time_str, "1 Hour")
    
    avail_w_count = sum(1 for v in w_avail.values() if v)
    avail_p_count = sum(1 for v in p_avail.values() if v)
    return avail_w_count, avail_p_count

# ─────────────────────────────────────────────────────────────
# BOOKING CREATION & CANCELLATION
# ─────────────────────────────────────────────────────────────

def create_booking(
    username: str,
    location_name: str,
    service_type: str,
    slot_id: str,
    booking_date: datetime.date,
    start_time_str: str,
    duration_str: str
) -> tuple[bool, str, dict | None]:
    """Create a new booking after checking overlap. Returns (success, message, booking_dict)."""
    start_dt, end_dt = parse_booking_times(booking_date, start_time_str, duration_str)
    
    # Overlap check
    if not is_slot_available(location_name, service_type, slot_id, start_dt, end_dt):
        return False, f"Slot {slot_id} is already booked for the selected time window. Please select another slot or time.", None

    amount = get_price(service_type, duration_str)
    booking_id = f"AIQ-BK-{uuid.uuid4().hex[:6].upper()}"
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    booking_record = {
        "booking_id": booking_id,
        "username": username,
        "location_name": location_name,
        "service_type": service_type,
        "slot_id": slot_id,
        "booking_date": booking_date.strftime("%Y-%m-%d"),
        "start_time": start_time_str,
        "end_time": end_dt.strftime("%H:%M"),
        "start_datetime": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "end_datetime": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_str": duration_str,
        "amount_inr": amount,
        "status": "Active",
        "created_at": created_at
    }

    bookings = load_bookings()
    bookings.append(booking_record)
    save_bookings(bookings)

    return True, f"Booking successfully confirmed! Booking ID: {booking_id}", booking_record

def cancel_booking(booking_id: str, username: str) -> tuple[bool, str]:
    """Cancel booking and immediately free slot."""
    bookings = load_bookings()
    updated = False
    for b in bookings:
        if b.get("booking_id") == booking_id and b.get("username", "").lower() == username.lower():
            if b.get("status") == "Cancelled":
                return False, "This booking has already been cancelled."
            b["status"] = "Cancelled"
            b["cancelled_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updated = True
            break
    if updated:
        save_bookings(bookings)
        return True, f"Booking {booking_id} has been cancelled successfully. Slot is released immediately."
    return False, "Booking record not found or unauthorized."

def get_user_bookings(username: str) -> list:
    """Retrieve all bookings for a user sorted by creation date."""
    bookings = load_bookings()
    user_b = [b for b in bookings if b.get("username", "").lower() == username.lower()]
    user_b.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return user_b

# ─────────────────────────────────────────────────────────────
# QR CODE GENERATION HELPER
# ─────────────────────────────────────────────────────────────

def generate_qr_code_svg(text: str) -> str:
    """
    Generate an SVG string for QR Code data using quickchart API image wrapper or pure SVG matrix.
    Fallback clean HTML/SVG component.
    """
    import urllib.parse
    encoded_text = urllib.parse.quote(text)
    qr_url = f"https://quickchart.io/qr?text={encoded_text}&size=200&margin=1"
    return qr_url
