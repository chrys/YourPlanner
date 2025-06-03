**Case ID:** orders_#001
**Title:** Create a new order
**Description:** Verify that a new order can be created with valid data.
**Pre-conditions:**
    - Customer exists in the system.
    - Services and items are available.
**Dependencies:** None
**Steps:**
    1. Log in as a customer.
    2. Navigate to the order creation page.
    3. Select items to add to the order.
    4. Confirm the order.
**Expected Result:**
    - A new order is created with the status "Pending Confirmation".
    - The order is associated with the correct customer.
    - The order items are correctly added to the order.
    - The total amount of the order is calculated correctly.
**Post-conditions:**
    - The order is saved in the database.

**Case ID:** orders_#002
**Title:** Calculate total amount of an order
**Description:** Verify that the total amount of an order is calculated correctly.
**Pre-conditions:**
    - An order exists with items.
**Dependencies:** None
**Steps:**
    1. Retrieve an existing order.
    2. Trigger the calculation of the total amount.
**Expected Result:**
    - The total amount is the sum of the prices of all items in the order, considering quantities and discounts.
**Post-conditions:**
    - The total amount of the order is updated in the database.

**Case ID:** orders_#003
**Title:** Check if an order can be cancelled
**Description:** Verify that an order can be cancelled only if its status allows cancellation (e.g., "Pending Confirmation" or "Confirmed").
**Pre-conditions:**
    - An order exists with a specific status.
**Dependencies:** None
**Steps:**
    1. Retrieve an existing order.
    2. Check if the order can be cancelled based on its current status.
**Expected Result:**
    - Returns true if the order status is "Pending Confirmation" or "Confirmed".
    - Returns false otherwise.
**Post-conditions:** None

**Case ID:** orders_#004
**Title:** Change the status of an order
**Description:** Verify that the status of an order can be changed.
**Pre-conditions:**
    - An order exists.
    - The user has the necessary permissions to change the order status.
**Dependencies:** None
**Steps:**
    1. Retrieve an existing order.
    2. Update the status of the order to a new valid status (e.g., "In Progress", "Completed", "Cancelled").
**Expected Result:**
    - The order status is updated to the new status.
    - An entry is added to the order status history.
**Post-conditions:**
    - The updated order status is saved in the database.
    - A new record is created in the OrderStatusHistory table.

**Case ID:** orders_#005
**Title:** Change the payment status of an order
**Description:** Verify that the payment status of an order can be changed.
**Pre-conditions:**
    - An order exists.
    - The user has the necessary permissions to change the payment status.
**Dependencies:** None
**Steps:**
    1. Retrieve an existing order.
    2. Update the payment status of the order to a new valid status (e.g., "Paid", "Refunded").
**Expected Result:**
    - The order payment status is updated to the new status.
**Post-conditions:**
    - The updated payment status is saved in the database.

**Case ID:** orders_#006
**Title:** Create a new order item
**Description:** Verify that a new item can be added to an order with valid data.
**Pre-conditions:**
    - An order exists with status "Pending Confirmation".
    - The item (Price) to be added is active and available.
**Dependencies:** Order exists.
**Steps:**
    1. Select an existing order.
    2. Choose a valid item (Price) to add.
    3. Specify the quantity for the item.
    4. Confirm adding the item.
**Expected Result:**
    - A new order item entry is created and associated with the order.
    - The `price_amount_at_order`, `price_currency_at_order`, and `price_frequency_at_order` fields are correctly populated from the selected Price.
    - The order's total amount is recalculated.
**Post-conditions:**
    - The new order item is saved in the database.
    - The parent order's `total_amount` and `updated_at` fields are updated.

**Case ID:** orders_#007
**Title:** Calculate final price of an order item
**Description:** Verify that the final price of an order item is calculated correctly, considering quantity and discount.
**Pre-conditions:**
    - An order item exists with a specified quantity, price at order, and discount amount.
**Dependencies:** None
**Steps:**
    1. Retrieve an existing order item.
    2. Access its `final_price` property.
**Expected Result:**
    - The final price is calculated as `(quantity * price_amount_at_order) - discount_amount`.
    - The result is not less than zero.
**Post-conditions:** None

**Case ID:** orders_#008
**Title:** Create an order status history entry
**Description:** Verify that an entry is added to the order status history when an order's status changes.
**Pre-conditions:**
    - An order exists.
    - The order's status is about to be changed.
**Dependencies:** Order exists.
**Steps:**
    1. Retrieve an existing order.
    2. Store its current status (old_status).
    3. Change the status of the order to a new_status.
    4. Save the order.
**Expected Result:**
    - A new `OrderStatusHistory` record is created.
    - The record correctly logs the `order`, `old_status`, `new_status`, and `changed_by` user (if applicable).
**Post-conditions:**
    - The new `OrderStatusHistory` record is saved in the database.

**Case ID:** orders_#009
**Title:** Create a new order using OrderForm
**Description:** Verify that the OrderForm can be used to initiate the creation of a new order.
**Pre-conditions:**
    - Customer is logged in and has a customer profile.
**Dependencies:** `users.Customer` model.
**Steps:**
    1. Instantiate `OrderForm` with no data (as it's empty).
    2. Simulate form submission within the `OrderCreateView`.
    3. The view should set the `customer` and initial `status` (PENDING).
**Expected Result:**
    - An `Order` instance is created.
    - The `customer` field of the order is correctly set to the logged-in customer.
    - The `status` field of the order is set to 'PENDING'.
    - The `total_amount` is initialized (e.g., to 0).
**Post-conditions:**
    - A new order record is saved in the database, ready for items to be added.

**Case ID:** orders_#010
**Title:** Update order status using OrderStatusUpdateForm
**Description:** Verify that the OrderStatusUpdateForm can be used to change an order's status.
**Pre-conditions:**
    - An order exists.
    - The logged-in user is an admin/staff.
**Dependencies:** `Order` model.
**Steps:**
    1. Instantiate `OrderStatusUpdateForm` with an existing order instance and valid POST data for the new status.
    2. Check if the form is valid.
    3. Save the form.
**Expected Result:**
    - The form is valid with correct status choices.
    - The `status` of the order instance is updated to the new status provided in the form.
    - An `OrderStatusHistory` entry is created (though this is typically handled by the model's save method or view logic, the form facilitates the status change).
**Post-conditions:**
    - The order's status is updated in the database.

**Case ID:** orders_#011
**Title:** Add an item to an order using OrderItemForm
**Description:** Verify that OrderItemForm can be used to add a new item to an order.
**Pre-conditions:**
    - An order exists with a status that allows item modification (e.g., "Pending Confirmation").
    - Active and available Prices (representing items) exist.
    - The form is provided with a queryset of available prices.
**Dependencies:** `Order` model, `services.Price` model.
**Steps:**
    1. Instantiate `OrderItemForm` with POST data including a valid `price` (from the available queryset) and `quantity`.
    2. Pass the parent `order_instance` and `available_prices_queryset` to the form.
    3. Check if the form is valid.
    4. Save the form (associating it with the order).
**Expected Result:**
    - The form is valid.
    - A new `OrderItem` instance is created and associated with the parent order.
    - The `quantity` is set as specified.
    - `price_amount_at_order`, `price_currency_at_order`, `price_frequency_at_order` are correctly populated from the selected `Price`.
    - The parent order's total amount is updated (this is usually handled by view/model logic post-form save).
**Post-conditions:**
    - A new `OrderItem` record is saved in the database.
    - The related `Order`'s `total_amount` is updated.

**Case ID:** orders_#012
**Title:** Update an item in an order using OrderItemForm
**Description:** Verify that OrderItemForm can be used to update an existing item's quantity in an order.
**Pre-conditions:**
    - An `OrderItem` exists within an order.
    - The order status allows item modification.
**Dependencies:** `OrderItem` model.
**Steps:**
    1. Instantiate `OrderItemForm` with an existing `OrderItem` instance and POST data for the updated `quantity`.
    2. The `price` field should be disabled or correctly handled for existing items.
    3. Check if the form is valid.
    4. Save the form.
**Expected Result:**
    - The form is valid.
    - The `quantity` of the existing `OrderItem` instance is updated.
    - The `price` related fields remain unchanged.
    - The parent order's total amount is updated.
**Post-conditions:**
    - The `OrderItem` record is updated in the database.
    - The related `Order`'s `total_amount` is updated.

**Case ID:** orders_#013
**Title:** View: Create an order
**Description:** Verify that a customer can initiate a new order.
**Pre-conditions:**
    - User is logged in as a customer with a customer profile.
**Dependencies:** `OrderCreateView`, `CustomerRequiredMixin`.
**Steps:**
    1. Log in as a customer.
    2. Navigate to the order creation URL (`orders:order_create`).
    3. (GET request) Verify the correct form and template are rendered.
    4. (POST request from the view, which is minimal for OrderForm) Verify a new order is created.
**Expected Result:**
    - (GET) HTTP 200 response, `orders/order_form.html` template used.
    - (POST) A new `Order` is created with status 'PENDING' and associated with the customer.
    - User is redirected to the `orders:select_items` view for the new order.
    - Success message is displayed.
**Post-conditions:**
    - New `Order` record in the database.

**Case ID:** orders_#014
**Title:** View: List orders
**Description:** Verify that users can see a list of their relevant orders.
**Pre-conditions:**
    - User is logged in.
    - Orders exist in the system.
**Dependencies:** `OrderListView`.
**Steps:**
    1. Log in as a customer. Navigate to `orders:order_list`.
    2. Log in as a professional. Navigate to `orders:order_list`.
    3. Log in as an admin. Navigate to `orders:order_list`.
**Expected Result:**
    - HTTP 200 response, `orders/order_list.html` template used.
    - Customer sees only their own orders.
    - Professional sees orders they are part of (i.e., containing their services).
    - Admin sees all orders.
    - Orders are correctly paginated if applicable.
**Post-conditions:** None

**Case ID:** orders_#015
**Title:** View: Order detail
**Description:** Verify that authorized users can view the details of a specific order.
**Pre-conditions:**
    - An order exists.
    - User is logged in.
**Dependencies:** `OrderDetailView`, `UserCanViewOrderMixin`.
**Steps:**
    1. Log in as the customer who owns the order. Navigate to `orders:order_detail` for that order.
    2. Log in as a professional associated with an item in the order. Navigate to `orders:order_detail`.
    3. Log in as an admin. Navigate to `orders:order_detail`.
    4. Log in as a customer who does NOT own the order. Navigate to `orders:order_detail`.
**Expected Result:**
    - (Steps 1-3) HTTP 200 response, `orders/order_detail.html` template used. Order details, items, and relevant actions (modify, cancel, update status based on role/status) are displayed.
    - (Step 4) Permission denied (e.g., redirect to order list with an error message or HTTP 403/404).
**Post-conditions:** None

**Case ID:** orders_#016
**Title:** View: Update order status
**Description:** Verify that an admin can update the status of an order.
**Pre-conditions:**
    - An order exists.
    - User is logged in as an admin.
**Dependencies:** `OrderStatusUpdateView`, `AdminAccessMixin`.
**Steps:**
    1. Log in as an admin.
    2. Navigate to the order detail page for an existing order.
    3. Use the status update form/mechanism to change the order's status (e.g., from 'PENDING' to 'CONFIRMED').
**Expected Result:**
    - The order's status is successfully updated.
    - An `OrderStatusHistory` entry is created.
    - User is redirected back to the order detail page.
    - Success message is displayed.
**Post-conditions:**
    - `Order` status updated in the database.
    - New `OrderStatusHistory` record.

**Case ID:** orders_#017
**Title:** View: Cancel an order
**Description:** Verify that a customer can cancel their PENDING order.
**Pre-conditions:**
    - An order exists with 'PENDING' status.
    - User is logged in as the customer who owns the order.
**Dependencies:** `OrderCancelView`, `CustomerOwnsOrderMixin`.
**Steps:**
    1. Log in as the customer.
    2. Navigate to the order detail page for a 'PENDING' order they own.
    3. Click the 'Cancel Order' button/link.
    4. Confirm cancellation on the `orders/order_confirm_cancel.html` page.
    5. Attempt to cancel an order that is NOT 'PENDING' (e.g., 'CONFIRMED' or 'COMPLETED').
    6. Attempt to cancel an order not owned by the customer.
**Expected Result:**
    - (Steps 1-4) Order status is changed to 'CANCELLED'. User is redirected to order detail page. Success message.
    - (Step 5) Cancellation fails. Error message displayed. Order status remains unchanged.
    - (Step 6) Permission denied.
**Post-conditions:**
    - (Successful cancellation) `Order` status updated to 'CANCELLED'.

**Case ID:** orders_#018
**Title:** View: Add an item to an order
**Description:** Verify that a user (customer or admin) can add an item to a PENDING order.
**Pre-conditions:**
    - An order exists with 'PENDING' status.
    - User is logged in (customer owning the order, or admin).
    - Active `Price` entries exist.
**Dependencies:** `OrderItemCreateView` (or logic within `SelectItemsView` post), `UserCanModifyOrderItemsMixin`.
**Steps:**
    1. Log in as the customer who owns the PENDING order.
    2. Navigate to the view for adding items (e.g., `orders:select_items` or a dedicated `orders:orderitem_create` if it exists).
    3. Select a valid item (Price) and specify quantity.
    4. Submit the form/request.
    5. Repeat as admin.
    6. Attempt to add an item to an order that is NOT 'PENDING'.
**Expected Result:**
    - (Steps 1-5) A new `OrderItem` is created and associated with the order. The order's total is recalculated. User is redirected to the order detail page. Success message.
    - (Step 6) Action fails. Error message or permission denied.
**Post-conditions:**
    - New `OrderItem` record in the database.
    - `Order.total_amount` updated.

**Case ID:** orders_#019
**Title:** View: Update an item in an order
**Description:** Verify that a user (customer or admin) can update an item's quantity in a PENDING order.
**Pre-conditions:**
    - An `OrderItem` exists in an order with 'PENDING' status.
    - User is logged in (customer owning the order, or admin).
**Dependencies:** `OrderItemUpdateView`, `UserCanModifyOrderItemsMixin`.
**Steps:**
    1. Log in as the customer who owns the PENDING order.
    2. Navigate to the `orders:orderitem_update` view for an existing item in that order.
    3. Change the quantity.
    4. Submit the form.
    5. Repeat as admin.
    6. Attempt to update an item in an order that is NOT 'PENDING'.
**Expected Result:**
    - (Steps 1-5) The `OrderItem`'s quantity is updated. The order's total is recalculated. User is redirected to the order detail page. Success message.
    - (Step 6) Action fails. Error message or permission denied.
**Post-conditions:**
    - `OrderItem.quantity` updated in the database.
    - `Order.total_amount` updated.

**Case ID:** orders_#020
**Title:** View: Delete an item from an order
**Description:** Verify that a user (customer or admin) can delete an item from a PENDING order.
**Pre-conditions:**
    - An `OrderItem` exists in an order with 'PENDING' status.
    - User is logged in (customer owning the order, or admin).
**Dependencies:** `OrderItemDeleteView`, `UserCanModifyOrderItemsMixin`.
**Steps:**
    1. Log in as the customer who owns the PENDING order.
    2. Navigate to the `orders:orderitem_delete` view for an existing item.
    3. Confirm deletion.
    4. Repeat as admin.
    5. Attempt to delete an item from an order that is NOT 'PENDING'.
**Expected Result:**
    - (Steps 1-4) The `OrderItem` is deleted. The order's total is recalculated. User is redirected to the order detail page. Success message.
    - (Step 5) Action fails. Error message or permission denied.
**Post-conditions:**
    - `OrderItem` record deleted from the database.
    - `Order.total_amount` updated.
