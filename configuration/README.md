# Configuration App

This Django app provides a dedicated configuration management system for administrators (superusers) to manage labels for different parts of the system.

## Features

- **Configuration Dashboard**: A central dashboard for managing all configuration categories and labels
- **Label Management**: Create, edit, and delete labels for different categories
- **Category-based Organization**: Labels are organized by categories (Website, Professional, Services/Items, Customer)
- **Integration with Models**: Labels can be assigned to Professionals, Customers, Services, and Items

## Categories

The system includes the following configuration categories:

1. **Website**: General website configuration labels
2. **Professional**: Labels for Professionals, available when adding/editing Professionals
3. **Services and Items**: Labels for Services and Items, available when adding/editing Services and Items
4. **Customer**: Labels for Customers, available when adding/editing Customers

## Usage

### Admin Interface

Administrators can access the configuration dashboard at `/configuration/` to manage labels.

### Model Integration

Labels are integrated with the following models:

- `Professional`: Labels with category "PROFESSIONAL"
- `Customer`: Labels with category "CUSTOMER"
- `Service` and `Item`: Labels with category "SERVICE"

### Adding Labels to Models

When creating or editing a model in the admin interface, you can assign labels from the appropriate category.

## Security

Only superusers have access to the configuration management interface.

