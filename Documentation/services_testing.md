# Test Cases for Django App: Services

## Test Cases for Models (`services/models.py`)

### Model: `ServiceCategory`

**Case ID:** services_TC_M_SC_001
**Title:** Create ServiceCategory with valid data
**Description:** Verify that a `ServiceCategory` instance can be created with all valid fields.
**Pre-conditions:** None
**Dependencies:** None
**Steps:**
1. Create a `ServiceCategory` instance with a unique `name` and `description`.
2. Save the instance.
**Expected Result:**
- The `ServiceCategory` instance is created successfully.
- The `slug` field is auto-generated based on the `name`.
- The instance is saved to the database.
**Post-conditions:** The created `ServiceCategory` instance exists in the database.

**Case ID:** services_TC_M_SC_002
**Title:** Create ServiceCategory with missing name (invalid)
**Description:** Verify that creating a `ServiceCategory` without a `name` raises a validation error.
**Pre-conditions:** None
**Dependencies:** None
**Steps:**
1. Attempt to create a `ServiceCategory` instance with `name` = None or empty string.
2. Try to save the instance.
**Expected Result:**
- A `ValidationError` (or equivalent database error for blank=False) is raised.
- The instance is not saved to the database.
**Post-conditions:** No new `ServiceCategory` instance is created.


### Model: `Service`

**Case ID:** services_TC_M_S_001
**Title:** Create Service with valid data
**Description:** Verify that a `Service` instance can be created with all valid required fields.
**Pre-conditions:**
- A `users.Professional` instance exists.
- A `ServiceCategory` instance exists (optional, as category can be null).
**Dependencies:** `users.Professional` model, `ServiceCategory` model.
**Steps:**
1. Create a `Service` instance, providing `professional`, `title`.
2. Optionally, provide `category`, `description`, `is_active`, `featured`.
3. Save the instance.
**Expected Result:**
- The `Service` instance is created successfully.
- The `slug` field is auto-generated based on the `title` and `professional.pk`.
- The instance is saved to the database.
**Post-conditions:** The created `Service` instance exists in the database.

**Case ID:** services_TC_M_S_002
**Title:** Create Service without a professional (invalid)
**Description:** Verify that creating a `Service` without a `professional` raises an error.
**Pre-conditions:** None
**Dependencies:** None
**Steps:**
1. Attempt to create a `Service` instance with `professional` = None.
2. Set other required fields like `title`.
3. Try to save the instance.
**Expected Result:**
- An `IntegrityError` or `ValidationError` is raised because `professional` cannot be null.
- The instance is not saved.
**Post-conditions:** No new `Service` instance is created.

**Case ID:** services_TC_M_S_003
**Title:** Create Service without a title (invalid via `clean` method)
**Description:** Verify that the `clean` method prevents saving a `Service` without a `title`.
**Pre-conditions:** A `users.Professional` instance exists.
**Dependencies:** `users.Professional` model.
**Steps:**
1. Create a `Service` instance with a `professional` but `title` = "" or None.
2. Call the `clean()` method on the instance.
**Expected Result:**
- A `ValidationError` is raised with a message like 'Service title cannot be empty'.
**Post-conditions:** The instance is not in a savable state if `clean()` is enforced before save.


**Case ID:** services_TC_M_S_009
**Title:** Service string representation
**Description:** Verify the `__str__` method of `Service` returns the correct format.
**Pre-conditions:** A `Service` instance exists with a known `title` and `professional`.
**Dependencies:** `users.Professional` model.
**Steps:**
1. Retrieve an existing `Service` instance.
2. Call `str()` on the instance.
**Expected Result:**
- The string representation is `"{self.title} (by {self.professional})"`.
**Post-conditions:** None.

**Case ID:** services_TC_M_S_010
**Title:** Service `active` manager
**Description:** Verify the `active` manager returns only services where `is_active=True`.
**Pre-conditions:**
- Multiple `Service` instances exist, some with `is_active=True`, some with `is_active=False`.
**Dependencies:** None.
**Steps:**
1. Query `Service.active.all()`.
**Expected Result:**
- Only `Service` instances with `is_active=True` are returned.
- Instances with `is_active=False` are excluded.
**Post-conditions:** None.

**Case ID:** services_TC_M_S_011
**Title:** Create Service with blank description
**Description:** Verify a `Service` can be created with a blank `description`.
**Pre-conditions:** A `users.Professional` instance exists.
**Dependencies:** `users.Professional` model.
**Steps:**
1. Create a `Service` with `professional`, `title`, and `description` = "".
2. Save the instance.
**Expected Result:**
- The `Service` is created and saved successfully.
**Post-conditions:** The `Service` instance exists.

**Case ID:** services_TC_M_S_013
**Title:** Service associated with a Category
**Description:** Verify a service can be successfully associated with a `ServiceCategory`.
**Pre-conditions:**
- A `users.Professional` instance exists.
- A `ServiceCategory` (SC1) instance exists.
**Dependencies:** `users.Professional`, `ServiceCategory` models.
**Steps:**
1. Create a `Service` instance, providing `professional`, `title`, and `category` = SC1.
2. Save the instance.
3. Retrieve the service and check its `category` attribute.
**Expected Result:**
- The `Service` is saved successfully.
- `service.category` is equal to SC1.
- SC1.services.all() includes the created service.
**Post-conditions:** The `Service` instance exists and is linked to SC1.

**Case ID:** services_TC_M_S_014
**Title:** Service with null Category
**Description:** Verify a service can be created with `category` = None.
**Pre-conditions:** A `users.Professional` instance exists.
**Dependencies:** `users.Professional` model.
**Steps:**
1. Create a `Service` instance, providing `professional`, `title`, and `category` = None.
2. Save the instance.
**Expected Result:**
- The `Service` is saved successfully.
- `service.category` is None.
**Post-conditions:** The `Service` instance exists with no category.

### Model: `Item`

**Case ID:** services_TC_M_I_001
**Title:** Create Item with valid data
**Description:** Verify that an `Item` instance can be created with all valid required fields.
**Pre-conditions:** A `Service` instance exists.
**Dependencies:** `Service` model.
**Steps:**
1. Create an `Item` instance, providing `service` and `title`.
2. Optionally, provide `description`, `image`, `sku`, `stock`, `position`.
3. Save the instance.
**Expected Result:**
- The `Item` instance is created successfully.
- The `slug` field is auto-generated based on the `title` and `service.pk`.
- The instance is saved to the database.
- The item is associated with the correct service (`item.service`).
**Post-conditions:** The created `Item` instance exists in the database and is linked to the specified `Service`.

**Case ID:** services_TC_M_I_002
**Title:** Create Item without a service (invalid)
**Description:** Verify that creating an `Item` without a `service` raises an error.
**Pre-conditions:** None
**Dependencies:** None
**Steps:**
1. Attempt to create an `Item` instance with `service` = None.
2. Set other required fields like `title`.
3. Try to save the instance.
**Expected Result:**
- An `IntegrityError` or `ValidationError` is raised because `service` cannot be null.
- The instance is not saved.
**Post-conditions:** No new `Item` instance is created.

**Case ID:** services_TC_M_I_003
**Title:** Create Item without a title (invalid via `clean` method)
**Description:** Verify that the `clean` method prevents saving an `Item` without a `title`.
**Pre-conditions:** A `Service` instance exists.
**Dependencies:** `Service` model.
**Steps:**
1. Create an `Item` instance with a `service` but `title` = "" or None.
2. Call the `clean()` method on the instance.
**Expected Result:**
- A `ValidationError` is raised with a message like 'Item title cannot be empty'.
**Post-conditions:** The instance is not in a savable state if `clean()` is enforced before save.


**Case ID:** services_TC_M_I_007
**Title:** Item string representation
**Description:** Verify the `__str__` method of `Item` returns the correct format.
**Pre-conditions:** An `Item` instance exists, linked to a `Service` with a known title.
**Dependencies:** `Service` model.
**Steps:**
1. Retrieve an existing `Item` instance (e.g., item title "Sample Item", service title "Main Service").
2. Call `str()` on the instance.
**Expected Result:**
- The string representation is `"{self.title} (in Service: {self.service.title})"`, e.g., "Sample Item (in Service: Main Service)".
**Post-conditions:** None.

**Case ID:** services_TC_M_I_012
**Title:** Item with blank description 
**Description:** Verify an `Item` can be created with blank `description` 
**Pre-conditions:** A `Service` instance exists.
**Dependencies:** `Service` model.
**Steps:**
1. Create an `Item` instance with `service`, `title`, `description`="", and `sku`="".
2. Save the instance.
**Expected Result:**
- The `Item` is saved successfully.
**Post-conditions:** The `Item` instance exists.

### Model: `Price`

**Case ID:** services_TC_M_P_001
**Title:** Create Price with valid data
**Description:** Verify that a `Price` instance can be created with all valid required fields.
**Pre-conditions:** An `Item` instance exists.
**Dependencies:** `Item` model.
**Steps:**
1. Create a `Price` instance, providing `item`, `amount`.
2. Optionally, provide `currency`, `frequency`, `description`, `is_active`, `valid_from`, `valid_until`, `min_quantity`, `max_quantity`, `discount_percentage`.
3. Save the instance.
**Expected Result:**
- The `Price` instance is created successfully.
- Default values for `currency` (EUR), `frequency` (ONE_TIME), `min_quantity` (1), `discount_percentage` (0.00) are applied if not provided.
- The instance is saved to the database.
- The price is associated with the correct item (`price.item`).
**Post-conditions:** The created `Price` instance exists in the database and is linked to the specified `Item`.

**Case ID:** services_TC_M_P_002
**Title:** Create Price without an item (invalid)
**Description:** Verify that creating a `Price` without an `item` raises an error.
**Pre-conditions:** None
**Dependencies:** None
**Steps:**
1. Attempt to create a `Price` instance with `item` = None.
2. Set other required fields like `amount`.
3. Try to save the instance.
**Expected Result:**
- An `IntegrityError` or `ValidationError` is raised because `item` cannot be null.
- The instance is not saved.
**Post-conditions:** No new `Price` instance is created.

**Case ID:** services_TC_M_P_003
**Title:** Create Price with negative amount (invalid via `clean` method)
**Description:** Verify that the `clean` method prevents saving a `Price` with a negative `amount`.
**Pre-conditions:** An `Item` instance exists.
**Dependencies:** `Item` model.
**Steps:**
1. Create a `Price` instance with an `item` but `amount` = -10.00.
2. Call the `clean()` method on the instance.
**Expected Result:**
- A `ValidationError` is raised with a message like 'Price amount cannot be negative'.
**Post-conditions:** The instance is not in a savable state if `clean()` is enforced.



**Case ID:** services_TC_M_P_015
**Title:** Price with default currency and frequency
**Description:** Verify `Price` is created with default `currency` ('EUR') and `frequency` ('ONCE') if not provided.
**Pre-conditions:** An `Item` instance exists.
**Dependencies:** `Item` model.
**Steps:**
1. Create a `Price` instance with `item` and `amount`, without specifying `currency` or `frequency`.
2. Save and retrieve the instance.
**Expected Result:**
- `price.currency` is 'EUR'.
- `price.frequency` is 'ONCE'.
**Post-conditions:** The `Price` instance exists with default currency and frequency.

**Case ID:** services_TC_M_P_016
**Title:** Price with all optional fields filled
**Description:** Verify a `Price` can be created with all optional fields (description, valid_from, valid_until, min_quantity, max_quantity, discount_percentage) correctly set.
**Pre-conditions:** An `Item` instance exists.
**Dependencies:** `Item` model.
**Steps:**
1. Create a `Price` instance providing valid values for all fields including all optional ones.
2. Save and retrieve the instance.
**Expected Result:**
- All fields are stored and retrieved correctly.
**Post-conditions:** The `Price` instance exists with all specified data.

## Test Cases for Views (`services/views.py`)

### Mixins (General Behavior to be verified in context of views)

**Case ID:** services_TC_V_MIX_001
**Title:** `ProfessionalRequiredMixin` - Access granted for professional user
**Description:** Verify users with a professional profile can access views using this mixin.
**Pre-conditions:** User is logged in AND has a `Professional` profile.
**Dependencies:** `users.Professional` model.
**Steps:** (Tested implicitly by accessing a view that uses this mixin, e.g., `ServiceCreateView`)
1. Logged-in professional user attempts to access the view.
**Expected Result:**
- View is accessible (HTTP 200 for GET, or proceeds to logic for POST).
- No redirection to login or 'profile_choice'.
**Post-conditions:** None.

**Case ID:** services_TC_V_MIX_002
**Title:** `ProfessionalRequiredMixin` - Access denied for non-professional user
**Description:** Verify users without a professional profile are redirected.
**Pre-conditions:** User is logged in BUT does NOT have a `Professional` profile.
**Dependencies:** None.
**Steps:** (Tested implicitly)
1. Logged-in non-professional user attempts to access a view using this mixin.
**Expected Result:**
- User is redirected (e.g., to `users:profile_choice`).
- An error message is displayed (e.g., "You are not registered as a professional.").
**Post-conditions:** None.

**Case ID:** services_TC_V_MIX_003
**Title:** `ProfessionalOwnsObjectMixin` - Access granted for owner
**Description:** Verify professional who owns the object can access views using this mixin (e.g., update/delete).
**Pre-conditions:**
    - User is logged in and is a `Professional` (P1).
    - An object (e.g., `Service` S1) exists where `S1.professional == P1`.
**Dependencies:** `users.Professional`, `Service` (or other relevant model).
**Steps:** (Tested implicitly by accessing e.g. `ServiceUpdateView` for S1 as P1)
1. P1 attempts to access the view for S1.
**Expected Result:**
- View is accessible (HTTP 200 for GET, or proceeds to logic for POST).
**Post-conditions:** None.

**Case ID:** services_TC_V_MIX_004
**Title:** `ProfessionalOwnsObjectMixin` - Access denied for non-owner
**Description:** Verify professional who does NOT own the object is denied access.
**Pre-conditions:**
    - User (P1) is logged in and is a `Professional`.
    - Another `Professional` (P2) exists.
    - An object (e.g., `Service` S2) exists where `S2.professional == P2`.
**Dependencies:** `users.Professional`, `Service` model.
**Steps:** (Tested implicitly)
1. P1 attempts to access a view using this mixin for object S2.
**Expected Result:**
- User is redirected (e.g., to `services:service_list`).
- An error message is displayed (e.g., "You do not have permission...").
**Post-conditions:** None.


### Service Views

#### View: `ServiceCreateView` (`services:service_create`)

**Case ID:** services_TC_V_SCV_001
**Title:** Access `ServiceCreateView` - Not logged in
**Description:** Verify unauthenticated users are redirected to login.
**Pre-conditions:** User is not logged in.
**Dependencies:** None.
**Steps:**
1. Attempt to GET the `services:service_create` URL.
**Expected Result:**
- Redirected to login page (HTTP 302).
**Post-conditions:** None.

**Case ID:** services_TC_V_SCV_002
**Title:** Access `ServiceCreateView` - Logged in, not professional
**Description:** Verify logged-in non-professional users are redirected (by `ProfessionalRequiredMixin`).
**Pre-conditions:** User is logged in but does not have a `Professional` profile.
**Dependencies:** None.
**Steps:**
1. Attempt to GET the `services:service_create` URL.
**Expected Result:**
- Redirected (e.g., to `users:profile_choice`).
- Error message displayed.
**Post-conditions:** None.

**Case ID:** services_TC_V_SCV_003
**Title:** `ServiceCreateView` GET request - Logged in, professional
**Description:** Verify a logged-in professional user can access the form page.
**Pre-conditions:** User is logged in and has a `Professional` profile.
**Dependencies:** None.
**Steps:**
1. GET the `services:service_create` URL.
**Expected Result:**
- HTTP 200 OK.
- Template `services/service_form.html` is rendered.
- Context contains an unbound `ServiceForm`.
- Context `page_title` is "Create New Service".
**Post-conditions:** None.

**Case ID:** services_TC_V_SCV_004
**Title:** `ServiceCreateView` POST request - Valid data
**Description:** Verify creating a new service with valid data.
**Pre-conditions:** User (P1) is logged in, has a `Professional` profile.
**Dependencies:** `users.Professional` model.
**Steps:**
1. POST valid data (e.g., `title`, `description`, `is_active`) to `services:service_create`.
**Expected Result:**
- A new `Service` object is created in the database, associated with P1.
- User is redirected to `services:service_list` (HTTP 302).
- A success message is displayed (e.g., "Service created successfully.").
**Post-conditions:** New `Service` record exists.

**Case ID:** services_TC_V_SCV_005
**Title:** `ServiceCreateView` POST request - Invalid data (e.g., missing title)
**Description:** Verify form re-renders with errors for invalid data.
**Pre-conditions:** User is logged in, has a `Professional` profile.
**Dependencies:** None.
**Steps:**
1. POST invalid data (e.g., `title`="", `description`="...") to `services:service_create`.
**Expected Result:**
- HTTP 200 OK (form re-rendered).
- Template `services/service_form.html` is rendered.
- The form in context contains errors (e.g., error for `title` field).
- No new `Service` object is created.
**Post-conditions:** No new `Service` record.

#### View: `ServiceListView` (`services:service_list`)

**Case ID:** services_TC_V_SLV_001
**Title:** Access `ServiceListView` - Not logged in
**Description:** Verify unauthenticated users are redirected to login.
**Pre-conditions:** User is not logged in.
**Dependencies:** None.
**Steps:**
1. Attempt to GET the `services:service_list` URL.
**Expected Result:**
- Redirected to login page (HTTP 302).
**Post-conditions:** None.



**Case ID:** services_TC_V_SDV_003
**Title:** `ServiceDetailView` GET - Non-owner viewing (current: denied)
**Description:** Verify non-owner professional cannot view another professional's service details (based on current `get_queryset` logic).
**Pre-conditions:**
    - User (P1) is logged in, `Professional` profile.
    - Service S2 exists, `S2.professional` is another professional (P2).
**Dependencies:** `users.Professional`, `Service` model.
**Steps:**
1. P1 GETs `services:service_detail` for S2.
**Expected Result:**
- HTTP 404 Not Found (as `qs.none()` then `get_object()` will fail).
**Post-conditions:** None.
**Note:** If view logic changes to allow public viewing of active services, this test needs update.

**Case ID:** services_TC_V_SDV_004
**Title:** `ServiceDetailView` GET - User with no professional profile (current: denied)
**Description:** Verify user without a professional profile cannot view service details (based on current `get_queryset` logic).
**Pre-conditions:**
    - User is logged in, but no `Professional` profile.
    - Service S1 exists.
**Dependencies:** `Service` model.
**Steps:**
1. User GETs `services:service_detail` for S1.
**Expected Result:**
- HTTP 404 Not Found.
**Post-conditions:** None.

#### View: `ServiceUpdateView` (`services:service_update`, pk=service.pk)

**Case ID:** services_TC_V_SUV_001
**Title:** Access `ServiceUpdateView` - Not logged in
**Description:** Verify unauthenticated users are redirected to login.
**Pre-conditions:** Service S1 exists. User not logged in.
**Dependencies:** `Service` model.
**Steps:**
1. Attempt GET on `services:service_update` for S1.
**Expected Result:**
- Redirect to login.
**Post-conditions:** None.

**Case ID:** services_TC_V_SUV_002
**Title:** Access `ServiceUpdateView` - Logged in, not professional
**Description:** Redirected by `ProfessionalRequiredMixin`.
**Pre-conditions:** Service S1 exists. User logged in, no professional profile.
**Dependencies:** `Service` model.
**Steps:**
1. Attempt GET on `services:service_update` for S1.
**Expected Result:**
- Redirected (e.g. to `users:profile_choice`), error message.
**Post-conditions:** None.


**Case ID:** services_TC_V_SUV_004
**Title:** `ServiceUpdateView` GET request - Owner
**Description:** Owner accesses the update form for their service.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S1 exists, `S1.professional == P1`.
**Dependencies:** `users.Professional`, `Service` models.
**Steps:**
1. P1 GETs `services:service_update` for S1.
**Expected Result:**
- HTTP 200 OK.
- Template `services/service_form.html` rendered.
- Form is bound with S1's data.
- Context `page_title` is "Edit Service: {S1.title}".
**Post-conditions:** None.

**Case ID:** services_TC_V_SUV_005
**Title:** `ServiceUpdateView` POST request - Valid data by owner
**Description:** Owner updates their service with valid data.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S1 exists, `S1.professional == P1`.
**Dependencies:** `users.Professional`, `Service` models.
**Steps:**
1. P1 POSTs valid updated data (e.g., new title, description) to `services:service_update` for S1.
**Expected Result:**
- S1 is updated in the database.
- Redirect to `services:service_detail` for S1 (HTTP 302).
- Success message displayed (e.g., "Service updated successfully.").
**Post-conditions:** S1 record is modified.

**Case ID:** services_TC_V_SUV_006
**Title:** `ServiceUpdateView` POST request - Invalid data by owner
**Description:** Owner submits invalid data, form re-renders with errors.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S1 exists, `S1.professional == P1`.
**Dependencies:** `users.Professional`, `Service` models.
**Steps:**
1. P1 POSTs invalid data (e.g., title="") to `services:service_update` for S1.
**Expected Result:**
- HTTP 200 OK (form re-rendered).
- Template `services/service_form.html` rendered.
- Form in context contains errors.
- S1 is NOT updated in the database.
**Post-conditions:** S1 record is unchanged.

#### View: `ServiceDeleteView` (`services:service_delete`, pk=service.pk)

**Case ID:** services_TC_V_SDV_D_001
**Title:** Access `ServiceDeleteView` - Not logged in
**Description:** Verify unauthenticated users are redirected.
**Pre-conditions:** Service S1 exists. User not logged in.
**Dependencies:** `Service` model.
**Steps:**
1. Attempt GET on `services:service_delete` for S1.
**Expected Result:**
- Redirect to login.
**Post-conditions:** None.


**Case ID:** services_TC_V_SDV_D_004
**Title:** `ServiceDeleteView` GET request - Owner
**Description:** Owner accesses the delete confirmation page.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S1 exists, `S1.professional == P1`.
**Dependencies:** `users.Professional`, `Service` models.
**Steps:**
1. P1 GETs `services:service_delete` for S1.
**Expected Result:**
- HTTP 200 OK.
- Template `services/service_confirm_delete.html` rendered.
- Context `service` is S1.
- Context `page_title` is "Delete Service: {S1.title}".
**Post-conditions:** None.

**Case ID:** services_TC_V_SDV_D_005
**Title:** `ServiceDeleteView` POST request - Owner confirms deletion
**Description:** Owner deletes their service.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S1 exists, `S1.professional == P1`.
**Dependencies:** `users.Professional`, `Service` models.
**Steps:**
1. P1 POSTs to `services:service_delete` for S1 (confirming deletion).
**Expected Result:**
- S1 is deleted from the database (and its associated Items/Prices due to CASCADE).
- Redirect to `services:service_list` (HTTP 302).
- Success message displayed (e.g., "Service '{S1.title}' deleted successfully.").
**Post-conditions:** S1 record (and related children) no longer exists.

**Case ID:** services_TC_V_SDV_D_006
**Title:** `ServiceDeleteView` - Service not found
**Description:** Verify HTTP 404 if attempting to delete non-existent service.
**Pre-conditions:** User logged in, professional.
**Dependencies:** None.
**Steps:**
1. GET or POST to `services:service_delete` with a non-existent PK.
**Expected Result:**
- HTTP 404 Not Found.
**Post-conditions:** None.

---

### Item Views

#### View: `ItemCreateView` (`services:item_create`, service_pk=service.pk)

**Case ID:** services_TC_V_ICV_001
**Title:** Access `ItemCreateView` - Not logged in
**Description:** Verify unauthenticated users are redirected.
**Pre-conditions:** Service S1 exists. User not logged in.
**Dependencies:** `Service` model.
**Steps:**
1. Attempt GET on `services:item_create` for S1.
**Expected Result:**
- Redirect to login.
**Post-conditions:** None.



**Case ID:** services_TC_V_ICV_003
**Title:** Access `ItemCreateView` - Logged in, professional, but not owner of parent Service
**Description:** Redirected by `UserOwnsParentServiceMixin`.
**Pre-conditions:**
    - User (P1) logged in, `Professional`.
    - Service S2 by another professional (P2) exists.
**Dependencies:** `users.Professional`, `Service` models.
**Steps:**
1. P1 attempts GET on `services:item_create` for S2.
**Expected Result:**
- Redirected (e.g. to `services:service_list`), error message.
**Post-conditions:** None.

**Case ID:** services_TC_V_ICV_004
**Title:** `ItemCreateView` GET request - Owner of parent Service
**Description:** Professional accesses item creation form for their service.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S1 exists, `S1.professional == P1`.
**Dependencies:** `users.Professional`, `Service` models.
**Steps:**
1. P1 GETs `services:item_create` for S1.
**Expected Result:**
- HTTP 200 OK.
- Template `services/item_form.html` rendered.
- Context contains an unbound `ItemForm`.
- Context `service` is S1.
- Context `page_title` is "Add Item to {S1.title}".
**Post-conditions:** None.


**Case ID:** services_TC_V_ICV_007
**Title:** `ItemCreateView` GET - Parent service not found
**Description:** Verify HTTP 404 if `service_pk` in URL does not exist.
**Pre-conditions:** User logged in, professional.
**Dependencies:** None.
**Steps:**
1. GET `services:item_create` with a non-existent `service_pk`.
**Expected Result:**
- HTTP 404 Not Found (due to `get_object_or_404` in `UserOwnsParentServiceMixin`).
**Post-conditions:** None.

#### View: `ItemUpdateView` (`services:item_update`, service_pk=service.pk, pk=item.pk)

**Case ID:** services_TC_V_IUV_001
**Title:** Access `ItemUpdateView` - Not logged in
**Description:** Redirect to login.
**Pre-conditions:** Service S1, Item I1 exist. User not logged in.
**Dependencies:** `Service`, `Item` models.
**Steps:**
1. Attempt GET on `services:item_update` for I1 under S1.
**Expected Result:**
- Redirect to login.
**Post-conditions:** None.

**Case ID:** services_TC_V_IUV_002
**Title:** Access `ItemUpdateView` - Non-owner of parent Service
**Description:** Redirected by `UserOwnsParentServiceMixin`.
**Pre-conditions:** User (P1) logged in, Professional. Service S2 by P2, Item I2 in S2.
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:**
1. P1 attempts GET on `services:item_update` for I2 under S2.
**Expected Result:**
- Redirected/HTTP 404.
**Post-conditions:** None.

**Case ID:** services_TC_V_IUV_003
**Title:** `ItemUpdateView` GET request - Owner of parent Service
**Description:** Owner accesses item update form.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S1 (by P1), Item I1 in S1.
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:**
1. P1 GETs `services:item_update` for I1 under S1.
**Expected Result:**
- HTTP 200 OK.
- Template `services/item_form.html` rendered.
- Form bound with I1's data.
- Context `service` is S1.
- Context `page_title` is "Edit Item: {I1.title}".
**Post-conditions:** None.

**Case ID:** services_TC_V_IUV_004
**Title:** `ItemUpdateView` POST - Valid data by owner
**Description:** Owner updates item with valid data.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S1 (by P1), Item I1 in S1.
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:**
1. P1 POSTs valid updated data (e.g., new title, description) to `services:item_update` for I1 under S1.
**Expected Result:**
- I1 is updated.
- Redirect to `services:item_detail` for I1 under S1.
- Success message displayed.
**Post-conditions:** I1 record modified.

**Case ID:** services_TC_V_IUV_005
**Title:** `ItemUpdateView` POST - Invalid data by owner
**Description:** Form re-renders with errors.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S1 (by P1), Item I1 in S1.
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:**
1. P1 POSTs invalid data (e.g., title="") to `services:item_update` for I1 under S1.
**Expected Result:**
- HTTP 200 OK.
- Form in context has errors.
- I1 not updated.
**Post-conditions:** I1 unchanged.

#### View: `ItemDeleteView` (`services:item_delete`, service_pk=service.pk, pk=item.pk)

**Case ID:** services_TC_V_IDV_D_001
**Title:** Access `ItemDeleteView` - Not logged in
**Description:** Redirect to login.
**Pre-conditions:** Service S1, Item I1 exist. User not logged in.
**Dependencies:** `Service`, `Item` models.
**Steps:**
1. Attempt GET on `services:item_delete` for I1 under S1.
**Expected Result:**
- Redirect to login.
**Post-conditions:** None.

**Case ID:** services_TC_V_IDV_D_003
**Title:** `ItemDeleteView` GET request - Owner
**Description:** Owner accesses delete confirmation page for item.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S1 (by P1), Item I1 in S1.
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:**
1. P1 GETs `services:item_delete` for I1 under S1.
**Expected Result:**
- HTTP 200 OK.
- Template `services/item_confirm_delete.html` rendered.
- Context `item` is I1, `service` is S1.
- Context `page_title` is "Delete Item: {I1.title}".
**Post-conditions:** None.

**Case ID:** services_TC_V_IDV_D_004
**Title:** `ItemDeleteView` POST request - Owner confirms deletion
**Description:** Owner deletes their item.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S1 (by P1), Item I1 in S1.
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:**
1. P1 POSTs to `services:item_delete` for I1 under S1.
**Expected Result:**
- I1 is deleted (and its associated Prices due to CASCADE).
- Redirect to `services:service_detail` for S1.
- Success message displayed.
**Post-conditions:** I1 record (and related Prices) no longer exists.

---

### Price Views

#### View: `PriceCreateView` (`services:price_create`, service_pk=service.pk, item_pk=item.pk)

**Case ID:** services_TC_V_PCV_001
**Title:** Access `PriceCreateView` - Not logged in
**Description:** Redirect.
**Pre-conditions:** Service S1, Item I1 in S1 exist. User not logged in.
**Dependencies:** `Service`, `Item` models.
**Steps:**
1. Attempt GET on `services:price_create` for I1 under S1.
**Expected Result:**
- Redirect to login.
**Post-conditions:** None.


**Case ID:** services_TC_V_PCV_004
**Title:** `PriceCreateView` POST - Valid data by owner
**Description:** Owner creates new price for their item with valid data.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S1 (by P1), Item I1 in S1.
**Dependencies:** `users.Professional`, `Service`, `Item`, `Price` models.
**Steps:**
1. P1 POSTs valid price data to `services:price_create` for I1 under S1.
**Expected Result:**
- New `Price` object created, associated with I1.
- Redirect to `services:item_detail` for I1 under S1.
- Success message displayed.
**Post-conditions:** New `Price` record exists.

**Case ID:** services_TC_V_PCV_005
**Title:** `PriceCreateView` POST - Invalid data by owner
**Description:** Form re-renders with errors.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S1 (by P1), Item I1 in S1.
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:**
1. P1 POSTs invalid price data (e.g., amount="") to `services:price_create` for I1 under S1.
**Expected Result:**
- HTTP 200 OK. Form in context has errors.
- No new `Price` created.
**Post-conditions:** No new `Price` record.

