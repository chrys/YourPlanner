# Django Models Documentation

This document provides an overview of the Django models used in the YourPlanner project.

## orders/models.py

### Order

Represents an order placed by a Customer.

**Fields:**

*   `customer`: ForeignKey to `users.Customer`
    *   `on_delete=models.PROTECT`: Prevents deletion of an order if the associated customer is deleted.
    *   `related_name='orders'`: Allows accessing a customer's orders via `customer.orders.all()`.
*   `order_date`: DateTimeField
    *   `default=timezone.now`: Sets the order date to the current time when an order is created.
*   `status`: CharField
    *   `max_length=15`
    *   `choices=Order.StatusChoices.choices`: Defines a set of predefined choices for the order status (e.g., PENDING, CONFIRMED).
    *   `default=Order.StatusChoices.PENDING`: Sets the default status to 'PENDING'.
*   `total_amount`: DecimalField
    *   `max_digits=12`, `decimal_places=2`
    *   `null=True`, `blank=True`: Allows the total amount to be optional, potentially calculated later.
*   `currency`: CharField
    *   `max_length=3`, `default='EUR'`: Sets the default currency to EUR.
*   `created_at`: DateTimeField
    *   `auto_now_add=True`: Automatically sets the timestamp when an order is first created.
*   `updated_at`: DateTimeField
    *   `auto_now=True`: Automatically updates the timestamp whenever the order is saved.

**Relationships:**

*   Many-to-One with `users.Customer`: An order belongs to one customer, and a customer can have multiple orders.
*   One-to-Many with `OrderItem`: An order can consist of multiple order items.

**`__str__` Method:**

Returns a string representation of the order, including its primary key, the associated customer, and the order date (formatted as YYYY-MM-DD).
Example: `Order #1 by CustomerObj on 2023-10-27`

**Methods:**

*   `calculate_total()`: Calculates the total amount of the order based on its `OrderItem` instances. It aggregates the sum of `quantity * price_amount_at_order` for all related items and updates the `total_amount` field of the order.

**Meta:**

*   `verbose_name = "Order"`
*   `verbose_name_plural = "Orders"`
*   `ordering = ['-order_date']`: Orders will be sorted by order date in descending order by default.

---

### OrderItem

Represents a specific item included within an Order.

**Fields:**

*   `order`: ForeignKey to `Order`
    *   `on_delete=models.CASCADE`: If an order is deleted, its associated order items are also deleted.
    *   `related_name='items'`: Allows accessing an order's items via `order.items.all()`.
*   `professional`: ForeignKey to `users.Professional`
    *   `on_delete=models.PROTECT`: Keeps a record of the professional even if their profile is deleted.
    *   `related_name='order_items'`.
*   `service`: ForeignKey to `services.Service`
    *   `on_delete=models.PROTECT`: Keeps a record of the service even if its definition changes or is deleted.
    *   `related_name='order_items'`.
*   `item`: ForeignKey to `services.Item`
    *   `on_delete=models.PROTECT`: Keeps a record of the item even if its definition changes or is deleted.
    *   `related_name='order_items'`.
*   `price`: ForeignKey to `services.Price`
    *   `on_delete=models.PROTECT`: Keeps a record of the price even if its definition changes or is deleted.
    *   `related_name='order_items'`.
*   `quantity`: PositiveIntegerField
    *   `default=1`: Sets the default quantity to 1.
*   `price_amount_at_order`: DecimalField
    *   `max_digits=10`, `decimal_places=2`: Stores the price amount at the time the order was placed.
*   `price_currency_at_order`: CharField
    *   `max_length=3`: Stores the currency at the time the order was placed.
*   `price_frequency_at_order`: CharField
    *   `max_length=10`: Stores the price frequency (e.g., 'ONCE', 'MONTHLY') at the time the order was placed.
*   `created_at`: DateTimeField
    *   `auto_now_add=True`: Automatically sets the timestamp when an order item is first created.

**Relationships:**

*   Many-to-One with `Order`: An order item belongs to one order.
*   Many-to-One with `users.Professional`: An order item is linked to a specific professional.
*   Many-to-One with `services.Service`: An order item is linked to a specific service.
*   Many-to-One with `services.Item`: An order item is linked to a specific item.
*   Many-to-One with `services.Price`: An order item is linked to a specific price.

**`__str__` Method:**

Returns a string representation of the order item, including the quantity, item title, and the associated order's primary key.
Example: `2 x Premium Widget in Order #1`

**`save()` Method:**

This method is overridden to automatically capture the price details (`price_amount_at_order`, `price_currency_at_order`, `price_frequency_at_order`) from the associated `Price` object when a new `OrderItem` is created and a price is set. This ensures historical accuracy of pricing.

**Meta:**

*   `verbose_name = "Order Item"`
*   `verbose_name_plural = "Order Items"`
*   `ordering = ['order', 'created_at']`: Order items will be sorted by their order and then by creation date by default.
*   `constraints`: Includes a commented-out example of a `UniqueConstraint` (`unique_order_item`) that could be used to prevent the same item from being added multiple times to a single order. This is not currently active.

---
## services/models.py

### Service

A service offered by a Professional.

**Fields:**

*   `professional`: ForeignKey to `users.Professional`
    *   `on_delete=models.CASCADE`: If a professional is deleted, their services are also deleted.
    *   `related_name='services'`: Allows accessing a professional's services via `professional.services.all()`.
*   `title`: CharField
    *   `max_length=255`
*   `description`: TextField
    *   `blank=True`: The description is optional.
*   `price`: DecimalField
    *   `max_digits=10`, `decimal_places=2`
    *   `null=True`, `blank=True`: The price is optional.
*   `image`: ImageField
    *   `upload_to='service_images/'`: Specifies the subdirectory of `MEDIA_ROOT` where images will be uploaded.
    *   `null=True`, `blank=True`: The image is optional.
*   `is_active`: BooleanField
    *   `default=True`: The service is active by default.
    *   `help_text="Is this service currently offered?"`
*   `created_at`: DateTimeField
    *   `auto_now_add=True`: Automatically sets the timestamp when a service is first created.
*   `updated_at`: DateTimeField
    *   `auto_now=True`: Automatically updates the timestamp whenever the service is saved.

**Relationships:**

*   Many-to-One with `users.Professional`: A service is offered by one professional, and a professional can offer multiple services.
*   One-to-Many with `Item`: A service can comprise multiple items.

**`__str__` Method:**

Returns a string representation of the service, including its title and the associated professional.
Example: `Web Design (by ProfessionalObj)`

**Meta:**

*   `verbose_name = "Service"`
*   `verbose_name_plural = "Services"`
*   `ordering = ['professional', 'title']`: Services will be sorted by professional and then by title by default.

---

### Item

An individual item or component within a Service.

**Fields:**

*   `service`: ForeignKey to `Service`
    *   `on_delete=models.CASCADE`: If a service is deleted, its items are also deleted.
    *   `related_name='items'`: Allows accessing a service's items via `service.items.all()`.
*   `title`: CharField
    *   `max_length=255`
*   `description`: TextField
    *   `blank=True`: The description is optional.
*   `image`: ImageField
    *   `upload_to='item_images/'`: Specifies the subdirectory of `MEDIA_ROOT` where images will be uploaded.
    *   `null=True`, `blank=True`: The image is optional.
*   `quantity`: IntegerField
    *   `default=0`: Default quantity is 0.
    *   `validators=[MinValueValidator(0)]`: Ensures quantity cannot be negative.
    *   `help_text="Available quantity, cannot be negative."`
*   `min_quantity`: IntegerField
    *   `null=True`, `blank=True`: Minimum quantity per order is optional.
    *   `validators=[MinValueValidator(1)]`: Ensures minimum quantity is at least 1, if set.
    *   `help_text="Minimum quantity per order."`
*   `max_quantity`: IntegerField
    *   `null=True`, `blank=True`: Maximum quantity per order is optional.
    *   `validators=[MinValueValidator(1)]`: Ensures maximum quantity is at least 1, if set.
    *   `help_text="Maximum quantity per order."`
*   `created_at`: DateTimeField
    *   `auto_now_add=True`: Automatically sets the timestamp when an item is first created.
*   `updated_at`: DateTimeField
    *   `auto_now=True`: Automatically updates the timestamp whenever the item is saved.

**Relationships:**

*   Many-to-One with `Service`: An item belongs to one service, and a service can have multiple items.
*   One-to-Many with `Price`: An item can have multiple price points.

**`__str__` Method:**

Returns a string representation of the item, including its title and the title of the service it belongs to.
Example: `Logo Design (in Service: Branding Package)`

**Meta:**

*   `verbose_name = "Item"`
*   `verbose_name_plural = "Items"`
*   `ordering = ['service', 'title']`: Items will be sorted by service and then by title by default.

---

### Price

Represents a price point for a specific Item.

**Fields:**

*   `item`: ForeignKey to `Item`
    *   `on_delete=models.CASCADE`: If an item is deleted, its prices are also deleted.
    *   `related_name='prices'`: Allows accessing an item's prices via `item.prices.all()`.
*   `amount`: DecimalField
    *   `max_digits=10`, `decimal_places=2`
*   `currency`: CharField
    *   `max_length=3`, `default='EUR'`: Sets the default currency to EUR.
*   `frequency`: CharField
    *   `max_length=10`
    *   `choices=Price.FrequencyChoices.choices`: Defines a set of predefined choices for the price frequency (e.g., ONE_TIME, HOURLY).
    *   `default=Price.FrequencyChoices.ONE_TIME`: Sets the default frequency to 'ONE_TIME'.
*   `description`: CharField
    *   `max_length=255`, `blank=True`
    *   `help_text="Optional description (e.g., 'Standard Tier', 'Discounted')"`
*   `is_active`: BooleanField
    *   `default=True`: The price is active by default.
    *   `help_text="Is this price option currently available?"`
*   `created_at`: DateTimeField
    *   `auto_now_add=True`: Automatically sets the timestamp when a price is first created.
*   `updated_at`: DateTimeField
    *   `auto_now=True`: Automatically updates the timestamp whenever the price is saved.

**Relationships:**

*   Many-to-One with `Item`: A price point is associated with one item.

**`__str__` Method:**

Returns a string representation of the price, including the amount, currency, frequency, and the title of the associated item.
Example: `100.00 EUR (ONCE) for Logo Design`

**Meta:**

*   `verbose_name = "Price"`
*   `verbose_name_plural = "Prices"`
*   `ordering = ['item', 'amount']`: Prices will be sorted by item and then by amount by default.

---
## users/models.py

### Professional

Represents a Professional user profile linked to a User account. This model extends the built-in Django User model using a One-to-One relationship.

**Fields:**

*   `user`: OneToOneField to `settings.AUTH_USER_MODEL`
    *   `on_delete=models.CASCADE`: If the associated User account is deleted, the Professional profile is also deleted.
    *   `primary_key=True`: Uses the User's ID as the primary key for the Professional table.
    *   `related_name='professional_profile'`: Allows accessing the professional profile via `user.professional_profile`.
*   `title`: CharField
    *   `max_length=200`, `blank=True`, `null=True`: The professional's title (e.g., Dr., Mr., Ms.) is optional.
*   `specialization`: CharField
    *   `max_length=200`, `blank=True`, `null=True`: The professional's area of specialization is optional.
*   `bio`: TextField
    *   `blank=True`, `null=True`: A short biography of the professional is optional.
*   `created_at`: DateTimeField
    *   `auto_now_add=True`: Automatically sets the timestamp when a professional profile is first created.
*   `updated_at`: DateTimeField
    *   `auto_now=True`: Automatically updates the timestamp whenever the professional profile is saved.

**Relationships:**

*   One-to-One with `settings.AUTH_USER_MODEL` (Django's built-in User model): Each Professional profile is linked to a single User account.
*   One-to-Many with `services.Service`: A professional can offer multiple services.
*   One-to-Many with `ProfessionalCustomerLink`: A professional can be linked to multiple customers.
*   One-to-Many with `orders.OrderItem`: An order item is handled by a specific professional.

**`__str__` Method:**

Returns the professional's `title` if available; otherwise, it falls back to the user's full name (if set) or username.
Example: `Dr. Jane Doe` or `jdoe`

**Meta:**

*   `verbose_name = "Professional"`
*   `verbose_name_plural = "Professionals"`

---

### Customer

Represents a Customer user profile linked to a User account. This model extends the built-in Django User model using a One-to-One relationship.

**Fields:**

*   `user`: OneToOneField to `settings.AUTH_USER_MODEL`
    *   `on_delete=models.CASCADE`: If the associated User account is deleted, the Customer profile is also deleted.
    *   `primary_key=True`: Uses the User's ID as the primary key for the Customer table.
    *   `related_name='customer_profile'`: Allows accessing the customer profile via `user.customer_profile`.
*   `company_name`: CharField
    *   `max_length=200`, `blank=True`, `null=True`: The customer's company name is optional.
*   `created_at`: DateTimeField
    *   `auto_now_add=True`: Automatically sets the timestamp when a customer profile is first created.
*   `updated_at`: DateTimeField
    *   `auto_now=True`: Automatically updates the timestamp whenever the customer profile is saved.

**Relationships:**

*   One-to-One with `settings.AUTH_USER_MODEL` (Django's built-in User model): Each Customer profile is linked to a single User account.
*   One-to-Many with `orders.Order`: A customer can place multiple orders.
*   One-to-Many with `ProfessionalCustomerLink`: A customer can be linked to multiple professionals.

**`__str__` Method:**

Returns a string identifying the user as a customer.
Example: `Customer: jdoe` (where `jdoe` is the string representation of the user object).

**Meta:**

*   `verbose_name = "Customer"`
*   `verbose_name_plural = "Customers"`

---

### Agent

Represents an Agent user profile linked to a User account. Agents are a special type of user that can create orders on behalf of customers. This model extends the built-in Django User model using a One-to-One relationship.

**Fields:**

*   `user`: OneToOneField to `settings.AUTH_USER_MODEL`
    *   `on_delete=models.CASCADE`: If the associated User account is deleted, the Agent profile is also deleted.
    *   `primary_key=True`: Uses the User's ID as the primary key for the Agent table.
    *   `related_name='agent_profile'`: Allows accessing the agent profile via `user.agent_profile`.
*   `agency_name`: CharField
    *   `max_length=200`, `blank=True`, `null=True`: The agent's agency name is optional.
*   `created_at`: DateTimeField
    *   `auto_now_add=True`: Automatically sets the timestamp when an agent profile is first created.
*   `updated_at`: DateTimeField
    *   `auto_now=True`: Automatically updates the timestamp whenever the agent profile is saved.

**Relationships:**

*   One-to-One with `settings.AUTH_USER_MODEL` (Django's built-in User model): Each Agent profile is linked to a single User account.
*   One-to-Many with `orders.Order`: An agent can create multiple orders.

**`__str__` Method:**

Returns a string identifying the user as an agent.
Example: `Agent: jdoe` (where `jdoe` is the string representation of the user object).

**Meta:**

*   `verbose_name = "Agent"`
*   `verbose_name_plural = "Agents"`

---

### ProfessionalCustomerLink

Represents a link or relationship between a Professional and a Customer. This acts as a many-to-many through table.

**Fields:**

*   `professional`: ForeignKey to `Professional`
    *   `on_delete=models.CASCADE`: If a professional is deleted, their links to customers are also deleted.
    *   `related_name='customer_links'`: Allows accessing a professional's customer links via `professional.customer_links.all()`.
*   `customer`: ForeignKey to `Customer`
    *   `on_delete=models.CASCADE`: If a customer is deleted, their links to professionals are also deleted.
    *   `related_name='professional_links'`: Allows accessing a customer's professional links via `customer.professional_links.all()`.
*   `relationship_start_date`: DateField
    *   `default=timezone.now`: Sets the start date of the relationship to the current date by default.
*   `status`: CharField
    *   `max_length=10`
    *   `choices=ProfessionalCustomerLink.StatusChoices.choices`: Defines a set of predefined choices for the link status (e.g., ACTIVE, INACTIVE, REQUESTED).
    *   `default=ProfessionalCustomerLink.StatusChoices.ACTIVE`: Sets the default status to 'ACTIVE'.
*   `created_at`: DateTimeField
    *   `auto_now_add=True`: Automatically sets the timestamp when a link is first created.

**Relationships:**

*   Many-to-One with `Professional`: A link belongs to one professional.
*   Many-to-One with `Customer`: A link belongs to one customer.

**`__str__` Method:**

Returns a string representation of the link, showing the linked professional, customer, and the status of the link.
Example: `Link: ProfessionalObj <-> CustomerObj (ACTIVE)`

**Meta:**

*   `verbose_name = "Professional-Customer Link"`
*   `verbose_name_plural = "Professional-Customer Links"`
*   `constraints`:
    *   `UniqueConstraint(fields=['professional', 'customer'], name='unique_professional_customer_link')`: Ensures that a specific professional and customer can only be linked once.
*   `ordering = ['-created_at']`: Links will be sorted by creation date in descending order by default.

---
## Migration Commands

Based on the current model definitions and existing migration files, all models appear to be up-to-date with the database schema. No new migrations seem to be immediately required.

However, if you make any changes to the models (e.g., add a new field, modify an existing field, create a new model), you will need to create and apply new database migrations.

The standard commands to do this are:

1.  **Create new migration files based on model changes:**
    ```bash
    python manage.py makemigrations <app_name>
    ```
    Replace `<app_name>` with the specific application where models were changed (e.g., `orders`, `services`, `users`). If you've made changes in multiple apps, you can run `python manage.py makemigrations` without specifying an app name to check all apps, or run the command for each app.

2.  **Apply the migrations to the database:**
    ```bash
    python manage.py migrate
    ```
    This command applies any unapplied migrations, bringing the database schema in sync with your model definitions.

It's good practice to run `python manage.py makemigrations` after any model change to ensure your schema definition is captured, and then `python manage.py migrate` to apply those changes.
