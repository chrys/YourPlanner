"""
Main test runner file that imports all test cases.
This file ensures that all tests are discovered and run by Django's test runner.
"""

from .test_registration import UserRegistrationTests
from .test_profile_management import UserProfileManagementTests
from .test_professional_customer_linking import ProfessionalCustomerLinkingTests
from .test_views import UserViewsTests

# The imports above ensure that all test cases are discovered by Django's test runner.
# No additional code is needed here.

