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
**Title:** Item with blank description and SKU
**Description:** Verify an `Item` can be created with blank `description` and `sku`.
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


**Case ID:** services_TC_M_P_007
**Title:** Price string representation
**Description:** Verify the `__str__` method of `Price` returns the correct format.
**Pre-conditions:** An `Item` (e.g., title "Test Item") and a `Price` (e.g., 100 USD, Monthly) for it exist.
**Dependencies:** `Item` model.
**Steps:**
1. Retrieve the `Price` instance.
2. Call `str()` on the instance.
**Expected Result:**
- The string representation is `"{self.amount} {self.currency} ({self.frequency}) for {self.item.title}"`, e.g., "100.00 USD (MONTHLY) for Test Item".
**Post-conditions:** None.

**Case ID:** services_TC_M_P_008
**Title:** Price `active` manager
**Description:** Verify the `active` manager returns only prices where `is_active=True`.
**Pre-conditions:**
- Multiple `Price` instances exist for an item, some `is_active=True`, some `is_active=False`.
**Dependencies:** `Item` model.
**Steps:**
1. Query `Price.active.all()`.
**Expected Result:**
- Only `Price` instances with `is_active=True` are returned.
**Post-conditions:** None.

**Case ID:** services_TC_M_P_009
**Title:** `is_valid_now` method - currently valid price
**Description:** Verify `is_valid_now()` returns `True` for an active price within its validity period or with no dates.
**Pre-conditions:** An `Item` and `Price` exist. Price `is_active=True`.
    - Scenario 1: `valid_from` is past, `valid_until` is future.
    - Scenario 2: `valid_from` is past, `valid_until` is None.
    - Scenario 3: `valid_from` is None, `valid_until` is future.
    - Scenario 4: `valid_from` is None, `valid_until` is None.
**Dependencies:** `Item` model.
**Steps:**
1. For each scenario, set dates accordingly.
2. Call `is_valid_now()` on the price instance.
**Expected Result:**
- The method returns `True` for all scenarios.
**Post-conditions:** None.


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

**Case ID:** services_TC_V_MIX_005
**Title:** `UserOwnsParentServiceMixin` - Access granted for owner of parent Service (for Item views)
**Description:** Verify professional who owns the parent Service can access Item views.
**Pre-conditions:**
    - User (P1) is logged in and is a `Professional`.
    - `Service` S1 exists, `S1.professional == P1`.
    - `Item` I1 exists, `I1.service == S1`.
    - URL requires `service_pk` for S1.
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:** (Tested implicitly by accessing e.g. `ItemCreateView` for S1 as P1)
1. P1 attempts to access an Item view related to S1.
**Expected Result:**
- View is accessible. `self.service` is set to S1 in the view.
**Post-conditions:** None.

**Case ID:** services_TC_V_MIX_006
**Title:** `UserOwnsParentServiceMixin` - Access denied for non-owner of parent Service
**Description:** Verify professional who does not own the parent Service is denied access to Item views.
**Pre-conditions:**
    - User (P1) is logged in, is a `Professional`.
    - `Service` S2 exists, `S2.professional` is another professional (P2).
    - URL requires `service_pk` for S2.
**Dependencies:** `users.Professional`, `Service` model.
**Steps:** (Tested implicitly)
1. P1 attempts to access an Item view related to S2.
**Expected Result:**
- Redirected, error message displayed. `self.service` might be None or raise Http404 internally first.
**Post-conditions:** None.

**Case ID:** services_TC_V_MIX_007
**Title:** `UserOwnsGrandparentServiceViaItemMixin` - Access granted (for Price views)
**Description:** Verify professional owning grandparent Service (via Item) can access Price views.
**Pre-conditions:**
    - User (P1) is logged in, `Professional`.
    - `Service` S1 exists, `S1.professional == P1`.
    - `Item` I1 exists, `I1.service == S1`.
    - `Price` Prc1 exists, `Prc1.item == I1`.
    - URL requires `service_pk` for S1 and `item_pk` for I1.
**Dependencies:** `users.Professional`, `Service`, `Item`, `Price` models.
**Steps:** (Tested implicitly, e.g. `PriceCreateView` for I1 under S1 as P1)
1. P1 attempts to access a Price view related to I1 (which is under S1).
**Expected Result:**
- View accessible. `self.service` is S1, `self.item` is I1.
**Post-conditions:** None.

**Case ID:** services_TC_V_MIX_008
**Title:** `UserOwnsGrandparentServiceViaItemMixin` - Access denied for non-owner
**Description:** Verify access denied if professional does not own the grandparent Service.
**Pre-conditions:**
    - User (P1) is logged in, `Professional`.
    - `Service` S2 by another professional (P2). `Item` I2 under S2.
    - URL for Price view under I2, S2.
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:** (Tested implicitly)
1. P1 attempts to access Price view related to I2.
**Expected Result:**
- Redirected, error message.
**Post-conditions:** None.

---

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

**Case ID:** services_TC_V_SLV_002
**Title:** `ServiceListView` GET request - Logged in, professional
**Description:** Verify professional sees only their services.
**Pre-conditions:**
    - User (P1) is logged in, has `Professional` profile.
    - P1 has created services S1, S2.
    - Another professional (P2) has created service S3.
**Dependencies:** `users.Professional`, `Service` models.
**Steps:**
1. P1 GETs the `services:service_list` URL.
**Expected Result:**
- HTTP 200 OK.
- Template `services/service_list.html` is rendered.
- Context `services` contains S1, S2, ordered by `-created_at`.
- Context `services` does NOT contain S3.
- Context `professional` is P1's profile.
- Context `page_title` is "My Services".
**Post-conditions:** None.

**Case ID:** services_TC_V_SLV_003
**Title:** `ServiceListView` GET request - Logged in, no professional profile
**Description:** Verify user with no professional profile sees an empty list or appropriate message.
**Pre-conditions:** User is logged in but does not have a `Professional` profile.
**Dependencies:** `Service` model.
**Steps:**
1. GET the `services:service_list` URL.
**Expected Result:**
- HTTP 200 OK.
- Template `services/service_list.html` is rendered.
- Context `services` is empty (`Service.objects.none()`).
- Context `professional` is None.
- An appropriate message might be shown in the template (e.g., "You have not created any services yet.").
**Post-conditions:** None.

**Case ID:** services_TC_V_SLV_004
**Title:** `ServiceListView` - No services created by professional
**Description:** Verify page renders correctly when professional has no services.
**Pre-conditions:** User (P1) is logged in, has `Professional` profile, but has not created any services.
**Dependencies:** `users.Professional` model.
**Steps:**
1. P1 GETs the `services:service_list` URL.
**Expected Result:**
- HTTP 200 OK.
- Template `services/service_list.html` is rendered.
- Context `services` is empty.
- Template shows a message like "You have not created any services yet." and a link to create one.
**Post-conditions:** None.

#### View: `ServiceDetailView` (`services:service_detail`, pk=service.pk)

**Case ID:** services_TC_V_SDV_001
**Title:** Access `ServiceDetailView` - Not logged in
**Description:** Verify unauthenticated users are redirected to login.
**Pre-conditions:** A `Service` (s1) exists. User is not logged in.
**Dependencies:** `Service` model.
**Steps:**
1. Attempt to GET `services:service_detail` for s1.
**Expected Result:**
- Redirected to login page (HTTP 302).
**Post-conditions:** None.

**Case ID:** services_TC_V_SDV_002
**Title:** `ServiceDetailView` GET - Owner viewing their service
**Description:** Professional views detail of their own service (active or inactive).
**Pre-conditions:**
    - User (P1) is logged in, `Professional` profile.
    - Service S1 exists, `S1.professional == P1`. S1 can be active or inactive.
**Dependencies:** `users.Professional`, `Service` model.
**Steps:**
1. P1 GETs `services:service_detail` for S1.
**Expected Result:**
- HTTP 200 OK.
- Template `services/service_detail.html` is rendered.
- Context `service` is S1.
- Context `page_title` is S1.title.
- Context `user_owns_service` is True.
- Associated items and prices are displayed (if any).
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

**Case ID:** services_TC_V_SDV_005
**Title:** `ServiceDetailView` - Service not found
**Description:** Verify HTTP 404 if service with given PK does not exist.
**Pre-conditions:** User is logged in and is a professional.
**Dependencies:** None.
**Steps:**
1. GET `services:service_detail` with a non-existent PK.
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

**Case ID:** services_TC_V_SUV_003
**Title:** Access `ServiceUpdateView` - Logged in, professional, but not owner
**Description:** Redirected by `ProfessionalOwnsObjectMixin`.
**Pre-conditions:**
    - User (P1) logged in, `Professional`.
    - Service S2 by another professional (P2) exists.
**Dependencies:** `users.Professional`, `Service` models.
**Steps:**
1. P1 attempts GET on `services:service_update` for S2.
**Expected Result:**
- Redirected (e.g. to `services:service_list`), error message.
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

**Case ID:** services_TC_V_SDV_D_002
**Title:** Access `ServiceDeleteView` - Logged in, not professional
**Description:** Redirected by `ProfessionalRequiredMixin`.
**Pre-conditions:** Service S1 exists. User logged in, no professional profile.
**Dependencies:** `Service` model.
**Steps:**
1. Attempt GET on `services:service_delete` for S1.
**Expected Result:**
- Redirected, error message.
**Post-conditions:** None.

**Case ID:** services_TC_V_SDV_D_003
**Title:** Access `ServiceDeleteView` - Logged in, professional, but not owner
**Description:** Redirected by `ProfessionalOwnsObjectMixin`.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S2 by P2 exists.
**Dependencies:** `users.Professional`, `Service` models.
**Steps:**
1. P1 attempts GET on `services:service_delete` for S2.
**Expected Result:**
- Redirected, error message.
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

**Case ID:** services_TC_V_ICV_002
**Title:** Access `ItemCreateView` - Logged in, not professional
**Description:** Redirected by `ProfessionalRequiredMixin`.
**Pre-conditions:** Service S1 exists. User logged in, no professional profile.
**Dependencies:** `Service` model.
**Steps:**
1. Attempt GET on `services:item_create` for S1.
**Expected Result:**
- Redirected (e.g. to `users:profile_choice`), error message.
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

**Case ID:** services_TC_V_ICV_005
**Title:** `ItemCreateView` POST request - Valid data by parent Service owner
**Description:** Owner creates a new item for their service with valid data.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S1 exists, `S1.professional == P1`.
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:**
1. P1 POSTs valid data (e.g., `title`, `description`, optional `image`) to `services:item_create` for S1.
**Expected Result:**
- A new `Item` object is created, associated with S1.
- Redirect to `services:service_detail` for S1 (HTTP 302).
- Success message displayed (e.g., "Item '{item.title}' created for service '{S1.title}'.").
**Post-conditions:** New `Item` record exists.

**Case ID:** services_TC_V_ICV_006
**Title:** `ItemCreateView` POST request - Invalid data by parent Service owner
**Description:** Form re-renders with errors for invalid data.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S1 exists, `S1.professional == P1`.
**Dependencies:** `users.Professional`, `Service` models.
**Steps:**
1. P1 POSTs invalid data (e.g., title="") to `services:item_create` for S1.
**Expected Result:**
- HTTP 200 OK (form re-rendered).
- Template `services/item_form.html` rendered.
- Form in context contains errors.
- Context `service` is S1.
- No new `Item` object is created.
**Post-conditions:** No new `Item` record.

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

#### View: `ItemListView` (`services:item_list`, service_pk=service.pk)
*(Note: This view might be integrated into `ServiceDetailView` in practice. If standalone, these tests apply.)*

**Case ID:** services_TC_V_ILV_001
**Title:** Access `ItemListView` - Not logged in
**Description:** Verify unauthenticated users are redirected.
**Pre-conditions:** Service S1 exists. User not logged in.
**Dependencies:** `Service` model.
**Steps:**
1. Attempt GET on `services:item_list` for S1.
**Expected Result:**
- Redirect to login.
**Post-conditions:** None.

**Case ID:** services_TC_V_ILV_002
**Title:** `ItemListView` GET - Owner of parent service
**Description:** Professional views list of items for their own service.
**Pre-conditions:**
    - User (P1) is logged in, `Professional`.
    - Service S1 exists, `S1.professional == P1`.
    - Items I1, I2 exist, associated with S1.
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:**
1. P1 GETs `services:item_list` for S1.
**Expected Result:**
- HTTP 200 OK.
- Template `services/item_list.html` is rendered.
- Context `items` contains I1, I2 (ordered by `-created_at`).
- Context `service` is S1.
- Context `page_title` is "Items for {S1.title}".
**Post-conditions:** None.

**Case ID:** services_TC_V_ILV_003
**Title:** `ItemListView` GET - Non-owner of parent service
**Description:** Redirected by `UserOwnsParentServiceMixin`.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S2 by P2 exists.
**Dependencies:** `users.Professional`, `Service` models.
**Steps:**
1. P1 attempts GET on `services:item_list` for S2.
**Expected Result:**
- Redirected, error message.
**Post-conditions:** None.

**Case ID:** services_TC_V_ILV_004
**Title:** `ItemListView` - Service has no items
**Description:** Page renders correctly if parent service has no items.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S1 (owned by P1) exists but has no items.
**Dependencies:** `users.Professional`, `Service` model.
**Steps:**
1. P1 GETs `services:item_list` for S1.
**Expected Result:**
- HTTP 200 OK.
- Context `items` is empty.
- Template shows a "no items" message.
**Post-conditions:** None.

#### View: `ItemDetailView` (`services:item_detail`, service_pk=service.pk, pk=item.pk)

**Case ID:** services_TC_V_IDV_001
**Title:** Access `ItemDetailView` - Not logged in
**Description:** Verify unauthenticated users are redirected.
**Pre-conditions:** Service S1, Item I1 (in S1) exist. User not logged in.
**Dependencies:** `Service`, `Item` models.
**Steps:**
1. Attempt GET on `services:item_detail` for I1 under S1.
**Expected Result:**
- Redirect to login.
**Post-conditions:** None.

**Case ID:** services_TC_V_IDV_002
**Title:** `ItemDetailView` GET - Owner of parent service
**Description:** Professional views detail of an item within their own service.
**Pre-conditions:**
    - User (P1) is logged in, `Professional`.
    - Service S1 exists, `S1.professional == P1`.
    - Item I1 exists, `I1.service == S1`.
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:**
1. P1 GETs `services:item_detail` for I1 under S1.
**Expected Result:**
- HTTP 200 OK.
- Template `services/item_detail.html` rendered.
- Context `item` is I1.
- Context `service` is S1.
- Context `page_title` is "Item: {I1.title}".
- Context `user_owns_service` is True.
- Associated prices for I1 are displayed.
**Post-conditions:** None.

**Case ID:** services_TC_V_IDV_003
**Title:** `ItemDetailView` GET - Non-owner of parent service
**Description:** Redirected by `UserOwnsParentServiceMixin`.
**Pre-conditions:**
    - User (P1) logged in, `Professional`.
    - Service S2 by P2 exists. Item I2 in S2.
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:**
1. P1 attempts GET on `services:item_detail` for I2 under S2.
**Expected Result:**
- HTTP 404 (or redirect with error if mixin handles it differently before `get_queryset`). `UserOwnsParentServiceMixin`'s `dispatch` will make `self.service` None or raise Http404, then `get_queryset` will fail to find the item.
**Post-conditions:** None.

**Case ID:** services_TC_V_IDV_004
**Title:** `ItemDetailView` GET - Item not found in specified service
**Description:** HTTP 404 if item PK exists but not under service_pk.
**Pre-conditions:**
    - User (P1) logged in, `Professional`. Owns Service S1.
    - Item I1 exists in S1. Item I2 exists in Service S2 (owned by P2).
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:**
1. P1 attempts GET `services:item_detail` with `service_pk=S1.pk` and `pk=I2.pk`.
**Expected Result:**
- HTTP 404 Not Found (because `get_queryset` filters by `service=self.service`).
**Post-conditions:** None.

**Case ID:** services_TC_V_IDV_005
**Title:** `ItemDetailView` GET - Item PK does not exist at all
**Description:** HTTP 404 if item PK is invalid.
**Pre-conditions:** User (P1) logged in, `Professional`. Owns Service S1.
**Dependencies:** `users.Professional`, `Service` model.
**Steps:**
1. P1 attempts GET `services:item_detail` for S1 with a non-existent item PK.
**Expected Result:**
- HTTP 404 Not Found.
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

**Case ID:** services_TC_V_IDV_D_002
**Title:** Access `ItemDeleteView` - Non-owner of parent Service
**Description:** Redirected by `UserOwnsParentServiceMixin`.
**Pre-conditions:** User (P1) logged in, Professional. Service S2 by P2, Item I2 in S2.
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:**
1. P1 attempts GET on `services:item_delete` for I2 under S2.
**Expected Result:**
- Redirected/HTTP 404.
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

**Case ID:** services_TC_V_PCV_002
**Title:** Access `PriceCreateView` - Non-owner of grandparent Service
**Description:** Redirected by `UserOwnsGrandparentServiceViaItemMixin`.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S2 by P2, Item I2 in S2.
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:**
1. P1 attempts GET on `services:price_create` for I2 under S2.
**Expected Result:**
- Redirected/HTTP 404.
**Post-conditions:** None.

**Case ID:** services_TC_V_PCV_003
**Title:** `PriceCreateView` GET request - Owner of grandparent Service
**Description:** Owner accesses price creation form for their item.
**Pre-conditions:** User (P1) logged in, `Professional`. Service S1 (by P1), Item I1 in S1.
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:**
1. P1 GETs `services:price_create` for I1 under S1.
**Expected Result:**
- HTTP 200 OK.
- Template `services/price_form.html` rendered.
- Unbound `PriceForm` in context.
- Context `service` is S1, `item` is I1.
- Context `page_title` is "Add Price to {I1.title} ({S1.title})".
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

**Case ID:** services_TC_V_PCV_006
**Title:** `PriceCreateView` GET - Parent Item or Service not found
**Description:** HTTP 404 if `service_pk` or `item_pk` in URL is invalid/mismatched.
**Pre-conditions:** User logged in, professional.
**Dependencies:** None.
**Steps:**
1. GET `services:price_create` with a non-existent `service_pk` or `item_pk`.
**Expected Result:**
- HTTP 404 Not Found (due to `get_object_or_404` in `UserOwnsGrandparentServiceViaItemMixin`).
**Post-conditions:** None.

#### View: `PriceListView` (`services:price_list`, service_pk=service.pk, item_pk=item.pk)
*(Note: This view might be integrated into `ItemDetailView`. If standalone, these tests apply.)*

**Case ID:** services_TC_V_PLV_001
**Title:** Access `PriceListView` - Not logged in
**Description:** Redirect.
**Pre-conditions:** Service S1, Item I1 exist. User not logged in.
**Dependencies:** `Service`, `Item` models.
**Steps:**
1. Attempt GET `services:price_list` for I1 under S1.
**Expected Result:**
- Redirect to login.
**Post-conditions:** None.

**Case ID:** services_TC_V_PLV_002
**Title:** `PriceListView` GET - Owner of grandparent service
**Description:** Professional views list of prices for an item in their service.
**Pre-conditions:** User (P1) logged in, `Professional`. S1 (by P1), I1 in S1. Prices Prc1, Prc2 for I1.
**Dependencies:** `users.Professional`, `Service`, `Item`, `Price` models.
**Steps:**
1. P1 GETs `services:price_list` for I1 under S1.
**Expected Result:**
- HTTP 200 OK. Template `services/price_list.html` rendered.
- Context `prices` contains Prc1, Prc2 (ordered by `-created_at`).
- Context `service` is S1, `item` is I1.
- Context `page_title` is "Prices for {I1.title}".
**Post-conditions:** None.

**Case ID:** services_TC_V_PLV_003
**Title:** `PriceListView` GET - Non-owner of grandparent service
**Description:** Redirected.
**Pre-conditions:** User (P1) logged in, `Professional`. S2 by P2, I2 in S2.
**Dependencies:** `users.Professional`, `Service`, `Item` models.
**Steps:**
1. P1 attempts GET `services:price_list` for I2 under S2.
**Expected Result:**
- Redirected/HTTP 404.
**Post-conditions:** None.

#### View: `PriceDetailView` (`services:price_detail`, service_pk=service.pk, item_pk=item.pk, pk=price.pk)

**Case ID:** services_TC_V_PDV_001
**Title:** Access `PriceDetailView` - Not logged in
**Description:** Redirect.
**Pre-conditions:** S1, I1 in S1, Price Prc1 for I1 exist. User not logged in.
**Dependencies:** `Service`, `Item`, `Price` models.
**Steps:**
1. Attempt GET `services:price_detail` for Prc1.
**Expected Result:**
- Redirect to login.
**Post-conditions:** None.

**Case ID:** services_TC_V_PDV_002
**Title:** `PriceDetailView` GET - Owner of grandparent service
**Description:** Owner views price details.
**Pre-conditions:** User (P1) logged in, `Professional`. S1 (by P1), I1 in S1, Prc1 for I1.
**Dependencies:** `users.Professional`, `Service`, `Item`, `Price` models.
**Steps:**
1. P1 GETs `services:price_detail` for Prc1 under I1, S1.
**Expected Result:**
- HTTP 200 OK. Template `services/price_detail.html` rendered.
- Context `price` is Prc1, `item` is I1, `service` is S1.
- Context `page_title` is "Price Details for {I1.title}".
- Context `user_owns_service` is True.
**Post-conditions:** None.

**Case ID:** services_TC_V_PDV_003
**Title:** `PriceDetailView` GET - Non-owner of grandparent service
**Description:** Redirected/HTTP 404.
**Pre-conditions:** User (P1) logged in, `Professional`. S2 by P2, I2 in S2, Prc2 for I2.
**Dependencies:** `users.Professional`, `Service`, `Item`, `Price` models.
**Steps:**
1. P1 attempts GET `services:price_detail` for Prc2.
**Expected Result:**
- Redirected/HTTP 404.
**Post-conditions:** None.

**Case ID:** services_TC_V_PDV_004
**Title:** `PriceDetailView` GET - Price not found for specified item/service
**Description:** HTTP 404 if price PK exists but not under specified item_pk/service_pk.
**Pre-conditions:** User (P1) logged in, `Professional`. Owns S1, I1. Price PrcX exists for another item/service.
**Dependencies:** `users.Professional`, `Service`, `Item`, `Price` models.
**Steps:**
1. P1 attempts GET `services:price_detail` with `service_pk=S1.pk`, `item_pk=I1.pk`, but `pk=PrcX.pk`.
**Expected Result:**
- HTTP 404.
**Post-conditions:** None.

#### View: `PriceUpdateView` (`services:price_update`, service_pk=service.pk, item_pk=item.pk, pk=price.pk)

**Case ID:** services_TC_V_PUV_001
**Title:** Access `PriceUpdateView` - Not logged in
**Description:** Redirect.
**Pre-conditions:** S1, I1, Prc1 exist. User not logged in.
**Dependencies:** `Service`, `Item`, `Price` models.
**Steps:**
1. Attempt GET `services:price_update` for Prc1.
**Expected Result:**
- Redirect to login.
**Post-conditions:** None.

**Case ID:** services_TC_V_PUV_002
**Title:** Access `PriceUpdateView` - Non-owner of grandparent service
**Description:** Redirected/HTTP 404.
**Pre-conditions:** User (P1) logged in, `Professional`. S2 by P2, I2 in S2, Prc2 for I2.
**Dependencies:** `users.Professional`, `Service`, `Item`, `Price` models.
**Steps:**
1. P1 attempts GET `services:price_update` for Prc2.
**Expected Result:**
- Redirected/HTTP 404.
**Post-conditions:** None.

**Case ID:** services_TC_V_PUV_003
**Title:** `PriceUpdateView` GET - Owner
**Description:** Owner accesses price update form.
**Pre-conditions:** User (P1) logged in, `Professional`. S1 (by P1), I1 in S1, Prc1 for I1.
**Dependencies:** `users.Professional`, `Service`, `Item`, `Price` models.
**Steps:**
1. P1 GETs `services:price_update` for Prc1.
**Expected Result:**
- HTTP 200 OK. Template `services/price_form.html` rendered.
- Form bound with Prc1's data.
- Context `service` is S1, `item` is I1.
- Context `page_title` is "Edit Price for {I1.title}".
**Post-conditions:** None.

**Case ID:** services_TC_V_PUV_004
**Title:** `PriceUpdateView` POST - Valid data by owner
**Description:** Owner updates price with valid data.
**Pre-conditions:** User (P1) logged in, `Professional`. S1 (by P1), I1 in S1, Prc1 for I1.
**Dependencies:** `users.Professional`, `Service`, `Item`, `Price` models.
**Steps:**
1. P1 POSTs valid updated price data to `services:price_update` for Prc1.
**Expected Result:**
- Prc1 is updated.
- Redirect to `services:price_detail` for Prc1.
- Success message.
**Post-conditions:** Prc1 record modified.

**Case ID:** services_TC_V_PUV_005
**Title:** `PriceUpdateView` POST - Invalid data by owner
**Description:** Form re-renders with errors.
**Pre-conditions:** User (P1) logged in, `Professional`. S1 (by P1), I1 in S1, Prc1 for I1.
**Dependencies:** `users.Professional`, `Service`, `Item`, `Price` models.
**Steps:**
1. P1 POSTs invalid data (e.g. amount="text") to `services:price_update` for Prc1.
**Expected Result:**
- HTTP 200 OK. Form has errors.
- Prc1 not updated.
**Post-conditions:** Prc1 unchanged.

#### View: `PriceDeleteView` (`services:price_delete`, service_pk=service.pk, item_pk=item.pk, pk=price.pk)

**Case ID:** services_TC_V_PDV_D_001
**Title:** Access `PriceDeleteView` - Not logged in
**Description:** Redirect.
**Pre-conditions:** S1, I1, Prc1 exist. User not logged in.
**Dependencies:** `Service`, `Item`, `Price` models.
**Steps:**
1. Attempt GET `services:price_delete` for Prc1.
**Expected Result:**
- Redirect to login.
**Post-conditions:** None.

**Case ID:** services_TC_V_PDV_D_002
**Title:** Access `PriceDeleteView` - Non-owner
**Description:** Redirected/HTTP 404.
**Pre-conditions:** User (P1) logged in, `Professional`. S2 by P2, I2 in S2, Prc2 for I2.
**Dependencies:** `users.Professional`, `Service`, `Item`, `Price` models.
**Steps:**
1. P1 attempts GET `services:price_delete` for Prc2.
**Expected Result:**
- Redirected/HTTP 404.
**Post-conditions:** None.

**Case ID:** services_TC_V_PDV_D_003
**Title:** `PriceDeleteView` GET - Owner
**Description:** Owner accesses delete confirmation page for price.
**Pre-conditions:** User (P1) logged in, `Professional`. S1 (by P1), I1 in S1, Prc1 for I1.
**Dependencies:** `users.Professional`, `Service`, `Item`, `Price` models.
**Steps:**
1. P1 GETs `services:price_delete` for Prc1.
**Expected Result:**
- HTTP 200 OK. Template `services/price_confirm_delete.html` rendered.
- Context `price` is Prc1, `item` is I1, `service` is S1.
- Context `page_title` is "Delete Price for {I1.title}".
**Post-conditions:** None.

**Case ID:** services_TC_V_PDV_D_004
**Title:** `PriceDeleteView` POST - Owner confirms deletion
**Description:** Owner deletes their price.
**Pre-conditions:** User (P1) logged in, `Professional`. S1 (by P1), I1 in S1, Prc1 for I1.
**Dependencies:** `users.Professional`, `Service`, `Item`, `Price` models.
**Steps:**
1. P1 POSTs to `services:price_delete` for Prc1.
**Expected Result:**
- Prc1 is deleted.
- Redirect to `services:item_detail` for I1 under S1.
- Success message.
**Post-conditions:** Prc1 record no longer exists.

