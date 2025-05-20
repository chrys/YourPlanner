# YourPlanner Requirements

YourPlanner is a SaaS website that enables professionals to offer their services to customers.

## Main Flows 

### User Registration
- Customers can register and create a profile.
    - Implemented in the `users` app.
    - This is done via a registration form in file `users/forms.py` in the class `RegistrationForm`.
- Professionals can register and create a profile.
    - Implemented in the `users` app.
    - This is done via a registration form in file `users/forms.py` in the class `RegistrationForm`.
- Customers can select a professional during registration.
    - Implemented in the `users` app.
    - This selection is done via a dropdown list of available professionals in file `users/forms.py` in the class `ProfessionalChoiceForm`.
- Professionals can view and manage their linked customers.
    - Not implemented yet.
- Customers can view and manage their linked professionals.
    - This is implemented in users/views.py in `change_professional(request)`.
- Customers can update their profile information.
    - Not implemented yet.
- Professionals can update their profile information.
    - Not implemented yet.
    
- Customers can view their linked professionals and their services.
    - Not implemented yet.
### Service Management
- Professionals can create and manage their services.
    - Implemented in the `services` app.
    - This is done via a service management page in file `services/views.py` in `service_items(request, service_id)`
- Professionals can add, edit, or remove items within their services.
    - Impemented in the `services` app.
    - This is done via a service management page in file `services/views.py` in `edit_item(request, item_id)`
### Order Management
- Customers can view their order history and details
    - This is implemented in `orders/views.py` in `basket(request)` 
- Customer can select items from their linked professional's services.
    - This is implemented in `orders/views.py` in `select_items(request)`

## Main Entities

- **Professionals**:  
  - Each professional is a user of the system.
  - Professionals can add, remove, or edit one or more services for their customers.

- **Customers**:  
  - Each customer is also a user of the system.
  - Each customer can be linked to one or more professionals.

- **Services**:  
  - Each service has:
    - **Title**
    - **Description**
    - One or more **Items**

- **Items**:  
  - Each item has:
    - **Title**
    - **Description**
    - One or more **Prices**

## Relationships

- A professional can have multiple services.
- A service can have multiple items.
- An item can have multiple prices.
- A customer can be linked to multiple professionals.
- A professional can be linked to multiple customers.

# Implementation

YourPlanner project is implemented as a Django application with the following main apps:

## core

- Contains the main landing page and shared templates (such as `base.html`).
- Provides the main navigation and layout for the site.
- Handles the root URL and static assets (CSS, images).

## users

- Manages user registration, authentication, and user profiles.
- Defines two main profile models:
  - `Professional`: Linked one-to-one with a Django user, includes fields like `title`, `specialization`, and `bio`.
  - `Customer`: Linked one-to-one with a Django user, includes optional company name.
- Handles the relationship between professionals and customers via the `ProfessionalCustomerLink` model, which tracks the status and uniqueness of each link.
- Provides registration forms and views for both customers and professionals, including professional selection for customers.
- Includes user management views and templates for profile, dashboard, and changing professional.

## services

- Allows professionals to create and manage their own services.
- Each `Service` is linked to a `Professional` and can have multiple `Item` objects.
- Each `Item` represents a component of a service and can have one or more `Price` objects.
- The `Price` model supports different frequencies (one-time, hourly, monthly, etc.), currencies, and active/inactive status.
- Provides admin-style pages for professionals to add, edit, and view their services and items, including price management.

## orders

- Manages the ordering process for customers.
- The `Order` model represents a customer's order, linked to a customer and tracks status (pending, confirmed, etc.), total amount, and currency.
- The `OrderItem` model represents individual items within an order, linking to the selected service, item, price, and quantity, and stores price details at the time of order.
- Customers can select items from their linked professional's services, update their basket, and view their current order with itemized pricing and totals.
- Includes views and templates for selecting items, updating the basket, and displaying the order summary.

## Integration

- The apps are integrated so that professionals can offer services and items with prices, customers can link to professionals, select and order items, and manage their orders and profiles.
- The UI uses both Django templates and Vue.js for dynamic forms and interactivity.
- All access to management and order pages is restricted to authenticated users.
