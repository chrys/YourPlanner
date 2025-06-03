# Test Cases for Users App

This document outlines test cases for the `users` app based on the requirements specified in `Documentation/REQUIREMENTS.md`.

---
*Each test case will follow the template:*
- **Case ID:** appName_#caseID (e.g., users_REG_001)
- **Title:**
- **Description:**
- **Pre-conditions:**
- **Dependencies:**
- **Steps:**
- **Expected Result:**
- **Post-conditions:**
---

## 1. User Registration

Test cases related to the registration process for both Customer and Professional users.

---
- **Case ID:** users_REG_001
- **Title:** Successful Customer Registration
- **Description:** Verify that a new user can successfully register as a 'Customer'.
- **Pre-conditions:** The user is not already registered (email is unique).
- **Dependencies:** None.
- **Steps:**
    1. Navigate to the registration page.
    2. Enter valid first name, last name, unique email address, and password.
    3. Select 'Customer' as the role.
    4. Submit the registration form.
- **Expected Result:**
    1. User is redirected to the login page (or a success message page).
    2. A new `User` object is created in the database with the provided details.
    3. A new `Customer` profile object, linked to the `User` object, is created.
    4. A success message "Registration successful. You can now log in." is displayed.
- **Post-conditions:** User account and Customer profile are created. User can log in.

---
- **Case ID:** users_REG_002
- **Title:** Successful Professional Registration
- **Description:** Verify that a new user can successfully register as a 'Professional'.
- **Pre-conditions:** The user is not already registered (email is unique).
- **Dependencies:** None.
- **Steps:**
    1. Navigate to the registration page.
    2. Enter valid first name, last name, unique email address, and password.
    3. Select 'Professional' as the role.
    4. Enter a valid 'Title' for the professional.
    5. Submit the registration form.
- **Expected Result:**
    1. User is redirected to the login page (or a success message page).
    2. A new `User` object is created in the database with the provided details.
    3. A new `Professional` profile object, linked to the `User` object, is created with the provided title.
    4. A success message "Registration successful. You can now log in." is displayed.
- **Post-conditions:** User account and Professional profile are created. User can log in.

---
- **Case ID:** users_REG_003
- **Title:** Attempt Registration with Existing Email
- **Description:** Verify that registration fails if the email address is already in use.
- **Pre-conditions:** An existing user account uses the email address intended for registration.
- **Dependencies:** An existing user account.
- **Steps:**
    1. Navigate to the registration page.
    2. Enter valid first name, last name, and password.
    3. Enter an email address that is already registered.
    4. Select either 'Customer' or 'Professional' as the role (and provide a title if Professional).
    5. Submit the registration form.
- **Expected Result:**
    1. User remains on the registration page (or is redirected back to it).
    2. An error message is displayed, indicating "This email is already registered. Please log in instead." (with a link to login).
    3. No new `User`, `Customer`, or `Professional` object is created.
- **Post-conditions:** Database state remains unchanged regarding new users.

---
- **Case ID:** users_REG_004
- **Title:** Attempt Professional Registration without Title
- **Description:** Verify that registration for a 'Professional' fails if the 'Title' field is not provided.
- **Pre-conditions:** The user is not already registered (email is unique).
- **Dependencies:** None.
- **Steps:**
    1. Navigate to the registration page.
    2. Enter valid first name, last name, unique email address, and password.
    3. Select 'Professional' as the role.
    4. Leave the 'Title' field blank.
    5. Submit the registration form.
- **Expected Result:**
    1. User remains on the registration page (or is redirected back to it).
    2. An error message is displayed for the 'Title' field, indicating "Title is required for professionals."
    3. No new `User`, `Customer`, or `Professional` object is created.
- **Post-conditions:** Database state remains unchanged regarding new users.

---
- **Case ID:** users_REG_005
- **Title:** Attempt Registration with Missing Required Fields (e.g., Email)
- **Description:** Verify that registration fails if a required field (e.g., email) is not provided.
- **Pre-conditions:** None.
- **Dependencies:** None.
- **Steps:**
    1. Navigate to the registration page.
    2. Enter valid first name, last name, and password.
    3. Leave the 'Email' field blank.
    4. Select 'Customer' as the role.
    5. Submit the registration form.
- **Expected Result:**
    1. User remains on the registration page (or is redirected back to it).
    2. An error message is displayed for the 'Email' field (e.g., "This field is required.").
    3. No new `User` or `Customer` object is created.
- **Post-conditions:** Database state remains unchanged regarding new users.

## 2. User Profile Management

Test cases related to viewing and managing user profiles. This includes functionalities for both Customers and Professionals, even if some UI elements for direct updates are not yet implemented (model fields can still be indirectly tested via creation or admin manipulation).

---
- **Case ID:** users_PRF_001
- **Title:** Verify Professional Profile Attributes
- **Description:** Ensure a Professional's profile can store and retrieve its attributes. Direct UI for updating all attributes may not exist, but attributes are part of the model.
- **Pre-conditions:** A Professional user account exists (e.g., created via registration USR_REG_002).
- **Dependencies:** User Registration (USR_REG_002).
- **Steps:**
    1. A Professional user is created (e.g., via registration or admin).
    2. The professional's profile is populated with data for fields like `title` (at registration), `specialization`, `bio`, `profile_image`, `contact_hours`, `rating`. (Note: Population of fields other than `title` might currently require admin access or future profile update UI).
    3. Access the professional's profile data (e.g., via `UserProfileView` or admin interface).
- **Expected Result:**
    1. The `Professional` model instance correctly stores the assigned `title`.
    2. Other fields like `specialization`, `bio`, etc., can hold valid data as per model definition, even if specific UI for user-driven updates is pending.
    3. The `UserProfileView` (or other means of access) displays the available profile information.
- **Post-conditions:** Professional profile attributes are verified as storable and retrievable.

---
- **Case ID:** users_PRF_002
- **Title:** Verify Customer Profile Attributes
- **Description:** Ensure a Customer's profile can store and retrieve its attributes. Direct UI for updating all attributes may not exist, but attributes are part of the model.
- **Pre-conditions:** A Customer user account exists (e.g., created via registration USR_REG_001).
- **Dependencies:** User Registration (USR_REG_001).
- **Steps:**
    1. A Customer user is created (e.g., via registration or admin).
    2. The customer's profile is populated with data for fields like `company_name`, `shipping_address`, `billing_address`, `preferred_currency`, `marketing_preferences`. (Note: Population of these fields might currently require admin access or future profile update UI).
    3. Access the customer's profile data (e.g., via `UserProfileView` or admin interface).
- **Expected Result:**
    1. The `Customer` model instance correctly stores data for its defined fields (e.g., `company_name`, `preferred_currency`).
    2. The `UserProfileView` (or other means of access) displays the available profile information.
- **Post-conditions:** Customer profile attributes are verified as storable and retrievable.

---
- **Case ID:** users_PRF_003
- **Title:** Placeholder - Customer Profile Update Functionality
- **Description:** Test customer's ability to update their profile information once implemented. (Requirement: "Customers can update their profile information - Not implemented yet").
- **Pre-conditions:** A logged-in Customer user.
- **Dependencies:** User Registration (USR_REG_001), Login functionality.
- **Steps:**
    1. Navigate to the customer profile update page (once available).
    2. Modify profile fields (e.g., `company_name`, `shipping_address`).
    3. Submit the form.
- **Expected Result:**
    1. Profile information is updated in the database.
    2. A success message is displayed.
    3. Updated information is reflected on the profile view page.
- **Post-conditions:** Customer profile is updated.

---
- **Case ID:** users_PRF_004
- **Title:** Placeholder - Professional Profile Update Functionality
- **Description:** Test professional's ability to update their profile information once implemented. (Requirement: "Professionals can update their profile information - Not implemented yet").
- **Pre-conditions:** A logged-in Professional user.
- **Dependencies:** User Registration (USR_REG_002), Login functionality.
- **Steps:**
    1. Navigate to the professional profile update page (once available).
    2. Modify profile fields (e.g., `specialization`, `bio`, `contact_hours`).
    3. Submit the form.
- **Expected Result:**
    1. Profile information is updated in the database.
    2. A success message is displayed.
    3. Updated information is reflected on the profile view page.
- **Post-conditions:** Professional profile is updated.

## 3. Professional-Customer Linking

Test cases related to the creation, viewing, and management of links between Professionals and Customers.

---
- **Case ID:** users_LINK_001
- **Title:** Successful Linking of Customer to Professional
- **Description:** Verify that a Customer can successfully link to an available Professional. This is typically done via `ProfessionalChoiceForm` in the `UserManagementView`.
- **Pre-conditions:**
    1. A Customer user is registered and logged in.
    2. The Customer is not currently linked to any Professional.
    3. At least one Professional user exists in the system.
- **Dependencies:** User Registration (USR_REG_001, USR_REG_002), Login.
- **Steps:**
    1. Customer navigates to the user management page (which should present `ProfessionalChoiceForm`).
    2. Select an available Professional from the list.
    3. Submit the form.
- **Expected Result:**
    1. A `ProfessionalCustomerLink` object is created in the database, linking the Customer and the selected Professional, with status 'ACTIVE'.
    2. Customer is redirected to their dashboard, now showing the linked Professional's information.
    3. A success message is displayed (e.g., "You are now linked with [Professional Name].").
- **Post-conditions:** Customer is linked to the chosen Professional.

---
- **Case ID:** users_LINK_002
- **Title:** Verify Unique Professional-Customer Link Constraint
- **Description:** Ensure that a Customer cannot be actively linked to the same Professional multiple times. The model has a `unique_professional_customer_link` constraint.
- **Pre-conditions:**
    1. A Customer user is registered.
    2. A Professional user exists.
    3. The Customer is already actively linked to this Professional.
- **Dependencies:** User Registration (USR_REG_001, USR_REG_002), Linking (users_LINK_001).
- **Steps:**
    1. Attempt to create another `ProfessionalCustomerLink` record programmatically or via UI (if possible) between the same Customer and Professional with 'ACTIVE' status. (Note: The UI in `UserManagementView` typically handles this by deleting/inactivating old links before creating a new one, so this test might be more relevant for direct model interaction or testing the view's logic for handling pre-existing links).
- **Expected Result:**
    1. If attempting direct model creation, a database integrity error (or Django `IntegrityError`) should occur due to the unique constraint.
    2. If via UI (like `UserManagementView` or `ChangeProfessionalView`), the existing link should be appropriately handled (e.g., replaced or updated, not duplicated with multiple active links for the same pair). The view should not create a duplicate active link.
- **Post-conditions:** No duplicate active links exist for the same Customer-Professional pair.

---
- **Case ID:** users_LINK_003
- **Title:** Customer Changing Linked Professional
- **Description:** Verify that a Customer can change their linked Professional. (Requirement: "Customers can view and manage their linked professionals - This is implemented in users/views.py in `change_professional(request)`" - assuming `change_professional` refers to `ChangeProfessionalView`).
- **Pre-conditions:**
    1. A Customer user is registered, logged in, and already linked to an initial Professional.
    2. At least one other Professional user exists in the system.
- **Dependencies:** User Registration (USR_REG_001, USR_REG_002), Linking (users_LINK_001), Login.
- **Steps:**
    1. Customer navigates to the 'Change Professional' page (e.g., via a link on their dashboard).
    2. The `ProfessionalChoiceForm` is displayed, potentially pre-filled or showing available professionals.
    3. Select a new Professional from the list.
    4. Submit the form.
- **Expected Result:**
    1. The existing `ProfessionalCustomerLink` for the Customer and old Professional is either deleted or set to 'INACTIVE'.
    2. A new `ProfessionalCustomerLink` object is created for the Customer and the newly selected Professional, with status 'ACTIVE'.
    3. Customer is redirected to their user management/dashboard page, now showing the new linked Professional's information.
    4. A success message is displayed (e.g., "You have successfully changed your professional to [New Professional Name].").
- **Post-conditions:** Customer is linked to the new Professional. The link with the old Professional is no longer active.

---
- **Case ID:** users_LINK_004
- **Title:** Placeholder - Professional Viewing Linked Customers
- **Description:** Test Professional's ability to view and manage their linked customers once implemented. (Requirement: "Professionals can view and manage their linked customers - Not implemented yet").
- **Pre-conditions:** A logged-in Professional user who has one or more Customers linked to them.
- **Dependencies:** User Registration (USR_REG_001, USR_REG_002), Linking (users_LINK_001), Login.
- **Steps:**
    1. Navigate to the professional's customer management page (once available).
- **Expected Result:**
    1. A list of Customers linked to the Professional is displayed.
    2. Details for each linked Customer are visible (e.g., name, contact info, link status).
    3. Functionality to manage links (e.g., view details, potentially deactivate - depending on final implementation) is present.
- **Post-conditions:** Professional can view their linked customers.

## 4. User Views and Templates
---
- **Case ID:** users_VIEW_001
- **Title:** Access User Registration Page (GET)
- **Description:** Verify that the user registration page (`UserRegistrationView`) loads correctly.
- **Pre-conditions:** None (user can be anonymous).
- **Dependencies:** None.
- **Steps:**
    1. Navigate to the registration page URL.
- **Expected Result:**
    1. HTTP status 200 (OK) is returned.
    2. The registration form (`RegistrationForm`) is displayed.
    3. The page title is "Register" (or similar, as set in `get_context_data`).
- **Post-conditions:** Registration page is displayed.

---
- **Case ID:** users_VIEW_002
- **Title:** User Registration View - Successful POST
- **Description:** Verify `UserRegistrationView` successfully processes a valid registration POST request. (This complements USR_REG_001 and USR_REG_002 by focusing on the view's direct response).
- **Pre-conditions:** Email is unique.
- **Dependencies:** None.
- **Steps:**
    1. Navigate to the registration page.
    2. Fill the form with valid data for a new 'Customer' or 'Professional'.
    3. Submit the form.
- **Expected Result:**
    1. User is redirected to the login page (HTTP 302).
    2. A success message ("Registration successful. You can now log in.") is generated (and displayed on the login page).
    3. Relevant `User` and `Customer`/`Professional` objects are created.
- **Post-conditions:** User is registered and redirected.

---
- **Case ID:** users_VIEW_003
- **Title:** User Registration View - POST with Existing Email
- **Description:** Verify `UserRegistrationView` handles POST with an existing email. (This complements USR_REG_003).
- **Pre-conditions:** An existing user has the email being used for registration.
- **Dependencies:** Existing user account.
- **Steps:**
    1. Navigate to the registration page.
    2. Fill the form with an email that already exists.
    3. Submit the form.
- **Expected Result:**
    1. HTTP status 200 (OK) is returned (user stays on/is returned to the registration page).
    2. The registration form is displayed again.
    3. An error message "This email is already registered. Please log in instead." is displayed via the messages framework.
- **Post-conditions:** No new user created. Error message shown.

---
- **Case ID:** users_VIEW_004
- **Title:** User Management View - New Customer (No Professional Link)
- **Description:** Verify `UserManagementView` for a logged-in customer not yet linked to a professional.
- **Pre-conditions:**
    1. A Customer user is registered and logged in.
    2. The Customer is not linked to any Professional.
- **Dependencies:** User Registration (USR_REG_001), Login.
- **Steps:**
    1. Customer navigates to the user management URL.
- **Expected Result:**
    1. HTTP status 200 (OK).
    2. The `customer_choose_professional.html` template is rendered.
    3. The `ProfessionalChoiceForm` is present in the context and displayed.
    4. Page title is "Choose Your Professional" (or similar).
- **Post-conditions:** Customer is presented with the professional selection form.

---
- **Case ID:** users_VIEW_005
- **Title:** User Management View - Customer Linked to Professional
- **Description:** Verify `UserManagementView` for a logged-in customer already linked to a professional.
- **Pre-conditions:**
    1. A Customer user is registered and logged in.
    2. A Professional user exists.
    3. The Customer is actively linked to the Professional (`ProfessionalCustomerLink` exists).
- **Dependencies:** User Registration (USR_REG_001, USR_REG_002), Linking (users_LINK_001), Login.
- **Steps:**
    1. Customer navigates to the user management URL.
- **Expected Result:**
    1. HTTP status 200 (OK).
    2. The `customer_dashboard.html` template is rendered.
    3. Information about the linked professional is displayed.
    4. Page title is "My Dashboard" (or similar).
- **Post-conditions:** Customer dashboard with professional details is shown.

---
- **Case ID:** users_VIEW_006
- **Title:** User Management View - Professional User
- **Description:** Verify `UserManagementView` for a logged-in professional user.
- **Pre-conditions:** A Professional user is registered and logged in.
- **Dependencies:** User Registration (USR_REG_002), Login.
- **Steps:**
    1. Professional user navigates to the user management URL.
- **Expected Result:**
    1. HTTP status 200 (OK).
    2. The `users/management.html` template is rendered (generic management page for non-customers with profiles).
    3. Page title is "User Management" (or similar).
- **Post-conditions:** Professional user sees their generic management page.

---
- **Case ID:** users_VIEW_007
- **Title:** User Management View - Customer Chooses Professional (POST)
- **Description:** Verify `UserManagementView` successfully handles a customer linking to a professional via POST. (This complements users_LINK_001).
- **Pre-conditions:**
    1. A Customer user is registered and logged in, not currently linked.
    2. At least one Professional user exists.
- **Dependencies:** User Registration (USR_REG_001, USR_REG_002), Login.
- **Steps:**
    1. Customer navigates to user management (sees `ProfessionalChoiceForm`).
    2. Selects a professional from the form.
    3. Submits the form.
- **Expected Result:**
    1. User is redirected (HTTP 302) to the user management URL (which should now show the dashboard).
    2. A `ProfessionalCustomerLink` is created.
    3. A success message is displayed.
- **Post-conditions:** Customer is linked, redirected to dashboard.

---
- **Case ID:** users_VIEW_008
- **Title:** User Profile View - Customer
- **Description:** Verify `UserProfileView` correctly displays a customer's profile.
- **Pre-conditions:** A Customer user is registered and logged in.
- **Dependencies:** User Registration (USR_REG_001), Login.
- **Steps:**
    1. Customer navigates to their profile page URL.
- **Expected Result:**
    1. HTTP status 200 (OK).
    2. The `users/profile.html` template is rendered.
    3. Customer-specific profile information (e.g., from `request.user` and `request.user.customer_profile`) is displayed.
    4. Page title is "My Profile" (or similar).
- **Post-conditions:** Customer profile is displayed.

---
- **Case ID:** users_VIEW_009
- **Title:** User Profile View - Professional
- **Description:** Verify `UserProfileView` correctly displays a professional's profile.
- **Pre-conditions:** A Professional user is registered and logged in.
- **Dependencies:** User Registration (USR_REG_002), Login.
- **Steps:**
    1. Professional navigates to their profile page URL.
- **Expected Result:**
    1. HTTP status 200 (OK).
    2. The `users/profile.html` template is rendered.
    3. Professional-specific profile information (e.g., from `request.user` and `request.user.professional_profile`, including title) is displayed.
    4. Page title is "My Profile" (or similar).
- **Post-conditions:** Professional profile is displayed.

---
- **Case ID:** users_VIEW_010
- **Title:** Change Professional View - Access (GET)
- **Description:** Verify a customer can access the `ChangeProfessionalView` page.
- **Pre-conditions:**
    1. A Customer user is registered, logged in, and linked to a Professional.
- **Dependencies:** User Registration (USR_REG_001), Linking (users_LINK_001), Login.
- **Steps:**
    1. Customer navigates to the 'change professional' URL.
- **Expected Result:**
    1. HTTP status 200 (OK).
    2. The `customer_choose_professional.html` template is rendered.
    3. `ProfessionalChoiceForm` is displayed.
    4. Page title is "Change Your Professional" (or similar).
- **Post-conditions:** Page for changing professional is displayed.

---
- **Case ID:** users_VIEW_011
- **Title:** Change Professional View - Successful Change (POST)
- **Description:** Verify a customer can successfully change their linked professional. (This complements users_LINK_003).
- **Pre-conditions:**
    1. A Customer user is registered, logged in, and linked to an initial Professional.
    2. At least one other Professional user exists.
- **Dependencies:** User Registration (USR_REG_001, USR_REG_002), Linking (users_LINK_001), Login.
- **Steps:**
    1. Customer navigates to the 'change professional' page.
    2. Selects a *new* professional from the `ProfessionalChoiceForm`.
    3. Submits the form.
- **Expected Result:**
    1. User is redirected (HTTP 302) to the user management URL (dashboard).
    2. The link to the old professional is deactivated/deleted.
    3. A new `ProfessionalCustomerLink` is created with the new professional.
    4. A success message is displayed.
- **Post-conditions:** Customer is linked to the new professional.

---
- **Case ID:** users_VIEW_012
- **Title:** Login Functionality
- **Description:** Verify that a registered user can successfully log in.
- **Pre-conditions:** A user (Customer or Professional) is registered.
- **Dependencies:** User Registration (USR_REG_001 or USR_REG_002).
- **Steps:**
    1. Navigate to the login page.
    2. Enter valid email and password for the registered user.
    3. Submit the login form.
- **Expected Result:**
    1. User is redirected to the appropriate page after login (e.g., user management/dashboard).
    2. User is authenticated (e.g., `request.user.is_authenticated` is True).
- **Post-conditions:** User is logged in and session is active.

---
- **Case ID:** users_VIEW_013
- **Title:** Logout Functionality
- **Description:** Verify that a logged-in user can successfully log out.
- **Pre-conditions:** A user is logged in.
- **Dependencies:** Login (users_VIEW_012).
- **Steps:**
    1. Navigate to the logout URL (or click a logout button).
- **Expected Result:**
    1. User is redirected to the logged-out page (or homepage).
    2. User is no longer authenticated (e.g., `request.user.is_authenticated` is False).
    3. A "You have been logged out" message might be displayed.
- **Post-conditions:** User is logged out, session is ended.

---
- **Case ID:** users_VIEW_014
- **Title:** Attempt to Access Profile Page When Not Logged In
- **Description:** Verify that an anonymous user is redirected to login when attempting to access the profile page.
- **Pre-conditions:** User is not logged in.
- **Dependencies:** None.
- **Steps:**
    1. Navigate to the user profile page URL.
- **Expected Result:**
    1. User is redirected to the login page (HTTP 302).
    2. The profile page is not displayed.
- **Post-conditions:** Anonymous user is prevented from accessing profile page.

---
- **Case ID:** users_VIEW_015
- **Title:** Attempt to Access Change Professional Page When Not Logged In
- **Description:** Verify that an anonymous user is redirected to login when attempting to access the change professional page.
- **Pre-conditions:** User is not logged in.
- **Dependencies:** None.
- **Steps:**
    1. Navigate to the 'change professional' URL.
- **Expected Result:**
    1. User is redirected to the login page (HTTP 302).
    2. The change professional page is not displayed.
- **Post-conditions:** Anonymous user is prevented from accessing change professional page.

---
- **Case ID:** users_VIEW_016
- **Title:** Attempt to Access Change Professional Page as Customer Not Linked to any Professional
- **Description:** Verify that a customer not linked to any professional cannot access the change professional page directly (they should be guided through initial linking first). Note: `ChangeProfessionalView` uses `CustomerRequiredMixin` which checks for `customer_profile`, not necessarily an *existing* link. The view itself might handle this, or redirect. `UserManagementView` handles the initial linking. This test checks if `ChangeProfessionalView` has any specific handling for this edge case if accessed directly.
- **Pre-conditions:**
    1. A Customer user is registered and logged in.
    2. The Customer is *not* linked to any Professional.
- **Dependencies:** User Registration (USR_REG_001), Login.
- **Steps:**
    1. Customer attempts to navigate directly to the 'change professional' URL.
- **Expected Result:**
    1. Behavior depends on `ChangeProfessionalView`'s robustness. Ideally, redirected to `UserManagementView` to choose a professional first, or displays the form but POST might be problematic. If it shows the form, it's covered by USR_VIEW_010 but this test emphasizes the "no prior link" state.
    2. (Primary expectation) If `ChangeProfessionalView` implicitly requires a current link to "change" from, user might be redirected or shown an error/guidance. If it allows selecting a "first" professional here, that's also an outcome to note.
    3. The `REQUIREMENTS.md` implies `ChangeProfessionalView` is for *managing* an existing link.
- **Post-conditions:** System handles customer with no professional attempting to "change" gracefully.
