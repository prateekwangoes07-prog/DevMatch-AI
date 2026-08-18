import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

class CalcomService:
    def __init__(self, api_key: str | None = None, base_url: str | None = None, event_type_id: int | None = None):
        self.api_key = api_key or settings.CALCOM_API_KEY
        self.base_url = base_url or settings.CALCOM_BASE_URL or "https://api.cal.com/v1"
        
        # event_type_id can be passed as int or str, let's coerce/handle
        raw_event_id = event_type_id or settings.CALCOM_EVENT_TYPE_ID
        if raw_event_id is not None:
            try:
                self.event_type_id = int(raw_event_id)
            except ValueError:
                self.event_type_id = None
        else:
            self.event_type_id = None

        # Determine if we should operate in mock mode
        self.is_mock = not self.api_key or self.api_key.lower() in ("mock", "placeholder", "") or self.event_type_id is None

        if self.is_mock:
            logger.warning("Cal.com Service is running in MOCK mode. Configure CALCOM_API_KEY and CALCOM_EVENT_TYPE_ID for real integration.")

    async def get_availability(self, start_date: datetime, end_date: datetime) -> List[str]:
        """
        Retrieves available ISO-8601 slots.
        In mock mode, returns sample slots.
        """
        if self.is_mock:
            # Generate dummy slots every day at 10:00, 14:00, 16:00 UTC
            slots = []
            current = start_date.replace(hour=10, minute=0, second=0, microsecond=0)
            while current <= end_date:
                # Only offer slots in future
                if current > datetime.now(timezone.utc):
                    slots.append(current.isoformat())
                    slots.append((current + timedelta(hours=4)).isoformat())
                    slots.append((current + timedelta(hours=6)).isoformat())
                current += timedelta(days=1)
            return slots

        # Real API request
        params = {
            "apiKey": self.api_key,
            "eventTypeId": self.event_type_id,
            "startTime": start_date.isoformat(),
            "endTime": end_date.isoformat(),
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/slots", params=params, timeout=10.0)
                if response.status_code != 200:
                    logger.error(f"Cal.com returned error status {response.status_code}: {response.text}")
                    raise httpx.HTTPStatusError(
                        f"Cal.com returned status {response.status_code}",
                        request=response.request,
                        response=response
                    )
                
                data = response.json()
                # Cal.com returns slots inside a dict, usually mapping date -> list of slots
                # e.g., {"slots": {"2026-08-18": [{"time": "2026-08-18T10:00:00.000Z"}]}}
                slots_data = data.get("slots", {})
                available_slots = []
                
                if isinstance(slots_data, dict):
                    for date_str, slots_list in slots_data.items():
                        for slot in slots_list:
                            if isinstance(slot, dict) and "time" in slot:
                                available_slots.append(slot["time"])
                elif isinstance(slots_data, list):
                    for slot in slots_data:
                        if isinstance(slot, dict) and "time" in slot:
                            available_slots.append(slot["time"])
                        elif isinstance(slot, str):
                            available_slots.append(slot)
                
                return sorted(available_slots)
            except Exception as e:
                logger.error(f"Error fetching availability from Cal.com: {e}")
                raise

    async def create_booking(self, client_name: str, client_email: str, appointment_time: datetime) -> Dict[str, Any]:
        """
        Creates a booking on Cal.com.
        """
        if self.is_mock:
            # Simulate a successful booking
            booking_id = f"mock_cal_{uuid.uuid4().hex[:8]}"
            return {
                "id": booking_id,
                "startTime": appointment_time.isoformat(),
                "status": "ACCEPTED",
                "uid": booking_id,
                "attendees": [{"name": client_name, "email": client_email}]
            }

        # Real API request
        booking_data = {
            "eventTypeId": self.event_type_id,
            "start": appointment_time.isoformat(),
            "end": (appointment_time + timedelta(minutes=45)).isoformat(),  # Default 45 mins slot
            "responses": {
                "name": client_name,
                "email": client_email,
            },
            "metadata": {},
            "timeZone": "UTC",
            "language": "en"
        }

        async with httpx.AsyncClient() as client:
            try:
                # API Key can be passed in request query parameter or Bearer token
                # Cal.com API v1 uses ?apiKey=
                response = await client.post(
                    f"{self.base_url}/bookings",
                    params={"apiKey": self.api_key},
                    json=booking_data,
                    timeout=10.0
                )
                if response.status_code not in (200, 201):
                    logger.error(f"Cal.com booking failed with status {response.status_code}: {response.text}")
                    raise httpx.HTTPStatusError(
                        f"Cal.com booking failed with status {response.status_code}",
                        request=response.request,
                        response=response
                    )
                
                # Check response content
                result = response.json()
                booking = result.get("booking") or result
                return booking
            except Exception as e:
                logger.error(f"Error creating booking in Cal.com: {e}")
                raise
