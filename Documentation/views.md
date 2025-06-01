# Django Views, Forms, and Templates Documentation

This document provides an overview of the views, forms, and templates used for handling CRUD (Create, Read, Update, Delete) operations for various models in the YourPlanner project. It will detail the Class-Based Views (CBVs), ModelForms, template structures, URL patterns, error handling, and authentication mechanisms.

The documentation will be presented on a per-model basis.
```markdown
## CRUD for Service Model (`services.models.Service`)

This section details the Class-Based Views (CBVs) for performing Create, Read, Update, and Delete operations on the `Service` model. All views should enforce authentication, ensuring only logged-in users can access them. Authorization will be implemented to ensure that professionals can only modify or delete services they own.

### Common Mixins and Decorators

*   **`django.contrib.auth.mixins.LoginRequiredMixin`**: This mixin will be used for all CRUD views to ensure that only authenticated users can access them. If an unauthenticated user attempts to access a view, they will be redirected to the login page.
*   **`django.contrib.auth.decorators.login_required`**: While CBVs use `LoginRequiredMixin`, function-based views (if any were used) would use this decorator.

### 1. Create View (`ServiceCreateView`)

*   **Purpose**: Allows a logged-in professional to create a new service.
*   **Class**: `ServiceCreateView(LoginRequiredMixin, CreateView)`
*   **Model**: `models.Service` (from `services.models`)
*   **Form Class**: `forms.ServiceForm` (to be defined in `services.forms`)
*   **Template Name**: `services/service_form.html` (shared with UpdateView)
*   **Success URL**: `reverse_lazy('services:service_list')` (or `service_detail` for the newly created service).
*   **Key Methods/Attributes**:
    *   `form_valid(self, form)`: This method will be overridden to automatically assign the currently logged-in professional (`self.request.user.professional_profile`) to the `professional` field of the new `Service` instance before saving. It should also check if the `request.user` actually has a `professional_profile`.
    *   It's assumed that only users who are Professionals can create services. Additional checks might be needed (e.g., using a custom mixin or `UserPassesTestMixin`) if non-professionals should be barred from even attempting to access this view.

### 2. Read Views

#### a. List View (`ServiceListView`)

*   **Purpose**: Displays a list of services. Can be configured to show all services or only those belonging to the currently logged-in professional. For this documentation, we'll assume it shows services owned by the current professional if they are one, or all services for other user types (e.g., an admin or customer browsing).
*   **Class**: `ServiceListView(LoginRequiredMixin, ListView)`
*   **Model**: `models.Service`
*   **Template Name**: `services/service_list.html`
*   **Context Object Name**: `services` (default is `object_list`)
*   **Key Methods/Attributes**:
    *   `get_queryset(self)`: This method can be overridden. If the logged-in user is a Professional, it could filter services to show only those where `service.professional == self.request.user.professional_profile`. Otherwise, it might show all active services or apply other filtering logic. For simplicity in this documentation, we can start with showing all services and note this customization point.
    *   `paginate_by`: Optionally set to add pagination to the list.

#### b. Detail View (`ServiceDetailView`)

*   **Purpose**: Displays the details of a single service.
*   **Class**: `ServiceDetailView(LoginRequiredMixin, DetailView)`
*   **Model**: `models.Service`
*   **Template Name**: `services/service_detail.html`
*   **Context Object Name**: `service` (default is `object`)
*   **Error Handling**: If a service with the given primary key (`pk`) does not exist, Django's `DetailView` automatically raises an `Http404` error.

### 3. Update View (`ServiceUpdateView`)

*   **Purpose**: Allows the professional who owns the service to update its details.
*   **Class**: `ServiceUpdateView(LoginRequiredMixin, UpdateView)`
    *   Consider adding a custom mixin (e.g., `UserOwnsServiceMixin`) or overriding `get_object` or `get_queryset` to ensure only the owner can update.
*   **Model**: `models.Service`
*   **Form Class**: `forms.ServiceForm`
*   **Template Name**: `services/service_form.html` (shared with CreateView)
*   **Success URL**: `reverse_lazy('services:service_detail', kwargs={'pk': self.object.pk})`
*   **Key Methods/Attributes**:
    *   `get_queryset(self)`: This method **must** be overridden to ensure that users can only update services they own. It should filter the queryset by `professional=self.request.user.professional_profile`. If a user tries to access an edit page for a service they don't own, this will result in a 404.
    *   `form_valid(self, form)`: Can be used for any additional logic upon successful form submission, though often not needed if `get_queryset` handles ownership.

### 4. Delete View (`ServiceDeleteView`)

*   **Purpose**: Allows the professional who owns the service to delete it.
*   **Class**: `ServiceDeleteView(LoginRequiredMixin, DeleteView)`
    *   Similar to `ServiceUpdateView`, requires ownership check.
*   **Model**: `models.Service`
*   **Template Name**: `services/service_confirm_delete.html`
*   **Success URL**: `reverse_lazy('services:service_list')`
*   **Key Methods/Attributes**:
    *   `get_queryset(self)`: This method **must** be overridden to ensure that users can only delete services they own, similar to `ServiceUpdateView`. It should filter by `professional=self.request.user.professional_profile`.
    *   **Confirmation**: `DeleteView` automatically handles showing a confirmation page before deletion. The template `service_confirm_delete.html` is used for this.

---
### Forms (`ServiceForm`)

For creating and updating `Service` instances, a `ModelForm` provides a convenient and efficient way to generate a form directly from the model, including default validation based on field types.

*   **File**: `services/forms.py`
*   **Class**: `ServiceForm(forms.ModelForm)`
*   **Purpose**: To handle the creation and updating of `Service` objects.
*   **Model**: `models.Service`
*   **Fields**:
    *   The form should include fields that the user needs to fill: `title`, `description`, and `is_active`.
    *   The `professional` field will be excluded from the form (`exclude = ['professional']` or specify `fields = ['title', 'description', 'is_active']`) because it will be set automatically in the view based on the logged-in user.

    ```python
    # Example services/forms.py:
    from django import forms
    from .models import Service

    class ServiceForm(forms.ModelForm):
        class Meta:
            model = Service
            fields = ['title', 'description', 'is_active']
            # Alternatively, to exclude only 'professional' and auto-fields:
            # exclude = ['professional', 'created_at', 'updated_at']


        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Optional: Add custom widgets or help texts here if needed
            self.fields['title'].widget.attrs.update({'class': 'form-control'})
            self.fields['description'].widget.attrs.update({'class': 'form-control'})
            self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})
    ```

*   **Validation**:
    *   Django's `ModelForm` automatically handles basic validation based on the model's field definitions (e.g., `CharField` `max_length`, `TextField` requirements, `BooleanField` input).
    *   For `title` (CharField), it will enforce `max_length=255`.
    *   `description` (TextField) is optional (`blank=True` in the model).
    *   `is_active` (BooleanField) will accept boolean values.
    *   Custom validation logic can be added by defining `clean_<fieldname>()` methods or a general `clean()` method within the `ServiceForm` class if more complex rules are needed beyond what the model provides. For example, ensuring the title is unique for a professional could be a custom validation. For now, we assume standard model validation is sufficient.

---
### Templates

The following HTML templates are used by the `Service` CRUD views. These examples provide basic structure and include essential Django template tags. They would typically extend a base template (e.g., `base.html`) which is not detailed here.

#### Common Template Features:

*   **CSRF Token**: All forms that submit data via POST (create, update) must include the `{% csrf_token %}` template tag for security.
*   **Vue.js for Presentation**: While the backend logic is handled by Django, Vue.js could be integrated into these templates to enhance user experience. For example, Vue could be used for:
    *   Client-side validation feedback before submitting a form.
    *   Dynamic filtering or sorting of the service list.
    *   Creating richer UI components for displaying service details or form fields.
    *   Making asynchronous updates to parts of a page without full reloads.
    The documentation below focuses on the Django template structure; actual Vue.js implementation would be separate and depends on specific frontend design choices.
*   **`safe` Filter**: The `safe` filter should be used with extreme caution and only on content that is known to be secure and not user-generated in a way that could lead to XSS vulnerabilities. For displaying model field data like `service.title` or `service.description`, direct output is usually safe as Django auto-escapes by default. If you were to render content explicitly marked as safe from a source you don't fully control, that would be a risk. In typical CRUD display, its use is minimal.

#### 1. Service Form (`services/service_form.html`)

*   **Purpose**: Used by `ServiceCreateView` and `ServiceUpdateView` to render the form for creating or editing a service.
*   **Context**:
    *   `form`: The `ServiceForm` instance.
    *   `object` or `service`: The service instance being edited (available in UpdateView).
*   **Structure Example**:

    ```html+django
    {% extends "base.html" %}

    {% block title %}{% if object %}Edit Service{% else %}Create Service{% endif %}{% endblock %}

    {% block content %}
      <h1>{% if object %}Edit Service: {{ object.title }}{% else %}Create New Service{% endif %}</h1>
      <form method="post">
        {% csrf_token %}
        {{ form.as_p }}  {# Renders form fields as paragraphs; can be customized #}
        <button type="submit" class="btn btn-primary">{% if object %}Save Changes{% else %}Create Service{% endif %}</button>
      </form>
      <a href="{% url 'services:service_list' %}" class="btn btn-secondary mt-2">Cancel</a>
    {% endblock %}
    ```

#### 2. Service List (`services/service_list.html`)

*   **Purpose**: Used by `ServiceListView` to display a list of services.
*   **Context**:
    *   `services` (or `object_list`): The queryset of service instances.
*   **Structure Example**:

    ```html+django
    {% extends "base.html" %}

    {% block title %}Services{% endblock %}

    {% block content %}
      <h1>Services</h1>
      <a href="{% url 'services:service_create' %}" class="btn btn-primary mb-3">Add New Service</a>
      {% if services %}
        <ul class="list-group">
          {% for service in services %}
            <li class="list-group-item d-flex justify-content-between align-items-center">
              <a href="{% url 'services:service_detail' pk=service.pk %}">{{ service.title }}</a>
              <span>
                (Professional: {{ service.professional.user.username }}) - {% if service.is_active %}Active{% else %}Inactive{% endif %}
                <a href="{% url 'services:service_edit' pk=service.pk %}" class="btn btn-sm btn-info ml-2">Edit</a>
                <a href="{% url 'services:service_delete' pk=service.pk %}" class="btn btn-sm btn-danger ml-1">Delete</a>
              </span>
            </li>
          {% endfor %}
        </ul>
      {% else %}
        <p>No services found.</p>
        {% if request.user.professional_profile %} {# Assuming only professionals create services #}
          <p>You haven't added any services yet. <a href="{% url 'services:service_create' %}">Add one now!</a></p>
        {% endif %}
      {% endif %}
    {% endblock %}
    ```
    *   **Note**: Links to edit/delete should ideally only be shown if the logged-in user has permission (e.g., is the owner of the service). This logic can be added in the template or handled by the views not providing these services in the context if not owned.

#### 3. Service Detail (`services/service_detail.html`)

*   **Purpose**: Used by `ServiceDetailView` to display the details of a single service.
*   **Context**:
    *   `service` (or `object`): The service instance.
*   **Structure Example**:

    ```html+django
    {% extends "base.html" %}

    {% block title %}{{ service.title }}{% endblock %}

    {% block content %}
      <h1>{{ service.title }}</h1>
      <p><strong>Professional:</strong> {{ service.professional.user.get_full_name|default:service.professional.user.username }}</p>
      <p><strong>Description:</strong></p>
      <p>{{ service.description|linebreaksbr }}</p>
      <p><strong>Status:</strong> {% if service.is_active %}Active{% else %}Inactive{% endif %}</p>
      <p><strong>Created:</strong> {{ service.created_at|date:"Y-m-d H:i" }}</p>
      <p><strong>Last Updated:</strong> {{ service.updated_at|date:"Y-m-d H:i" }}</p>

      {# Example: Displaying related items (if applicable) #}
      {% if service.items.all %}
        <h2>Items in this Service</h2>
        <ul>
        {% for item in service.items.all %}
          <li>{{ item.title }}</li>
        {% endfor %}
        </ul>
      {% endif %}

      {% if user.professional_profile == service.professional %} {# Show edit/delete only to owner #}
        <a href="{% url 'services:service_edit' pk=service.pk %}" class="btn btn-info">Edit Service</a>
        <a href="{% url 'services:service_delete' pk=service.pk %}" class="btn btn-danger">Delete Service</a>
      {% endif %}
      <a href="{% url 'services:service_list' %}" class="btn btn-secondary mt-2">Back to List</a>
    {% endblock %}
    ```

#### 4. Service Confirm Delete (`services/service_confirm_delete.html`)

*   **Purpose**: Used by `ServiceDeleteView` to provide a confirmation page before a service is deleted.
*   **Context**:
    *   `service` (or `object`): The service instance to be deleted.
*   **Structure Example**:

    ```html+django
    {% extends "base.html" %}

    {% block title %}Confirm Delete Service{% endblock %}

    {% block content %}
      <h1>Confirm Delete: {{ service.title }}</h1>
      <p>Are you sure you want to delete the service "{{ service.title }}"?</p>
      <form method="post">
        {% csrf_token %}
        <button type="submit" class="btn btn-danger">Yes, Delete</button>
        <a href="{% url 'services:service_detail' pk=service.pk %}" class="btn btn-secondary">Cancel</a>
      </form>
    {% endblock %}
    ```

---
### URL Patterns

The following URL patterns are defined in `services/urls.py` to route requests to the appropriate `Service` CRUD views. An `app_name = 'services'` is assumed in this file for namespacing URLs.

*   **File**: `services/urls.py`

```python
# Example services/urls.py:
from django.urls import path
from . import views # Assuming views are in services/views.py

app_name = 'services'

urlpatterns = [
    # Service CRUD URLs
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('services/new/', views.ServiceCreateView.as_view(), name='service_create'),
    path('services/<int:pk>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('services/<int:pk>/edit/', views.ServiceUpdateView.as_view(), name='service_edit'),
    path('services/<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='service_delete'),

    # ... other URLs for Item, Price, etc. would go here
]
```

**Explanation of URL Patterns:**

*   **`path('services/', views.ServiceListView.as_view(), name='service_list')`**
    *   **URL**: `/services/`
    *   **View**: `ServiceListView`
    *   **Name**: `services:service_list`
    *   **Purpose**: Displays the list of services.

*   **`path('services/new/', views.ServiceCreateView.as_view(), name='service_create')`**
    *   **URL**: `/services/new/`
    *   **View**: `ServiceCreateView`
    *   **Name**: `services:service_create`
    *   **Purpose**: Displays the form to create a new service and handles form submission.

*   **`path('services/<int:pk>/', views.ServiceDetailView.as_view(), name='service_detail')`**
    *   **URL**: `/services/<pk>/` (e.g., `/services/1/`)
    *   **View**: `ServiceDetailView`
    *   **Name**: `services:service_detail`
    *   **Purpose**: Displays details of a specific service, identified by its primary key (`pk`).

*   **`path('services/<int:pk>/edit/', views.ServiceUpdateView.as_view(), name='service_edit')`**
    *   **URL**: `/services/<pk>/edit/` (e.g., `/services/1/edit/`)
    *   **View**: `ServiceUpdateView`
    *   **Name**: `services:service_edit`
    *   **Purpose**: Displays the form to edit an existing service and handles form submission.

*   **`path('services/<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='service_delete')`**
    *   **URL**: `/services/<pk>/delete/` (e.g., `/services/1/delete/`)
    *   **View**: `ServiceDeleteView`
    *   **Name**: `services:service_delete`
    *   **Purpose**: Displays a confirmation page and handles the deletion of a specific service.

**Integration with Project URLs:**

These app-specific URLs would then be included in the main project's `urls.py` file (e.g., `YourPlanner/urls.py`):

```python
# Example YourPlanner/urls.py:
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', include('services.urls', namespace='services')), # Or whatever base path
    # ... other app urls
]
```
This setup allows using namespaced URLs like `{% url 'services:service_list' %}` in templates.

**Suggestions:**

*   The current URL structure (`services/...`) is clear and conventional for RESTful resource management.
*   Ensure that the `<int:pk>` converter is used for primary keys to provide type checking at the URL routing level.
*   Consider if a more nested structure would be beneficial if services were always accessed in the context of a professional in the URL (e.g., `/professionals/<prof_pk>/services/`), but for general CRUD, the current approach is standard. The views themselves will handle authorization based on the logged-in professional.

---
```markdown
### CRUD for Item Model (`services.models.Item`)

This section details the Class-Based Views (CBVs) for CRUD operations on the `Item` model. Items are components of a `Service`. Operations on `Item` instances are typically performed in the context of their parent `Service`, and authorization is tied to the professional who owns that `Service`.

#### Common Assumptions for Item Views:

*   **Nested URLs**: URLs for `Item` CRUD operations are assumed to be nested under a specific `Service`'s URL. For example: `/services/<int:service_pk>/items/new/`. The `service_pk` will be used to fetch the parent `Service` object.
*   **Authorization**: All views will use `LoginRequiredMixin`. Additionally, a custom mixin or checks within view methods (e.g., `get_queryset`, `get_object`, `dispatch`) will be necessary to ensure that the logged-in user (Professional) owns the parent `Service` associated with the `Item`.

#### Helper Mixin (Conceptual for Authorization)

A conceptual mixin like `UserOwnsParentServiceMixin` could be created to handle the authorization logic for `Item` views. This mixin would:
1.  Extract `service_pk` from `self.kwargs`.
2.  Fetch the `Service` object.
3.  Verify `service.professional == self.request.user.professional_profile`.
4.  If not the owner, raise `Http404` or `PermissionDenied`.
5.  Store the fetched `service` object on `self` for use in other view methods.

```python
# Conceptual Mixin (not part of the generated documentation file, but for context)
# from django.shortcuts import get_object_or_404
# from django.core.exceptions import PermissionDenied
# from .models import Service # Assuming this is in services.views

# class UserOwnsParentServiceMixin:
#     def dispatch(self, request, *args, **kwargs):
#         service_pk = self.kwargs.get('service_pk')
#         self.service = get_object_or_404(Service, pk=service_pk)
#         if not request.user.is_authenticated or #            not hasattr(request.user, 'professional_profile') or #            self.service.professional != request.user.professional_profile:
#             raise PermissionDenied("You do not have permission to manage items for this service.")
#         return super().dispatch(request, *args, **kwargs)
```

*(The actual implementation of such a mixin would be in the views.py file, not the documentation itself. The documentation will refer to this principle.)*

---

#### 1. Create View (`ItemCreateView`)

*   **Purpose**: Allows the professional (owner of the parent `Service`) to add a new item to a specific service.
*   **Class**: `ItemCreateView(LoginRequiredMixin, UserOwnsParentServiceMixin, CreateView)` (assuming `UserOwnsParentServiceMixin` or similar check)
*   **Model**: `models.Item`
*   **Form Class**: `forms.ItemForm`
*   **Template Name**: `services/item_form.html`
*   **Success URL**: Will likely redirect to the parent `Service`'s detail page or the list of items for that service. E.g., `reverse_lazy('services:service_detail', kwargs={'pk': self.kwargs['service_pk']})`.
*   **Key Methods/Attributes**:
    *   `dispatch()`: Would use `UserOwnsParentServiceMixin` or similar logic to ensure the user owns the parent `Service` (identified by `service_pk` from URL).
    *   `get_form_kwargs(self)`: To pass the parent `service` instance to the form if needed, though the `form_valid` approach is often cleaner for setting the foreign key.
    *   `form_valid(self, form)`:
        *   The parent `Service` (fetched via `service_pk` from the URL and verified by the mixin/dispatch) is assigned to `form.instance.service`.
        *   `self.object = form.save()`
    *   `get_context_data(self, **kwargs)`: Add the parent `service` to the context so the template can display information about it (e.g., "Adding item to Service: [Service Title]").

#### 2. Read Views

##### a. List View (`ItemListView`)

*   **Purpose**: Displays a list of items, typically for a specific service.
*   **Class**: `ItemListView(LoginRequiredMixin, UserOwnsParentServiceMixin, ListView)`
*   **Model**: `models.Item`
*   **Template Name**: `services/item_list.html` (could be part of the `service_detail.html` or a standalone page).
*   **Context Object Name**: `items`
*   **Key Methods/Attributes**:
    *   `dispatch()`: Authorization check for parent `Service`.
    *   `get_queryset(self)`: Overridden to filter items belonging to the parent `Service` ( `self.service.items.all()`).
    *   `get_context_data(self, **kwargs)`: Add the parent `service` to the context.

##### b. Detail View (`ItemDetailView`)

*   **Purpose**: Displays the details of a single item.
*   **Class**: `ItemDetailView(LoginRequiredMixin, UserOwnsParentServiceMixin, DetailView)`
*   **Model**: `models.Item`
*   **Template Name**: `services/item_detail.html`
*   **Context Object Name**: `item`
*   **Key Methods/Attributes**:
    *   `dispatch()` or `get_queryset()`: Authorization check. The `DetailView`'s `get_object` will fetch the item, but it's crucial to ensure it belongs to a `Service` owned by the user. This is often done by filtering the queryset.
    *   `get_queryset(self)`: Overridden to filter items ensuring they belong to the `self.service` (parent service, verified by `UserOwnsParentServiceMixin`). This ensures a user cannot guess an item's PK and view it if it's not within their service.
    *   `get_context_data(self, **kwargs)`: Add the parent `service` to the context.
    *   **Error Handling**: `Http404` if the item or parent service doesn't exist or if not authorized.

#### 3. Update View (`ItemUpdateView`)

*   **Purpose**: Allows the professional (owner of the parent `Service`) to update an item's details.
*   **Class**: `ItemUpdateView(LoginRequiredMixin, UserOwnsParentServiceMixin, UpdateView)`
*   **Model**: `models.Item`
*   **Form Class**: `forms.ItemForm`
*   **Template Name**: `services/item_form.html`
*   **Success URL**: E.g., `reverse_lazy('services:item_detail', kwargs={'service_pk': self.kwargs['service_pk'], 'pk': self.object.pk})`.
*   **Key Methods/Attributes**:
    *   `dispatch()` or `get_queryset()`: Authorization check.
    *   `get_queryset(self)`: Crucial for security. Filters items to only those belonging to `self.service` (parent service, verified by `UserOwnsParentServiceMixin`).
    *   `get_context_data(self, **kwargs)`: Add the parent `service` to the context.
    *   `form_valid(self, form)`: The `service` field on the item is already set and should not change during an update of other fields.

#### 4. Delete View (`ItemDeleteView`)

*   **Purpose**: Allows the professional (owner of the parent `Service`) to delete an item.
*   **Class**: `ItemDeleteView(LoginRequiredMixin, UserOwnsParentServiceMixin, DeleteView)`
*   **Model**: `models.Item`
*   **Template Name**: `services/item_confirm_delete.html`
*   **Success URL**: E.g., `reverse_lazy('services:service_detail', kwargs={'pk': self.kwargs['service_pk']})` (redirects to parent service detail page).
*   **Key Methods/Attributes**:
    *   `dispatch()` or `get_queryset()`: Authorization check.
    *   `get_queryset(self)`: Crucial for security, similar to `ItemUpdateView`.
    *   `get_context_data(self, **kwargs)`: Add the parent `service` and the `item` to be deleted to the context.

---
### Forms (`ItemForm`)

An `ItemForm` derived from `ModelForm` is used for creating and updating `Item` instances.

*   **File**: `services/forms.py` (This form would be added to the existing `forms.py` in the `services` app).
*   **Class**: `ItemForm(forms.ModelForm)`
*   **Purpose**: To handle the creation and updating of `Item` objects, typically within the context of a parent `Service`.
*   **Model**: `models.Item`
*   **Fields**:
    *   The form will include user-editable fields: `title`, `description`, and `image`.
    *   The `service` field (ForeignKey to `Service`) will be excluded from the form (`exclude = ['service']` or list fields explicitly). This is because the parent `Service` will be determined from the URL and assigned in the view (e.g., in `form_valid` or by passing it to the form's `__init__` and setting it on `self.instance`).

    ```python
    # Example addition to services/forms.py:
    from django import forms
    from .models import Service, Item # Add Item

    # ... (ServiceForm from previous documentation) ...

    class ItemForm(forms.ModelForm):
        class Meta:
            model = Item
            fields = ['title', 'description', 'image']
            # Alternatively, to exclude only 'service' and auto-fields:
            # exclude = ['service', 'created_at', 'updated_at']

        def __init__(self, *args, **kwargs):
            # Optional: Pop the service instance if passed by the view,
            # though often it's easier to set form.instance.service in the view.
            # self.service = kwargs.pop('service', None)
            super().__init__(*args, **kwargs)

            # Optional: Add custom widgets or help texts
            self.fields['title'].widget.attrs.update({'class': 'form-control'})
            self.fields['description'].widget.attrs.update({'class': 'form-control'})
            self.fields['image'].widget.attrs.update({'class': 'form-control-file'}) # Basic styling for file input

            # If the item instance already exists (i.e., editing an existing item)
            # and it has an image, you might want to display the current image
            # and provide a clearable file input. Django's ImageField handles
            # this by default with ClearableFileInput when not required and has data.
            if self.instance and self.instance.image:
                self.fields['image'].help_text = f"""
                    Currently: <a href="{self.instance.image.url}">{self.instance.image.name}</a><br>
                    To change, select a new image. To remove, check the 'clear' box.
                """
            # Note: For the help_text to render HTML, you might need to use mark_safe
            # in the template or use a custom widget if doing it from the form.
            # However, ClearableFileInput often provides a "Currently:" and "Clear" checkbox.
    ```

*   **Validation**:
    *   Standard `ModelForm` validation applies based on `Item` model field definitions:
        *   `title`: `CharField(max_length=255)` will be enforced.
        *   `description`: `TextField(blank=True)` is optional.
        *   `image`: `ImageField` handles image file validation (e.g., ensuring it's a valid image format). If `Pillow` is not installed, or if `MEDIA_ROOT` and `MEDIA_URL` are not configured, image uploads will fail. The documentation should assume these are set up. `null=True, blank=True` makes it optional.
    *   Custom validation (e.g., image dimensions, file size limits, or ensuring item title is unique within a service) can be added via `clean_image()`, `clean_title()`, or a general `clean()` method in the `ItemForm`.

*   **`ImageField` Handling**:
    *   The `ImageField` requires `enctype="multipart/form-data"` in the HTML `<form>` tag for file uploads to work. This will be noted in the template documentation.
    *   Django's `ClearableFileInput` widget is typically used for `ImageField` when the field is not required or has an existing value, allowing users to clear the current image.

---
### Templates (for Item Model)

These HTML templates support the CRUD operations for the `Item` model. They are typically rendered within the context of a parent `Service`.

#### Common Template Features for Item:

*   **Parent Service Context**: Most item templates will need access to the parent `service` object in their context to display relevant information (e.g., "Add Item to Service [Name]") or for constructing URLs.
*   **`enctype="multipart/form-data"`**: Forms that include file uploads (like `ItemForm` with its `image` field) **must** have `enctype="multipart/form-data"` set on the `<form>` tag.
*   **CSRF Token**: As always, `{% csrf_token %}` is required in forms.
*   **Vue.js & `safe` filter**: Considerations are similar to those for `Service` templates.

#### 1. Item Form (`services/item_form.html`)

*   **Purpose**: Used by `ItemCreateView` and `ItemUpdateView` for `Item` objects.
*   **Context**:
    *   `form`: The `ItemForm` instance.
    *   `service`: The parent `Service` instance (passed from the view).
    *   `object` or `item`: The `Item` instance being edited (in UpdateView).
*   **Structure Example**:

    ```html+django
    {% extends "base.html" %}

    {% block title %}{% if item %}Edit Item{% else %}Add Item to {{ service.title }}{% endif %}{% endblock %}

    {% block content %}
      <h1>{% if item %}Edit Item: {{ item.title }}{% else %}Add New Item to Service: {{ service.title }}{% endif %}</h1>
      {# Ensure enctype for ImageField #}
      <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">{% if item %}Save Changes{% else %}Add Item{% endif %}</button>
      </form>
      <a href="{% url 'services:service_detail' pk=service.pk %}" class="btn btn-secondary mt-2">Cancel (Back to Service)</a>
    {% endblock %}
    ```
    *   **Note on Image Display**: The `{{ form.as_p }}` will render the `ImageField`. For existing items, Django's `ClearableFileInput` widget (default for optional `ImageField`s with an existing image) usually shows the current image path and a checkbox to clear it. You might customize the form widget or template for a better preview if needed.

#### 2. Item List (`services/item_list.html` or integrated into `service_detail.html`)

*   **Purpose**: Used by `ItemListView` to display items, typically for a specific `Service`. Often, this functionality is integrated directly into the `service_detail.html` template. If a separate list page is used:
*   **Context**:
    *   `items` (or `object_list`): Queryset of `Item` instances for the specific service.
    *   `service`: The parent `Service` instance.
*   **Structure Example (Standalone List)**:

    ```html+django
    {% extends "base.html" %}

    {% block title %}Items for {{ service.title }}{% endblock %}

    {% block content %}
      <h1>Items in Service: {{ service.title }}</h1>
      <a href="{% url 'services:item_create' service_pk=service.pk %}" class="btn btn-primary mb-3">Add New Item to this Service</a>
      {% if items %}
        <div class="list-group">
          {% for item_obj in items %} {# Renamed to avoid conflict if 'item' is used elsewhere #}
            <div class="list-group-item">
              <h5 class="mb-1">
                <a href="{% url 'services:item_detail' service_pk=service.pk pk=item_obj.pk %}">{{ item_obj.title }}</a>
              </h5>
              {% if item_obj.image %}
                <img src="{{ item_obj.image.url }}" alt="{{ item_obj.title }}" style="max-width: 100px; max-height: 100px; float: right;">
              {% endif %}
              <p class="mb-1">{{ item_obj.description|truncatewords:30|linebreaksbr }}</p>
              <a href="{% url 'services:item_edit' service_pk=service.pk pk=item_obj.pk %}" class="btn btn-sm btn-info">Edit</a>
              <a href="{% url 'services:item_delete' service_pk=service.pk pk=item_obj.pk %}" class="btn btn-sm btn-danger">Delete</a>
            </div>
          {% endfor %}
        </div>
      {% else %}
        <p>No items found for this service.</p>
      {% endif %}
      <a href="{% url 'services:service_detail' pk=service.pk %}" class="btn btn-secondary mt-3">Back to Service Details</a>
    {% endblock %}
    ```

#### 3. Item Detail (`services/item_detail.html`)

*   **Purpose**: Used by `ItemDetailView` to display a single `Item`'s details.
*   **Context**:
    *   `item`: The `Item` instance.
    *   `service`: The parent `Service` instance.
*   **Structure Example**:

    ```html+django
    {% extends "base.html" %}

    {% block title %}{{ item.title }} - {{ service.title }}{% endblock %}

    {% block content %}
      <h1>Item: {{ item.title }}</h1>
      <p><strong>Part of Service:</strong> <a href="{% url 'services:service_detail' pk=service.pk %}">{{ service.title }}</a></p>

      {% if item.image %}
        <div class="mb-3">
          <img src="{{ item.image.url }}" alt="{{ item.title }}" class="img-fluid" style="max-height: 300px;">
        </div>
      {% endif %}

      <p><strong>Description:</strong></p>
      <p>{{ item.description|linebreaksbr }}</p>
      <p><strong>Created:</strong> {{ item.created_at|date:"Y-m-d H:i" }}</p>
      <p><strong>Last Updated:</strong> {{ item.updated_at|date:"Y-m-d H:i" }}</p>

      {# Placeholder for listing related Prices if applicable #}
      {% if item.prices.all %}
        <h2>Prices for this Item</h2>
        <ul>
        {% for price in item.prices.all %}
          <li>{{ price }}</li> {# Relies on Price.__str__ #}
        {% endfor %}
        </ul>
        {# Link to add new price for this item could go here #}
      {% endif %}

      {# Authorization for edit/delete would typically be handled by the view ensuring this template is only reachable by authorized users,
         but an extra check based on service ownership can be added. #}
      {% if user.professional_profile == service.professional %}
        <a href="{% url 'services:item_edit' service_pk=service.pk pk=item.pk %}" class="btn btn-info">Edit Item</a>
        <a href="{% url 'services:item_delete' service_pk=service.pk pk=item.pk %}" class="btn btn-danger">Delete Item</a>
      {% endif %}
      <a href="{% url 'services:service_detail' pk=service.pk %}" class="btn btn-secondary mt-2">Back to Service Details</a>
    {% endblock %}
    ```

#### 4. Item Confirm Delete (`services/item_confirm_delete.html`)

*   **Purpose**: Used by `ItemDeleteView` for confirming deletion of an `Item`.
*   **Context**:
    *   `item`: The `Item` instance to be deleted.
    *   `service`: The parent `Service` instance.
*   **Structure Example**:

    ```html+django
    {% extends "base.html" %}

    {% block title %}Confirm Delete Item{% endblock %}

    {% block content %}
      <h1>Confirm Delete: {{ item.title }}</h1>
      <p>This item belongs to the service "{{ service.title }}".</p>
      <p>Are you sure you want to delete the item "{{ item.title }}"?</p>
      <form method="post">
        {% csrf_token %}
        <button type="submit" class="btn btn-danger">Yes, Delete Item</button>
        <a href="{% url 'services:item_detail' service_pk=service.pk pk=item.pk %}" class="btn btn-secondary">Cancel</a>
      </form>
    {% endblock %}
    ```

---
### URL Patterns (for Item Model)

`Item` objects are typically managed within the context of a parent `Service`. Therefore, their URL patterns are best structured as nested under the URLs of their parent `Service`. This makes the URLs more intuitive and helps in passing the `service_pk` to the views for context and authorization.

*   **File**: `services/urls.py` (these would be added to the existing `urlpatterns`)

```python
# Example additions to services/urls.py:
from django.urls import path, include # include might be needed if further nesting
from . import views # Assuming views are in services/views.py

# app_name = 'services' # Should already be defined

urlpatterns = [
    # ... (Service CRUD URLs from previous documentation) ...
    # Example: path('services/', views.ServiceListView.as_view(), name='service_list'),
    # etc.

    # Nested Item CRUD URLs
    # These are typically accessed via a specific service.
    # For example, to list items for service 1: /services/1/items/
    # To create an item for service 1: /services/1/items/new/

    path('services/<int:service_pk>/items/',
         views.ItemListView.as_view(), name='item_list'),
    path('services/<int:service_pk>/items/new/',
         views.ItemCreateView.as_view(), name='item_create'),
    path('services/<int:service_pk>/items/<int:pk>/',
         views.ItemDetailView.as_view(), name='item_detail'),
    path('services/<int:service_pk>/items/<int:pk>/edit/',
         views.ItemUpdateView.as_view(), name='item_edit'),
    path('services/<int:service_pk>/items/<int:pk>/delete/',
         views.ItemDeleteView.as_view(), name='item_delete'),

    # ... other URLs for Price, etc. might follow a similar nested pattern if applicable ...
]
```

**Explanation of Nested URL Patterns for `Item`:**

*   **`path('services/<int:service_pk>/items/', views.ItemListView.as_view(), name='item_list')`**
    *   **URL Example**: `/services/1/items/`
    *   **View**: `ItemListView`
    *   **Name**: `services:item_list`
    *   **Purpose**: Displays a list of items belonging to the service identified by `service_pk`.
    *   **URL Parameters**: `service_pk` (for the parent `Service`).

*   **`path('services/<int:service_pk>/items/new/', views.ItemCreateView.as_view(), name='item_create')`**
    *   **URL Example**: `/services/1/items/new/`
    *   **View**: `ItemCreateView`
    *   **Name**: `services:item_create`
    *   **Purpose**: Displays the form to create a new item for the service `service_pk`.
    *   **URL Parameters**: `service_pk`.

*   **`path('services/<int:service_pk>/items/<int:pk>/', views.ItemDetailView.as_view(), name='item_detail')`**
    *   **URL Example**: `/services/1/items/3/`
    *   **View**: `ItemDetailView`
    *   **Name**: `services:item_detail`
    *   **Purpose**: Displays details of a specific item (identified by `pk`) belonging to service `service_pk`.
    *   **URL Parameters**: `service_pk`, `pk` (for the `Item`).

*   **`path('services/<int:service_pk>/items/<int:pk>/edit/', views.ItemUpdateView.as_view(), name='item_edit')`**
    *   **URL Example**: `/services/1/items/3/edit/`
    *   **View**: `ItemUpdateView`
    *   **Name**: `services:item_edit`
    *   **Purpose**: Displays the form to edit item `pk` belonging to service `service_pk`.
    *   **URL Parameters**: `service_pk`, `pk`.

*   **`path('services/<int:service_pk>/items/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete')`**
    *   **URL Example**: `/services/1/items/3/delete/`
    *   **View**: `ItemDeleteView`
    *   **Name**: `services:item_delete`
    *   **Purpose**: Displays confirmation and handles deletion of item `pk` from service `service_pk`.
    *   **URL Parameters**: `service_pk`, `pk`.

**Suggestions for `Item` URLs:**

*   **Nesting is Recommended**: The nested structure `services/<service_pk>/items/...` is highly recommended as it clearly defines the parent-child relationship and makes it easy to pass `service_pk` to the views for context and authorization.
*   **URL Naming Consistency**: Maintain consistent naming for URL patterns (e.g., `model_list`, `model_create`, `model_detail`, `model_edit`, `model_delete`).
*   **Primary Keys**: Using `<int:service_pk>` and `<int:pk>` ensures type safety at the routing level.

---
```markdown
### CRUD for Price Model (`services.models.Price`)

This section details the Class-Based Views (CBVs) for CRUD operations on the `Price` model. Prices are specific to an `Item`, which in turn belongs to a `Service`. Authorization for managing prices is tied to the professional who owns the grandparent `Service`.

#### Common Assumptions for Price Views:

*   **Deeply Nested URLs**: URLs for `Price` CRUD operations are assumed to be nested under a specific `Service` and `Item`. For example: `/services/<int:service_pk>/items/<int:item_pk>/prices/new/`. The `service_pk` and `item_pk` will be used to fetch the parent `Service` and `Item` objects for context and authorization.
*   **Authorization**: All views will use `LoginRequiredMixin`. A custom mixin or checks within view methods will be essential to ensure the logged-in user (Professional) owns the grandparent `Service` of the `Item` for which the price is being managed.

#### Helper Mixin (Conceptual for Authorization - extended)

A conceptual mixin like `UserOwnsGrandparentServiceViaItemMixin` could handle authorization:
1.  Extract `service_pk` and `item_pk` from `self.kwargs`.
2.  Fetch the `Service` and `Item` objects. Ensure the `Item` belongs to the `Service`.
3.  Verify `service.professional == self.request.user.professional_profile`.
4.  If any check fails, raise `Http404` or `PermissionDenied`.
5.  Store fetched `service` and `item` objects on `self`.

```python
# Conceptual Mixin (for context, not direct documentation inclusion)
# from django.shortcuts import get_object_or_404
# from django.core.exceptions import PermissionDenied
# from .models import Service, Item # Assuming this is in services.views

# class UserOwnsGrandparentServiceViaItemMixin:
#     def dispatch(self, request, *args, **kwargs):
#         service_pk = self.kwargs.get('service_pk')
#         item_pk = self.kwargs.get('item_pk')
#         self.service = get_object_or_404(Service, pk=service_pk)
#         self.item = get_object_or_404(Item, pk=item_pk, service=self.service) # Ensure item belongs to service

#         if not request.user.is_authenticated or #            not hasattr(request.user, 'professional_profile') or #            self.service.professional != request.user.professional_profile:
#             raise PermissionDenied("You do not have permission to manage prices for this item.")
#         return super().dispatch(request, *args, **kwargs)
```

*(The documentation will refer to this principle of authorization.)*

---

#### 1. Create View (`PriceCreateView`)

*   **Purpose**: Allows the authorized professional to add a new price to a specific item.
*   **Class**: `PriceCreateView(LoginRequiredMixin, UserOwnsGrandparentServiceViaItemMixin, CreateView)`
*   **Model**: `models.Price`
*   **Form Class**: `forms.PriceForm`
*   **Template Name**: `services/price_form.html`
*   **Success URL**: Typically redirects to the parent `Item`'s detail page. E.g., `reverse_lazy('services:item_detail', kwargs={'service_pk': self.kwargs['service_pk'], 'pk': self.kwargs['item_pk']})`.
*   **Key Methods/Attributes**:
    *   `dispatch()`: Uses `UserOwnsGrandparentServiceViaItemMixin` (or similar logic) for authorization and to load `self.service` and `self.item`.
    *   `form_valid(self, form)`:
        *   The parent `Item` ( `self.item` from the mixin) is assigned to `form.instance.item`.
        *   `self.object = form.save()`
    *   `get_context_data(self, **kwargs)`: Add parent `service` and `item` to the context for display in the template (e.g., "Adding Price to Item: [Item Title] of Service: [Service Title]").

#### 2. Read Views

##### a. List View (`PriceListView`)

*   **Purpose**: Displays a list of prices, typically for a specific item. This is often integrated into the `item_detail.html` template rather than being a standalone page.
*   **Class**: `PriceListView(LoginRequiredMixin, UserOwnsGrandparentServiceViaItemMixin, ListView)`
*   **Model**: `models.Price`
*   **Template Name**: `services/price_list.html` (or part of `item_detail.html`).
*   **Context Object Name**: `prices`
*   **Key Methods/Attributes**:
    *   `dispatch()`: Authorization check and loading of `self.service` and `self.item`.
    *   `get_queryset(self)`: Overridden to filter prices belonging to the parent `Item` (`self.item.prices.all()`).
    *   `get_context_data(self, **kwargs)`: Add parent `service` and `item` to the context.

##### b. Detail View (`PriceDetailView`)

*   **Purpose**: Displays the details of a single price.
*   **Class**: `PriceDetailView(LoginRequiredMixin, UserOwnsGrandparentServiceViaItemMixin, DetailView)`
*   **Model**: `models.Price`
*   **Template Name**: `services/price_detail.html`
*   **Context Object Name**: `price`
*   **Key Methods/Attributes**:
    *   `dispatch()` or `get_queryset()`: Authorization and context loading.
    *   `get_queryset(self)`: Overridden to filter prices ensuring they belong to `self.item` (parent item, verified by the mixin). This prevents viewing a price by guessing its PK if it's not within an authorized item/service.
    *   `get_context_data(self, **kwargs)`: Add parent `service` and `item` to the context.
    *   **Error Handling**: `Http404` if price, item, or service doesn't exist or if not authorized.

#### 3. Update View (`PriceUpdateView`)

*   **Purpose**: Allows the authorized professional to update a price's details.
*   **Class**: `PriceUpdateView(LoginRequiredMixin, UserOwnsGrandparentServiceViaItemMixin, UpdateView)`
*   **Model**: `models.Price`
*   **Form Class**: `forms.PriceForm`
*   **Template Name**: `services/price_form.html`
*   **Success URL**: E.g., `reverse_lazy('services:price_detail', kwargs={'service_pk': self.kwargs['service_pk'], 'item_pk': self.kwargs['item_pk'], 'pk': self.object.pk})`.
*   **Key Methods/Attributes**:
    *   `dispatch()` or `get_queryset()`: Authorization and context loading.
    *   `get_queryset(self)`: Crucial. Filters prices to only those belonging to `self.item`.
    *   `get_context_data(self, **kwargs)`: Add parent `service` and `item` to the context.
    *   The `item` field on the price is fixed and should not be editable in this view.

#### 4. Delete View (`PriceDeleteView`)

*   **Purpose**: Allows the authorized professional to delete a price.
*   **Class**: `PriceDeleteView(LoginRequiredMixin, UserOwnsGrandparentServiceViaItemMixin, DeleteView)`
*   **Model**: `models.Price`
*   **Template Name**: `services/price_confirm_delete.html`
*   **Success URL**: E.g., `reverse_lazy('services:item_detail', kwargs={'service_pk': self.kwargs['service_pk'], 'pk': self.kwargs['item_pk']})` (redirects to parent item detail page).
*   **Key Methods/Attributes**:
    *   `dispatch()` or `get_queryset()`: Authorization and context loading.
    *   `get_queryset(self)`: Crucial, similar to `PriceUpdateView`.
    *   `get_context_data(self, **kwargs)`: Add parent `service`, `item`, and the `price` to be deleted to the context.

---
### Forms (`PriceForm`)

A `PriceForm` (a `ModelForm`) is used for creating and updating `Price` instances for an `Item`.

*   **File**: `services/forms.py` (This form would be added to the `forms.py` file in the `services` app).
*   **Class**: `PriceForm(forms.ModelForm)`
*   **Purpose**: To handle the creation and updating of `Price` objects, which are always associated with a parent `Item`.
*   **Model**: `models.Price`
*   **Fields**:
    *   The form will include user-editable fields: `amount`, `currency`, `frequency`, `description`, and `is_active`.
    *   The `item` field (ForeignKey to `Item`) will be excluded from the form (e.g., `exclude = ['item']`). The parent `Item` is determined from the URL parameters and assigned in the view (e.g., in `form_valid`).

    ```python
    # Example addition to services/forms.py:
    from django import forms
    from .models import Service, Item, Price # Add Price

    # ... (ServiceForm and ItemForm from previous documentation) ...

    class PriceForm(forms.ModelForm):
        class Meta:
            model = Price
            fields = ['amount', 'currency', 'frequency', 'description', 'is_active']
            # Alternatively, to exclude only 'item' and auto-fields:
            # exclude = ['item', 'created_at', 'updated_at']

        def __init__(self, *args, **kwargs):
            # self.item = kwargs.pop('item', None) # Item instance can be passed by the view
            super().__init__(*args, **kwargs)

            # Optional: Add custom widgets or help texts
            self.fields['amount'].widget.attrs.update({'class': 'form-control', 'step': '0.01'})
            self.fields['currency'].widget.attrs.update({'class': 'form-control'})
            # Frequency field will use a Select widget by default due to 'choices' in the model
            self.fields['frequency'].widget.attrs.update({'class': 'form-select'})
            self.fields['description'].widget.attrs.update({'class': 'form-control'})
            self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})

            # Example: If you wanted to ensure currency is always uppercase
            # self.fields['currency'].widget = forms.TextInput(attrs={'class': 'form-control text-uppercase'})
    ```

*   **Validation**:
    *   Standard `ModelForm` validation applies based on `Price` model field definitions:
        *   `amount`: `DecimalField` validation (e.g., numeric, `max_digits`, `decimal_places`).
        *   `currency`: `CharField(max_length=3)` will be enforced.
        *   `frequency`: `CharField` with `choices` ensures only valid frequency options are selected.
        *   `description`: `CharField(max_length=255, blank=True)` is optional.
        *   `is_active`: `BooleanField` input.
    *   Custom validation can be added if needed. For example, one might want to ensure that for a given `Item`, there aren't multiple active prices with the exact same amount, currency, and frequency (though this might be better enforced with a `UniqueConstraint` on the model if it's a strict rule).

---
### Templates (for Price Model)

These HTML templates support CRUD operations for the `Price` model. Prices are children of `Item` objects, which are themselves children of `Service` objects. Templates will often need context from both parent objects.

#### Common Template Features for Price:

*   **Parent Context**: Templates will usually require `service` and `item` objects in their context for navigation, display, and URL construction.
*   **CSRF Token**: `{% csrf_token %}` is essential in forms.
*   **Vue.js & `safe` filter**: General considerations apply as previously discussed.

#### 1. Price Form (`services/price_form.html`)

*   **Purpose**: Used by `PriceCreateView` and `PriceUpdateView` for `Price` objects.
*   **Context**:
    *   `form`: The `PriceForm` instance.
    *   `service`: The grandparent `Service` instance.
    *   `item`: The parent `Item` instance.
    *   `object` or `price`: The `Price` instance being edited (in UpdateView).
*   **Structure Example**:

    ```html+django
    {% extends "base.html" %}

    {% block title %}
      {% if price %}Edit Price{% else %}Add Price{% endif %} for {{ item.title }}
    {% endblock %}

    {% block content %}
      <h1>
        {% if price %}Edit Price{% else %}Add New Price{% endif %}
         for Item: <a href="{% url 'services:item_detail' service_pk=service.pk pk=item.pk %}">{{ item.title }}</a>
         (Service: <a href="{% url 'services:service_detail' pk=service.pk %}">{{ service.title }}</a>)
      </h1>

      <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">{% if price %}Save Changes{% else %}Add Price{% endif %}</button>
      </form>

      <a href="{% url 'services:item_detail' service_pk=service.pk pk=item.pk %}" class="btn btn-secondary mt-2">
        Cancel (Back to Item Details)
      </a>
    {% endblock %}
    ```

#### 2. Price List (`services/price_list.html` or integrated into `item_detail.html`)

*   **Purpose**: Displays prices for a specific `Item`. This is very often part of `item_detail.html`. If a separate list page is used by `PriceListView`:
*   **Context**:
    *   `prices` (or `object_list`): Queryset of `Price` instances for the specific item.
    *   `item`: The parent `Item` instance.
    *   `service`: The grandparent `Service` instance.
*   **Structure Example (Standalone List - less common)**:

    ```html+django
    {% extends "base.html" %}

    {% block title %}Prices for {{ item.title }}{% endblock %}

    {% block content %}
      <h1>
        Prices for Item: <a href="{% url 'services:item_detail' service_pk=service.pk pk=item.pk %}">{{ item.title }}</a>
      </h1>
      <p>Part of Service: <a href="{% url 'services:service_detail' pk=service.pk %}">{{ service.title }}</a></p>

      <a href="{% url 'services:price_create' service_pk=service.pk item_pk=item.pk %}" class="btn btn-primary mb-3">
        Add New Price for this Item
      </a>

      {% if prices %}
        <div class="list-group">
          {% for price_obj in prices %} {# Renamed to avoid conflict #}
            <div class="list-group-item">
              <h5 class="mb-1">
                <a href="{% url 'services:price_detail' service_pk=service.pk item_pk=item.pk pk=price_obj.pk %}">
                  {{ price_obj.amount }} {{ price_obj.currency }} ({{ price_obj.get_frequency_display }})
                </a>
                {% if not price_obj.is_active %} (Inactive){% endif %}
              </h5>
              <p class="mb-1">{{ price_obj.description|default:"No description." }}</p>
              <a href="{% url 'services:price_edit' service_pk=service.pk item_pk=item.pk pk=price_obj.pk %}" class="btn btn-sm btn-info">Edit</a>
              <a href="{% url 'services:price_delete' service_pk=service.pk item_pk=item.pk pk=price_obj.pk %}" class="btn btn-sm btn-danger">Delete</a>
            </div>
          {% endfor %}
        </div>
      {% else %}
        <p>No prices found for this item.</p>
      {% endif %}

      <a href="{% url 'services:item_detail' service_pk=service.pk pk=item.pk %}" class="btn btn-secondary mt-3">
        Back to Item Details
      </a>
    {% endblock %}
    ```

#### 3. Price Detail (`services/price_detail.html`)

*   **Purpose**: Used by `PriceDetailView` to display a single `Price`'s details.
*   **Context**:
    *   `price`: The `Price` instance.
    *   `item`: The parent `Item` instance.
    *   `service`: The grandparent `Service` instance.
*   **Structure Example**:

    ```html+django
    {% extends "base.html" %}

    {% block title %}Price Details for {{ item.title }}{% endblock %}

    {% block content %}
      <h1>
        Price: {{ price.amount }} {{ price.currency }} ({{ price.get_frequency_display }})
      </h1>
      <p>
        For Item: <a href="{% url 'services:item_detail' service_pk=service.pk pk=item.pk %}">{{ item.title }}</a>
      </p>
      <p>
        Part of Service: <a href="{% url 'services:service_detail' pk=service.pk %}">{{ service.title }}</a>
      </p>

      <p><strong>Description:</strong> {{ price.description|default:"N/A" }}</p>
      <p><strong>Status:</strong> {% if price.is_active %}Active{% else %}Inactive{% endif %}</p>
      <p><strong>Created:</strong> {{ price.created_at|date:"Y-m-d H:i" }}</p>
      <p><strong>Last Updated:</strong> {{ price.updated_at|date:"Y-m-d H:i" }}</p>

      {% if user.professional_profile == service.professional %}
        <a href="{% url 'services:price_edit' service_pk=service.pk item_pk=item.pk pk=price.pk %}" class="btn btn-info">Edit Price</a>
        <a href="{% url 'services:price_delete' service_pk=service.pk item_pk=item.pk pk=price.pk %}" class="btn btn-danger">Delete Price</a>
      {% endif %}
      <a href="{% url 'services:item_detail' service_pk=service.pk pk=item.pk %}" class="btn btn-secondary mt-2">
        Back to Item Details
      </a>
    {% endblock %}
    ```

#### 4. Price Confirm Delete (`services/price_confirm_delete.html`)

*   **Purpose**: Used by `PriceDeleteView` for confirming deletion of a `Price`.
*   **Context**:
    *   `price`: The `Price` instance to be deleted.
    *   `item`: The parent `Item` instance.
    *   `service`: The grandparent `Service` instance.
*   **Structure Example**:

    ```html+django
    {% extends "base.html" %}

    {% block title %}Confirm Delete Price{% endblock %}

    {% block content %}
      <h1>Confirm Delete: {{ price.amount }} {{ price.currency }} ({{ price.get_frequency_display }})</h1>
      <p>
        This price is for item "<a href="{% url 'services:item_detail' service_pk=service.pk pk=item.pk %}">{{ item.title }}</a>"
        in service "<a href="{% url 'services:service_detail' pk=service.pk %}">{{ service.title }}</a>".
      </p>
      <p>Are you sure you want to delete this price?</p>

      <form method="post">
        {% csrf_token %}
        <button type="submit" class="btn btn-danger">Yes, Delete Price</button>
        <a href="{% url 'services:price_detail' service_pk=service.pk item_pk=item.pk pk=price.pk %}" class="btn btn-secondary">
          Cancel
        </a>
      </form>
    {% endblock %}
    ```

---
### URL Patterns (for Price Model)

`Price` objects are intrinsically linked to an `Item`, which is part of a `Service`. Their URL patterns should reflect this hierarchy, making them nested under both service and item routes. This helps pass necessary primary keys (`service_pk`, `item_pk`) to the views.

*   **File**: `services/urls.py` (these patterns would be added to the existing `urlpatterns`)

```python
# Example additions to services/urls.py:
from django.urls import path
from . import views # Assuming views are in services/views.py

# app_name = 'services' # Should already be defined

urlpatterns = [
    # ... (Service CRUD URLs) ...
    # ... (Nested Item CRUD URLs) ...

    # Deeply Nested Price CRUD URLs
    # Example: /services/1/items/3/prices/
    #          /services/1/items/3/prices/new/
    #          /services/1/items/3/prices/5/

    path('services/<int:service_pk>/items/<int:item_pk>/prices/',
         views.PriceListView.as_view(), name='price_list'),
    path('services/<int:service_pk>/items/<int:item_pk>/prices/new/',
         views.PriceCreateView.as_view(), name='price_create'),
    path('services/<int:service_pk>/items/<int:item_pk>/prices/<int:pk>/',
         views.PriceDetailView.as_view(), name='price_detail'),
    path('services/<int:service_pk>/items/<int:item_pk>/prices/<int:pk>/edit/',
         views.PriceUpdateView.as_view(), name='price_edit'),
    path('services/<int:service_pk>/items/<int:item_pk>/prices/<int:pk>/delete/',
         views.PriceDeleteView.as_view(), name='price_delete'),
]
```

**Explanation of Nested URL Patterns for `Price`:**

*   **`path('services/<int:service_pk>/items/<int:item_pk>/prices/', views.PriceListView.as_view(), name='price_list')`**
    *   **URL Example**: `/services/1/items/3/prices/`
    *   **View**: `PriceListView`
    *   **Name**: `services:price_list`
    *   **Purpose**: Displays a list of prices for item `item_pk` within service `service_pk`.
    *   **URL Parameters**: `service_pk`, `item_pk`.

*   **`path('services/<int:service_pk>/items/<int:item_pk>/prices/new/', views.PriceCreateView.as_view(), name='price_create')`**
    *   **URL Example**: `/services/1/items/3/prices/new/`
    *   **View**: `PriceCreateView`
    *   **Name**: `services:price_create`
    *   **Purpose**: Form to create a new price for item `item_pk`.
    *   **URL Parameters**: `service_pk`, `item_pk`.

*   **`path('services/<int:service_pk>/items/<int:item_pk>/prices/<int:pk>/', views.PriceDetailView.as_view(), name='price_detail')`**
    *   **URL Example**: `/services/1/items/3/prices/5/`
    *   **View**: `PriceDetailView`
    *   **Name**: `services:price_detail`
    *   **Purpose**: Details of price `pk` for item `item_pk`.
    *   **URL Parameters**: `service_pk`, `item_pk`, `pk` (for the `Price`).

*   **`path('services/<int:service_pk>/items/<int:item_pk>/prices/<int:pk>/edit/', views.PriceUpdateView.as_view(), name='price_edit')`**
    *   **URL Example**: `/services/1/items/3/prices/5/edit/`
    *   **View**: `PriceUpdateView`
    *   **Name**: `services:price_edit`
    *   **Purpose**: Form to edit price `pk` for item `item_pk`.
    *   **URL Parameters**: `service_pk`, `item_pk`, `pk`.

*   **`path('services/<int:service_pk>/items/<int:item_pk>/prices/<int:pk>/delete/', views.PriceDeleteView.as_view(), name='price_delete')`**
    *   **URL Example**: `/services/1/items/3/prices/5/delete/`
    *   **View**: `PriceDeleteView`
    *   **Name**: `services:price_delete`
    *   **Purpose**: Confirmation and deletion of price `pk` for item `item_pk`.
    *   **URL Parameters**: `service_pk`, `item_pk`, `pk`.

**Suggestions for `Price` URLs:**

*   **Deep Nesting**: This structure is logical for prices, clearly showing their belonging to an item within a service. It also aids views in obtaining necessary context for authorization and data retrieval.
*   **Clarity vs. Length**: While URLs can become long, the clarity gained for these types of hierarchical relationships is often worth it.
*   **Primary Key Types**: Continue using `<int:...>` converters for all primary keys.

---
```markdown
## CRUD for Order Model (`orders.models.Order`)

This section details Class-Based Views (CBVs) for operations on the `Order` model. Managing orders involves distinct workflows for Customers, Professionals (who fulfill order items), and Administrators. Full CRUD in the traditional sense might not apply to all roles for all fields.

### Common Assumptions for Order Views:

*   **Authorization by Role**: Access and actions are heavily dependent on the user's role (Customer, Professional, Admin). Mixins or custom dispatch logic will be essential.
*   **Status Transitions**: Many "updates" to an order are changes in its `status` field.
*   **Order Items**: The `OrderDetailView` is critical for displaying associated `OrderItem` records. Managing `OrderItem`s will have its own set of views, typically nested under an order's URL.

#### Conceptual Authorization Mixins (Examples)

*   `CustomerOwnsOrderMixin`: Ensures a customer can only view/modify their own orders.
*   `ProfessionalManagesOrderMixin`: Ensures a professional can only view/update orders they are associated with via `OrderItem`s. (This can be complex if multiple professionals are on one order).
*   `AdminAccessMixin`: For admin unrestricted access.

*(These are for conceptual illustration; actual implementation details will vary.)*

---

#### 1. Create View (`OrderCreateView`)

*   **Purpose**: Allows a logged-in `Customer` to initiate a new order. This might create an empty order shell to which `OrderItem`s are subsequently added, or it could be part of a more complex checkout process.
*   **Class**: `OrderCreateView(LoginRequiredMixin, CustomerRequiredMixin, CreateView)` (assuming `CustomerRequiredMixin` verifies `request.user.customer_profile` exists).
*   **Model**: `models.Order`
*   **Form Class**: `forms.OrderForm` (likely minimal, e.g., for initial notes or if there's a step before adding items).
*   **Template Name**: `orders/order_form.html`
*   **Success URL**: Typically to a page where items can be added to the order, or to the order detail page. E.g., `reverse_lazy('orders:order_detail', kwargs={'pk': self.object.pk})`.
*   **Key Methods/Attributes**:
    *   `form_valid(self, form)`:
        *   Assign `self.request.user.customer_profile` to `form.instance.customer`.
        *   The `status` will default to `PENDING`.
        *   `total_amount` and `currency` might be set later or based on initial items if the form supports that.
    *   **Note**: Order creation might also be a programmatic step at the end of a "shopping cart" process, rather than a direct form view. For documentation, we assume a simple direct creation view.

#### 2. Read Views

##### a. Order List View (`OrderListView`)

*   **Purpose**: Displays a list of orders. The queryset will vary based on the user role.
*   **Class**: `OrderListView(LoginRequiredMixin, ListView)`
*   **Model**: `models.Order`
*   **Template Name**: `orders/order_list.html`
*   **Context Object Name**: `orders`
*   **Key Methods/Attributes**:
    *   `get_queryset(self)`:
        *   If user is a `Customer`: `Order.objects.filter(customer=self.request.user.customer_profile)`.
        *   If user is a `Professional`: `Order.objects.filter(items__professional=self.request.user.professional_profile).distinct()`.
        *   If user is an `Admin`: `Order.objects.all()`.
        *   This logic requires knowing the user's role (e.g., checking `hasattr(self.request.user, 'customer_profile')` or `hasattr(self.request.user, 'professional_profile')` or `self.request.user.is_staff`).

##### b. Order Detail View (`OrderDetailView`)

*   **Purpose**: Displays the details of a single order, including its items.
*   **Class**: `OrderDetailView(LoginRequiredMixin, DetailView)` (Requires additional authorization mixin like `CustomerOwnsOrderMixin` or `ProfessionalManagesOrderMixin` or `AdminAccessMixin`).
*   **Model**: `models.Order`
*   **Template Name**: `orders/order_detail.html`
*   **Context Object Name**: `order`
*   **Key Methods/Attributes**:
    *   `get_queryset(self)`: Must be overridden to enforce ownership/relevance based on user role, similar to `OrderListView` but for a single object.
    *   `get_context_data(self, **kwargs)`:
        *   Add related `OrderItem`s: `context['order_items'] = self.object.items.all().select_related('professional', 'service', 'item', 'price')`.
        *   The `total_amount` should be displayed. The template might offer a button to trigger `order.calculate_total()` if changes to items are made asynchronously or if it's not guaranteed to be up-to-date.
    *   **Error Handling**: `Http404` if the order doesn't exist or the user is not authorized to view it.

#### 3. Update Views (Primarily Status Changes)

Directly editing most `Order` fields by a customer after creation is uncommon. Updates usually involve status changes by Professionals or Admins, or cancellation by Customers under certain conditions.

##### a. Order Status Update View (`OrderStatusUpdateView`) - Conceptual

*   **Purpose**: Allows an authorized user (Admin, or Professional associated with the order) to change the `status` of an order.
*   **Class**: `OrderStatusUpdateView(LoginRequiredMixin, UpdateView)` (Requires role-specific authorization mixin).
*   **Model**: `models.Order`
*   **Form Class**: `forms.OrderStatusUpdateForm` (a form specifically for the `status` field, possibly with limited choices based on current status and user role).
*   **Template Name**: `orders/order_status_update_form.html`
*   **Success URL**: `reverse_lazy('orders:order_detail', kwargs={'pk': self.object.pk})`.
*   **Key Methods/Attributes**:
    *   `get_queryset(self)`: Enforce ownership/relevance.
    *   `get_form_kwargs(self)` or `get_form(self)`: To limit status choices in the form based on current status and user role (e.g., a Professional can't set it back to 'PENDING' from 'COMPLETED').
    *   `form_valid(self, form)`: Logic to handle side-effects of status changes (e.g., sending notifications).

##### b. Order Cancel View (`OrderCancelView`) - Conceptual

*   **Purpose**: Allows a `Customer` to cancel their own order if it's in a cancellable state (e.g., 'PENDING').
*   **Class**: `OrderCancelView(LoginRequiredMixin, CustomerOwnsOrderMixin, UpdateView)`
*   **Model**: `models.Order`
*   **Fields**: Only `status` (implicitly set to `CANCELLED`). No form needed, or a simple confirmation.
*   **Template Name**: `orders/order_confirm_cancel.html` (Confirmation page).
*   **Success URL**: `reverse_lazy('orders:order_detail', kwargs={'pk': self.object.pk})`.
*   **Key Methods/Attributes**:
    *   `get_queryset(self)`: Ensure customer owns the order and it's in a cancellable state (e.g., `status=Order.StatusChoices.PENDING`).
    *   `form_valid(self, form)` or `post(self, request, *args, **kwargs)`: Set `self.object.status = Order.StatusChoices.CANCELLED` and save.

#### 4. Delete View (`OrderDeleteView`)

*   **General Practice**: Orders are typically not deleted from the system to maintain historical data. Cancellation (setting `status` to `CANCELLED`) is the standard approach.
*   **Documentation Note**: For this documentation, we will state that direct deletion of orders is generally disallowed. If it were to be implemented, it would be highly restricted (e.g., Admin-only, for orders in specific states) and would use a standard `DeleteView` with strong authorization.

---
### Forms (for Order Model)

Forms for the `Order` model cater to its specific lifecycle: initial creation (often minimal) and status updates.

#### 1. Order Creation Form (`OrderForm`) - Conceptual

This form would be used by `OrderCreateView` if customers directly create an order shell before adding items.

*   **File**: `orders/forms.py`
*   **Class**: `OrderForm(forms.ModelForm)`
*   **Purpose**: To handle the initial creation of an `Order` by a `Customer`.
*   **Model**: `models.Order`
*   **Fields**:
    *   This form is often very simple. The `customer` is set from the logged-in user in the view. `order_date` defaults to now. `status` defaults to 'PENDING'. `total_amount` and `currency` are typically determined later by `OrderItem`s or system settings.
    *   It might include fields for customer notes or initial details if applicable to the business logic. For this documentation, we'll assume no extra fields are needed at the point of basic order shell creation.
    *   `fields = []` or `exclude` all fields that are auto-set or set in the view.

    ```python
    # Example orders/forms.py:
    from django import forms
    from .models import Order, OrderItem # Assuming OrderItemForm will be here too

    class OrderForm(forms.ModelForm):
        class Meta:
            model = Order
            fields = [] # No fields for the customer to fill at this stage,
                        # or perhaps a 'notes' field if added to the Order model.
            # Example if a 'customer_notes' field existed on the Order model:
            # fields = ['customer_notes']

        # def __init__(self, *args, **kwargs):
        #     super().__init__(*args, **kwargs)
        #     if 'customer_notes' in self.fields:
        #         self.fields['customer_notes'].widget = forms.Textarea(attrs={'rows': 3})
    ```
*   **Note**: Often, order creation doesn't involve a direct `OrderForm` presented to the user. Instead, an order object is created programmatically (e.g., when a shopping cart is converted to an order). The documentation above describes a scenario where a simple, direct form might be used.

#### 2. Order Status Update Form (`OrderStatusUpdateForm`)

This form is used by views like `OrderStatusUpdateView` to allow authorized users (e.g., Admins, Professionals) to modify an order's status.

*   **File**: `orders/forms.py`
*   **Class**: `OrderStatusUpdateForm(forms.ModelForm)`
*   **Purpose**: To update the `status` of an existing `Order`.
*   **Model**: `models.Order`
*   **Fields**:
    *   Primarily, this form will only include the `status` field.
    *   The choices for the `status` field might be dynamically limited in the form's `__init__` method based on the order's current status and the user's role (e.g., a Professional might only be able to move an order to 'IN_PROGRESS' or 'COMPLETED', not 'CANCELLED').

    ```python
    # Example addition to orders/forms.py:

    class OrderStatusUpdateForm(forms.ModelForm):
        class Meta:
            model = Order
            fields = ['status']

        def __init__(self, *args, **kwargs):
            user = kwargs.pop('user', None) # The view can pass the user
            super().__init__(*args, **kwargs)
            self.fields['status'].widget.attrs.update({'class': 'form-select'})

            # Optional: Dynamic choices based on user role and current status
            # This is complex and depends on business logic. Example concept:
            # instance = kwargs.get('instance')
            # if instance and user:
            #     available_statuses = []
            #     if user.is_staff: # Admin
            #         available_statuses = Order.StatusChoices.choices
            #     elif hasattr(user, 'professional_profile'):
            #         # Professionals might have limited transitions
            #         if instance.status == Order.StatusChoices.CONFIRMED:
            #             available_statuses = [
            #                 (Order.StatusChoices.CONFIRMED, Order.StatusChoices.CONFIRMED.label),
            #                 (Order.StatusChoices.IN_PROGRESS, Order.StatusChoices.IN_PROGRESS.label),
            #             ]
            #         # ... other professional logic ...
            #     # self.fields['status'].choices = available_statuses
            # else: # Default if no instance or user provided (e.g. new unbound form)
            #     self.fields['status'].choices = Order.StatusChoices.choices
    ```

*   **Validation**:
    *   The `status` field will be validated against the `Order.StatusChoices`.
    *   Further custom validation in the form's `clean_status()` method can prevent invalid status transitions if not handled by dynamically setting choices.

---
### Templates (for Order Model)

Templates for the `Order` model support viewing order lists, individual order details (including items), and managing order statuses.

#### 1. Order Form (`orders/order_form.html`) - Minimal Create

*   **Purpose**: Used by `OrderCreateView` if a simple form is used to initiate an order shell.
*   **Context**:
    *   `form`: The `OrderForm` instance (likely minimal).
*   **Structure Example**:

    ```html+django
    {% extends "base.html" %}

    {% block title %}Create New Order{% endblock %}

    {% block content %}
      <h1>Initiate New Order</h1>
      <p>This will create a new order. You can add items in the next step.</p>
      <form method="post">
        {% csrf_token %}
        {{ form.as_p }} {# If form has fields like 'notes', otherwise this might be empty #}
        <button type="submit" class="btn btn-primary">Confirm and Add Items</button>
      </form>
      <a href="{% url 'some_previous_page_or_dashboard' %}" class="btn btn-secondary mt-2">Cancel</a>
    {% endblock %}
    ```

#### 2. Order List (`orders/order_list.html`)

*   **Purpose**: Used by `OrderListView` to display a list of orders relevant to the logged-in user.
*   **Context**:
    *   `orders` (or `object_list`): Queryset of `Order` instances.
    *   User role (implicitly via `request.user`) determines the content of `orders`.
*   **Structure Example**:

    ```html+django
    {% extends "base.html" %}

    {% block title %}My Orders{% if request.user.is_staff %} - Admin View{% endif %}{% endblock %}

    {% block content %}
      <h1>{% if request.user.customer_profile %}My Orders{% elif request.user.professional_profile %}Orders I'm Involved In{% else %}All Orders{% endif %}</h1>

      {% if request.user.customer_profile %}
      <a href="{% url 'orders:order_create' %}" class="btn btn-primary mb-3">Create New Order</a>
      {% endif %}

      {% if orders %}
        <div class="list-group">
          {% for order_obj in orders %} {# Renamed to avoid var name conflict #}
            <a href="{% url 'orders:order_detail' pk=order_obj.pk %}" class="list-group-item list-group-item-action">
              <div class="d-flex w-100 justify-content-between">
                <h5 class="mb-1">Order #{{ order_obj.pk }}</h5>
                <small>Date: {{ order_obj.order_date|date:"Y-m-d" }}</small>
              </div>
              <p class="mb-1">Status: {{ order_obj.get_status_display }}</p>
              {% if request.user.is_staff or request.user.professional_profile %}
                <small>Customer: {{ order_obj.customer.user.username }}</small><br>
              {% endif %}
              <small>Total: {{ order_obj.total_amount|default:"N/A" }} {{ order_obj.currency }}</small>
            </a>
          {% endfor %}
        </div>
      {% else %}
        <p>No orders found.</p>
      {% endif %}
    {% endblock %}
    ```

#### 3. Order Detail (`orders/order_detail.html`)

*   **Purpose**: Used by `OrderDetailView`. This is a crucial template that displays comprehensive details of an order, including its line items (`OrderItem`s).
*   **Context**:
    *   `order`: The `Order` instance.
    *   `order_items`: Queryset of `OrderItem`s related to this order (passed from the view).
*   **Structure Example**:

    ```html+django
    {% extends "base.html" %}

    {% block title %}Order #{{ order.pk }} Details{% endblock %}

    {% block content %}
      <h1>Order #{{ order.pk }}</h1>
      <div class="row mb-3">
        <div class="col-md-6">
          <p><strong>Customer:</strong> {{ order.customer.user.get_full_name|default:order.customer.user.username }}</p>
          <p><strong>Order Date:</strong> {{ order.order_date|date:"Y-m-d H:i" }}</p>
          <p><strong>Status:</strong> <span class="badge bg-info text-dark">{{ order.get_status_display }}</span></p>
        </div>
        <div class="col-md-6 text-md-end">
          <p><strong>Total Amount:</strong> {{ order.total_amount|default:"Pending Calculation" }} {{ order.currency }}</p>
          {# Button to recalculate total could be added if needed #}
          {# {% if order.status == "PENDING" and user.customer_profile == order.customer %} #}
          {# <a href="{% url 'orders:order_cancel' pk=order.pk %}" class="btn btn-warning btn-sm">Cancel Order</a> #}
          {# {% endif %} #}
          {# {% if user.is_staff or user.professional_profile %} #}
          {# <a href="{% url 'orders:order_status_update' pk=order.pk %}" class="btn btn-info btn-sm">Update Status</a> #}
          {# {% endif %} #}
        </div>
      </div>

      <h2>Order Items</h2>
      {% if order_items %}
        <table class="table">
          <thead>
            <tr>
              <th>Item</th>
              <th>Service</th>
              <th>Professional</th>
              <th>Quantity</th>
              <th>Price at Order</th>
              <th>Subtotal</th>
            </tr>
          </thead>
          <tbody>
            {% for item_entry in order_items %}
              <tr>
                <td>{{ item_entry.item.title }}</td>
                <td>{{ item_entry.service.title }}</td>
                <td>{{ item_entry.professional.user.username }}</td>
                <td>{{ item_entry.quantity }}</td>
                <td>{{ item_entry.price_amount_at_order }} {{ item_entry.price_currency_at_order }} ({{ item_entry.price_frequency_at_order }})</td>
                <td>{% oiseaux_calc_subtotal item_entry.quantity item_entry.price_amount_at_order %} {{ item_entry.price_currency_at_order }}</td> {# Assuming a template tag for subtotal #}
              </tr>
            {% endfor %}
          </tbody>
        </table>
        {# Link to add/manage items in the order could go here, e.g. /orders/{{ order.pk }}/items/add/ #}
        {# if order.status == "PENDING" and user.customer_profile == order.customer (or staff) #}
        {#  <a href="{% url 'orders:order_add_item' pk=order.pk %}" class="btn btn-success">Add Item to Order</a> #}
        {# endif #}
      {% else %}
        <p>No items in this order yet.</p>
        {# if order.status == "PENDING" and user.customer_profile == order.customer (or staff) #}
        {#  <a href="{% url 'orders:order_add_item' pk=order.pk %}" class="btn btn-success">Add Item to Order</a> #}
        {# endif #}
      {% endif %}

      <a href="{% url 'orders:order_list' %}" class="btn btn-secondary mt-3">Back to Order List</a>
    {% endblock %}

    {# Example templatetag for subtotal (e.g., orders/templatetags/order_extras.py)
    from django import template
    register = template.Library()

    @register.simple_tag
    def calculate_subtotal(quantity, price_amount):
        return quantity * price_amount
    #}
    ```

#### 4. Order Status Update Form (`orders/order_status_update_form.html`)

*   **Purpose**: Used by `OrderStatusUpdateView` for Admins/Professionals to change an order's status.
*   **Context**:
    *   `form`: The `OrderStatusUpdateForm` instance.
    *   `order`: The `Order` instance being updated.
*   **Structure Example**:

    ```html+django
    {% extends "base.html" %}

    {% block title %}Update Status for Order #{{ order.pk }}{% endblock %}

    {% block content %}
      <h1>Update Status for Order #{{ order.pk }}</h1>
      <p><strong>Current Status:</strong> {{ order.get_status_display }}</p>
      <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">Save Status</button>
      </form>
      <a href="{% url 'orders:order_detail' pk=order.pk %}" class="btn btn-secondary mt-2">Cancel</a>
    {% endblock %}
    ```

#### 5. Order Confirm Cancel (`orders/order_confirm_cancel.html`) - Conceptual

*   **Purpose**: Used by a conceptual `OrderCancelView` for Customers to confirm cancellation.
*   **Context**:
    *   `order`: The `Order` instance to be cancelled.
*   **Structure Example**:

    ```html+django
    {% extends "base.html" %}

    {% block title %}Confirm Cancel Order #{{ order.pk }}{% endblock %}

    {% block content %}
      <h1>Confirm Cancellation for Order #{{ order.pk }}</h1>
      <p>Are you sure you want to cancel this order?</p>
      <p><strong>Status:</strong> {{ order.get_status_display }}</p>
      {# Add more order details if necessary #}
      <form method="post"> {# This form might not actually take input, just confirm action #}
        {% csrf_token %}
        <button type="submit" class="btn btn-danger">Yes, Cancel Order</button>
        <a href="{% url 'orders:order_detail' pk=order.pk %}" class="btn btn-secondary">No, Keep Order</a>
      </form>
    {% endblock %}
    ```

---
### URL Patterns (for Order Model)

URL patterns for the `Order` model should be defined in `orders/urls.py`. They will handle listing orders, viewing order details, and managing order statuses.

*   **File**: `orders/urls.py`

```python
# Example orders/urls.py:
from django.urls import path
from . import views # Assuming views are in orders/views.py

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order_list'),
    path('new/', views.OrderCreateView.as_view(), name='order_create'), # If direct creation is implemented
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/update_status/', views.OrderStatusUpdateView.as_view(), name='order_status_update'), # Conceptual
    path('<int:pk>/cancel/', views.OrderCancelView.as_view(), name='order_cancel'), # Conceptual for customer cancellation

    # Nested URLs for OrderItems will go here, e.g.:
    # path('<int:order_pk>/items/add/', views.OrderItemCreateView.as_view(), name='order_item_add'),
    # path('<int:order_pk>/items/<int:item_pk>/update/', views.OrderItemUpdateView.as_view(), name='order_item_update'),
    # path('<int:order_pk>/items/<int:item_pk>/delete/', views.OrderItemDeleteView.as_view(), name='order_item_delete'),
]
```

**Explanation of URL Patterns for `Order`:**

*   **`path('', views.OrderListView.as_view(), name='order_list')`**
    *   **URL Example**: `/orders/` (assuming the app's URLs are included under `/orders/` in the project)
    *   **View**: `OrderListView`
    *   **Name**: `orders:order_list`
    *   **Purpose**: Displays a list of orders. The content is contextual based on the logged-in user's role (Customer, Professional, Admin).

*   **`path('new/', views.OrderCreateView.as_view(), name='order_create')`**
    *   **URL Example**: `/orders/new/`
    *   **View**: `OrderCreateView`
    *   **Name**: `orders:order_create`
    *   **Purpose**: Displays a form for a `Customer` to initiate a new order. (Note: Order creation might be programmatic in many systems, e.g., from a cart).

*   **`path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail')`**
    *   **URL Example**: `/orders/123/`
    *   **View**: `OrderDetailView`
    *   **Name**: `orders:order_detail`
    *   **Purpose**: Displays details of a specific order, identified by its primary key (`pk`), including its `OrderItem`s.

*   **`path('<int:pk>/update_status/', views.OrderStatusUpdateView.as_view(), name='order_status_update')`** (Conceptual)
    *   **URL Example**: `/orders/123/update_status/`
    *   **View**: `OrderStatusUpdateView` (A view focused on changing the `status` field)
    *   **Name**: `orders:order_status_update`
    *   **Purpose**: Allows authorized users (Admin/Professional) to update the status of an order.

*   **`path('<int:pk>/cancel/', views.OrderCancelView.as_view(), name='order_cancel')`** (Conceptual)
    *   **URL Example**: `/orders/123/cancel/`
    *   **View**: `OrderCancelView` (A view for `Customer` to cancel their order)
    *   **Name**: `orders:order_cancel`
    *   **Purpose**: Allows a customer to cancel an order if it's in a cancellable state. This typically changes the order's status to 'CANCELLED'.

**Integration with Project URLs:**

These app-specific URLs for `orders` would be included in the main project's `urls.py`:

```python
# Example YourPlanner/urls.py:
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('services/', include('services.urls', namespace='services')),
    path('orders/', include('orders.urls', namespace='orders')), # Added orders app
    # ... other app urls ...
]
```

**Suggestions for `Order` URLs:**

*   The base path `/orders/` is standard.
*   Specific actions like `update_status` or `cancel` are clearer as distinct paths rather than overloading a generic `update` view, given the limited scope of changes allowed for orders.
*   URLs for managing `OrderItem`s should be nested under the specific order they belong to (e.g., `/orders/<int:order_pk>/items/...`) as indicated by the commented-out examples. This will be detailed in the `OrderItem` section.

---
```markdown
### CRUD for OrderItem Model (`orders.models.OrderItem`)

This section details Class-Based Views (CBVs) for managing `OrderItem` instances. `OrderItem`s represent the individual line items within an `Order`. Their management is tightly coupled with their parent `Order`.

#### Common Assumptions for OrderItem Views:

*   **Nested URLs**: URLs are nested under a specific `Order`. E.g., `/orders/<int:order_pk>/items/add/`. The `order_pk` is crucial for context and authorization.
*   **Authorization**: All views use `LoginRequiredMixin`. Authorization logic ensures that only users permitted to modify the parent `Order` (e.g., the owning `Customer` if the order is in a 'PENDING' state, or an Admin) can manage its items.
*   **Order State**: Operations like adding, updating, or deleting items are typically only allowed if the parent `Order` is in a modifiable state (e.g., `Order.StatusChoices.PENDING`).

#### Conceptual Authorization Mixin for OrderItems (Example)

A mixin like `UserCanModifyOrderItemsMixin` would be used:
1.  Extract `order_pk` from `self.kwargs`.
2.  Fetch the `Order` object (`self.order`).
3.  Check if the `request.user` (e.g., `Customer` owning the order, or `Admin`) is authorized to modify items for this order, potentially also checking `self.order.status`.
4.  If not authorized, raise `Http404` or `PermissionDenied`.

*(This is for conceptual illustration.)*

---

#### 1. Create View (`OrderItemCreateView`)

*   **Purpose**: Allows an authorized user to add a new item to a specific `Order`.
*   **Class**: `OrderItemCreateView(LoginRequiredMixin, UserCanModifyOrderItemsMixin, CreateView)`
*   **Model**: `models.OrderItem`
*   **Form Class**: `forms.OrderItemForm` (This form will need to handle selection of `price` and `quantity`).
*   **Template Name**: `orders/orderitem_form.html`
*   **Success URL**: Redirects to the parent `Order`'s detail page: `reverse_lazy('orders:order_detail', kwargs={'pk': self.kwargs['order_pk']})`.
*   **Key Methods/Attributes**:
    *   `dispatch()`: Uses `UserCanModifyOrderItemsMixin` (or similar) to load `self.order` and check permissions.
    *   `get_form_kwargs(self)`: May pass `self.order` or available choices for `price` (e.g., prices related to items from professionals the customer has access to) to the form.
    *   `form_valid(self, form)`:
        *   Assign `self.order` to `form.instance.order`.
        *   The `OrderItem.save()` method will then populate `professional`, `service`, `item`, and historical price fields based on the selected `price` FK.
        *   After saving the `OrderItem`, it's crucial to recalculate the parent order's total: `self.order.calculate_total()`.
    *   `get_context_data(self, **kwargs)`: Add `self.order` to the context for display in the template.

#### 2. Read Views (OrderItem List/Detail)

*   **General Note**: `OrderItem`s are almost always listed and viewed as part of their parent `Order`'s detail page (`OrderDetailView`). Standalone list or detail views for `OrderItem`s are rare for end-users but might exist for administrative purposes. This documentation will focus on their management within the order context, assuming they are displayed via `OrderDetailView`. If dedicated views were needed, they would follow similar patterns to other detail/list views with appropriate authorization.

#### 3. Update View (`OrderItemUpdateView`)

*   **Purpose**: Allows an authorized user to update an existing item in an `Order` (typically just the `quantity`).
*   **Class**: `OrderItemUpdateView(LoginRequiredMixin, UserCanModifyOrderItemsMixin, UpdateView)`
*   **Model**: `models.OrderItem`
*   **Form Class**: `forms.OrderItemForm` (The form should likely only allow `quantity` to be edited).
*   **Template Name**: `orders/orderitem_form.html`
*   **Success URL**: Redirects to the parent `Order`'s detail page: `reverse_lazy('orders:order_detail', kwargs={'pk': self.kwargs['order_pk']})`.
*   **Key Methods/Attributes**:
    *   `dispatch()`: Uses `UserCanModifyOrderItemsMixin` to load `self.order` and check permissions.
    *   `get_queryset(self)`: Filters `OrderItem`s to ensure the item being updated belongs to `self.order`.
    *   `form_valid(self, form)`:
        *   After saving the `OrderItem`, recalculate the parent order's total: `self.order.calculate_total()`.
    *   `get_context_data(self, **kwargs)`: Add `self.order` to the context.
    *   **Note**: Changing the `item` or `price` itself is usually not done; instead, the old item is removed and a new one added. The form should reflect this by making those fields read-only or not present for editing.

#### 4. Delete View (`OrderItemDeleteView`)

*   **Purpose**: Allows an authorized user to remove an item from an `Order`.
*   **Class**: `OrderItemDeleteView(LoginRequiredMixin, UserCanModifyOrderItemsMixin, DeleteView)`
*   **Model**: `models.OrderItem`
*   **Template Name**: `orders/orderitem_confirm_delete.html`
*   **Success URL**: Redirects to the parent `Order`'s detail page: `reverse_lazy('orders:order_detail', kwargs={'pk': self.kwargs['order_pk']})`.
*   **Key Methods/Attributes**:
    *   `dispatch()`: Uses `UserCanModifyOrderItemsMixin` to load `self.order` and check permissions.
    *   `get_queryset(self)`: Filters `OrderItem`s to ensure the item being deleted belongs to `self.order`.
    *   `delete(self, request, *args, **kwargs)`:
        *   After calling `super().delete()`, recalculate the parent order's total: `self.order.calculate_total()`.
    *   `get_context_data(self, **kwargs)`: Add `self.order` and the `orderitem` to be deleted to the context.

---
### Forms (for OrderItem Model)

An `OrderItemForm` (a `ModelForm`) is used for adding items to an order and modifying their quantity.

*   **File**: `orders/forms.py` (This form would be added to the `forms.py` file in the `orders` app, alongside `OrderForm` and `OrderStatusUpdateForm`).
*   **Class**: `OrderItemForm(forms.ModelForm)`
*   **Purpose**: To handle the creation of new `OrderItem`s and the updating of existing `OrderItem`s (primarily their quantity) within a parent `Order`.
*   **Model**: `models.OrderItem`
*   **Fields**:

    *   **For Creation**:
        *   `price`: `ModelChoiceField` to select a `services.Price` object. This is the most crucial field as it determines the `item`, `service`, `professional`, and the base price details that will be copied into historical fields by the `OrderItem.save()` method. The queryset for this field should be appropriately filtered (e.g., showing available prices relevant to the customer or context).
        *   `quantity`: `IntegerField` (or `PositiveIntegerField`).
    *   **For Update**:
        *   `quantity`: `IntegerField`.
        *   Other fields (like `price` and thus `item`, `service`, `professional`) are typically not changed after an item is added to an order. If a different item/price is needed, the workflow is usually to remove the existing `OrderItem` and add a new one. The form can be dynamically adjusted in the view or its `__init__` to make `price` read-only or not present for updates.

    *   The `order` field is excluded as it's set by the view from URL context.
    *   Historical price fields (`price_amount_at_order`, `price_currency_at_order`, `price_frequency_at_order`) are excluded as they are populated by the `OrderItem.save()` method.

    ```python
    # Example addition to orders/forms.py:
    from django import forms
    from .models import Order, OrderItem
    from services.models import Price # Need to import Price for ModelChoiceField

    # ... (OrderForm, OrderStatusUpdateForm) ...

    class OrderItemForm(forms.ModelForm):
        # price field will use ModelChoiceField by default.
        # Queryset should be set/filtered in the view or form's __init__.
        price = forms.ModelChoiceField(
            queryset=Price.objects.none(), # Base queryset, to be overridden
            widget=forms.Select(attrs={'class': 'form-select'}),
            help_text="Select the item and its price."
        )

        class Meta:
            model = OrderItem
            fields = ['price', 'quantity']
            # Exclude: 'order', 'professional', 'service', 'item',
            # 'price_amount_at_order', 'price_currency_at_order', 'price_frequency_at_order',
            # 'created_at' (these are set programmatically or by the model's save method)

        def __init__(self, *args, **kwargs):
            # The view should pass 'order_instance' and potentially 'professional_profile'
            # to help filter the available prices.
            order_instance = kwargs.pop('order_instance', None)
            # Example: available_prices_queryset = kwargs.pop('available_prices_queryset', Price.objects.all())
            super().__init__(*args, **kwargs)

            self.fields['quantity'].widget.attrs.update({'class': 'form-control', 'min': '1'})

            # Dynamically set the queryset for the 'price' field
            # This is crucial: The view needs to pass a filtered queryset of Price objects
            # that are actually available/selectable for this order/customer.
            # For example, only prices for items from services the customer can order.
            if 'available_prices_queryset' in self.fields['price'].widget.attrs: # A way to pass from view
                 self.fields['price'].queryset = self.fields['price'].widget.attrs.pop('available_prices_queryset')
            elif Price.objects.all().exists(): # Fallback, but ideally view provides specific queryset
                 self.fields['price'].queryset = Price.objects.filter(is_active=True, item__service__is_active=True)


            if self.instance and self.instance.pk:
                # If updating an existing OrderItem, make 'price' read-only or hide it.
                # The actual item/price shouldn't change, only quantity.
                if 'price' in self.fields:
                    self.fields['price'].disabled = True
                    # Or to remove it from the form: del self.fields['price']
                    # If removed, ensure the view doesn't expect it in POST data for updates.
                    # For simplicity of example, we disable it.
                    # Help text to explain it's not changeable
                    self.fields['price'].help_text = "The item/price cannot be changed once added to the order. To change items, remove this and add a new one."
    ```

*   **Validation**:
    *   `ModelForm` validation for `quantity` (`PositiveIntegerField`).
    *   The `price` field, being a `ModelChoiceField`, ensures a valid `Price` instance is selected.
    *   Custom validation in `clean()` could be added, e.g., to check stock if inventory management were a feature, or to enforce limits on quantity.
*   **Important Note on `price` field queryset**:
    *   The `queryset` for the `price` `ModelChoiceField` **must** be carefully managed. It should be dynamically set in the view (or the form's `__init__` method if the view passes necessary data) to only show relevant, orderable `Price` instances. Displaying all `Price` objects in the database would be incorrect and a potential security/usability issue. The example above provides a conceptual way this might be handled.

---
### Templates (for OrderItem Model)

Templates for `OrderItem` are typically used to add, edit (quantity), or remove items from a parent `Order`. These forms are often integrated into the order detail page or displayed in modals.

#### Common Template Features for OrderItem:

*   **Parent Order Context**: Templates will always need the parent `order` object for context, navigation, and URL construction (e.g., `order.pk`).
*   **CSRF Token**: `{% csrf_token %}` is required in forms.

#### 1. OrderItem Form (`orders/orderitem_form.html`)

*   **Purpose**: Used by `OrderItemCreateView` and `OrderItemUpdateView`. This template can be rendered as a standalone page or included within another template (e.g., `order_detail.html` or a modal).
*   **Context**:
    *   `form`: The `OrderItemForm` instance.
    *   `order`: The parent `Order` instance.
    *   `orderitem` (or `object`): The `OrderItem` instance being edited (available in UpdateView).
*   **Structure Example**:

    ```html+django
    {% comment %}
    This template can be used as a standalone page or included in another template.
    If included, the {% extends %} and block structure might be omitted or adjusted.
    {% endcomment %}
    {% extends "base.html" %} {# Assuming a base template if used as standalone page #}

    {% block title %}
      {% if orderitem %}Edit Item in Order{% else %}Add Item to Order{% endif %} #{{ order.pk }}
    {% endblock %}

    {% block content %}
      <h3>
        {% if orderitem %}
          Edit Item: {{ orderitem.item.title }}
        {% else %}
          Add New Item
        {% endif %}
        for Order #{{ order.pk }}
      </h3>

      <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">
          {% if orderitem %}Save Changes{% else %}Add Item to Order{% endif %}
        </button>
      </form>

      {# Link back to the order detail page #}
      <a href="{% url 'orders:order_detail' pk=order.pk %}" class="btn btn-secondary mt-2">
        Back to Order Details
      </a>
    {% endblock %}
    ```
    *   **Notes**:
        *   The `OrderItemForm`'s `price` field (a `ModelChoiceField`) will render as a select dropdown. The choices in this dropdown must be carefully populated by the view/form's `__init__` method to show only relevant/available prices.
        *   If this form is used for updates, the `price` field might be disabled (as shown in the `OrderItemForm` example) to prevent changing the item itself, allowing only quantity updates.

#### 2. OrderItem Confirm Delete (`orders/orderitem_confirm_delete.html`)

*   **Purpose**: Used by `OrderItemDeleteView` for confirming the removal of an item from an order.
*   **Context**:
    *   `orderitem`: The `OrderItem` instance to be deleted.
    *   `order`: The parent `Order` instance (passed from the view, or accessed via `orderitem.order`).
*   **Structure Example**:

    ```html+django
    {% extends "base.html" %} {# Assuming a base template #}

    {% block title %}Confirm Remove Item from Order{% endblock %}

    {% block content %}
      <h1>Confirm Removal</h1>
      <p>
        Are you sure you want to remove the item
        "<strong>{{ orderitem.quantity }} x {{ orderitem.item.title }}</strong>"
        from Order #{{ orderitem.order.pk }}?
      </p>
      <p>
        (Original Price: {{ orderitem.price_amount_at_order }} {{ orderitem.price_currency_at_order }} each)
      </p>

      <form method="post">
        {% csrf_token %}
        <button type="submit" class="btn btn-danger">Yes, Remove Item</button>
        <a href="{% url 'orders:order_detail' pk=orderitem.order.pk %}" class="btn btn-secondary">
          Cancel
        </a>
      </form>
    {% endblock %}
    ```

---
### URL Patterns (for OrderItem Model)

`OrderItem` instances are managed as part of an `Order`. Their URLs are therefore nested under the specific `Order` they belong to.

*   **File**: `orders/urls.py` (these patterns would be added to or integrated with the existing `urlpatterns` for the `orders` app)

```python
# Example additions to orders/urls.py:
from django.urls import path
from . import views # Assuming views are in orders.views

# app_name = 'orders' # Should already be defined

urlpatterns = [
    # ... (Order CRUD URLs from previous documentation) ...
    # path('', views.OrderListView.as_view(), name='order_list'),
    # path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    # etc.

    # Nested OrderItem CRUD URLs
    # These are accessed in the context of a specific order.
    # Example: /orders/123/items/add/
    #          /orders/123/items/5/edit/
    #          /orders/123/items/5/delete/

    path('<int:order_pk>/items/add/',
         views.OrderItemCreateView.as_view(), name='orderitem_add'), # Changed from order_item_add
    path('<int:order_pk>/items/<int:pk>/edit/', # Changed item_pk to pk for consistency with DetailView convention
         views.OrderItemUpdateView.as_view(), name='orderitem_edit'),
    path('<int:order_pk>/items/<int:pk>/delete/', # Changed item_pk to pk
         views.OrderItemDeleteView.as_view(), name='orderitem_delete'),

    # Note: A separate list view for OrderItems is usually not needed, as they are
    # displayed as part of the OrderDetailView. Similarly, a dedicated OrderItemDetailView
    # is often not required for users, but might be for admins.
    # If needed, it would look like:
    # path('<int:order_pk>/items/<int:pk>/',
    #      views.OrderItemDetailView.as_view(), name='orderitem_detail'),
]
```

**Explanation of Nested URL Patterns for `OrderItem`:**

*   **`path('<int:order_pk>/items/add/', views.OrderItemCreateView.as_view(), name='orderitem_add')`**
    *   **URL Example**: `/orders/123/items/add/`
    *   **View**: `OrderItemCreateView`
    *   **Name**: `orders:orderitem_add`
    *   **Purpose**: Displays a form to add a new item to the order identified by `order_pk`.
    *   **URL Parameters**: `order_pk` (for the parent `Order`).

*   **`path('<int:order_pk>/items/<int:pk>/edit/', views.OrderItemUpdateView.as_view(), name='orderitem_edit')`**
    *   **URL Example**: `/orders/123/items/5/edit/`
    *   **View**: `OrderItemUpdateView`
    *   **Name**: `orders:orderitem_edit`
    *   **Purpose**: Displays a form to edit an existing order item (identified by `pk`) within order `order_pk`. Typically for updating quantity.
    *   **URL Parameters**: `order_pk`, `pk` (for the `OrderItem`).

*   **`path('<int:order_pk>/items/<int:pk>/delete/', views.OrderItemDeleteView.as_view(), name='orderitem_delete')`**
    *   **URL Example**: `/orders/123/items/5/delete/`
    *   **View**: `OrderItemDeleteView`
    *   **Name**: `orders:orderitem_delete`
    *   **Purpose**: Displays a confirmation page and handles the deletion of order item `pk` from order `order_pk`.
    *   **URL Parameters**: `order_pk`, `pk`.

**Suggestions for `OrderItem` URLs:**

*   **Consistent Nesting**: The `orders/<int:order_pk>/items/...` structure clearly defines the relationship and provides necessary context to the views.
*   **PK Naming**: Using `pk` for the `OrderItem`'s primary key in its own URLs (`.../items/<int:pk>/...`) is conventional, even when nested. `order_pk` distinguishes the parent order's key.
*   **Simplicity**: For `OrderItem`s, often only create, update (quantity), and delete actions are needed as separate views/URLs. Listing and detailed viewing are usually part of the parent `Order`'s detail template.

---
```
