# Templates App Documentation

## Overview

The "Templates" app allows Professionals to create and manage predefined templates for services they offer. Each template acts as a blueprint that can include a title, a detailed description, a collection of images (one of which is marked as default), and a list of specific services.

This feature helps Professionals streamline the process of offering standardized packages or service combinations to their Customers.

## Functionality

### 1. Template Creation

Professionals can create new templates through a dedicated form. The following fields are available:

*   **Title:** A concise name for the template (e.g., "Basic Website Package", "Wedding Photography Gold Tier").
*   **Description:** A detailed explanation of what the template includes, its benefits, or any terms and conditions. This field supports rich text formatting.
*   **Services:** Professionals can select multiple services from their existing list of offerings to include in this template. This allows for bundling different services together.
*   **Images:** Multiple images can be uploaded for each template. This is useful for showcasing the results or components of the service package.

### 2. Image Management

*   **Multiple Uploads:** The system allows uploading several images for a single template.
*   **Default Image:** One image must be designated as the "default" image. This image will be used as the primary visual representation of the template in listings or summaries.
*   **Gallery:** On the template's detail page, all uploaded images are displayed in a gallery format, with the default image typically shown more prominently or listed first.
*   **Image Deletion:** Professionals can remove images from a template during an update.

### 3. Template Management

*   **My Templates Page:** Professionals have a page listing all templates they have created. This page shows a summary of each template (title, snippet of description, default image thumbnail, service count) and provides quick access to view or edit them.
*   **Template Detail Page:** Each template has its own dedicated page displaying:
    *   Full Title and Description.
    *   A gallery of all its images.
    *   A comprehensive list of all services included in the template.
*   **Updating Templates:** Professionals can modify any aspect of their existing templates, including adding or removing services, changing text, and managing images (uploading new ones, deleting old ones, or changing the default image).

### 4. How it Works for Professionals

1.  **Navigate to "My Templates":** Find a link in your professional dashboard or navigation menu.
2.  **Create New:** Click "Create New Template".
3.  **Fill Details:** Provide a title, description, and select the services to include.
4.  **Upload Images:** Add one or more images. Remember to mark one as the default. If you upload images, you *must* select one as default. If only one image is uploaded, it might be automatically set as default.
5.  **Save:** Once saved, the template appears in "My Templates".
6.  **View/Edit:** Click on any template in the list to see its detail page or to update it.

### Using Templates as a Customer

Customers can easily discover and utilize service templates created by Professionals to quickly assemble an order.

1.  **Finding Templates:**
    *   Customers will find an "Add new services using templates" link on their main management page or dashboard. Clicking this link navigates them to the "Customer Templates" page.

2.  **Customer Templates Page:**
    *   This page displays all available templates in a user-friendly grid layout (powered by Vue.js).
    *   For each template, the following information is shown:
        *   **Title:** The name of the template.
        *   **Description:** A brief summary of the template.
        *   **Default Image:** The primary image representing the template.
    *   Both the **Title** and the **Default Image** serve as clickable links that take the customer to the individual Template Page for more details.

3.  **Individual Template Page (Customer View):**
    *   This page provides a comprehensive view of a single template, showing:
        *   Full Title
        *   Complete Description
        *   All uploaded images for the template, typically in a gallery view.
        *   A clear list of all services included within that template.
    *   A prominent button or option labeled **"Update Basket"** (or similar wording like "Add to Order") is available.

4.  **"Update Basket" Functionality:**
    *   When a customer is on an individual Template Page and clicks the "Update Basket" button:
        *   All services listed in that template are added to their current active order or basket.
        *   Crucially, this action also adds all the constituent line items associated with each of those services, reflecting their current prices. For example, if a "Basic Website Package" service within the template includes "Domain Registration," "Basic Hosting," and "Homepage Design" as its items, all these items will be added to the basket with their respective current prices.
        *   This ensures that the customer's basket is populated with a complete set of items as defined by the Professional in the template.

### Technical Details (For Developers)

*   **Models:**
    *   `Template`: Stores the main template information (professional, title, description, M2M with `Service`).
    *   `TemplateImage`: Stores image files, a foreign key to `Template`, and an `is_default` boolean flag. A database constraint ensures only one `is_default=True` image per template.
*   **Views:** Class-based views (`ListView`, `DetailView`, `CreateView`, `UpdateView`) are used, protected by `LoginRequiredMixin` and a custom `ProfessionalRequiredMixin`.
*   **Forms:** `TemplateForm` and an `inlineformset_factory` for `TemplateImage` are used.
*   **URLs:** Namespaced under `/templates/`.
*   **Templates:** Located in `templates/templates/templates/`.
