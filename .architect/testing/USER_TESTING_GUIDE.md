# 🧑‍💻 F-001 User Testing Guide

**Version**: 1.0
**Date**: 2025-10-23
**Environment**: Production (Railway)
**URL**: https://web-production-2765.up.railway.app
**Estimated Testing Time**: 30-45 minutes

---

## 📋 Overview

This guide walks you through comprehensive user acceptance testing (UAT) for **F-001: Stayfull PMS Core**.

### What You'll Test
1. Django Admin Panel (back-office operations)
2. API Endpoints (via Swagger UI)
3. Core hotel management workflows
4. Data integrity and security features

### Prerequisites
- Access to: https://web-production-2765.up.railway.app
- Admin credentials: `admin` / `Stayfull2025!`
- Basic understanding of hotel operations

---

## 🎯 Testing Objectives

By the end of this testing session, you should validate:

✅ **Functionality**: All features work as expected
✅ **Usability**: Admin interface is intuitive and efficient
✅ **Data Integrity**: No data loss, proper relationships maintained
✅ **Security**: PII encryption, authentication, permissions work
✅ **Performance**: System responds quickly (< 2 seconds for most operations)

---

## 🧪 Test Scenarios

### **Scenario 1: Initial System Access & Setup** (5 minutes)

#### 1.1 First-Time Login
**Goal**: Verify admin access and change default password.

**Steps**:
1. Navigate to: https://web-production-2765.up.railway.app/admin/
2. Login with:
   - Username: `admin`
   - Password: `Stayfull2025!`
3. **IMMEDIATELY** change password:
   - Click your username (top right) → "Change password"
   - Enter current password: `Stayfull2025!`
   - Enter new secure password (twice)
   - Click "Change my password"

**Expected Result**:
- ✅ Login successful
- ✅ Password changed successfully
- ✅ Redirected to Django Admin dashboard

**What to Check**:
- Admin interface loads cleanly (CSS/JS working)
- Navigation menu visible on left
- Welcome message shows your username

---

#### 1.2 Verify Test Data
**Goal**: Confirm auto-created test data exists.

**Steps**:
1. In Django Admin, click "Hotels" → "Hotels"
2. Verify you see: **"Test Grand Hotel"**
3. Click "Room types" → "Room types"
4. Verify you see:
   - **Standard Room** ($99)
   - **Deluxe Suite** ($199)
5. Click "Rooms" → "Rooms"
6. Verify you see 10 rooms (101-105, 201-205)

**Expected Result**:
- ✅ 1 hotel exists
- ✅ 2 room types exist
- ✅ 10 rooms exist
- ✅ All data displays correctly in list view

**Screenshot Checkpoints**:
- [ ] Hotel list view
- [ ] Room type list with prices visible

---

### **Scenario 2: Hotel Management** (10 minutes)

#### 2.1 Create a New Hotel
**Goal**: Test creating a hotel from scratch.

**Steps**:
1. Navigate to "Hotels" → "Hotels"
2. Click "ADD HOTEL +" (top right)
3. Fill in the form:
   - **Name**: "Stayfull Demo Hotel"
   - **Type**: Independent
   - **Total rooms**: 25
   - **Check-in time**: 15:00:00
   - **Check-out time**: 11:00:00
   - **Timezone**: America/New_York
   - **Currency**: USD
   - **Languages**: en (type and press enter)
   - **Address (JSON)**:
     ```json
     {
       "street": "456 Demo Avenue",
       "city": "San Francisco",
       "state": "CA",
       "country": "US",
       "postal_code": "94102"
     }
     ```
   - **Contact (JSON)**:
     ```json
     {
       "phone": "+1-555-0199",
       "email": "info@stayfulldemo.com"
     }
     ```
4. Click "SAVE"

**Expected Result**:
- ✅ Hotel saved successfully
- ✅ Success message appears
- ✅ Redirected to hotel list showing new hotel

**What to Check**:
- All fields saved correctly
- JSON fields formatted properly
- Hotel appears in list view

---

#### 2.2 Edit Existing Hotel
**Goal**: Test updating hotel information.

**Steps**:
1. Click on "Test Grand Hotel" from the list
2. Change **Total rooms** from 50 to 60
3. Add a new language: `es` (Spanish)
4. Click "SAVE"

**Expected Result**:
- ✅ Changes saved successfully
- ✅ Updated values visible in list view

---

#### 2.3 Bulk Actions (Optional)
**Goal**: Test admin bulk operations.

**Steps**:
1. Select both hotels (checkboxes)
2. Action dropdown: "Delete selected hotels"
3. Click "Go"
4. **CANCEL** (don't actually delete)

**Expected Result**:
- ✅ Confirmation page appears
- ✅ Shows correct count of items to delete

---

### **Scenario 3: Room Type & Room Management** (10 minutes)

#### 3.1 Create Room Type for Your New Hotel
**Goal**: Test room type creation with complex data.

**Steps**:
1. Navigate to "Room types" → "Room types"
2. Click "ADD ROOM TYPE +"
3. Fill in:
   - **Hotel**: Stayfull Demo Hotel (dropdown)
   - **Name**: Ocean View Suite
   - **Code**: OVS
   - **Description**: Luxury suite with ocean views and balcony
   - **Base price**: 299.00
   - **Max occupancy**: 3
   - **Max adults**: 2
   - **Max children**: 2
   - **Size sqm**: 55.0
   - **Bed configuration (JSON)**:
     ```json
     {
       "beds": [
         {"type": "King", "count": 1},
         {"type": "Sofa Bed", "count": 1}
       ]
     }
     ```
   - **Amenities (JSON Array)**:
     ```json
     ["WiFi", "TV", "Air Conditioning", "Ocean View", "Balcony", "Mini Bar", "Safe"]
     ```
4. Click "SAVE"

**Expected Result**:
- ✅ Room type created successfully
- ✅ All fields saved correctly
- ✅ JSON fields validated and formatted

**What to Check**:
- Price displays with 2 decimal places
- Hotel association correct
- Amenities list visible

---

#### 3.2 Create Rooms for Your Room Type
**Goal**: Test batch room creation workflow.

**Steps**:
1. Navigate to "Rooms" → "Rooms"
2. Create 3 rooms:

   **Room 1**:
   - Hotel: Stayfull Demo Hotel
   - Room number: 301
   - Room type: Ocean View Suite
   - Floor: 3
   - Status: available
   - Cleaning status: clean
   - Click "SAVE and add another"

   **Room 2**:
   - Hotel: Stayfull Demo Hotel
   - Room number: 302
   - Room type: Ocean View Suite
   - Floor: 3
   - Status: available
   - Cleaning status: clean
   - Click "SAVE and add another"

   **Room 3**:
   - Hotel: Stayfull Demo Hotel
   - Room number: 303
   - Room type: Ocean View Suite
   - Floor: 3
   - Status: maintenance (test different status)
   - Cleaning status: dirty (test different status)
   - Click "SAVE"

**Expected Result**:
- ✅ All 3 rooms created successfully
- ✅ Room statuses visible in list
- ✅ Can filter by hotel, status, floor

**What to Check**:
- Room numbers are unique per hotel
- Status fields have correct choices
- List view shows room type name

---

### **Scenario 4: Guest Management** (10 minutes)

#### 4.1 Create Guest with PII Encryption
**Goal**: Test guest creation and verify ID document encryption.

**Steps**:
1. Navigate to "Guests" → "Guests"
2. Click "ADD GUEST +"
3. Fill in:
   - **First name**: Sarah
   - **Last name**: Johnson
   - **Email**: sarah.johnson@example.com
   - **Phone**: +1-555-0250
   - **Date of birth**: 1990-03-15
   - **Nationality**: US
   - **ID document type**: passport
   - **ID document number**: XY9876543 (⚠️ This will be encrypted!)
   - **Account status**: active
   - **Loyalty tier**: silver
   - **Loyalty points**: 100
   - **Preferences (JSON)**:
     ```json
     {
       "room_type": "non-smoking",
       "floor": "high",
       "special_requests": "Extra pillows, late check-in"
     }
     ```
4. Click "SAVE"

**Expected Result**:
- ✅ Guest created successfully
- ✅ ID document number is stored encrypted in database
- ✅ When viewing guest, ID shows as encrypted hash (not plain text)

**What to Check**:
- Email is unique (try creating duplicate)
- Full name computed correctly (display shows "Sarah Johnson")
- Loyalty tier affects UI display

---

#### 4.2 Search and Filter Guests
**Goal**: Test admin search and filtering.

**Steps**:
1. In guest list, use search box: type "Sarah"
2. Expected: Guest appears
3. Use filters (right sidebar):
   - Filter by: Loyalty tier = Silver
   - Filter by: Account status = Active
4. Click "Apply"

**Expected Result**:
- ✅ Search works by name, email
- ✅ Filters narrow results correctly
- ✅ Results update instantly

---

### **Scenario 5: Reservation Management** (15 minutes)

#### 5.1 Create Complete Reservation
**Goal**: Test end-to-end reservation flow.

**Steps**:
1. Navigate to "Reservations" → "Reservations"
2. Click "ADD RESERVATION +"
3. Fill in:
   - **Hotel**: Stayfull Demo Hotel
   - **Room**: 301 (Ocean View Suite)
   - **Guest**: Sarah Johnson (select from dropdown)
   - **Check-in date**: Tomorrow's date (e.g., 2025-10-24)
   - **Check-out date**: 3 days later (e.g., 2025-10-27)
   - **Number of adults**: 2
   - **Number of children**: 0
   - **Total price**: 897.00 (3 nights × $299)
   - **Status**: confirmed
   - **Payment status**: paid
   - **Booking source**: direct
   - **Special requests (JSON Array)**:
     ```json
     ["Late check-in (9 PM)", "Extra pillows", "Wake-up call at 7 AM"]
     ```
4. Click "SAVE"

**Expected Result**:
- ✅ Reservation created successfully
- ✅ Room marked as occupied (auto-calculated?)
- ✅ Total price matches calculation
- ✅ Success message confirms confirmation number

**What to Check**:
- Confirmation number generated automatically
- Check-out date must be after check-in date (validation)
- Guest can't double-book same dates (business rule)

---

#### 5.2 Test Check-In Process
**Goal**: Simulate front desk check-in.

**Steps**:
1. Click on the reservation you just created
2. Change **Status** from "confirmed" to "checked_in"
3. Note the **Actual check-in** timestamp (should auto-populate)
4. Click "SAVE"

**Expected Result**:
- ✅ Status updated to "checked_in"
- ✅ Actual check-in timestamp recorded
- ✅ Room status may update (if implemented)

---

#### 5.3 Test Check-Out Process
**Goal**: Simulate guest check-out.

**Steps**:
1. Edit the same reservation
2. Change **Status** from "checked_in" to "checked_out"
3. Note the **Actual check-out** timestamp
4. Change **Payment status** to "refunded" (if needed) or leave as "paid"
5. Click "SAVE"

**Expected Result**:
- ✅ Status updated to "checked_out"
- ✅ Actual check-out timestamp recorded
- ✅ Room becomes available again (if cleaning status = clean)

---

#### 5.4 Test Cancellation Workflow
**Goal**: Test canceling a reservation.

**Steps**:
1. Create a new reservation (any future dates)
2. Change **Status** to "cancelled"
3. Change **Payment status** to "refunded"
4. Click "SAVE"

**Expected Result**:
- ✅ Reservation cancelled
- ✅ Room availability restored
- ✅ Cancellation visible in list view

---

### **Scenario 6: Staff Management** (5 minutes)

#### 6.1 Create Staff Member
**Goal**: Test staff creation and permissions.

**Steps**:
1. First, create a Django user:
   - Navigate to "Authentication and Authorization" → "Users"
   - Click "ADD USER +"
   - Username: `front_desk_1`
   - Password: `TestPassword123!` (enter twice)
   - Click "SAVE"
   - Add details:
     - First name: Maria
     - Last name: Rodriguez
     - Email: maria@stayfulldemo.com
   - **DO NOT** check "Staff status" or "Superuser status"
   - Click "SAVE"

2. Now create Staff profile:
   - Navigate to "Staff" → "Staff"
   - Click "ADD STAFF +"
   - Fill in:
     - **User**: front_desk_1 (dropdown)
     - **Hotel**: Stayfull Demo Hotel
     - **Role**: front_desk
     - **Employee ID**: FD001
     - **Phone**: +1-555-0300
     - **Is active**: Checked
     - **Permissions (JSON Array)**:
       ```json
       ["view_reservations", "create_reservations", "check_in_guest", "check_out_guest"]
       ```
   - Click "SAVE"

**Expected Result**:
- ✅ Staff member created successfully
- ✅ Linked to Django user
- ✅ Role and permissions set correctly

**What to Check**:
- Staff can only be linked to one hotel
- Employee ID is unique per hotel
- Role choices match hotel operations

---

### **Scenario 7: API Testing via Swagger UI** (10 minutes)

#### 7.1 Access Swagger UI
**Goal**: Test API documentation and authentication.

**Steps**:
1. Navigate to: https://web-production-2765.up.railway.app/api/docs/
2. You should see interactive API documentation

**Expected Result**:
- ✅ Swagger UI loads
- ✅ All 24+ endpoints visible
- ✅ Organized by resource (hotels, rooms, guests, etc.)

---

#### 7.2 Authenticate in Swagger
**Goal**: Test API authentication.

**Steps**:
1. Click "Authorize" button (top right, lock icon)
2. Enter Django admin credentials:
   - Username: `admin`
   - Password: (your new password)
3. Click "Authorize"
4. Click "Close"

**Expected Result**:
- ✅ Authentication successful
- ✅ Lock icon changes to "locked" (authenticated)

---

#### 7.3 Test API Endpoints

**Test 1: List Hotels**
1. Expand `GET /api/v1/hotels/`
2. Click "Try it out"
3. Click "Execute"

**Expected Response**:
- Status: 200 OK
- Body: JSON array with your hotels
  ```json
  [
    {
      "id": 1,
      "name": "Test Grand Hotel",
      "type": "independent",
      ...
    },
    {
      "id": 2,
      "name": "Stayfull Demo Hotel",
      ...
    }
  ]
  ```

---

**Test 2: Get Single Hotel**
1. Expand `GET /api/v1/hotels/{id}/`
2. Click "Try it out"
3. Enter ID: `1` (Test Grand Hotel)
4. Click "Execute"

**Expected Response**:
- Status: 200 OK
- Body: Full hotel details with address, contact, settings

---

**Test 3: Create Room (POST)**
1. Expand `POST /api/v1/rooms/`
2. Click "Try it out"
3. Edit request body:
   ```json
   {
     "hotel": 2,
     "room_number": "401",
     "room_type": 3,
     "floor": 4,
     "status": "available",
     "cleaning_status": "clean"
   }
   ```
4. Click "Execute"

**Expected Response**:
- Status: 201 Created
- Body: Created room object with ID

---

**Test 4: Filter Rooms**
1. Expand `GET /api/v1/rooms/`
2. Click "Try it out"
3. Add query parameters:
   - `hotel`: 2
   - `status`: available
4. Click "Execute"

**Expected Response**:
- Status: 200 OK
- Body: Array of available rooms for Stayfull Demo Hotel

---

**Test 5: Test Permissions (Negative Test)**
1. Log out from Swagger (Authorize → Logout)
2. Try `GET /api/v1/hotels/`
3. Click "Execute"

**Expected Response**:
- Status: 401 Unauthorized
- Body: `{"detail": "Authentication credentials were not provided."}`

**Result**: ✅ Security working correctly

---

### **Scenario 8: Data Integrity Tests** (5 minutes)

#### 8.1 Test Referential Integrity
**Goal**: Verify cascading deletes and constraints.

**Steps**:
1. Try to delete a hotel that has rooms:
   - Navigate to "Hotels" → "Hotels"
   - Select "Test Grand Hotel" (has 10 rooms)
   - Action: "Delete selected hotels"
   - Click "Go"
   - Review confirmation page (shows related objects)
   - **CANCEL** (don't actually delete)

**Expected Result**:
- ✅ Warning shows: "Deleting hotel will delete X rooms, Y reservations"
- ✅ Cascading delete behavior documented

---

#### 8.2 Test Unique Constraints
**Goal**: Test database constraints.

**Steps**:
1. Try to create duplicate guest email:
   - Create guest with email: `sarah.johnson@example.com`
   - Expected: Error message "Guest with this Email already exists"

2. Try to create duplicate room number:
   - Create room 301 in same hotel again
   - Expected: Error message "Room with this number already exists in this hotel"

**Expected Result**:
- ✅ Unique constraints enforced
- ✅ Clear error messages

---

## 📊 Testing Checklist

Use this checklist to track your testing progress:

### Admin Access
- [ ] Login successful with default credentials
- [ ] Password changed successfully
- [ ] Django Admin interface loads correctly

### Hotel Management
- [ ] View existing hotels
- [ ] Create new hotel
- [ ] Edit hotel details
- [ ] Bulk actions work

### Room Management
- [ ] View room types
- [ ] Create room type with complex JSON data
- [ ] Create individual rooms
- [ ] Room statuses update correctly

### Guest Management
- [ ] Create guest with encrypted PII
- [ ] Search guests by name/email
- [ ] Filter guests by loyalty tier, status
- [ ] ID document encryption verified

### Reservation Management
- [ ] Create complete reservation
- [ ] Check-in process works
- [ ] Check-out process works
- [ ] Cancel reservation
- [ ] Confirmation numbers generated

### Staff Management
- [ ] Create Django user
- [ ] Create staff profile
- [ ] Link staff to hotel
- [ ] Set role and permissions

### API Testing
- [ ] Swagger UI accessible
- [ ] API authentication works
- [ ] List operations work
- [ ] Create operations work
- [ ] Filter/search operations work
- [ ] Unauthenticated requests blocked

### Data Integrity
- [ ] Cascading deletes protected
- [ ] Unique constraints enforced
- [ ] JSON fields validated
- [ ] Business rules enforced

---

## 🐛 Bug Reporting Template

If you find issues during testing, document them using this template:

```markdown
### Bug #[Number]: [Short Description]

**Severity**: Critical / High / Medium / Low
**Location**: Django Admin / API / Database
**Steps to Reproduce**:
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happened]

**Screenshots**:
[Attach screenshots if applicable]

**Environment**:
- URL: https://web-production-2765.up.railway.app
- Browser: [Chrome/Firefox/Safari]
- Date: 2025-10-23
```

**Submit bugs to**: `.architect/testing/bugs.md` or create GitHub issue

---

## ✅ Success Criteria

Your testing is successful if:

1. ✅ **All 8 scenarios completed** without critical errors
2. ✅ **Data persists** correctly across page refreshes
3. ✅ **Performance is acceptable** (< 2 seconds for most operations)
4. ✅ **No security vulnerabilities** discovered
5. ✅ **Admin interface is intuitive** for hotel staff
6. ✅ **API documentation is clear** and functional
7. ✅ **At least 90% of checklist items** marked complete

---

## 📝 Post-Testing Report

After completing testing, document your findings:

### Overall Assessment
- **Readiness**: Production Ready / Needs Minor Fixes / Needs Major Fixes
- **User Experience**: Excellent / Good / Needs Improvement
- **Performance**: Fast / Acceptable / Slow
- **Stability**: Stable / Occasional Issues / Unstable

### Key Findings
- **Strengths**: [What worked well]
- **Weaknesses**: [What needs improvement]
- **Blockers**: [Critical issues preventing launch]
- **Nice-to-Haves**: [Non-critical enhancements]

### Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

---

## 🎉 Congratulations!

You've completed comprehensive testing of **F-001: Stayfull PMS Core**!

**Next Steps**:
1. Share your findings with the development team
2. Log any bugs discovered
3. Approve for production launch (if ready)
4. Plan for F-002: AI Onboarding Agent

---

**Questions?** Contact the Senior Product Architect or review `.architect/ARCHITECT_DEVELOPER_COMMS.md`

**Happy Testing!** 🧪✨
