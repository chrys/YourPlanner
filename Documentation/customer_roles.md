# Customer Roles

## Overview

The Customer Roles feature allows administrators to assign different roles to customers, which can be used to determine access levels, feature availability, and pricing tiers. This document explains how to use and extend this functionality.

## Available Roles

The following roles are available for customers:

- **STANDARD**: Default role for all customers
- **PREMIUM**: Premium customers with additional benefits
- **VIP**: VIP customers with enhanced services
- **ENTERPRISE**: Enterprise-level customers with full access to all features

## Implementation Details

### Model

The role field is implemented in the `Customer` model in `users/models.py`:

```python
class Customer(TimeStampedModel):
    # ...
    class RoleChoices(models.TextChoices):
        STANDARD = 'STANDARD', 'Standard'
        PREMIUM = 'PREMIUM', 'Premium'
        VIP = 'VIP', 'VIP'
        ENTERPRISE = 'ENTERPRISE', 'Enterprise'
    
    # ...
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.STANDARD,
        help_text="Customer role - determines access levels and features"
    )
    # ...
```

### Utility Methods

The `Customer` model provides two utility methods for checking roles:

1. `has_role(role_name)`: Checks if a customer has a specific role
2. `has_minimum_role(role_name)`: Checks if a customer has at least the specified role level

### Usage Examples

#### Checking if a customer has a specific role

```python
# Check if the customer has the VIP role
if customer.has_role(Customer.RoleChoices.VIP):
    # Provide VIP-specific functionality
    pass
```

#### Checking if a customer has at least a minimum role level

```python
# Check if the customer has at least PREMIUM role
if customer.has_minimum_role(Customer.RoleChoices.PREMIUM):
    # Provide functionality available to PREMIUM, VIP, and ENTERPRISE customers
    pass
```

## Administration

Customer roles can only be set by administrators through the Django admin interface. The role field is intentionally excluded from the `CustomerForm` to prevent customers from modifying their own role.

To change a customer's role:

1. Log in to the Django admin interface
2. Navigate to Users > Customers
3. Select the customer to modify
4. Change the role field
5. Save the changes

## Security Considerations

- The role field is not accessible to customers through forms
- Role checks should be performed in views and templates to restrict access to features
- Always use the provided utility methods (`has_role` and `has_minimum_role`) for consistent role checking

## Extending the Roles System

To add new roles:

1. Add the new role to the `RoleChoices` class in the `Customer` model
2. Update the `role_levels` dictionary in the `has_minimum_role` method to include the new role
3. Create a migration to apply the changes to the database

Example of adding a new "GOLD" role between PREMIUM and VIP:

```python
class RoleChoices(models.TextChoices):
    STANDARD = 'STANDARD', 'Standard'
    PREMIUM = 'PREMIUM', 'Premium'
    GOLD = 'GOLD', 'Gold'  # New role
    VIP = 'VIP', 'VIP'
    ENTERPRISE = 'ENTERPRISE', 'Enterprise'

# Update role levels in has_minimum_role method
role_levels = {
    self.RoleChoices.STANDARD: 0,
    self.RoleChoices.PREMIUM: 1,
    self.RoleChoices.GOLD: 2,    # New role level
    self.RoleChoices.VIP: 3,     # Updated level
    self.RoleChoices.ENTERPRISE: 4  # Updated level
}
```

