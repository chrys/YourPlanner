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

**Case ID:** services_TC_M_SC_003
**Title:** ServiceCategory slug auto-generation
**Description:** Verify that the `slug` is correctly auto-generated from the `name` upon saving if not provided.
**Pre-conditions:** None
**Dependencies:** None
**Steps:**
1. Create a `ServiceCategory` instance with a specific `name` (e.g., "New Category 123").
2. Do not provide a `slug`.
3. Save the instance.
**Expected Result:**
- The instance is saved successfully.
- The `slug` field is populated with the slugified version of the name (e.g., "new-category-123").
**Post-conditions:** The `ServiceCategory` instance exists with an auto-generated slug.

**Case ID:** services_TC_M_SC_004
**Title:** ServiceCategory slug uniqueness
**Description:** Verify that attempting to save a `ServiceCategory` with a duplicate slug raises an integrity error.
**Pre-conditions:** A `ServiceCategory` with a specific slug (e.g., "unique-slug") already exists.
**Dependencies:** None
**Steps:**
1. Create another `ServiceCategory` instance.
2. Manually set its `slug` to be identical to an existing one ("unique-slug").
3. Attempt to save the new instance.
**Expected Result:**
- An `IntegrityError` (or similar database error) is raised due to the unique constraint on the `slug` field.
- The new instance is not saved.
**Post-conditions:** No new `ServiceCategory` instance with the duplicate slug is created.

**Case ID:** services_TC_M_SC_005
**Title:** ServiceCategory string representation
**Description:** Verify the `__str__` method of `ServiceCategory` returns the category name.
**Pre-conditions:** A `ServiceCategory` instance exists with a known name.
**Dependencies:** None
**Steps:**
1. Retrieve an existing `ServiceCategory` instance.
2. Call `str()` on the instance.
**Expected Result:**
- The string representation is equal to the `name` of the category.
**Post-conditions:** None.

**Case ID:** services_TC_M_SC_006
**Title:** Create ServiceCategory with blank description
**Description:** Verify that a `ServiceCategory` instance can be created with a blank `description`.
**Pre-conditions:** None
**Dependencies:** None
**Steps:**
1. Create a `ServiceCategory` instance with a unique `name` and `description` = "" or None.
2. Save the instance.
**Expected Result:**
- The `ServiceCategory` instance is created successfully.
- The instance is saved to the database.
**Post-conditions:** The created `ServiceCategory` instance exists in the database.

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

**Case ID:** services_TC_M_S_004
**Title:** Service slug auto-generation
**Description:** Verify that the `slug` is correctly auto-generated from `title` and `professional.pk` upon saving if not provided.
**Pre-conditions:** A `users.Professional` instance (e.g., with pk=1) exists.
**Dependencies:** `users.Professional` model.
**Steps:**
1. Create a `Service` instance with `professional` and `title` (e.g., "My Awesome Service").
2. Do not provide a `slug`.
3. Save the instance.
**Expected Result:**
- The instance is saved successfully.
- The `slug` field is populated (e.g., "my-awesome-service-1").
**Post-conditions:** The `Service` instance exists with an auto-generated slug.

**Case ID:** services_TC_M_S_005
**Title:** Service slug uniqueness per professional
**Description:** Verify `UniqueConstraint(fields=['professional', 'slug'], name='unique_professional_service_slug')`.
**Pre-conditions:**
- A `users.Professional` (P1) exists.
- P1 has a `Service` (S1) with a specific slug (e.g., "my-service-slug").
**Dependencies:** `users.Professional` model.
**Steps:**
1. Create a new `Service` instance (S2) for the same professional P1.
2. Manually set its `slug` to be identical to S1's slug ("my-service-slug").
3. Attempt to save S2.
**Expected Result:**
- An `IntegrityError` is raised.
- S2 is not saved.
**Post-conditions:** No new `Service` instance with the duplicate professional/slug combination is created.

**Case ID:** services_TC_M_S_006
**Title:** Service slug can be non-unique for different professionals
**Description:** Verify that two different professionals can have services with the same slug.
**Pre-conditions:**
- Two `users.Professional` instances (P1, P2) exist.
- P1 has a `Service` (S1) with a specific slug (e.g., "common-slug").
**Dependencies:** `users.Professional` model.
**Steps:**
1. Create a new `Service` instance (S2) for professional P2.
2. Set its `slug` to "common-slug".
3. Save S2.
**Expected Result:**
- S2 is saved successfully.
**Post-conditions:** S2 exists in the database.

**Case ID:** services_TC_M_S_007
**Title:** Service `clean` method - duplicate title for the same professional
**Description:** Verify `clean()` prevents a professional from having two services with the exact same title.
**Pre-conditions:**
- A `users.Professional` (P1) exists.
- P1 has a `Service` (S1) with `title` = "Unique Title for P1".
**Dependencies:** `users.Professional` model.
**Steps:**
1. Create a new `Service` instance (S2) for professional P1.
2. Set `title` of S2 to "Unique Title for P1".
3. Call `clean()` on S2.
**Expected Result:**
- A `ValidationError` is raised with a message like 'You already have a service with this title'.
**Post-conditions:** S2 is not in a savable state if `clean()` is enforced.

**Case ID:** services_TC_M_S_008
**Title:** Service `clean` method - allows same title for different professionals
**Description:** Verify `clean()` allows different professionals to have services with the same title.
**Pre-conditions:**
- `users.Professional` P1 exists and has a service titled "Common Service Title".
- `users.Professional` P2 exists.
**Dependencies:** `users.Professional` model.
**Steps:**
1. Create a new `Service` instance (S_P2) for professional P2.
2. Set `title` of S_P2 to "Common Service Title".
3. Call `clean()` on S_P2.
**Expected Result:**
- No `ValidationError` is raised regarding the title.
**Post-conditions:** S_P2 is considered valid by the `clean` method regarding its title.

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

**Case ID:** services_TC_M_S_012
**Title:** `calculate_average_rating` method (placeholder)
**Description:** Verify the `calculate_average_rating` method returns 0.0 as per current implementation.
**Pre-conditions:** A `Service` instance exists.
**Dependencies:** None.
**Steps:**
1. Call `calculate_average_rating()` on the service instance.
**Expected Result:**
- The method returns `0.0`.
**Post-conditions:** None.

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

**Case ID:** services_TC_M_I_004
**Title:** Item slug auto-generation
**Description:** Verify that the `slug` is correctly auto-generated from `title` and `service.pk` upon saving if not provided.
**Pre-conditions:** A `Service` instance (e.g., with pk=1) exists.
**Dependencies:** `Service` model.
**Steps:**
1. Create an `Item` instance with `service` and `title` (e.g., "New Component").
2. Do not provide a `slug`.
3. Save the instance.
**Expected Result:**
- The instance is saved successfully.
- The `slug` field is populated (e.g., "new-component-1").
**Post-conditions:** The `Item` instance exists with an auto-generated slug.

**Case ID:** services_TC_M_I_005
**Title:** Item slug uniqueness per service
**Description:** Verify `UniqueConstraint(fields=['service', 'slug'], name='unique_service_item_slug')`.
**Pre-conditions:**
- A `Service` (S1) exists.
- S1 has an `Item` (I1) with a specific slug (e.g., "item-slug-a").
**Dependencies:** `Service` model.
**Steps:**
1. Create a new `Item` instance (I2) for the same service S1.
2. Manually set its `slug` to be identical to I1's slug ("item-slug-a").
3. Attempt to save I2.
**Expected Result:**
- An `IntegrityError` is raised.
- I2 is not saved.
**Post-conditions:** No new `Item` instance with the duplicate service/slug combination is created.

**Case ID:** services_TC_M_I_006
**Title:** Item slug can be non-unique for different services
**Description:** Verify that two different services can have items with the same slug.
**Pre-conditions:**
- Two `Service` instances (S1, S2) exist.
- S1 has an `Item` (I1) with a specific slug (e.g., "common-item-slug").
**Dependencies:** `Service` model.
**Steps:**
1. Create a new `Item` instance (I2) for service S2.
2. Set its `slug` to "common-item-slug".
3. Save I2.
**Expected Result:**
- I2 is saved successfully.
**Post-conditions:** I2 exists in the database.

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

**Case ID:** services_TC_M_I_008
**Title:** Item `is_available` method - stock > 0
**Description:** Verify `is_available()` returns `True` if `stock` is greater than 0.
**Pre-conditions:** An `Item` instance exists with `stock` = 10.
**Dependencies:** None.
**Steps:**
1. Call `is_available()` on the item instance.
**Expected Result:**
- The method returns `True`.
**Post-conditions:** None.

**Case ID:** services_TC_M_I_009
**Title:** Item `is_available` method - stock = 0 (unlimited/not applicable)
**Description:** Verify `is_available()` returns `True` if `stock` is 0.
**Pre-conditions:** An `Item` instance exists with `stock` = 0.
**Dependencies:** None.
**Steps:**
1. Call `is_available()` on the item instance.
**Expected Result:**
- The method returns `True`.
**Post-conditions:** None.

**Case ID:** services_TC_M_I_010
**Title:** Item with image upload
**Description:** Verify an `Item` can be created with an image.
**Pre-conditions:** A `Service` instance exists. A valid image file is available.
**Dependencies:** `Service` model.
**Steps:**
1. Create an `Item` instance with `service`, `title`, and provide a file to the `image` field.
2. Save the instance.
**Expected Result:**
- The `Item` is saved successfully.
- The `image` field has a path to the uploaded image.
**Post-conditions:** The `Item` instance exists with an associated image.

**Case ID:** services_TC_M_I_011
**Title:** Item with default stock and position
**Description:** Verify `Item` is created with default `stock` (0) and `position` (0) if not provided.
**Pre-conditions:** A `Service` instance exists.
**Dependencies:** `Service` model.
**Steps:**
1. Create an `Item` instance with `service` and `title`, without specifying `stock` or `position`.
2. Save the instance.
3. Retrieve the item and check its `stock` and `position`.
**Expected Result:**
- `item.stock` is 0.
- `item.position` is 0.
**Post-conditions:** The `Item` instance exists with default stock and position.

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

**Case ID:** services_TC_M_P_004
**Title:** Price `clean` method - `valid_from` after `valid_until`
**Description:** Verify `clean()` prevents saving if `valid_from` is after `valid_until`.
**Pre-conditions:** An `Item` instance exists.
**Dependencies:** `Item` model.
**Steps:**
1. Create a `Price` instance with `valid_from` = (today + 1 day), `valid_until` = today.
2. Call `clean()` on the instance.
**Expected Result:**
- A `ValidationError` is raised with a message like 'End date must be after start date'.
**Post-conditions:** Not savable.

**Case ID:** services_TC_M_P_005
**Title:** Price `clean` method - `min_quantity` less than 1
**Description:** Verify `clean()` prevents saving if `min_quantity` is less than 1.
**Pre-conditions:** An `Item` instance exists.
**Dependencies:** `Item` model.
**Steps:**
1. Create a `Price` instance with `min_quantity` = 0.
2. Call `clean()` on the instance.
**Expected Result:**
- A `ValidationError` is raised with a message like 'Minimum quantity must be at least 1'.
**Post-conditions:** Not savable.

**Case ID:** services_TC_M_P_006
**Title:** Price `clean` method - `min_quantity` greater than `max_quantity`
**Description:** Verify `clean()` prevents saving if `min_quantity` > `max_quantity` (and `max_quantity` is set).
**Pre-conditions:** An `Item` instance exists.
**Dependencies:** `Item` model.
**Steps:**
1. Create a `Price` instance with `min_quantity` = 10, `max_quantity` = 5.
2. Call `clean()` on the instance.
**Expected Result:**
- A `ValidationError` is raised with a message like 'Maximum quantity must be greater than minimum quantity'.
**Post-conditions:** Not savable.

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

**Case ID:** services_TC_M_P_010
**Title:** `is_valid_now` method - not yet valid price
**Description:** Verify `is_valid_now()` returns `False` if `valid_from` is in the future.
**Pre-conditions:** An `Item` and `Price` exist. Price `is_active=True`, `valid_from` is set to tomorrow.
**Dependencies:** `Item` model.
**Steps:**
1. Call `is_valid_now()` on the price instance.
**Expected Result:**
- The method returns `False`.
**Post-conditions:** None.

**Case ID:** services_TC_M_P_011
**Title:** `is_valid_now` method - expired price
**Description:** Verify `is_valid_now()` returns `False` if `valid_until` is in the past.
**Pre-conditions:** An `Item` and `Price` exist. Price `is_active=True`, `valid_until` is set to yesterday.
**Dependencies:** `Item` model.
**Steps:**
1. Call `is_valid_now()` on the price instance.
**Expected Result:**
- The method returns `False`.
**Post-conditions:** None.

**Case ID:** services_TC_M_P_012
**Title:** `is_valid_now` method - inactive price
**Description:** Verify `is_valid_now()` returns `False` if `is_active=False`, even if dates are valid.
**Pre-conditions:** An `Item` and `Price` exist. Price `is_active=False`. Dates are otherwise valid.
**Dependencies:** `Item` model.
**Steps:**
1. Call `is_valid_now()` on the price instance.
**Expected Result:**
- The method returns `False`.
**Post-conditions:** None.

**Case ID:** services_TC_M_P_013
**Title:** `get_discounted_amount` method - no discount
**Description:** Verify `get_discounted_amount()` returns original amount if `discount_percentage` is 0.
**Pre-conditions:** A `Price` instance exists with `amount` = 100.00, `discount_percentage` = 0.00.
**Dependencies:** `Item` model.
**Steps:**
1. Call `get_discounted_amount()` on the price instance.
**Expected Result:**
- The method returns 100.00.
**Post-conditions:** None.

**Case ID:** services_TC_M_P_014
**Title:** `get_discounted_amount` method - with discount
**Description:** Verify `get_discounted_amount()` returns correctly calculated discounted amount.
**Pre-conditions:** A `Price` instance exists with `amount` = 100.00, `discount_percentage` = 10.00 (i.e., 10%).
**Dependencies:** `Item` model.
**Steps:**
1. Call `get_discounted_amount()` on the price instance.
**Expected Result:**
- The method returns 90.00.
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

## Test Cases for Forms (`services/forms.py`)

### Form: `ServiceForm`

**Case ID:** services_TC_F_SF_001
**Title:** Render empty ServiceForm
**Description:** Verify that an unbound `ServiceForm` renders correctly with all its fields and widgets.
**Pre-conditions:** None
**Dependencies:** `Service` model.
**Steps:**
1. Instantiate an empty `ServiceForm`.
2. Render the form (e.g., using `as_p()`, `as_table()`, or by rendering a template containing the form).
**Expected Result:**
- The form renders with fields: `title`, `description`, `is_active`.
- `title` widget is `forms.TextInput` with class `form-control`.
- `description` widget is `forms.Textarea` with class `form-control` and `rows: 3`.
- `is_active` widget is `forms.CheckboxInput` with class `form-check-input`.
**Post-conditions:** None.

**Case ID:** services_TC_F_SF_002
**Title:** Render bound ServiceForm with initial data
**Description:** Verify that a `ServiceForm` bound to a `Service` instance displays the instance's data.
**Pre-conditions:** A `Service` instance (s1) exists with known `title`, `description`, and `is_active` status.
**Dependencies:** `Service` model.
**Steps:**
1. Instantiate `ServiceForm` with `instance=s1`.
2. Render the form.
**Expected Result:**
- The form fields are pre-populated with the data from s1.
- `title` field shows s1.title.
- `description` field shows s1.description.
- `is_active` checkbox reflects s1.is_active.
**Post-conditions:** None.

**Case ID:** services_TC_F_SF_003
**Title:** Submit ServiceForm with valid data (create new)
**Description:** Verify that a `ServiceForm` submitted with valid data passes validation and can save a new `Service` instance.
**Pre-conditions:** A `users.Professional` instance (prof1) exists to associate the service with.
**Dependencies:** `Service` model, `users.Professional` model.
**Steps:**
1. Prepare valid data for the form: `title` = "New Test Service", `description` = "Details", `is_active` = True.
2. Instantiate `ServiceForm` with the prepared data.
3. Check if `form.is_valid()` is True.
4. If valid, call `form.save(commit=False)` to get an instance.
5. Assign `form.instance.professional = prof1`.
6. Call `form.instance.save()` (or `form.save()` if professional is handled by the view).
**Expected Result:**
- `form.is_valid()` returns `True`.
- `form.errors` is empty.
- A new `Service` instance is created with the submitted data and associated professional.
**Post-conditions:** A new `Service` record exists in the database.

**Case ID:** services_TC_F_SF_004
**Title:** Submit ServiceForm with valid data (update existing)
**Description:** Verify that a `ServiceForm` submitted with valid data can update an existing `Service` instance.
**Pre-conditions:** A `Service` instance (s1) exists.
**Dependencies:** `Service` model.
**Steps:**
1. Prepare valid data for update: `title` = "Updated Test Service", `description` = "Updated Details", `is_active` = False.
2. Instantiate `ServiceForm` with `data=prepared_data` and `instance=s1`.
3. Check if `form.is_valid()` is True.
4. If valid, call `form.save()`.
**Expected Result:**
- `form.is_valid()` returns `True`.
- `form.errors` is empty.
- The `Service` instance s1 is updated in the database with the new data.
**Post-conditions:** The `Service` record s1 is updated.

**Case ID:** services_TC_F_SF_005
**Title:** Submit ServiceForm with missing title (invalid)
**Description:** Verify that submitting a `ServiceForm` without a `title` results in a validation error.
**Pre-conditions:** None
**Dependencies:** `Service` model.
**Steps:**
1. Prepare data with `title` = "" or None, valid `description` and `is_active`.
2. Instantiate `ServiceForm` with this data.
3. Check `form.is_valid()`.
**Expected Result:**
- `form.is_valid()` returns `False`.
- `form.errors` contains an error for the `title` field (e.g., "This field is required.").
**Post-conditions:** No `Service` instance is created or updated.

**Case ID:** services_TC_F_SF_006
**Title:** Submit ServiceForm with description only spaces (valid)
**Description:** Verify that submitting a `ServiceForm` with a description containing only spaces is considered valid as description is not mandatory and can be blank.
**Pre-conditions:** None
**Dependencies:** `Service` model.
**Steps:**
1. Prepare data with valid `title`, `description` = "   ", `is_active` = True.
2. Instantiate `ServiceForm` with this data.
3. Check `form.is_valid()`.
**Expected Result:**
- `form.is_valid()` returns `True`.
- `form.cleaned_data['description']` should be "   " (or stripped, depending on form/model cleaning).
**Post-conditions:** No `Service` instance is created or updated if not saved.

**Case ID:** services_TC_F_SF_007
**Title:** ServiceForm fields attribute check
**Description:** Verify that `ServiceForm.Meta.fields` includes 'title', 'description', 'is_active'.
**Pre-conditions:** None
**Dependencies:** None
**Steps:**
1. Inspect `ServiceForm.Meta.fields`.
**Expected Result:**
- The fields list is `['title', 'description', 'is_active']`.
**Post-conditions:** None.

### Form: `ItemForm`

**Case ID:** services_TC_F_IF_001
**Title:** Render empty ItemForm
**Description:** Verify that an unbound `ItemForm` renders correctly with all its fields and widgets.
**Pre-conditions:** None
**Dependencies:** `Item` model.
**Steps:**
1. Instantiate an empty `ItemForm`.
2. Render the form.
**Expected Result:**
- The form renders with fields: `title`, `description`, `image`.
- `title` widget is `forms.TextInput` with class `form-control`.
- `description` widget is `forms.Textarea` with class `form-control` and `rows: 3`.
- `image` widget is `forms.ClearableFileInput` with class `form-control-file`.
- Help text for `image` field is displayed: "Upload an image for the item (optional)."
**Post-conditions:** None.

**Case ID:** services_TC_F_IF_002
**Title:** Render bound ItemForm with initial data (including image)
**Description:** Verify that an `ItemForm` bound to an `Item` instance displays the instance's data, including image information.
**Pre-conditions:** An `Item` instance (i1) exists with known `title`, `description`, and an uploaded `image`.
**Dependencies:** `Item` model.
**Steps:**
1. Instantiate `ItemForm` with `instance=i1`.
2. Render the form.
**Expected Result:**
- The form fields are pre-populated. `title` shows i1.title, `description` shows i1.description.
- The `image` field shows information about the current image and options to clear or change it.
**Post-conditions:** None.

**Case ID:** services_TC_F_IF_003
**Title:** Submit ItemForm with valid data (create new, no image)
**Description:** Verify `ItemForm` submitted with valid text data (no image) passes validation and can save a new `Item`.
**Pre-conditions:** A `Service` instance (s1) exists to associate the item with.
**Dependencies:** `Item` model, `Service` model.
**Steps:**
1. Prepare valid data: `title` = "New Test Item", `description` = "Item Details". (No image file).
2. Instantiate `ItemForm` with `data=prepared_data`.
3. Check `form.is_valid()`.
4. If valid, `form.save(commit=False)`, then set `form.instance.service = s1`.
5. `form.instance.save()`.
**Expected Result:**
- `form.is_valid()` returns `True`.
- `form.errors` is empty.
- A new `Item` instance is created with the submitted data, associated service, and no image.
**Post-conditions:** A new `Item` record exists.

**Case ID:** services_TC_F_IF_004
**Title:** Submit ItemForm with valid data (create new, with image)
**Description:** Verify `ItemForm` submitted with valid data including an image file passes validation and saves the `Item` with the image.
**Pre-conditions:**
    - A `Service` instance (s1) exists.
    - A valid image file is prepared for upload.
**Dependencies:** `Item` model, `Service` model.
**Steps:**
1. Prepare data: `title` = "Item With Image", `description` = "Desc.".
2. Prepare files data: `image` = (UploadedFile object for the image).
3. Instantiate `ItemForm` with `data=prepared_data`, `files=prepared_files_data`.
4. Check `form.is_valid()`.
5. If valid, `form.save(commit=False)`, then set `form.instance.service = s1`.
6. `form.instance.save()`.
**Expected Result:**
- `form.is_valid()` returns `True`.
- A new `Item` is created with the image correctly uploaded and associated.
**Post-conditions:** A new `Item` record exists with an image.

**Case ID:** services_TC_F_IF_005
**Title:** Submit ItemForm with valid data (update existing, change image)
**Description:** Verify `ItemForm` can update an existing `Item` and change its image.
**Pre-conditions:**
    - An `Item` instance (i1) exists, possibly with an old image.
    - A new valid image file is prepared.
**Dependencies:** `Item` model.
**Steps:**
1. Prepare data: `title` = i1.title (or new title).
2. Prepare files data: `image` = (UploadedFile for the new image).
3. Instantiate `ItemForm` with `data=prepared_data`, `files=prepared_files_data`, `instance=i1`.
4. Check `form.is_valid()`.
5. If valid, `form.save()`.
**Expected Result:**
- `form.is_valid()` returns `True`.
- Item i1 is updated, and its `image` field points to the new image. The old image might be deleted depending on storage backend.
**Post-conditions:** Item i1 is updated with the new image.

**Case ID:** services_TC_F_IF_006
**Title:** Submit ItemForm with valid data (update existing, clear image)
**Description:** Verify `ItemForm` can update an `Item` and clear its existing image.
**Pre-conditions:** An `Item` instance (i1) exists with an image.
**Dependencies:** `Item` model.
**Steps:**
1. Prepare data: `title` = i1.title, and include the special form field for clearing the image (e.g., `image-clear` = 'on', depending on how `ClearableFileInput` works).
2. Instantiate `ItemForm` with `data=prepared_data`, `instance=i1`.
3. Check `form.is_valid()`.
4. If valid, `form.save()`.
**Expected Result:**
- `form.is_valid()` returns `True`.
- Item i1 is updated, and its `image` field becomes empty/None.
**Post-conditions:** Item i1's image is cleared.

**Case ID:** services_TC_F_IF_007
**Title:** Submit ItemForm with missing title (invalid)
**Description:** Verify submitting `ItemForm` without a `title` results in a validation error.
**Pre-conditions:** None
**Dependencies:** `Item` model.
**Steps:**
1. Prepare data with `title` = "", valid `description`.
2. Instantiate `ItemForm` with this data.
3. Check `form.is_valid()`.
**Expected Result:**
- `form.is_valid()` returns `False`.
- `form.errors` contains an error for `title`.
**Post-conditions:** No `Item` is created/updated.

**Case ID:** services_TC_F_IF_008
**Title:** Submit ItemForm with invalid image file type
**Description:** Verify submitting `ItemForm` with an invalid file type for the image results in a validation error.
**Pre-conditions:** A non-image file (e.g., a .txt file) is prepared.
**Dependencies:** `Item` model.
**Steps:**
1. Prepare data: `title` = "Item with Bad Image".
2. Prepare files data: `image` = (UploadedFile object for the .txt file).
3. Instantiate `ItemForm` with `data=prepared_data`, `files=prepared_files_data`.
4. Check `form.is_valid()`.
**Expected Result:**
- `form.is_valid()` returns `False`.
- `form.errors` contains an error for the `image` field related to invalid file type.
**Post-conditions:** No `Item` is created/updated.

**Case ID:** services_TC_F_IF_009
**Title:** ItemForm fields attribute check
**Description:** Verify that `ItemForm.Meta.fields` includes 'title', 'description', 'image'.
**Pre-conditions:** None
**Dependencies:** None
**Steps:**
1. Inspect `ItemForm.Meta.fields`.
**Expected Result:**
- The fields list is `['title', 'description', 'image']`.
**Post-conditions:** None.

### Form: `PriceForm`

**Case ID:** services_TC_F_PF_001
**Title:** Render empty PriceForm
**Description:** Verify that an unbound `PriceForm` renders correctly with its fields, widgets, and initial values.
**Pre-conditions:** None
**Dependencies:** `Price` model.
**Steps:**
1. Instantiate an empty `PriceForm`.
2. Render the form.
**Expected Result:**
- The form renders with fields: `amount`, `currency`, `frequency`, `description`, `is_active`.
- `amount` widget is `forms.NumberInput` with class `form-control`.
- `currency` widget is `forms.Select` with class `form-select`, populated with `Price.CURRENCY_CHOICES`. Initial value should be 'EUR' due to form's `__init__`.
- `frequency` widget is `forms.Select` with class `form-select`, populated with `Price.FrequencyChoices.choices`.
- `description` widget is `forms.Textarea` with class `form-control`, `rows: 2`.
- `is_active` widget is `forms.CheckboxInput` with class `form-check-input`.
- Labels are: 'Price' for `amount`, 'Currency' for `currency`, 'Frequency' for `frequency`, 'Active' for `is_active`.
**Post-conditions:** None.

**Case ID:** services_TC_F_PF_002
**Title:** Render bound PriceForm with initial data
**Description:** Verify that a `PriceForm` bound to a `Price` instance displays the instance's data.
**Pre-conditions:** A `Price` instance (p1) exists with known values for all fields.
**Dependencies:** `Price` model.
**Steps:**
1. Instantiate `PriceForm` with `instance=p1`.
2. Render the form.
**Expected Result:**
- Form fields are pre-populated with data from p1 (amount, currency, frequency, description, is_active status).
**Post-conditions:** None.

**Case ID:** services_TC_F_PF_003
**Title:** Submit PriceForm with valid data (create new)
**Description:** Verify `PriceForm` submitted with valid data passes validation and can save a new `Price` instance.
**Pre-conditions:** An `Item` instance (i1) exists to associate the price with.
**Dependencies:** `Price` model, `Item` model.
**Steps:**
1. Prepare valid data: `amount`=50.00, `currency`='USD', `frequency`='HOURLY', `description`="Hourly rate", `is_active`=True.
2. Instantiate `PriceForm` with this data.
3. Check `form.is_valid()`.
4. If valid, `form.save(commit=False)`, then set `form.instance.item = i1`.
5. `form.instance.save()`.
**Expected Result:**
- `form.is_valid()` returns `True`.
- `form.errors` is empty.
- A new `Price` instance is created with submitted data and associated item.
**Post-conditions:** A new `Price` record exists.

**Case ID:** services_TC_F_PF_004
**Title:** Submit PriceForm with valid data (update existing)
**Description:** Verify `PriceForm` can update an existing `Price` instance.
**Pre-conditions:** A `Price` instance (p1) exists.
**Dependencies:** `Price` model.
**Steps:**
1. Prepare update data: `amount`=75.00, `currency`='GBP', `is_active`=False.
2. Instantiate `PriceForm` with `data=prepared_data`, `instance=p1`.
3. Check `form.is_valid()`.
4. If valid, `form.save()`.
**Expected Result:**
- `form.is_valid()` returns `True`.
- Price instance p1 is updated in the database.
**Post-conditions:** Price record p1 is updated.

**Case ID:** services_TC_F_PF_005
**Title:** Submit PriceForm with missing amount (invalid)
**Description:** Verify submitting `PriceForm` without `amount` results in a validation error.
**Pre-conditions:** None
**Dependencies:** `Price` model.
**Steps:**
1. Prepare data with `amount`=None, other fields valid.
2. Instantiate `PriceForm` with this data.
3. Check `form.is_valid()`.
**Expected Result:**
- `form.is_valid()` returns `False`.
- `form.errors` contains an error for `amount`.
**Post-conditions:** No `Price` is created/updated.

**Case ID:** services_TC_F_PF_006
**Title:** Submit PriceForm with invalid amount (e.g., text)
**Description:** Verify submitting `PriceForm` with non-numeric `amount` results in validation error.
**Pre-conditions:** None
**Dependencies:** `Price` model.
**Steps:**
1. Prepare data with `amount`="abc", other fields valid.
2. Instantiate `PriceForm` with this data.
3. Check `form.is_valid()`.
**Expected Result:**
- `form.is_valid()` returns `False`.
- `form.errors` contains an error for `amount` (e.g., "Enter a number.").
**Post-conditions:** No `Price` is created/updated.

**Case ID:** services_TC_F_PF_007
**Title:** Submit PriceForm with invalid currency choice
**Description:** Verify submitting `PriceForm` with a `currency` value not in `Price.CURRENCY_CHOICES` results in a validation error.
**Pre-conditions:** None
**Dependencies:** `Price` model.
**Steps:**
1. Prepare data with `currency`="XYZ", other fields valid.
2. Instantiate `PriceForm` with this data.
3. Check `form.is_valid()`.
**Expected Result:**
- `form.is_valid()` returns `False`.
- `form.errors` contains an error for `currency` (e.g., "Select a valid choice. XYZ is not one of the available choices.").
**Post-conditions:** No `Price` is created/updated.

**Case ID:** services_TC_F_PF_008
**Title:** Submit PriceForm with invalid frequency choice
**Description:** Verify submitting `PriceForm` with a `frequency` value not in `Price.FrequencyChoices` results in a validation error.
**Pre-conditions:** None
**Dependencies:** `Price` model.
**Steps:**
1. Prepare data with `frequency`="SOMETIMES", other fields valid.
2. Instantiate `PriceForm` with this data.
3. Check `form.is_valid()`.
**Expected Result:**
- `form.is_valid()` returns `False`.
- `form.errors` contains an error for `frequency`.
**Post-conditions:** No `Price` is created/updated.

**Case ID:** services_TC_F_PF_009
**Title:** PriceForm `__init__` currency default for new instance
**Description:** Verify that a new, unbound `PriceForm` has `initial['currency']` set to 'EUR'.
**Pre-conditions:** None
**Dependencies:** `Price` model.
**Steps:**
1. Instantiate `form = PriceForm()`.
2. Check `form.initial.get('currency')`.
**Expected Result:**
- `form.initial.get('currency')` is 'EUR'.
**Post-conditions:** None.

**Case ID:** services_TC_F_PF_010
**Title:** PriceForm `__init__` currency not overridden for instance or POST data
**Description:** Verify `initial['currency']` is not set if form is bound to an instance or has POST data.
**Pre-conditions:**
    - Scenario 1: A `Price` instance (p_usd) with `currency`='USD'.
    - Scenario 2: POST data `{'currency': 'GBP', ...}`.
**Dependencies:** `Price` model.
**Steps:**
1. Scenario 1: `form = PriceForm(instance=p_usd)`. Check `form.initial.get('currency')`.
2. Scenario 2: `form = PriceForm(data=post_data)`. Check `form.initial.get('currency')`.
**Expected Result:**
- Scenario 1: `form.initial.get('currency')` is None (initial is not used to override instance data). The rendered form should show 'USD'.
- Scenario 2: `form.initial.get('currency')` is None. The rendered form should show 'GBP' (from data).
**Post-conditions:** None.

**Case ID:** services_TC_F_PF_011
**Title:** PriceForm fields attribute check
**Description:** Verify `PriceForm.Meta.fields` list.
**Pre-conditions:** None
**Dependencies:** None
**Steps:**
1. Inspect `PriceForm.Meta.fields`.
**Expected Result:**
- Fields are `['amount', 'currency', 'frequency', 'description', 'is_active']`.
**Post-conditions:** None.

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

## Test Cases for Templates (`services/templates/services/`)

**General Template Testing Notes:**
-   These test cases often rely on the correct context being passed from the view.
-   Verification would typically involve rendering the template with a mock context and inspecting the resulting HTML (e.g., using Django's test client and tools like BeautifulSoup or PyQuery).
-   Focus is on what the template *should* display given certain context variables.

---

### Template: `service_list.html`

**Context Variables Expected:** `services` (QuerySet of Service), `messages` (Django messages), `user` (request.user), `professional` (Professional profile or None).

**Case ID:** services_TC_T_SL_001
**Title:** Render `service_list.html` - With services
**Description:** Verify the template correctly displays a list of services.
**Pre-conditions:** `services` context variable contains multiple `Service` objects. User is authenticated and is a professional.
**Dependencies:** `Service` model.
**Steps:**
1. Render `service_list.html` with a list of services in context.
**Expected Result:**
- Page title "My Services" is present.
- "My Services" header (H2) is present.
- "Add New Service" button linking to `services:service_create` is present.
- For each service in `services`:
    - Service `title` is displayed.
    - Service `created_at` date is displayed.
    - Truncated `description` is displayed.
    - "View Details" button linking to `services:service_detail` for the service.
    - "Edit" button linking to `services:service_update` for the service.
    - "Delete" button linking to `services:service_delete` for the service.
    - Status (Active/Inactive) is displayed.
**Post-conditions:** None.

**Case ID:** services_TC_T_SL_002
**Title:** Render `service_list.html` - No services
**Description:** Verify the template displays a "no services yet" message.
**Pre-conditions:** `services` context variable is empty or None. User is authenticated and is a professional.
**Dependencies:** None.
**Steps:**
1. Render `service_list.html` with an empty `services` list.
**Expected Result:**
- "Add New Service" button is present.
- An alert message "You have not created any services yet." is displayed.
- A link within the alert prompts to "Add your first service!" pointing to `services:service_create`.
- No service items are listed.
**Post-conditions:** None.

**Case ID:** services_TC_T_SL_003
**Title:** Render `service_list.html` - With messages
**Description:** Verify Django messages are displayed if present.
**Pre-conditions:** `messages` framework has messages (e.g., success message after creation).
**Dependencies:** None.
**Steps:**
1. Render `service_list.html` with messages in context.
**Expected Result:**
- Messages are displayed correctly with appropriate alert classes (e.g., `alert-success`).
**Post-conditions:** None.

---

### Template: `service_form.html`

**Context Variables Expected:** `form` (ServiceForm instance), `object` (Service instance, if editing), `page_title` (string).

**Case ID:** services_TC_T_SFM_001
**Title:** Render `service_form.html` - Create new service
**Description:** Verify template for creating a new service.
**Pre-conditions:** `form` is an unbound `ServiceForm`. `object` is None. `page_title` = "Create New Service".
**Dependencies:** `ServiceForm`.
**Steps:**
1. Render `service_form.html` with the specified context.
**Expected Result:**
- Page title block contains "Create New Service".
- H2 header is "Create Service".
- Form tag with `method="post"` and `enctype="multipart/form-data"` is present.
- CSRF token is present.
- Form fields for `title`, `description`, `is_active` are rendered via `{{ form.as_p }}`.
- Submit button text is "Create Service".
- Cancel button links to `services:service_list`.
**Post-conditions:** None.

**Case ID:** services_TC_T_SFM_002
**Title:** Render `service_form.html` - Edit existing service
**Description:** Verify template for editing an existing service.
**Pre-conditions:** `form` is a `ServiceForm` bound to `object`. `object` is a `Service` instance (e.g., with title "My Old Service"). `page_title` = "Edit Service: My Old Service".
**Dependencies:** `ServiceForm`, `Service` model.
**Steps:**
1. Render `service_form.html` with the context for an existing service.
**Expected Result:**
- Page title block contains "Edit Service: My Old Service".
- H2 header is "Edit Service".
- Form fields are pre-populated with `object`'s data.
- Submit button text is "Save Changes".
- Cancel button links to `services:service_detail` for the `object`.
**Post-conditions:** None.

**Case ID:** services_TC_T_SFM_003
**Title:** Render `service_form.html` - With form errors
**Description:** Verify form errors are displayed.
**Pre-conditions:** `form` is a bound `ServiceForm` with errors (e.g., title missing).
**Dependencies:** `ServiceForm`.
**Steps:**
1. Render `service_form.html` with a form containing errors.
**Expected Result:**
- General form errors (non-field errors) are displayed if any.
- Field-specific errors are displayed near the respective fields (handled by `{{ form.as_p }}`).
**Post-conditions:** None.

---

### Template: `service_detail.html`

**Context Variables Expected:** `service` (Service object), `user_owns_service` (boolean), `messages`.

**Case ID:** services_TC_T_SDTL_001
**Title:** Render `service_detail.html` - Owner viewing
**Description:** Verify template display when service owner views the page.
**Pre-conditions:**
    - `service` is a `Service` instance.
    - `user_owns_service` is True.
    - `service.items.all` might return some items.
**Dependencies:** `Service`, `Item`, `Price` models.
**Steps:**
1. Render `service_detail.html` with `user_owns_service` = True.
**Expected Result:**
- Page title block is `service.title`.
- H2 header is `service.title`.
- "Edit Service" button linking to `services:service_update` is present.
- "Delete Service" button linking to `services:service_delete` is present.
- Service `description`, `status` (Active/Inactive), `created_at`, `updated_at` are displayed.
- "Items for this Service" section header is present.
- "Add New Item" button linking to `services:item_create` for this service is present.
- If `service.items.all` has items:
    - Each item's `title`, truncated `description`, and image (if any) are displayed.
    - "View Item", "Edit Item", "Delete Item" buttons for each item are present.
    - For each item, its prices are listed (amount, currency, frequency, status).
    - "Details" and "Edit Price" links for each price are present.
    - "Add Price" button for each item is present.
- If `service.items.all` is empty:
    - "No items have been added..." message with "Add the first item!" link is present.
- "Back to Services List" button links to `services:service_list`.
**Post-conditions:** None.

**Case ID:** services_TC_T_SDTL_002
**Title:** Render `service_detail.html` - Non-owner viewing (if applicable)
**Description:** Verify template display for non-owners (assuming view logic allows non-owners to see some details).
**Pre-conditions:** `service` is a `Service` instance. `user_owns_service` is False.
**Dependencies:** `Service` model.
**Steps:**
1. Render `service_detail.html` with `user_owns_service` = False.
**Expected Result:**
- "Edit Service", "Delete Service", "Add New Item", "Edit Item", "Delete Item", "Edit Price", "Add Price" buttons/links are NOT present.
- Basic service information (title, description, status, items, prices) is visible if allowed by view.
**Post-conditions:** None.

**Case ID:** services_TC_T_SDTL_003
**Title:** Render `service_detail.html` - Service with no items
**Description:** Verify "no items" message when service has no items, for owner.
**Pre-conditions:** `service.items.all` is empty. `user_owns_service` is True.
**Dependencies:** `Service` model.
**Steps:**
1. Render `service_detail.html`.
**Expected Result:**
- "No items have been added to this service yet." message is displayed.
- "Add the first item!" link (inside the alert) points to `services:item_create`.
**Post-conditions:** None.

**Case ID:** services_TC_T_SDTL_004
**Title:** Render `service_detail.html` - Item with no prices
**Description:** Verify "no prices set" message for an item without prices, for owner.
**Pre-conditions:** `service` has an item, but that `item.prices.all` is empty. `user_owns_service` is True.
**Dependencies:** `Service`, `Item` models.
**Steps:**
1. Render `service_detail.html`.
**Expected Result:**
- For the item without prices, "No prices set for this item yet." message is displayed.
- "Add Price" button for that item is still present.
**Post-conditions:** None.

**Case ID:** services_TC_T_SDTL_005
**Title:** Render `service_detail.html` - With messages
**Description:** Verify Django messages are displayed.
**Pre-conditions:** `messages` framework has messages.
**Dependencies:** None.
**Steps:**
1. Render `service_detail.html` with messages.
**Expected Result:**
- Messages are displayed correctly.
**Post-conditions:** None.

---

### Template: `service_confirm_delete.html`

**Context Variables Expected:** `service` (Service object).

**Case ID:** services_TC_T_SCD_001
**Title:** Render `service_confirm_delete.html`
**Description:** Verify the delete confirmation page for a service.
**Pre-conditions:** `service` is a `Service` instance (e.g., title "Old Service").
**Dependencies:** `Service` model.
**Steps:**
1. Render `service_confirm_delete.html` with the service context.
**Expected Result:**
- Page title block contains "Confirm Delete: Old Service".
- H2 header is "Confirm Deletion".
- Confirmation message "Are you sure you want to delete the service "<strong>Old Service</strong>"?" is displayed.
- Warning "All associated items and prices will also be deleted." is present.
- Form with `method="post"` and CSRF token is present.
- Submit button text is "Yes, Delete".
- Cancel button links to `services:service_detail` for the service.
**Post-conditions:** None.

---

### Template: `item_detail.html`

**Context Variables Expected:** `item` (Item object), `service` (parent Service object), `user_owns_service` (boolean), `messages`.

**Case ID:** services_TC_T_IDTL_001
**Title:** Render `item_detail.html` - Owner viewing
**Description:** Verify template display when item's service owner views the page.
**Pre-conditions:**
    - `service` is a `Service` instance (e.g., title "Parent Service").
    - `item` is an `Item` instance belonging to `service` (e.g., title "Cool Item").
    - `user_owns_service` is True.
    - `item.prices.all` might return some prices.
**Dependencies:** `Service`, `Item`, `Price` models.
**Steps:**
1. Render `item_detail.html` with `user_owns_service` = True.
**Expected Result:**
- Page title block is "Item: Cool Item".
- Breadcrumbs: "My Services" (to service_list) -> "Parent Service" (to service_detail) -> "Cool Item" (active).
- H3 header is `item.title`.
- If `user_owns_service` is True:
    - "Edit Item" button linking to `services:item_update` for this item and service.
    - "Delete Item" button linking to `services:item_delete` for this item and service.
- Item `description`, `image` (if any), `created_at`, `updated_at` are displayed.
- "Prices for this Item" section header is present.
- If `user_owns_service` is True, "Add New Price" button linking to `services:price_create` for this item and service.
- If `item.prices.all` has prices:
    - Each price's `amount`, `currency`, `frequency`, `description`, and status (Active/Inactive) are displayed.
    - If `user_owns_service` is True: "Details", "Edit", "Delete" links/buttons for each price, linking to respective price views.
- If `item.prices.all` is empty:
    - "No prices have been set..." message. If `user_owns_service` is True, includes "Add the first price!" link.
- "Back to Parent Service" button linking to `services:service_detail` for the parent `service`.
**Post-conditions:** None.

**Case ID:** services_TC_T_IDTL_002
**Title:** Render `item_detail.html` - Non-owner viewing (if applicable)
**Description:** Verify template display for non-owners (assuming view logic allows non-owners to see some details).
**Pre-conditions:** `item` and `service` context variables are set. `user_owns_service` is False.
**Dependencies:** `Service`, `Item` models.
**Steps:**
1. Render `item_detail.html` with `user_owns_service` = False.
**Expected Result:**
- "Edit Item", "Delete Item", "Add New Price", and individual price action buttons/links are NOT present.
- Basic item information (title, description, image, prices) is visible if allowed by view.
**Post-conditions:** None.

**Case ID:** services_TC_T_IDTL_003
**Title:** Render `item_detail.html` - Item with no prices
**Description:** Verify "no prices" message for an item without prices, for owner.
**Pre-conditions:** `item.prices.all` is empty. `user_owns_service` is True.
**Dependencies:** `Service`, `Item` models.
**Steps:**
1. Render `item_detail.html`.
**Expected Result:**
- "No prices have been set for this item yet." message is displayed.
- If `user_owns_service` is True, "Add the first price!" link pointing to `services:price_create` is present.
**Post-conditions:** None.

**Case ID:** services_TC_T_IDTL_004
**Title:** Render `item_detail.html` - With messages
**Description:** Verify Django messages are displayed.
**Pre-conditions:** `messages` framework has messages.
**Dependencies:** None.
**Steps:**
1. Render `item_detail.html` with messages.
**Expected Result:**
- Messages are displayed correctly.
**Post-conditions:** None.

---

### Template: `item_form.html`

**Context Variables Expected:** `form` (ItemForm instance), `service` (parent Service object), `object` (Item instance, if editing), `page_title` (string, though block is overridden).

**Case ID:** services_TC_T_IFM_001
**Title:** Render `item_form.html` - Add new item
**Description:** Verify template for adding a new item to a service.
**Pre-conditions:**
    - `form` is an unbound `ItemForm`.
    - `service` is a `Service` instance (e.g., title "Parent Service").
    - `object` is None.
**Dependencies:** `ItemForm`, `Service` model.
**Steps:**
1. Render `item_form.html` with the specified context.
**Expected Result:**
- Page title block: "Add Item to Parent Service".
- H2 header: "Add New Item to Parent Service".
- Form tag with `method="post"` and `enctype="multipart/form-data"`. CSRF token.
- Form fields for `title`, `description`, `image` rendered via `{{ form.as_p }}`.
- Submit button text: "Add Item".
- Cancel button links to `services:service_detail` for the parent `service`.
**Post-conditions:** None.

**Case ID:** services_TC_T_IFM_002
**Title:** Render `item_form.html` - Edit existing item
**Description:** Verify template for editing an existing item.
**Pre-conditions:**
    - `service` is a `Service` instance (e.g., title "Parent Service").
    - `object` is an `Item` instance belonging to `service` (e.g., title "My Old Item").
    - `form` is an `ItemForm` bound to `object`.
**Dependencies:** `ItemForm`, `Service`, `Item` models.
**Steps:**
1. Render `item_form.html` with context for an existing item.
**Expected Result:**
- Page title block: "Edit Item: My Old Item".
- H2 header: "Edit Item for Parent Service".
- Form fields pre-populated with `object`'s data.
- Submit button text: "Save Changes".
- Cancel button links to `services:item_detail` for this `object` and `service`.
**Post-conditions:** None.

**Case ID:** services_TC_T_IFM_003
**Title:** Render `item_form.html` - With form errors
**Description:** Verify form errors are displayed.
**Pre-conditions:** `form` is a bound `ItemForm` with errors. `service` context is provided.
**Dependencies:** `ItemForm`, `Service` model.
**Steps:**
1. Render `item_form.html` with a form containing errors.
**Expected Result:**
- Field-specific errors are displayed near respective fields.
**Post-conditions:** None.

---

### Template: `item_confirm_delete.html`

**Context Variables Expected:** `item` (Item object), `service` (parent Service object).

**Case ID:** services_TC_T_ICD_001
**Title:** Render `item_confirm_delete.html`
**Description:** Verify the delete confirmation page for an item.
**Pre-conditions:**
    - `service` is a `Service` instance (e.g., title "Parent Service").
    - `item` is an `Item` instance belonging to `service` (e.g., title "Item to Delete").
**Dependencies:** `Service`, `Item` models.
**Steps:**
1. Render `item_confirm_delete.html` with the item and service context.
**Expected Result:**
- Page title block: "Confirm Delete: Item to Delete".
- Breadcrumbs: "My Services" -> "Parent Service" -> "Item to Delete" -> "Confirm Delete" (active).
- H2 header: "Confirm Deletion".
- Confirmation message: "Are you sure you want to delete the item "<strong>Item to Delete</strong>" from the service "<strong>Parent Service</strong>"?"
- Warning: "This action cannot be undone. All associated prices for this item will also be deleted."
- Form with `method="post"` and CSRF token.
- Submit button text: "Yes, Delete Item".
- Cancel button links to `services:item_detail` for this `item` and `service`.
**Post-conditions:** None.

---

### Template: `price_detail.html`

**Context Variables Expected:** `price` (Price object), `item` (parent Item object), `service` (grandparent Service object), `user_owns_service` (boolean), `messages`.

**Case ID:** services_TC_T_PDTL_001
**Title:** Render `price_detail.html` - Owner viewing
**Description:** Verify template display when owner views price details.
**Pre-conditions:**
    - `service` is a `Service` instance (e.g., title "Grandparent Service").
    - `item` is an `Item` instance in `service` (e.g., title "Parent Item").
    - `price` is a `Price` instance for `item` (e.g., 100 USD Monthly).
    - `user_owns_service` is True.
**Dependencies:** `Service`, `Item`, `Price` models.
**Steps:**
1. Render `price_detail.html` with `user_owns_service` = True.
**Expected Result:**
- Page title block: "Price Details for Parent Item".
- Breadcrumbs: "My Services" -> "Grandparent Service" -> "Parent Item" -> "Price Details" (active).
- H3 header: "Price Details".
- If `user_owns_service` is True:
    - "Edit Price" button linking to `services:price_update` for this price, item, and service.
    - "Delete Price" button linking to `services:price_delete` for this price, item, and service.
- Price details displayed:
    - Link to parent `item`'s detail page.
    - `amount` and `currency`.
    - `frequency` (display name).
    - `description`.
    - Status (Active/Inactive).
    - `created_at`, `updated_at`.
- "Back to Parent Item" button linking to `services:item_detail` for the parent `item` and `service`.
**Post-conditions:** None.

**Case ID:** services_TC_T_PDTL_002
**Title:** Render `price_detail.html` - Non-owner viewing (if applicable)
**Description:** Verify display for non-owners.
**Pre-conditions:** `price`, `item`, `service` context set. `user_owns_service` is False.
**Dependencies:** `Service`, `Item`, `Price` models.
**Steps:**
1. Render `price_detail.html` with `user_owns_service` = False.
**Expected Result:**
- "Edit Price", "Delete Price" buttons are NOT present.
- Basic price information is visible if allowed by view.
**Post-conditions:** None.

**Case ID:** services_TC_T_PDTL_003
**Title:** Render `price_detail.html` - With messages
**Description:** Verify Django messages are displayed.
**Pre-conditions:** `messages` framework has messages.
**Dependencies:** None.
**Steps:**
1. Render `price_detail.html` with messages.
**Expected Result:**
- Messages are displayed correctly.
**Post-conditions:** None.

---

### Template: `price_form.html`

**Context Variables Expected:** `form` (PriceForm), `item` (parent Item), `service` (grandparent Service), `object` (Price instance, if editing).

**Case ID:** services_TC_T_PFM_001
**Title:** Render `price_form.html` - Add new price
**Description:** Verify template for adding a new price to an item.
**Pre-conditions:**
    - `form` is an unbound `PriceForm`.
    - `service` is a `Service` instance (e.g., title "Grandparent Service").
    - `item` is an `Item` instance in `service` (e.g., title "Parent Item").
    - `object` is None.
**Dependencies:** `PriceForm`, `Item`, `Service` models.
**Steps:**
1. Render `price_form.html` with the specified context.
**Expected Result:**
- Page title block: "Add Price to Parent Item".
- Breadcrumbs: "My Services" -> "Grandparent Service" -> "Parent Item" -> "Add Price" (active).
- H2 header: "Add New Price to Parent Item".
- Form tag with `method="post"`. CSRF token.
- Form fields for `amount`, `currency`, `frequency`, etc., rendered via `{{ form.as_p }}`.
- Submit button text: "Add Price".
- Cancel button links to `services:item_detail` for the parent `item` and `service`.
**Post-conditions:** None.

**Case ID:** services_TC_T_PFM_002
**Title:** Render `price_form.html` - Edit existing price
**Description:** Verify template for editing an existing price.
**Pre-conditions:**
    - `service`, `item` are set.
    - `object` is a `Price` instance for `item`.
    - `form` is a `PriceForm` bound to `object`.
**Dependencies:** `PriceForm`, `Item`, `Service`, `Price` models.
**Steps:**
1. Render `price_form.html` with context for an existing price.
**Expected Result:**
- Page title block: "Edit Price for Parent Item".
- Breadcrumbs: "My Services" -> ... -> "Parent Item" -> "Edit Price" (active).
- H2 header: "Edit Price for Parent Item".
- Form fields pre-populated with `object`'s data.
- Submit button text: "Save Changes".
- Cancel button links to `services:price_detail` for this `object`, `item`, and `service`.
**Post-conditions:** None.

**Case ID:** services_TC_T_PFM_003
**Title:** Render `price_form.html` - With form errors
**Description:** Verify form errors are displayed.
**Pre-conditions:** `form` is a bound `PriceForm` with errors. `item`, `service` context provided.
**Dependencies:** `PriceForm`, `Item`, `Service` models.
**Steps:**
1. Render `price_form.html` with a form containing errors.
**Expected Result:**
- Field-specific errors are displayed.
**Post-conditions:** None.

---

### Template: `price_confirm_delete.html`

**Context Variables Expected:** `price` (Price object), `item` (parent Item), `service` (grandparent Service).

**Case ID:** services_TC_T_PCD_001
**Title:** Render `price_confirm_delete.html`
**Description:** Verify the delete confirmation page for a price.
**Pre-conditions:**
    - `service` (e.g., title "Grandparent Service").
    - `item` (e.g., title "Parent Item").
    - `price` (e.g., 100 USD Monthly).
**Dependencies:** `Service`, `Item`, `Price` models.
**Steps:**
1. Render `price_confirm_delete.html` with context.
**Expected Result:**
- Page title block: "Confirm Delete Price".
- Breadcrumbs: "My Services" -> "Grandparent Service" -> "Parent Item" -> "Confirm Delete Price" (active).
- H2 header: "Confirm Deletion".
- Confirmation message: "Are you sure you want to delete this price?"
- Price details displayed: `{{ price.amount }} {{ price.currency }} ({{ price.get_frequency_display }}) for item "{{ item.title }}"`.
- Warning: "This action cannot be undone."
- Form with `method="post"` and CSRF token.
- Submit button text: "Yes, Delete Price".
- Cancel button links to `services:price_detail` for this `price`, `item`, and `service`.
**Post-conditions:** None.

---

### Template: `not_a_professional.html`

**Context Variables Expected:** None specific beyond base template context.

**Case ID:** services_TC_T_NAP_001
**Title:** Render `not_a_professional.html`
**Description:** Verify the content of the "not a professional" access denial page.
**Pre-conditions:** This template is rendered when a user tries to access a professional-only area without credentials.
**Dependencies:** None.
**Steps:**
1. Render `not_a_professional.html`.
**Expected Result:**
- Page title block: "Not Authorized".
- H2 header: "Access Denied".
- Message: "You are not registered as a professional or do not have the necessary permissions to view this page."
- Link to "Return to Homepage" (pointing to `home` URL name).
**Post-conditions:** None.
