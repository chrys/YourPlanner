from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from users.models import Professional
from services.models import ServiceCategory, Service, Item, Price
from decimal import Decimal
from django.utils import timezone
import datetime

User = get_user_model()

class ServiceCategoryModelTests(TestCase):
    """
    Test cases for the ServiceCategory model.
    
    This test class implements the test cases specified in the documentation
    for the ServiceCategory model. Each test method corresponds to a specific
    test case ID from the documentation.
    """
    
    def test_create_service_category_with_valid_data(self):
        """
        Test Case ID: services_TC_M_SC_001
        Verify that a ServiceCategory instance can be created with all valid fields.
        """
        # Create a ServiceCategory with valid name and description
        category = ServiceCategory(
            name="Test Category",
            description="This is a test category"
        )
        category.save()
        
        # Verify the category was created successfully
        self.assertEqual(ServiceCategory.objects.count(), 1)
        saved_category = ServiceCategory.objects.first()
        self.assertEqual(saved_category.name, "Test Category")
        self.assertEqual(saved_category.description, "This is a test category")
        self.assertEqual(saved_category.slug, "test-category")  # Auto-generated slug
    
    def test_create_service_category_with_missing_name(self):
        """
        Test Case ID: services_TC_M_SC_002
        Verify that creating a ServiceCategory without a name raises a validation error.
        """
        # Test with None
        category = ServiceCategory(name=None, description="Test description")
        with self.assertRaises(ValidationError):
            category.full_clean()  # Django's validation
        
        # Test with empty string
        category = ServiceCategory(name="", description="Test description")
        with self.assertRaises(ValidationError):
            category.full_clean()
    
    def test_service_category_slug_auto_generation(self):
        """
        Test Case ID: services_TC_M_SC_003
        Verify that the slug is correctly auto-generated from the name upon saving if not provided.
        """
        # Create a category with a specific name but no slug
        category = ServiceCategory(name="New Category 123")
        category.save()
        
        # Verify the slug was auto-generated correctly
        self.assertEqual(category.slug, "new-category-123")
    
    def test_service_category_slug_uniqueness(self):
        """
        Test Case ID: services_TC_M_SC_004
        Verify that attempting to save a ServiceCategory with a duplicate slug raises an integrity error.
        """
        # Create first category with a specific slug
        category1 = ServiceCategory(name="Unique Category", slug="unique-slug")
        category1.save()
        
        # Try to create another category with the same slug
        category2 = ServiceCategory(name="Different Name", slug="unique-slug")
        
        # This should raise an IntegrityError due to the unique constraint on slug
        with self.assertRaises(IntegrityError):
            category2.save()
    
    def test_service_category_string_representation(self):
        """
        Test Case ID: services_TC_M_SC_005
        Verify the __str__ method of ServiceCategory returns the category name.
        """
        # Create a category and check its string representation
        category = ServiceCategory(name="Test Category")
        self.assertEqual(str(category), "Test Category")
    
    def test_create_service_category_with_blank_description(self):
        """
        Test Case ID: services_TC_M_SC_006
        Verify that a ServiceCategory instance can be created with a blank description.
        """
        # Test with empty string
        category1 = ServiceCategory(name="Category with Empty Description", description="")
        category1.save()
        self.assertEqual(category1.description, "")
        
        # Test with None
        category2 = ServiceCategory(name="Category with None Description", description=None)
        category2.save()
        self.assertEqual(category2.description, None)


class ServiceModelTests(TestCase):
    """
    Test cases for the Service model.
    
    This test class implements the test cases specified in the documentation
    for the Service model. Each test method corresponds to a specific
    test case ID from the documentation.
    """
    
    def setUp(self):
        """
        Set up test data for Service model tests.
        Creates a user, professional, and service category for testing.
        """
        # Create a user and professional for testing
        self.user = User.objects.create_user(username='testpro', password='password')
        self.professional = Professional.objects.create(
            user=self.user,
            title="Test Professional",
            specialization="Testing",
            bio="Test bio"
        )
        
        # Create a service category
        self.category = ServiceCategory.objects.create(
            name="Test Category",
            description="Test category description"
        )
    
    def test_create_service_with_valid_data(self):
        """
        Test Case ID: services_TC_M_S_001
        Verify that a Service instance can be created with all valid required fields.
        """
        # Create a service with all valid fields
        service = Service(
            professional=self.professional,
            title="Test Service",
            description="This is a test service",
            category=self.category,
            is_active=True,
            featured=False
        )
        service.save()
        
        # Verify the service was created successfully
        self.assertEqual(Service.objects.count(), 1)
        saved_service = Service.objects.first()
        self.assertEqual(saved_service.professional, self.professional)
        self.assertEqual(saved_service.title, "Test Service")
        self.assertEqual(saved_service.description, "This is a test service")
        self.assertEqual(saved_service.category, self.category)
        self.assertTrue(saved_service.is_active)
        self.assertFalse(saved_service.featured)
        self.assertEqual(saved_service.slug, f"test-service-{self.professional.pk}")
    
    def test_create_service_without_professional(self):
        """
        Test Case ID: services_TC_M_S_002
        Verify that creating a Service without a professional raises an error.
        """
        # Try to create a service without a professional
        service = Service(
            professional=None,
            title="Test Service",
            description="This is a test service"
        )
        
        # This should raise an IntegrityError because professional cannot be null
        with self.assertRaises(IntegrityError):
            service.save()
    
    def test_create_service_without_title(self):
        """
        Test Case ID: services_TC_M_S_003
        Verify that the clean method prevents saving a Service without a title.
        """
        # Test with empty string
        service = Service(
            professional=self.professional,
            title="",
            description="This is a test service"
        )
        with self.assertRaises(ValidationError):
            service.clean()
        
        # Test with None
        service = Service(
            professional=self.professional,
            title=None,
            description="This is a test service"
        )
        with self.assertRaises(ValidationError):
            service.clean()
    
    def test_service_slug_auto_generation(self):
        """
        Test Case ID: services_TC_M_S_004
        Verify that the slug is correctly auto-generated from title and professional.pk upon saving if not provided.
        """
        # Create a service without providing a slug
        service = Service(
            professional=self.professional,
            title="My Awesome Service"
        )
        service.save()
        
        # Verify the slug was auto-generated correctly
        expected_slug = f"my-awesome-service-{self.professional.pk}"
        self.assertEqual(service.slug, expected_slug)
    
    def test_service_slug_uniqueness_per_professional(self):
        """
        Test Case ID: services_TC_M_S_005
        Verify that the unique constraint on professional and slug works.
        """
        # Create first service with a specific slug
        service1 = Service(
            professional=self.professional,
            title="First Service",
            slug="my-service-slug"
        )
        service1.save()
        
        # Try to create another service with the same slug for the same professional
        service2 = Service(
            professional=self.professional,
            title="Second Service",
            slug="my-service-slug"
        )
        
        # This should raise an IntegrityError due to the unique constraint
        with self.assertRaises(IntegrityError):
            service2.save()
    
    def test_service_slug_can_be_non_unique_for_different_professionals(self):
        """
        Test Case ID: services_TC_M_S_006
        Verify that two different professionals can have services with the same slug.
        """
        # Create another professional
        user2 = User.objects.create_user(username='anotherpro', password='password')
        professional2 = Professional.objects.create(
            user=user2,
            title="Another Professional",
            specialization="Testing",
            bio="Another bio"
        )
        
        # Create service for first professional
        service1 = Service(
            professional=self.professional,
            title="Service Title",
            slug="common-slug"
        )
        service1.save()
        
        # Create service for second professional with the same slug
        service2 = Service(
            professional=professional2,
            title="Different Service Title",
            slug="common-slug"
        )
        
        # This should not raise an error
        try:
            service2.save()
            success = True
        except IntegrityError:
            success = False
        
        self.assertTrue(success)
        self.assertEqual(service2.slug, "common-slug")
    
    def test_service_clean_method_duplicate_title_same_professional(self):
        """
        Test Case ID: services_TC_M_S_007
        Verify clean() prevents a professional from having two services with the exact same title.
        """
        # Create first service
        service1 = Service(
            professional=self.professional,
            title="Unique Title for P1"
        )
        service1.save()
        
        # Try to create another service with the same title for the same professional
        service2 = Service(
            professional=self.professional,
            title="Unique Title for P1"
        )
        
        # This should raise a ValidationError in the clean method
        with self.assertRaises(ValidationError):
            service2.clean()
    
    def test_service_clean_method_allows_same_title_for_different_professionals(self):
        """
        Test Case ID: services_TC_M_S_008
        Verify clean() allows different professionals to have services with the same title.
        """
        # Create another professional
        user2 = User.objects.create_user(username='anotherpro', password='password')
        professional2 = Professional.objects.create(
            user=user2,
            title="Another Professional",
            specialization="Testing",
            bio="Another bio"
        )
        
        # Create service for first professional
        service1 = Service(
            professional=self.professional,
            title="Common Service Title"
        )
        service1.save()
        
        # Create service for second professional with the same title
        service2 = Service(
            professional=professional2,
            title="Common Service Title"
        )
        
        # This should not raise a ValidationError
        try:
            service2.clean()
            service2.save()
            success = True
        except ValidationError:
            success = False
        
        self.assertTrue(success)
    
    def test_service_string_representation(self):
        """
        Test Case ID: services_TC_M_S_009
        Verify the __str__ method of Service returns the correct format.
        """
        # Create a service and check its string representation
        service = Service(
            professional=self.professional,
            title="Test Service"
        )
        expected_str = f"Test Service (by {self.professional})"
        self.assertEqual(str(service), expected_str)


class ItemModelTests(TestCase):
    """
    Test cases for the Item model.
    
    This test class implements the test cases specified in the documentation
    for the Item model. Each test method corresponds to a specific
    test case ID from the documentation.
    """
    
    def setUp(self):
        """
        Set up test data for Item model tests.
        Creates a user, professional, service category, and service for testing.
        """
        # Create a user and professional for testing
        self.user = User.objects.create_user(username='testpro', password='password')
        self.professional = Professional.objects.create(
            user=self.user,
            title="Test Professional",
            specialization="Testing",
            bio="Test bio"
        )
        
        # Create a service category
        self.category = ServiceCategory.objects.create(
            name="Test Category",
            description="Test category description"
        )
        
        # Create a service
        self.service = Service.objects.create(
            professional=self.professional,
            title="Test Service",
            description="Test service description",
            category=self.category,
            is_active=True
        )
    
    def test_create_item_with_valid_data(self):
        """
        Test Case ID: services_TC_M_I_001
        Verify that an Item instance can be created with all valid required fields.
        """
        # Create an item with all valid fields
        item = Item(
            service=self.service,
            title="Test Item",
            description="This is a test item",
            stock=10,
            position=1
        )
        item.save()
        
        # Verify the item was created successfully
        self.assertEqual(Item.objects.count(), 1)
        saved_item = Item.objects.first()
        self.assertEqual(saved_item.service, self.service)
        self.assertEqual(saved_item.title, "Test Item")
        self.assertEqual(saved_item.description, "This is a test item")
        self.assertEqual(saved_item.stock, 10)
        self.assertEqual(saved_item.position, 1)
        self.assertEqual(saved_item.slug, f"test-item-{self.service.pk}")
    
    def test_create_item_without_service(self):
        """
        Test Case ID: services_TC_M_I_002
        Verify that creating an Item without a service raises an error.
        """
        # Try to create an item without a service
        item = Item(
            service=None,
            title="Test Item",
            description="This is a test item"
        )
        
        # This should raise an IntegrityError because service cannot be null
        with self.assertRaises(IntegrityError):
            item.save()
    
    def test_create_item_without_title(self):
        """
        Test Case ID: services_TC_M_I_003
        Verify that the clean method prevents saving an Item without a title.
        """
        # Test with empty string
        item = Item(
            service=self.service,
            title="",
            description="This is a test item"
        )
        with self.assertRaises(ValidationError):
            item.clean()
        
        # Test with None
        item = Item(
            service=self.service,
            title=None,
            description="This is a test item"
        )
        with self.assertRaises(ValidationError):
            item.clean()
    
    def test_item_slug_auto_generation(self):
        """
        Test Case ID: services_TC_M_I_004
        Verify that the slug is correctly auto-generated from title and service.pk upon saving if not provided.
        """
        # Create an item without providing a slug
        item = Item(
            service=self.service,
            title="My Awesome Item"
        )
        item.save()
        
        # Verify the slug was auto-generated correctly
        expected_slug = f"my-awesome-item-{self.service.pk}"
        self.assertEqual(item.slug, expected_slug)
    
    def test_item_slug_uniqueness_per_service(self):
        """
        Test Case ID: services_TC_M_I_005
        Verify that the unique constraint on service and slug works.
        """
        # Create first item with a specific slug
        item1 = Item(
            service=self.service,
            title="First Item",
            slug="my-item-slug"
        )
        item1.save()
        
        # Try to create another item with the same slug for the same service
        item2 = Item(
            service=self.service,
            title="Second Item",
            slug="my-item-slug"
        )
        
        # This should raise an IntegrityError due to the unique constraint
        with self.assertRaises(IntegrityError):
            item2.save()
    
    def test_item_slug_can_be_non_unique_for_different_services(self):
        """
        Test Case ID: services_TC_M_I_006
        Verify that two different services can have items with the same slug.
        """
        # Create another service
        service2 = Service.objects.create(
            professional=self.professional,
            title="Another Service",
            description="Another service description"
        )
        
        # Create item for first service
        item1 = Item(
            service=self.service,
            title="Item Title",
            slug="common-slug"
        )
        item1.save()
        
        # Create item for second service with the same slug
        item2 = Item(
            service=service2,
            title="Different Item Title",
            slug="common-slug"
        )
        
        # This should not raise an error
        try:
            item2.save()
            success = True
        except IntegrityError:
            success = False
        
        self.assertTrue(success)
        self.assertEqual(item2.slug, "common-slug")
    
    def test_item_string_representation(self):
        """
        Test Case ID: services_TC_M_I_007
        Verify the __str__ method of Item returns the correct format.
        """
        # Create an item and check its string representation
        item = Item(
            service=self.service,
            title="Test Item"
        )
        expected_str = f"Test Item (in Service: {self.service.title})"
        self.assertEqual(str(item), expected_str)
    
    def test_item_is_available_method(self):
        """
        Test Case ID: services_TC_M_I_008
        Verify the is_available method returns the correct availability status.
        """
        # Test with positive stock
        item1 = Item(
            service=self.service,
            title="In Stock Item",
            stock=5
        )
        self.assertTrue(item1.is_available())
        
        # Test with zero stock (unlimited)
        item2 = Item(
            service=self.service,
            title="Unlimited Item",
            stock=0
        )
        self.assertTrue(item2.is_available())


class PriceModelTests(TestCase):
    """
    Test cases for the Price model.
    
    This test class implements the test cases specified in the documentation
    for the Price model. Each test method corresponds to a specific
    test case ID from the documentation.
    """
    
    def setUp(self):
        """
        Set up test data for Price model tests.
        Creates a user, professional, service, and item for testing.
        """
        # Create a user and professional for testing
        self.user = User.objects.create_user(username='testpro', password='password')
        self.professional = Professional.objects.create(
            user=self.user,
            title="Test Professional",
            specialization="Testing",
            bio="Test bio"
        )
        
        # Create a service
        self.service = Service.objects.create(
            professional=self.professional,
            title="Test Service",
            description="Test service description",
            is_active=True
        )
        
        # Create an item
        self.item = Item.objects.create(
            service=self.service,
            title="Test Item",
            description="Test item description",
            stock=10
        )
    
    def test_create_price_with_valid_data(self):
        """
        Test Case ID: services_TC_M_P_001
        Verify that a Price instance can be created with all valid required fields.
        """
        # Create a price with all valid fields
        price = Price(
            item=self.item,
            amount=Decimal('99.99'),
            currency='USD',
            frequency=Price.FrequencyChoices.MONTHLY,
            description="Standard price",
            is_active=True
        )
        price.save()
        
        # Verify the price was created successfully
        self.assertEqual(Price.objects.count(), 1)
        saved_price = Price.objects.first()
        self.assertEqual(saved_price.item, self.item)
        self.assertEqual(saved_price.amount, Decimal('99.99'))
        self.assertEqual(saved_price.currency, 'USD')
        self.assertEqual(saved_price.frequency, Price.FrequencyChoices.MONTHLY)
        self.assertEqual(saved_price.description, "Standard price")
        self.assertTrue(saved_price.is_active)
    
    def test_create_price_without_item(self):
        """
        Test Case ID: services_TC_M_P_002
        Verify that creating a Price without an item raises an error.
        """
        # Try to create a price without an item
        price = Price(
            item=None,
            amount=Decimal('99.99'),
            currency='USD',
            frequency=Price.FrequencyChoices.MONTHLY
        )
        
        # This should raise an IntegrityError because item cannot be null
        with self.assertRaises(IntegrityError):
            price.save()
    
    def test_price_clean_method_negative_amount(self):
        """
        Test Case ID: services_TC_M_P_003
        Verify that the clean method prevents saving a Price with a negative amount.
        """
        # Try to create a price with a negative amount
        price = Price(
            item=self.item,
            amount=Decimal('-10.00'),
            currency='USD',
            frequency=Price.FrequencyChoices.ONE_TIME
        )
        
        # This should raise a ValidationError in the clean method
        with self.assertRaises(ValidationError):
            price.clean()
    
    def test_price_clean_method_invalid_date_range(self):
        """
        Test Case ID: services_TC_M_P_004
        Verify that the clean method prevents saving a Price with an end date before the start date.
        """
        # Set up dates for testing
        now = timezone.now()
        tomorrow = now + datetime.timedelta(days=1)
        yesterday = now - datetime.timedelta(days=1)
        
        # Try to create a price with an invalid date range
        price = Price(
            item=self.item,
            amount=Decimal('99.99'),
            currency='USD',
            frequency=Price.FrequencyChoices.MONTHLY,
            valid_from=tomorrow,  # Future date
            valid_until=yesterday  # Past date (before valid_from)
        )
        
        # This should raise a ValidationError in the clean method
        with self.assertRaises(ValidationError):
            price.clean()
    
    def test_price_clean_method_invalid_quantity_range(self):
        """
        Test Case ID: services_TC_M_P_005
        Verify that the clean method prevents saving a Price with min_quantity > max_quantity.
        """
        # Try to create a price with an invalid quantity range
        price = Price(
            item=self.item,
            amount=Decimal('99.99'),
            currency='USD',
            frequency=Price.FrequencyChoices.MONTHLY,
            min_quantity=10,
            max_quantity=5  # Less than min_quantity
        )
        
        # This should raise a ValidationError in the clean method
        with self.assertRaises(ValidationError):
            price.clean()
    
    def test_price_clean_method_min_quantity_less_than_one(self):
        """
        Test Case ID: services_TC_M_P_006
        Verify that the clean method prevents saving a Price with min_quantity < 1.
        """
        # Try to create a price with min_quantity less than 1
        price = Price(
            item=self.item,
            amount=Decimal('99.99'),
            currency='USD',
            frequency=Price.FrequencyChoices.MONTHLY,
            min_quantity=0  # Less than 1
        )
        
        # This should raise a ValidationError in the clean method
        with self.assertRaises(ValidationError):
            price.clean()
    
    def test_price_is_valid_now_with_active_price(self):
        """
        Test Case ID: services_TC_M_P_007
        Verify that is_valid_now() returns True for an active price with no date constraints.
        """
        # Create an active price with no date constraints
        price = Price(
            item=self.item,
            amount=Decimal('99.99'),
            currency='USD',
            frequency=Price.FrequencyChoices.MONTHLY,
            is_active=True,
            valid_from=None,
            valid_until=None
        )
        price.save()
        
        # Verify is_valid_now() returns True
        self.assertTrue(price.is_valid_now())
    
    def test_price_is_valid_now_with_inactive_price(self):
        """
        Test Case ID: services_TC_M_P_008
        Verify that is_valid_now() returns False for an inactive price.
        """
        # Create an inactive price
        price = Price(
            item=self.item,
            amount=Decimal('99.99'),
            currency='USD',
            frequency=Price.FrequencyChoices.MONTHLY,
            is_active=False
        )
        price.save()
        
        # Verify is_valid_now() returns False
        self.assertFalse(price.is_valid_now())
    
    def test_price_is_valid_now_with_future_start_date(self):
        """
        Test Case ID: services_TC_M_P_009
        Verify that is_valid_now() returns False for a price with a future start date.
        """
        # Set up a future date
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        
        # Create a price with a future start date
        price = Price(
            item=self.item,
            amount=Decimal('99.99'),
            currency='USD',
            frequency=Price.FrequencyChoices.MONTHLY,
            is_active=True,
            valid_from=tomorrow
        )
        price.save()
        
        # Verify is_valid_now() returns False
        self.assertFalse(price.is_valid_now())
    
    def test_price_is_valid_now_with_past_end_date(self):
        """
        Test Case ID: services_TC_M_P_010
        Verify that is_valid_now() returns False for a price with a past end date.
        """
        # Set up a past date
        yesterday = timezone.now() - datetime.timedelta(days=1)
        
        # Create a price with a past end date
        price = Price(
            item=self.item,
            amount=Decimal('99.99'),
            currency='USD',
            frequency=Price.FrequencyChoices.MONTHLY,
            is_active=True,
            valid_until=yesterday
        )
        price.save()
        
        # Verify is_valid_now() returns False
        self.assertFalse(price.is_valid_now())
    
    def test_price_get_discounted_amount_with_discount(self):
        """
        Test Case ID: services_TC_M_P_011
        Verify that get_discounted_amount() correctly calculates the discounted price.
        """
        # Create a price with a discount
        price = Price(
            item=self.item,
            amount=Decimal('100.00'),
            currency='USD',
            frequency=Price.FrequencyChoices.MONTHLY,
            discount_percentage=Decimal('20.00')  # 20% discount
        )
        
        # Calculate the expected discounted amount
        expected_discounted_amount = Decimal('80.00')  # 100 - (100 * 20/100)
        
        # Verify get_discounted_amount() returns the correct value
        self.assertEqual(price.get_discounted_amount(), expected_discounted_amount)
    
    def test_price_get_discounted_amount_without_discount(self):
        """
        Test Case ID: services_TC_M_P_012
        Verify that get_discounted_amount() returns the original amount when no discount is applied.
        """
        # Create a price with no discount
        price = Price(
            item=self.item,
            amount=Decimal('100.00'),
            currency='USD',
            frequency=Price.FrequencyChoices.MONTHLY,
            discount_percentage=Decimal('0.00')  # No discount
        )
        
        # Verify get_discounted_amount() returns the original amount
        self.assertEqual(price.get_discounted_amount(), Decimal('100.00'))
    
    def test_price_string_representation(self):
        """
        Test Case ID: services_TC_M_P_013
        Verify the __str__ method of Price returns the correct format.
        """
        # Create a price and check its string representation
        price = Price(
            item=self.item,
            amount=Decimal('99.99'),
            currency='USD',
            frequency=Price.FrequencyChoices.MONTHLY
        )
        
        # Verify the string representation is correct
        expected_str = f"99.99 USD (MONTHLY) for {self.item.title}"
        self.assertEqual(str(price), expected_str)
    
    def test_price_active_manager(self):
        """
        Test Case ID: services_TC_M_P_014
        Verify the active manager returns only prices where is_active=True.
        """
        # Create active price
        active_price = Price.objects.create(
            item=self.item,
            amount=Decimal('99.99'),
            currency='USD',
            frequency=Price.FrequencyChoices.MONTHLY,
            is_active=True
        )
        
        # Create inactive price
        inactive_price = Price.objects.create(
            item=self.item,
            amount=Decimal('79.99'),
            currency='USD',
            frequency=Price.FrequencyChoices.MONTHLY,
            is_active=False
        )
        
        # Get all prices using the default manager
        all_prices = Price.objects.all()
        self.assertEqual(all_prices.count(), 2)
        
        # Get active prices using the active manager
        active_prices = Price.active.all()
        self.assertEqual(active_prices.count(), 1)
        self.assertEqual(active_prices.first(), active_price)

