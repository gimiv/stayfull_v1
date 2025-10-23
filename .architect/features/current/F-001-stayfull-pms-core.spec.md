# F-001: Stayfull PMS Core - Feature Specification

**Feature ID**: F-001
**Feature Name**: Stayfull PMS Core
**Priority**: 1 (Foundation)
**Status**: SPECIFICATION
**Architect**: Senior Product Architect
**Date**: 2025-10-22
**Estimated Effort**: 2-3 weeks

---

## 1. Feature Overview

### 1.1 Purpose
The Stayfull PMS Core provides the foundational property management system for hotels. It manages hotels, rooms, room types, guests, reservations, and staff within a multi-tenant architecture.

### 1.2 Business Value
- Enables hotels to manage their core operations
- Foundation for all 21 AI features
- Multi-tenant isolation ensures data security
- Provides admin interface for hotel configuration

### 1.3 Key Requirements
- Multi-tenancy: Each hotel's data is isolated
- Role-based access control (RBAC)
- RESTful API for all operations
- Django Admin interface for back-office management
- Test coverage: >80%
- API response time: <200ms p95

---

## 2. Domain Model Specifications

### 2.1 Hotel Entity

**Purpose**: Represents a hotel property in the system

**Attributes:**
| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `id` | UUID | Yes | Auto-generated | Primary key |
| `name` | String(200) | Yes | 3-200 chars | Hotel name |
| `slug` | String(200) | Yes | Unique, URL-safe | URL identifier |
| `brand` | String(100) | No | Max 100 chars | Brand name (if chain) |
| `type` | Enum | Yes | One of: `independent`, `chain`, `boutique` | Hotel type |
| `address` | JSON | Yes | Valid address schema | Physical address |
| `contact` | JSON | Yes | Valid contact schema | Contact info (phone, email, website) |
| `timezone` | String(50) | Yes | Valid timezone | IANA timezone (e.g., "America/New_York") |
| `currency` | String(3) | Yes | ISO 4217 code | Currency code (e.g., "USD") |
| `languages` | JSON Array | Yes | ISO 639-1 codes | Supported languages ["en", "es"] |
| `check_in_time` | Time | Yes | HH:MM format | Default check-in time (e.g., "15:00") |
| `check_out_time` | Time | Yes | HH:MM format | Default check-out time (e.g., "11:00") |
| `total_rooms` | Integer | Yes | > 0 | Total number of rooms |
| `is_active` | Boolean | Yes | Default: true | Hotel active status |
| `settings` | JSON | No | Valid settings schema | Additional settings |
| `created_at` | DateTime | Yes | Auto | Creation timestamp |
| `updated_at` | DateTime | Yes | Auto | Last update timestamp |

**JSON Schemas:**

```json
// address schema
{
  "street_address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "US"
}

// contact schema
{
  "phone": "+1-555-0123",
  "email": "info@hotel.com",
  "website": "https://hotel.com"
}

// settings schema
{
  "booking_lead_time_days": 365,
  "min_stay_nights": 1,
  "max_stay_nights": 30,
  "cancellation_policy": "flexible"
}
```

**Business Rules:**
1. Hotel `slug` must be globally unique
2. Hotel `name` must be unique per organization
3. `check_out_time` must be before `check_in_time` (next day checkout)
4. `total_rooms` should match count of Room entities
5. At least one `language` must be specified

**Relationships:**
- Has many: `RoomType`, `Room`, `Reservation`, `Staff`
- Belongs to: `Organization` (multi-tenancy)

---

### 2.2 RoomType Entity

**Purpose**: Defines categories of rooms (e.g., Standard, Deluxe, Suite)

**Attributes:**
| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `id` | UUID | Yes | Auto-generated | Primary key |
| `hotel_id` | UUID | Yes | FK to Hotel | Parent hotel |
| `name` | String(100) | Yes | 3-100 chars | Room type name |
| `code` | String(20) | Yes | Unique per hotel | Short code (e.g., "STD", "DLX") |
| `description` | Text | No | Max 2000 chars | Detailed description |
| `max_occupancy` | Integer | Yes | 1-20 | Maximum guests |
| `max_adults` | Integer | Yes | 1-20 | Maximum adults |
| `max_children` | Integer | Yes | 0-20 | Maximum children |
| `base_price` | Decimal(10,2) | Yes | > 0 | Base nightly rate |
| `size_sqm` | Decimal(6,2) | No | > 0 | Room size in square meters |
| `bed_configuration` | JSON Array | Yes | Valid bed schema | Bed types and counts |
| `amenities` | JSON Array | Yes | Array of strings | Room amenities |
| `images` | JSON Array | No | Valid image URLs | Room photos |
| `is_active` | Boolean | Yes | Default: true | Availability for booking |
| `display_order` | Integer | Yes | Default: 0 | Sort order in listings |
| `created_at` | DateTime | Yes | Auto | Creation timestamp |
| `updated_at` | DateTime | Yes | Auto | Last update timestamp |

**JSON Schemas:**

```json
// bed_configuration schema
[
  {"type": "king", "count": 1},
  {"type": "twin", "count": 2}
]
// Valid bed types: "king", "queen", "double", "twin", "single", "sofa_bed"

// amenities schema
[
  "wifi",
  "tv",
  "mini_fridge",
  "safe",
  "coffee_maker",
  "balcony",
  "bathtub",
  "shower",
  "air_conditioning",
  "heating"
]

// images schema
[
  {
    "url": "https://storage.example.com/room1.jpg",
    "alt": "King bed with city view",
    "order": 1
  }
]
```

**Business Rules:**
1. `code` must be unique within a hotel
2. `max_adults + max_children` must equal `max_occupancy`
3. `base_price` must be in hotel's currency
4. At least one bed must be specified in `bed_configuration`
5. Total bed capacity should accommodate `max_occupancy`

**Relationships:**
- Belongs to: `Hotel`
- Has many: `Room`

---

### 2.3 Room Entity

**Purpose**: Represents individual room units

**Attributes:**
| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `id` | UUID | Yes | Auto-generated | Primary key |
| `hotel_id` | UUID | Yes | FK to Hotel | Parent hotel |
| `room_type_id` | UUID | Yes | FK to RoomType | Room type |
| `room_number` | String(20) | Yes | Unique per hotel | Room identifier (e.g., "101", "A-205") |
| `floor` | Integer | No | Can be negative | Floor number (e.g., -1 for basement) |
| `status` | Enum | Yes | Valid status | Operational status |
| `cleaning_status` | Enum | Yes | Valid status | Housekeeping status |
| `features` | JSON Array | No | Array of strings | Room-specific features |
| `notes` | Text | No | Max 1000 chars | Internal notes |
| `is_active` | Boolean | Yes | Default: true | Available for assignment |
| `created_at` | DateTime | Yes | Auto | Creation timestamp |
| `updated_at` | DateTime | Yes | Auto | Last update timestamp |

**Enumerations:**

```
status:
  - "available"     # Ready for guest assignment
  - "occupied"      # Currently occupied by guest
  - "maintenance"   # Under maintenance
  - "blocked"       # Blocked by management
  - "out_of_order"  # Not usable

cleaning_status:
  - "clean"         # Clean and inspected
  - "dirty"         # Needs cleaning
  - "in_progress"   # Currently being cleaned
  - "inspected"     # Cleaned and inspected
```

**Business Rules:**
1. `room_number` must be unique within a hotel
2. Cannot be assigned to reservation if `status != "available"`
3. Cannot be assigned if `is_active = false`
4. `cleaning_status` must be "clean" or "inspected" before guest check-in
5. Room inherits all properties from `room_type_id`

**Relationships:**
- Belongs to: `Hotel`, `RoomType`
- Has many: `Reservation` (through assignments)

---

### 2.4 Guest Entity

**Purpose**: Represents a hotel guest

**Attributes:**
| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `id` | UUID | Yes | Auto-generated | Primary key |
| `user_id` | UUID | No | FK to User | Linked user account (if registered) |
| `first_name` | String(100) | Yes | 1-100 chars | First name |
| `last_name` | String(100) | Yes | 1-100 chars | Last name |
| `email` | String(255) | Yes | Valid email | Email address |
| `phone` | String(20) | Yes | Valid phone format | Phone number with country code |
| `date_of_birth` | Date | No | Past date | Date of birth |
| `nationality` | String(2) | No | ISO 3166-1 alpha-2 | Country code |
| `id_document_type` | Enum | No | Valid type | Document type |
| `id_document_number` | String(50) | No | Encrypted | ID document number |
| `address` | JSON | No | Valid address schema | Home address |
| `preferences` | JSON | No | Valid preferences schema | Guest preferences |
| `loyalty_tier` | Enum | No | Valid tier | Loyalty program tier |
| `loyalty_points` | Integer | Yes | >= 0, Default: 0 | Loyalty points balance |
| `vip_status` | Boolean | Yes | Default: false | VIP flag |
| `notes` | Text | No | Max 2000 chars | Staff notes about guest |
| `created_at` | DateTime | Yes | Auto | Creation timestamp |
| `updated_at` | DateTime | Yes | Auto | Last update timestamp |

**Enumerations:**

```
id_document_type:
  - "passport"
  - "drivers_license"
  - "national_id"
  - "other"

loyalty_tier:
  - "bronze"
  - "silver"
  - "gold"
  - "platinum"
```

**JSON Schemas:**

```json
// preferences schema
{
  "room_floor": "high",  // "high", "low", "no_preference"
  "bed_type": "king",    // "king", "queen", "twin"
  "pillow": "firm",      // "firm", "soft"
  "newspaper": null,
  "dietary": ["vegetarian"],
  "accessibility": ["wheelchair_accessible"]
}
```

**Business Rules:**
1. `email` must be unique across all guests
2. `phone` must include country code (e.g., "+1-555-0123")
3. `id_document_number` must be encrypted at rest
4. If `user_id` exists, guest can access self-service portal
5. Guest must be 18+ years old for primary guest on reservation

**Relationships:**
- Belongs to: `User` (optional)
- Has many: `Reservation`

---

### 2.5 Reservation Entity

**Purpose**: Represents a booking/reservation

**Attributes:**
| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `id` | UUID | Yes | Auto-generated | Primary key |
| `confirmation_number` | String(20) | Yes | Unique, auto-generated | Confirmation code |
| `hotel_id` | UUID | Yes | FK to Hotel | Hotel |
| `guest_id` | UUID | Yes | FK to Guest | Primary guest |
| `room_id` | UUID | No | FK to Room | Assigned room (null until check-in) |
| `room_type_id` | UUID | Yes | FK to RoomType | Requested room type |
| `check_in_date` | Date | Yes | Future or today | Check-in date |
| `check_out_date` | Date | Yes | After check_in_date | Check-out date |
| `nights` | Integer | Yes | Auto-calculated | Number of nights |
| `adults` | Integer | Yes | 1-20 | Number of adults |
| `children` | Integer | Yes | 0-20 | Number of children |
| `status` | Enum | Yes | Valid status | Reservation status |
| `source` | Enum | Yes | Valid source | Booking source |
| `channel` | String(100) | No | If source = "ota" | OTA channel name |
| `rate_per_night` | Decimal(10,2) | Yes | > 0 | Nightly rate |
| `total_room_charges` | Decimal(10,2) | Yes | Auto-calculated | Total room charges |
| `taxes` | Decimal(10,2) | Yes | >= 0 | Total taxes |
| `fees` | Decimal(10,2) | Yes | >= 0, Default: 0 | Additional fees |
| `extras` | Decimal(10,2) | Yes | >= 0, Default: 0 | Extra charges |
| `discounts` | Decimal(10,2) | Yes | >= 0, Default: 0 | Total discounts |
| `total_amount` | Decimal(10,2) | Yes | Auto-calculated | Grand total |
| `deposit_paid` | Decimal(10,2) | Yes | >= 0, Default: 0 | Deposit amount |
| `special_requests` | Text | No | Max 1000 chars | Guest requests |
| `notes` | Text | No | Max 2000 chars | Internal notes |
| `booked_at` | DateTime | Yes | Auto | Booking timestamp |
| `checked_in_at` | DateTime | No | Null until check-in | Check-in timestamp |
| `checked_out_at` | DateTime | No | Null until check-out | Check-out timestamp |
| `cancelled_at` | DateTime | No | Null unless cancelled | Cancellation timestamp |
| `cancellation_reason` | Text | No | Max 500 chars | Cancellation reason |
| `created_at` | DateTime | Yes | Auto | Creation timestamp |
| `updated_at` | DateTime | Yes | Auto | Last update timestamp |

**Enumerations:**

```
status:
  - "pending"         # Awaiting confirmation
  - "confirmed"       # Confirmed booking
  - "checked_in"      # Guest has checked in
  - "checked_out"     # Guest has checked out
  - "cancelled"       # Cancelled by guest or hotel
  - "no_show"         # Guest didn't show up

source:
  - "direct"          # Direct booking (website, phone)
  - "ota"             # Online travel agency
  - "gds"             # Global distribution system
  - "walkin"          # Walk-in guest
  - "corporate"       # Corporate booking
  - "voice"           # AI voice agent (F-009)
  - "chatbot"         # AI chatbot (F-004)
```

**Business Rules:**
1. `check_out_date` must be after `check_in_date`
2. `nights` = difference between check-out and check-in dates
3. `total_room_charges` = `rate_per_night` × `nights`
4. `total_amount` = `total_room_charges` + `taxes` + `fees` + `extras` - `discounts`
5. `adults + children` must not exceed room type `max_occupancy`
6. Cannot create overlapping reservations for same room
7. `confirmation_number` must be 8-12 alphanumeric characters, unique
8. Room cannot be assigned until `room_id` is set
9. Status transitions:
   - `pending` → `confirmed` → `checked_in` → `checked_out`
   - Any status → `cancelled` (except `checked_out`)
   - `confirmed` → `no_show` (after check-in date passes)

**Relationships:**
- Belongs to: `Hotel`, `Guest`, `Room` (optional), `RoomType`
- Has many: `Payment`

---

### 2.6 Staff Entity

**Purpose**: Represents hotel staff members

**Attributes:**
| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `id` | UUID | Yes | Auto-generated | Primary key |
| `user_id` | UUID | Yes | FK to User | User account |
| `hotel_id` | UUID | Yes | FK to Hotel | Hotel |
| `employee_id` | String(50) | No | Unique per hotel | Employee number |
| `role` | Enum | Yes | Valid role | Staff role |
| `department` | String(100) | No | Max 100 chars | Department name |
| `shift` | JSON | No | Valid shift schema | Work schedule |
| `is_active` | Boolean | Yes | Default: true | Active employment status |
| `hired_at` | Date | Yes | Past or today | Hire date |
| `terminated_at` | Date | No | After hired_at | Termination date |
| `created_at` | DateTime | Yes | Auto | Creation timestamp |
| `updated_at` | DateTime | Yes | Auto | Last update timestamp |

**Enumerations:**

```
role:
  - "admin"              # Full system access
  - "manager"            # Hotel manager
  - "front_desk"         # Front desk staff
  - "housekeeping"       # Housekeeping staff
  - "housekeeping_supervisor"  # Housekeeping supervisor
  - "maintenance"        # Maintenance staff
  - "accountant"         # Finance/accounting
  - "guest_services"     # Guest services
```

**JSON Schemas:**

```json
// shift schema
{
  "type": "rotating",  // "fixed", "rotating", "flexible"
  "schedule": {
    "monday": {"start": "08:00", "end": "16:00"},
    "tuesday": {"start": "08:00", "end": "16:00"},
    "wednesday": {"start": "08:00", "end": "16:00"},
    "thursday": {"start": "08:00", "end": "16:00"},
    "friday": {"start": "08:00", "end": "16:00"},
    "saturday": "off",
    "sunday": "off"
  }
}
```

**Business Rules:**
1. Each staff member must have a `user_id` for authentication
2. `employee_id` must be unique within a hotel
3. Cannot delete staff, only deactivate (`is_active = false`)
4. `role` determines permissions in the system
5. Multiple staff members can have same `role`

**Relationships:**
- Belongs to: `Hotel`, `User`

---

## 3. API Endpoint Specifications

### 3.1 Hotel Endpoints

#### GET `/api/v1/hotels`
**Purpose**: List all hotels (for admin/multi-hotel management)
**Auth**: Required (admin only)
**Query Parameters**:
- `page` (integer, default: 1)
- `page_size` (integer, default: 20, max: 100)
- `is_active` (boolean, optional)
- `search` (string, optional) - searches name, slug

**Response** (200 OK):
```json
{
  "count": 42,
  "next": "https://api.stayfull.com/api/v1/hotels?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "name": "Grand Plaza Hotel",
      "slug": "grand-plaza-hotel",
      "type": "independent",
      "city": "New York",
      "total_rooms": 150,
      "is_active": true,
      "created_at": "2025-10-22T10:00:00Z"
    }
  ]
}
```

#### GET `/api/v1/hotels/{hotel_id}`
**Purpose**: Get hotel details
**Auth**: Required (staff of hotel)
**Path Parameters**: `hotel_id` (UUID)
**Response** (200 OK):
```json
{
  "id": "uuid",
  "name": "Grand Plaza Hotel",
  "slug": "grand-plaza-hotel",
  "brand": null,
  "type": "independent",
  "address": { ... },
  "contact": { ... },
  "timezone": "America/New_York",
  "currency": "USD",
  "languages": ["en", "es"],
  "check_in_time": "15:00",
  "check_out_time": "11:00",
  "total_rooms": 150,
  "settings": { ... },
  "is_active": true,
  "created_at": "2025-10-22T10:00:00Z",
  "updated_at": "2025-10-22T10:00:00Z"
}
```

#### POST `/api/v1/hotels`
**Purpose**: Create new hotel
**Auth**: Required (super admin only)
**Request Body**:
```json
{
  "name": "Grand Plaza Hotel",
  "type": "independent",
  "address": {
    "street_address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "US"
  },
  "contact": {
    "phone": "+1-555-0123",
    "email": "info@grandplaza.com",
    "website": "https://grandplaza.com"
  },
  "timezone": "America/New_York",
  "currency": "USD",
  "languages": ["en"],
  "check_in_time": "15:00",
  "check_out_time": "11:00",
  "total_rooms": 150
}
```
**Response** (201 Created): Full hotel object

**Validation Errors** (400 Bad Request):
```json
{
  "errors": {
    "name": ["This field is required."],
    "email": ["Enter a valid email address."]
  }
}
```

#### PATCH `/api/v1/hotels/{hotel_id}`
**Purpose**: Update hotel details
**Auth**: Required (hotel manager/admin)
**Request Body**: Partial hotel object
**Response** (200 OK): Full updated hotel object

#### DELETE `/api/v1/hotels/{hotel_id}`
**Purpose**: Soft delete hotel (sets is_active = false)
**Auth**: Required (super admin only)
**Response** (204 No Content)

---

### 3.2 RoomType Endpoints

#### GET `/api/v1/hotels/{hotel_id}/room-types`
**Purpose**: List room types for a hotel
**Auth**: Required (any staff or public for availability)
**Query Parameters**:
- `is_active` (boolean, optional)
- `min_occupancy` (integer, optional)
- `max_price` (decimal, optional)

**Response** (200 OK):
```json
{
  "results": [
    {
      "id": "uuid",
      "name": "Deluxe King",
      "code": "DLX-K",
      "description": "Spacious room with king bed...",
      "max_occupancy": 2,
      "base_price": "199.00",
      "size_sqm": "35.00",
      "amenities": ["wifi", "tv", "mini_fridge"],
      "images": [...],
      "is_active": true
    }
  ]
}
```

#### POST `/api/v1/hotels/{hotel_id}/room-types`
**Purpose**: Create room type
**Auth**: Required (hotel manager/admin)
**Request Body**: RoomType object
**Response** (201 Created)

#### PATCH `/api/v1/hotels/{hotel_id}/room-types/{room_type_id}`
**Purpose**: Update room type
**Auth**: Required (hotel manager/admin)
**Response** (200 OK)

---

### 3.3 Room Endpoints

#### GET `/api/v1/hotels/{hotel_id}/rooms`
**Purpose**: List rooms
**Auth**: Required (hotel staff)
**Query Parameters**:
- `room_type_id` (UUID, optional)
- `status` (string, optional)
- `floor` (integer, optional)

**Response** (200 OK):
```json
{
  "results": [
    {
      "id": "uuid",
      "room_number": "101",
      "room_type": {
        "id": "uuid",
        "name": "Standard Queen"
      },
      "floor": 1,
      "status": "available",
      "cleaning_status": "clean",
      "is_active": true
    }
  ]
}
```

#### POST `/api/v1/hotels/{hotel_id}/rooms`
**Purpose**: Create room
**Auth**: Required (hotel manager/admin)
**Response** (201 Created)

#### PATCH `/api/v1/hotels/{hotel_id}/rooms/{room_id}/status`
**Purpose**: Update room status
**Auth**: Required (hotel staff)
**Request Body**:
```json
{
  "status": "maintenance",
  "cleaning_status": "dirty",
  "notes": "AC unit needs repair"
}
```
**Response** (200 OK)

---

### 3.4 Guest Endpoints

#### GET `/api/v1/guests`
**Purpose**: Search guests (hotel-scoped)
**Auth**: Required (hotel staff)
**Query Parameters**:
- `search` (string) - searches name, email, phone
- `email` (string, exact match)

**Response** (200 OK): List of guests

#### POST `/api/v1/guests`
**Purpose**: Create guest
**Auth**: Required (hotel staff or public for self-registration)
**Request Body**: Guest object
**Response** (201 Created)

#### GET `/api/v1/guests/{guest_id}`
**Purpose**: Get guest details
**Auth**: Required (hotel staff or guest themselves)
**Response** (200 OK)

#### PATCH `/api/v1/guests/{guest_id}`
**Purpose**: Update guest
**Auth**: Required (hotel staff or guest themselves)
**Response** (200 OK)

---

### 3.5 Reservation Endpoints

#### GET `/api/v1/hotels/{hotel_id}/reservations`
**Purpose**: List reservations
**Auth**: Required (hotel staff)
**Query Parameters**:
- `status` (string, optional)
- `check_in_date` (date, optional)
- `check_out_date` (date, optional)
- `guest_id` (UUID, optional)
- `room_id` (UUID, optional)

**Response** (200 OK):
```json
{
  "results": [
    {
      "id": "uuid",
      "confirmation_number": "ABC123XYZ",
      "guest": {
        "id": "uuid",
        "name": "John Doe",
        "email": "john@example.com"
      },
      "room_type": {
        "id": "uuid",
        "name": "Deluxe King"
      },
      "room_number": "205",
      "check_in_date": "2025-11-01",
      "check_out_date": "2025-11-03",
      "nights": 2,
      "adults": 2,
      "children": 0,
      "status": "confirmed",
      "total_amount": "498.00",
      "booked_at": "2025-10-22T14:30:00Z"
    }
  ]
}
```

#### POST `/api/v1/hotels/{hotel_id}/reservations`
**Purpose**: Create reservation
**Auth**: Required (hotel staff or public for booking)
**Request Body**:
```json
{
  "guest_id": "uuid",
  "room_type_id": "uuid",
  "check_in_date": "2025-11-01",
  "check_out_date": "2025-11-03",
  "adults": 2,
  "children": 0,
  "rate_per_night": "199.00",
  "special_requests": "Early check-in if possible",
  "source": "direct"
}
```
**Response** (201 Created): Full reservation object with confirmation number

**Business Logic**:
1. Validate availability for room type and dates
2. Auto-generate confirmation number
3. Calculate nights, total charges, taxes
4. Set status to "pending" or "confirmed" based on payment
5. Send confirmation email (async)

#### GET `/api/v1/hotels/{hotel_id}/reservations/{reservation_id}`
**Purpose**: Get reservation details
**Auth**: Required (hotel staff or guest themselves)
**Response** (200 OK)

#### PATCH `/api/v1/hotels/{hotel_id}/reservations/{reservation_id}`
**Purpose**: Update reservation
**Auth**: Required (hotel staff)
**Allowed updates**:
- Dates (if no conflicts)
- Guest details
- Room assignment
- Special requests
- Notes

**Response** (200 OK)

#### POST `/api/v1/hotels/{hotel_id}/reservations/{reservation_id}/check-in`
**Purpose**: Check in guest
**Auth**: Required (hotel staff)
**Request Body**:
```json
{
  "room_id": "uuid",
  "actual_check_in_time": "2025-11-01T14:00:00Z",
  "notes": "Guest arrived early"
}
```
**Response** (200 OK)

**Business Logic**:
1. Validate room is available and clean
2. Assign room to reservation
3. Update status to "checked_in"
4. Record check-in timestamp
5. Update room status to "occupied"
6. Trigger F-022 (Smart Room): Send digital key if enabled

#### POST `/api/v1/hotels/{hotel_id}/reservations/{reservation_id}/check-out`
**Purpose**: Check out guest
**Auth**: Required (hotel staff)
**Request Body**:
```json
{
  "actual_check_out_time": "2025-11-03T10:30:00Z",
  "final_charges": "25.00",
  "notes": "Minibar charges"
}
```
**Response** (200 OK)

**Business Logic**:
1. Add any final charges (extras)
2. Calculate final total
3. Update status to "checked_out"
4. Record check-out timestamp
5. Update room status to "available", cleaning_status to "dirty"
6. Trigger housekeeping task (future feature)
7. Send receipt email (async)

#### POST `/api/v1/hotels/{hotel_id}/reservations/{reservation_id}/cancel`
**Purpose**: Cancel reservation
**Auth**: Required (hotel staff or guest)
**Request Body**:
```json
{
  "cancellation_reason": "Guest changed plans",
  "refund_amount": "498.00"
}
```
**Response** (200 OK)

**Business Logic**:
1. Validate cancellation allowed (based on policy)
2. Calculate refund amount (if applicable)
3. Update status to "cancelled"
4. Record cancellation timestamp
5. Release room assignment
6. Process refund (future: integrate with payments)
7. Send cancellation confirmation email

---

### 3.6 Availability Endpoint

#### POST `/api/v1/hotels/{hotel_id}/check-availability`
**Purpose**: Check room availability for dates
**Auth**: Public or authenticated
**Request Body**:
```json
{
  "check_in_date": "2025-11-01",
  "check_out_date": "2025-11-03",
  "adults": 2,
  "children": 0,
  "room_type_id": "uuid"  // optional, checks specific type
}
```

**Response** (200 OK):
```json
{
  "available": true,
  "room_types": [
    {
      "id": "uuid",
      "name": "Standard Queen",
      "available_rooms": 5,
      "rate": "149.00",
      "total": "298.00"
    },
    {
      "id": "uuid",
      "name": "Deluxe King",
      "available_rooms": 3,
      "rate": "199.00",
      "total": "398.00"
    }
  ]
}
```

**Business Logic**:
1. Query rooms of requested type (or all types)
2. Filter out rooms with overlapping reservations
3. Filter out rooms with status != "available"
4. Return available count per room type
5. Apply dynamic pricing if F-005 is enabled (future)

---

## 4. Test Scenarios

### 4.1 Hotel Management Tests

**Test**: Create hotel with valid data
- Given: Valid hotel data
- When: POST /api/v1/hotels
- Then: Hotel created, returns 201, auto-generates slug

**Test**: Create hotel with duplicate name
- Given: Hotel with same name exists
- When: POST /api/v1/hotels with duplicate name
- Then: Returns 400, error message "Hotel name already exists"

**Test**: Update hotel check-in time
- Given: Existing hotel
- When: PATCH /api/v1/hotels/{id} with new check_in_time
- Then: Hotel updated, returns 200

**Test**: Cannot set check_out before check_in
- Given: Existing hotel
- When: PATCH with check_out_time = "10:00", check_in_time = "15:00"
- Then: Returns 400, validation error

---

### 4.2 Room Type Tests

**Test**: Create room type with valid data
- Given: Valid room type data for existing hotel
- When: POST /api/v1/hotels/{hotel_id}/room-types
- Then: Room type created, returns 201

**Test**: Room type code must be unique per hotel
- Given: Room type with code "DLX" exists
- When: Create another with same code
- Then: Returns 400, error "Code already exists"

**Test**: Max occupancy validation
- Given: max_adults=2, max_children=1
- When: max_occupancy=2 (should be 3)
- Then: Returns 400, validation error

---

### 4.3 Room Management Tests

**Test**: Create room with valid data
- Given: Valid room data, existing hotel and room type
- When: POST /api/v1/hotels/{hotel_id}/rooms
- Then: Room created, returns 201, default status="available"

**Test**: Room number must be unique per hotel
- Given: Room "101" exists
- When: Create another room "101"
- Then: Returns 400, error

**Test**: Update room status
- Given: Room with status="available"
- When: PATCH room status to "maintenance"
- Then: Status updated, returns 200

**Test**: Cannot assign dirty room to guest
- Given: Room with cleaning_status="dirty"
- When: Attempt check-in
- Then: Returns 400, error "Room must be cleaned first"

---

### 4.4 Guest Management Tests

**Test**: Create guest with valid data
- Given: Valid guest data
- When: POST /api/v1/guests
- Then: Guest created, returns 201, id_document encrypted

**Test**: Email must be unique
- Given: Guest with email "john@example.com" exists
- When: Create guest with same email
- Then: Returns 400, error

**Test**: Update guest preferences
- Given: Existing guest
- When: PATCH guest preferences
- Then: Preferences updated, returns 200

**Test**: Guest must be 18+ for primary reservation
- Given: Guest with date_of_birth = 2010-01-01
- When: Create reservation with this guest as primary
- Then: Returns 400, error "Primary guest must be 18+"

---

### 4.5 Reservation Tests

**Test**: Create reservation with available room type
- Given: Hotel with available rooms for dates
- When: POST reservation
- Then: Reservation created, confirmation number generated, returns 201

**Test**: Calculate nights correctly
- Given: check_in="2025-11-01", check_out="2025-11-05"
- When: Create reservation
- Then: nights=4

**Test**: Calculate total correctly
- Given: rate_per_night=199, nights=2, taxes=50, fees=10
- When: Create reservation
- Then: total_amount=498 (room) + 50 + 10 = 558

**Test**: Cannot create overlapping reservation
- Given: Reservation for room "101" from Nov 1-3
- When: Create reservation for same room Nov 2-4
- Then: Returns 409, error "Room not available for these dates"

**Test**: Occupancy validation
- Given: Room type with max_occupancy=2
- When: Create reservation with adults=2, children=1 (total=3)
- Then: Returns 400, error "Exceeds maximum occupancy"

**Test**: Check-in flow
- Given: Reservation status="confirmed", room is "available" and "clean"
- When: POST check-in with room_id
- Then: status="checked_in", room assigned, room status="occupied"

**Test**: Cannot check-in to dirty room
- Given: Room with cleaning_status="dirty"
- When: Attempt check-in
- Then: Returns 400, error

**Test**: Check-out flow
- Given: Reservation status="checked_in"
- When: POST check-out
- Then: status="checked_out", room status="available", cleaning_status="dirty"

**Test**: Cancel reservation
- Given: Reservation status="confirmed"
- When: POST cancel
- Then: status="cancelled", room released

**Test**: Cannot cancel checked-out reservation
- Given: Reservation status="checked_out"
- When: POST cancel
- Then: Returns 400, error

---

### 4.6 Availability Tests

**Test**: Check availability for available dates
- Given: Hotel with 5 rooms of type "Standard"
- And: 2 rooms already booked for Nov 1-3
- When: Check availability for Nov 1-3
- Then: Returns available=true, available_rooms=3

**Test**: No availability when fully booked
- Given: All rooms booked for dates
- When: Check availability
- Then: Returns available=false

**Test**: Room in maintenance excluded from availability
- Given: Room with status="maintenance"
- When: Check availability
- Then: Room not counted in available rooms

---

### 4.7 Multi-tenancy Tests

**Test**: Hotel staff can only see their hotel's data
- Given: Staff member for Hotel A
- When: GET /api/v1/hotels/{hotel_b_id}/rooms
- Then: Returns 403 Forbidden

**Test**: Guest can only see their own reservations
- Given: Guest with reservation at Hotel A
- When: GET reservations for Hotel A
- Then: Returns only their own reservations

**Test**: Admin can see all hotels
- Given: Super admin user
- When: GET /api/v1/hotels
- Then: Returns all hotels

---

## 5. Integration Points

### 5.1 Integration with F-002 (AI Onboarding Agent)
- **Hotel creation**: AI agent calls POST /api/v1/hotels during onboarding
- **Room type setup**: AI extracts room types from conversation, creates via API
- **Room creation**: AI generates rooms based on room types and quantities
- **Validation**: AI validates all data before submission

### 5.2 Integration with F-003 (Dynamic Commerce Engine)
- **Availability check**: Website calls check-availability endpoint
- **Guest creation**: Self-service booking creates guest record
- **Reservation creation**: Direct bookings via API
- **Confirmation**: Returns confirmation number for display

### 5.3 Integration with F-004 (AI Chat Bot)
- **Guest queries**: Chatbot queries reservation status
- **Booking modifications**: Chatbot can update reservations
- **Information retrieval**: Chatbot fetches hotel info, room types

### 5.4 Integration with F-005 (AI Dynamic Pricing)
- **Rate updates**: Pricing engine updates room_type base_price
- **Dynamic rates**: check-availability returns AI-adjusted rates
- **Historical data**: Pricing engine analyzes past reservations

### 5.5 Integration with F-009 (AI Voice Agent)
- **Voice bookings**: Creates reservations with source="voice"
- **Availability queries**: Real-time availability checks
- **Modification requests**: Updates via API

### 5.6 Integration with F-010 (Unified Inbox)
- **Reservation context**: Links messages to reservation_id
- **Guest context**: Links messages to guest_id
- **Status updates**: Notifies guests of reservation changes

### 5.7 Integration with F-022 (Smart Room Automation)
- **Check-in trigger**: On check-in, sends digital key via Seam.co
- **Pre-arrival**: Sets thermostat before arrival
- **Check-out trigger**: Deactivates access codes
- **Housekeeping**: Updates cleaning status from IoT sensors

### 5.8 Integration with Stripe (Payments)
- **Deposit collection**: Charges deposit_paid amount
- **Final payment**: Charges remaining balance at check-out
- **Refunds**: Processes cancellation refunds

---

## 6. Success Criteria

### 6.1 Functional Requirements
- ✅ All CRUD operations work for all entities
- ✅ Multi-tenancy: Data isolation verified
- ✅ Role-based access control enforced
- ✅ Availability algorithm accurate (no double-booking)
- ✅ Business rules enforced (validation)
- ✅ API returns correct HTTP status codes
- ✅ Django Admin interface functional

### 6.2 Non-Functional Requirements
- ✅ Test coverage: >80%
- ✅ API response time: <200ms p95
- ✅ Database queries optimized (N+1 avoided)
- ✅ API documentation complete (OpenAPI/Swagger)
- ✅ All endpoints have integration tests
- ✅ All models have unit tests

### 6.3 Quality Gates
- ✅ All tests passing
- ✅ No security vulnerabilities (bandit scan)
- ✅ Code follows PEP 8 (flake8)
- ✅ No type errors (mypy)
- ✅ Documentation complete

---

## 7. Data Migration & Seeding

### 7.1 Initial Data
- Create sample hotel for development
- Create room types (Standard, Deluxe, Suite)
- Create 50 rooms across types
- Create sample guests
- Create test reservations

### 7.2 Migration Strategy
- Use Django migrations for schema changes
- Provide rollback scripts
- Test migrations on staging before production

---

## 8. Acceptance Criteria

### 8.1 Definition of Done
- [ ] All domain models created with migrations
- [ ] All API endpoints implemented
- [ ] All test scenarios passing (>80% coverage)
- [ ] Django Admin configured for all models
- [ ] API documentation generated (drf-spectacular)
- [ ] Integration tests written
- [ ] Code reviewed and approved
- [ ] Deployed to staging
- [ ] Manual QA completed
- [ ] Performance benchmarks met

### 8.2 Demo Scenario
1. Create hotel via Django Admin
2. Create room types and rooms
3. Create guest via API
4. Check availability via API
5. Create reservation via API
6. Check-in guest via API
7. Check-out guest via API
8. Verify room status updated

---

## 9. Dependencies

### 9.1 External Dependencies
- Django 5.x
- Django REST Framework
- PostgreSQL (Supabase)
- pytest + pytest-django

### 9.2 Feature Dependencies
- Must be completed before:
  - F-002: AI Onboarding Agent
  - F-003: Dynamic Commerce Engine
  - F-004: AI Chat Bot
  - All other features depend on PMS Core

---

## 10. Risks & Mitigation

### 10.1 Risks
1. **Risk**: Availability algorithm complex, may have edge cases
   - **Mitigation**: Extensive test scenarios, stress testing

2. **Risk**: Multi-tenancy data leakage
   - **Mitigation**: Row-level security tests, security audit

3. **Risk**: Performance issues with large datasets
   - **Mitigation**: Database indexing, query optimization, caching

### 10.2 Assumptions
- Supabase PostgreSQL is available and configured
- Development environment has Python 3.13.7
- All third-party integrations will be added in later phases

---

## 11. Timeline

**Estimated Effort**: 2-3 weeks

**Week 1**:
- Models and migrations
- Django admin setup
- Basic CRUD endpoints
- Unit tests

**Week 2**:
- Complex endpoints (availability, check-in/out)
- Business logic implementation
- Integration tests
- Bug fixes

**Week 3** (if needed):
- Performance optimization
- Additional test coverage
- Documentation
- Deployment preparation

---

## 12. Notes for Developer

### 12.1 Implementation Guidelines
- Use Django's built-in UUID field for primary keys
- Use `JSONField` for flexible data (address, preferences, etc.)
- Implement soft deletes (is_active) instead of hard deletes
- Use Django's timezone-aware datetime fields
- Add database indexes on foreign keys and frequently queried fields
- Use Django REST Framework serializers for validation
- Implement proper exception handling and error responses
- Use Django signals for side effects (e.g., send email on reservation)

### 12.2 Security Considerations
- Encrypt `id_document_number` field at rest
- Implement rate limiting on API endpoints
- Validate all user input
- Use Django's CSRF protection
- Implement proper authentication/authorization
- Sanitize all output to prevent XSS
- Use parameterized queries (Django ORM handles this)

### 12.3 Performance Optimization
- Use `select_related()` and `prefetch_related()` to avoid N+1 queries
- Add database indexes on:
  - hotel_id (all tables)
  - guest.email
  - reservation.confirmation_number
  - reservation.check_in_date, check_out_date
  - room.room_number, hotel_id
- Use Redis caching for:
  - Hotel settings
  - Room type details
  - Availability queries (short TTL)

---

**End of Specification**

This specification should provide complete guidance for implementing F-001: Stayfull PMS Core. All implementation decisions should refer back to this document.
