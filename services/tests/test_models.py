# Test cases for models in the 'services' app.

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils.text import slugify # For verifying slug generation
from decimal import Decimal # For Price model tests

# Import models from the 'services' app
from ..models import ServiceCategory, Service, Item, Price

# Import models from other apps if needed for relationships (e.g., users.Professional)
from users.models import Professional, User # Assuming User is needed to create Professional

# Further imports might be added as specific tests are written.

class ServiceCategoryModelTests(TestCase):
    """
    Test cases for the ServiceCategory model.
    Corresponds to test cases starting with services_TC_M_SC_
    """

    def test_services_TC_M_SC_001_create_service_category_valid(self):
        """
        Test Case ID: services_TC_M_SC_001
        Title: Create ServiceCategory with valid data
        Description: Verify that a ServiceCategory instance can be created with all valid fields.
                     The slug field should be auto-generated based on the name.
        Expected Result:
        - The ServiceCategory instance is created successfully.
        - The slug field is auto-generated.
        - The instance is saved to the database.
        """
        category_name = "Digital Marketing"
        category_description = "Services related to online marketing and advertising."
        category = ServiceCategory.objects.create(
            name=category_name,
            description=category_description
        )
        self.assertEqual(category.name, category_name)
        self.assertEqual(category.description, category_description)
        self.assertEqual(category.slug, slugify(category_name))
        self.assertIsNotNone(category.pk) # Check it was saved
        # print(f"Test services_TC_M_SC_001 PASSED. Slug generated: {category.slug}")

    def test_services_TC_M_SC_002_create_service_category_missing_name(self):
        """
        Test Case ID: services_TC_M_SC_002
        Title: Create ServiceCategory with missing name (invalid)
        Description: Verify that creating a ServiceCategory without a name raises an error.
                     Since 'name' is a CharField without null=True or blank=True,
                     this should raise an IntegrityError at the database level if not caught by full_clean().
        Expected Result:
        - An IntegrityError (or ValidationError if full_clean() is called before save) is raised.
        - The instance is not saved to the database.
        """
        # Test with name=None directly during creation (should hit IntegrityError if DB constraints are strict)
        # or ValidationError if .save() calls full_clean() implicitly or model's save overrides it.
        # Given standard Django behavior, direct create without full_clean might lead to IntegrityError.
        with self.assertRaises((IntegrityError, ValidationError)):
            ServiceCategory.objects.create(name=None, description="Test description for None name")

        # Test with name="" (empty string) by first instantiating then calling full_clean()
        # This should reliably raise ValidationError because `blank=False` (default) for CharField.
        category_invalid_empty_name = ServiceCategory(name="", description="Test description for empty name")
        with self.assertRaises(ValidationError) as context:
            category_invalid_empty_name.full_clean()

        self.assertIn('name', context.exception.message_dict) # Check that 'name' field caused the error

        # Ensure no category with problematic names was actually created
        self.assertFalse(ServiceCategory.objects.filter(name="").exists())
        # Querying for name=None might depend on DB (e.g. Oracle treats empty string as NULL)
        # but Django's ORM usually handles this. Given `name` cannot be null, this should be false.
        if ServiceCategory.objects.filter(name=None).exists():
             print("Warning: A ServiceCategory with name=None was found in the DB.") # Should not happen
        self.assertFalse(ServiceCategory.objects.filter(name__isnull=True).exists())
        # print(f"Test services_TC_M_SC_002 PASSED. Error raised for missing/empty name.")

class ServiceModelTests(TestCase):
    """
    Test cases for the Service model.
    Corresponds to test cases starting with services_TC_M_S_
    """
    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        cls.user = User.objects.create_user(
            username='pro_user_service_tests',
            email='pro_user_service_tests@example.com',
            password='testpassword'
        )
        cls.professional = Professional.objects.create(
            user=cls.user,
            title="Dr. Service Provider",
            specialization="General Services",
            bio="Experienced service provider."
        )
        cls.category = ServiceCategory.objects.create(
            name="Test Category for Service",
            description="A test category."
        )

    def test_services_TC_M_S_001_create_service_valid(self):
        """
        Test Case ID: services_TC_M_S_001
        Title: Create Service with valid data
        """
        service_title = "Comprehensive Web Development"
        service = Service.objects.create(
            professional=self.professional,
            title=service_title,
            description="Full stack web development services.",
            category=self.category,
            is_active=True,
            featured=True
        )
        self.assertEqual(service.professional, self.professional)
        self.assertEqual(service.title, service_title)
        self.assertEqual(service.description, "Full stack web development services.")
        self.assertEqual(service.category, self.category)
        self.assertTrue(service.is_active)
        self.assertTrue(service.featured)
        expected_slug = slugify(f"{service_title}-{self.professional.pk}")
        self.assertEqual(service.slug, expected_slug)
        self.assertIsNotNone(service.pk)

    def test_services_TC_M_S_002_create_service_no_professional(self):
        """
        Test Case ID: services_TC_M_S_002
        Title: Create Service without a professional (invalid)
        """
        with self.assertRaises((IntegrityError, ValueError)):
            Service.objects.create(
                professional=None,
                title="Service without Pro",
                category=self.category
            )

    def test_services_TC_M_S_003_create_service_no_title_clean(self):
        """
        Test Case ID: services_TC_M_S_003
        Title: Create Service without a title (invalid via clean method)
        """
        service_no_title = Service(
            professional=self.professional,
            title="",
            category=self.category
        )
        with self.assertRaises(ValidationError) as context:
            service_no_title.full_clean()
        self.assertIn('title', context.exception.message_dict)
        self.assertEqual(context.exception.message_dict['title'][0], 'Service title cannot be empty')

    def test_services_TC_M_S_009_service_string_representation(self):
        """
        Test Case ID: services_TC_M_S_009
        Title: Service string representation
        """
        service_title = "My Unique Service For Str Test"
        service = Service.objects.create(
            professional=self.professional,
            title=service_title,
            category=self.category
        )
        expected_str = f"{service_title} (by {self.professional})"
        self.assertEqual(str(service), expected_str)

    def test_services_TC_M_S_010_service_active_manager(self):
        """
        Test Case ID: services_TC_M_S_010
        Title: Service active manager
        """
        # Create a new professional for this specific test to avoid interference from other tests' services
        user_active_mgr = User.objects.create_user(username='pro_active_mgr', password='password')
        pro_active_mgr = Professional.objects.create(user=user_active_mgr, title="Active Manager Pro")

        Service.objects.create(professional=pro_active_mgr, title="Active Service Test", is_active=True)
        Service.objects.create(professional=pro_active_mgr, title="Inactive Service Test", is_active=False)

        active_services_count = Service.active.filter(professional=pro_active_mgr).count()
        self.assertEqual(active_services_count, 1)

        active_service_instance = Service.active.get(professional=pro_active_mgr, title="Active Service Test")
        self.assertTrue(active_service_instance.is_active)

        # Ensure the manager only returns active services
        for service in Service.active.filter(professional=pro_active_mgr):
            self.assertTrue(service.is_active)

        # Verify against all objects for this professional
        total_services_for_pro = Service.objects.filter(professional=pro_active_mgr).count()
        self.assertEqual(total_services_for_pro, 2)


    def test_services_TC_M_S_011_create_service_blank_description(self):
        """
        Test Case ID: services_TC_M_S_011
        Title: Create Service with blank description
        """
        service_title = "Service With Blank Description Test"
        service = Service.objects.create(
            professional=self.professional,
            title=service_title,
            description="",
            category=self.category
        )
        self.assertEqual(service.title, service_title)
        self.assertEqual(service.description, "")
        self.assertIsNotNone(service.pk)

    def test_services_TC_M_S_013_service_associated_with_category(self):
        """
        Test Case ID: services_TC_M_S_013
        Title: Service associated with a Category
        """
        service_title = "Categorized Service Test"
        # Use a fresh category to ensure no interference if tests run in parallel or category is modified elsewhere.
        specific_category = ServiceCategory.objects.create(name="Specific Category for S013")
        service = Service.objects.create(
            professional=self.professional,
            title=service_title,
            category=specific_category
        )
        self.assertEqual(service.category, specific_category)
        self.assertIn(service, specific_category.services.all())

    def test_services_TC_M_S_014_service_with_null_category(self):
        """
        Test Case ID: services_TC_M_S_014
        Title: Service with null Category
        """
        service_title = "Uncategorized Service Test"
        service = Service.objects.create(
            professional=self.professional,
            title=service_title,
            category=None
        )
        self.assertIsNone(service.category)
        self.assertIsNotNone(service.pk)

class ItemModelTests(TestCase):
    """
    Test cases for the Item model.
    Corresponds to test cases starting with services_TC_M_I_
    """
    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        # User for Professional
        cls.user = User.objects.create_user(
            username='pro_user_item_tests',
            email='pro_user_item_tests@example.com',
            password='testpassword'
        )
        # Professional
        cls.professional = Professional.objects.create(
            user=cls.user,
            title="Mr. Item Creator",
            specialization="Itemization"
        )
        # Service
        cls.service = Service.objects.create(
            professional=cls.professional,
            title="Parent Service for Items",
            description="A service that will contain items."
        )

    def test_services_TC_M_I_001_create_item_valid(self):
        """
        Test Case ID: services_TC_M_I_001
        Title: Create Item with valid data
        """
        item_title = "Standard Item Alpha"
        item = Item.objects.create(
            service=self.service,
            title=item_title,
            description="A standard item for testing.",
            sku="ITEM-ALPHA-001",
            stock=10,
            position=1,
            is_active=True
        )
        self.assertEqual(item.service, self.service)
        self.assertEqual(item.title, item_title)
        self.assertEqual(item.description, "A standard item for testing.")
        self.assertEqual(item.sku, "ITEM-ALPHA-001")
        self.assertEqual(item.stock, 10)
        self.assertEqual(item.position, 1)
        self.assertTrue(item.is_active)
        # Check slug generation: {self.title}-{self.service.pk}
        expected_slug = slugify(f"{item_title}-{self.service.pk}")
        self.assertEqual(item.slug, expected_slug)
        self.assertIsNotNone(item.pk)

    def test_services_TC_M_I_002_create_item_no_service(self):
        """
        Test Case ID: services_TC_M_I_002
        Title: Create Item without a service (invalid)
        Description: Service is a ForeignKey without null=True.
        """
        with self.assertRaises((IntegrityError, ValueError)): # ValueError if caught by Django before DB
            Item.objects.create(
                service=None,
                title="Item without Service"
            )

    def test_services_TC_M_I_003_create_item_no_title_clean(self):
        """
        Test Case ID: services_TC_M_I_003
        Title: Create Item without a title (invalid via clean method)
        """
        item_no_title = Item(
            service=self.service,
            title="" # Empty title
        )
        with self.assertRaises(ValidationError) as context:
            item_no_title.full_clean()
        self.assertIn('title', context.exception.message_dict)
        self.assertEqual(context.exception.message_dict['title'][0], 'Item title cannot be empty')

    def test_services_TC_M_I_007_item_string_representation(self):
        """
        Test Case ID: services_TC_M_I_007
        Title: Item string representation
        """
        item_title = "Item For Str Test"
        item = Item.objects.create(
            service=self.service,
            title=item_title
        )
        # Expected: "{self.title} (in Service: {self.service.title})"
        expected_str = f"{item_title} (in Service: {self.service.title})"
        self.assertEqual(str(item), expected_str)

    def test_services_TC_M_I_012_item_blank_description_sku(self):
        """
        Test Case ID: services_TC_M_I_012
        Title: Item with blank description and SKU
        Description: 'description' and 'sku' fields allow blank=True.
        """
        item_title = "Item Blank Fields Test"
        item = Item.objects.create(
            service=self.service,
            title=item_title,
            description="", # Blank description
            sku=""         # Blank SKU
        )
        self.assertEqual(item.title, item_title)
        self.assertEqual(item.description, "")
        self.assertEqual(item.sku, "")
        self.assertIsNotNone(item.pk)

class PriceModelTests(TestCase):
    """
    Test cases for the Price model.
    Corresponds to test cases starting with services_TC_M_P_
    """
    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        # User for Professional
        cls.user = User.objects.create_user(
            username='pro_user_price_tests',
            email='pro_user_price_tests@example.com',
            password='testpassword'
        )
        # Professional
        cls.professional = Professional.objects.create(
            user=cls.user,
            title="Madam Price Setter",
            specialization="Pricing Strategies"
        )
        # Service
        cls.service = Service.objects.create(
            professional=cls.professional,
            title="Parent Service for Priced Items",
        )
        # Item
        cls.item = Item.objects.create(
            service=cls.service,
            title="Priced Item Alpha"
        )

    def test_services_TC_M_P_001_create_price_valid(self):
        """
        Test Case ID: services_TC_M_P_001
        Title: Create Price with valid data
        """
        price_amount = Decimal('99.99')
        price = Price.objects.create(
            item=self.item,
            amount=price_amount,
            currency='USD',
            frequency=Price.FrequencyChoices.MONTHLY,
            description="Standard monthly price.",
            is_active=True,
            min_quantity=1,
            discount_percentage=Decimal('5.00')
        )
        self.assertEqual(price.item, self.item)
        self.assertEqual(price.amount, price_amount)
        self.assertEqual(price.currency, 'USD')
        self.assertEqual(price.frequency, Price.FrequencyChoices.MONTHLY)
        self.assertEqual(price.description, "Standard monthly price.")
        self.assertTrue(price.is_active)
        self.assertEqual(price.min_quantity, 1)
        self.assertEqual(price.discount_percentage, Decimal('5.00'))
        self.assertIsNotNone(price.pk)

    def test_services_TC_M_P_002_create_price_no_item(self):
        """
        Test Case ID: services_TC_M_P_002
        Title: Create Price without an item (invalid)
        Description: Item is a ForeignKey without null=True.
        """
        with self.assertRaises((IntegrityError, ValueError)): # ValueError if caught by Django before DB
            Price.objects.create(
                item=None,
                amount=Decimal('10.00')
            )

    def test_services_TC_M_P_003_create_price_negative_amount_clean(self):
        """
        Test Case ID: services_TC_M_P_003
        Title: Create Price with negative amount (invalid via clean method)
        """
        price_negative_amount = Price(
            item=self.item,
            amount=Decimal('-5.00') # Negative amount
        )
        with self.assertRaises(ValidationError) as context:
            price_negative_amount.full_clean()
        self.assertIn('amount', context.exception.message_dict)
        self.assertEqual(context.exception.message_dict['amount'][0], 'Price amount cannot be negative')

    def test_services_TC_M_P_015_price_default_currency_frequency(self):
        """
        Test Case ID: services_TC_M_P_015
        Title: Price with default currency and frequency
        """
        price = Price.objects.create(
            item=self.item,
            amount=Decimal('50.00')
            # Currency and frequency not specified, should use defaults
        )
        self.assertEqual(price.currency, 'EUR') # Default from model
        self.assertEqual(price.frequency, Price.FrequencyChoices.ONE_TIME) # Default from model
        self.assertIsNotNone(price.pk)

    def test_services_TC_M_P_016_price_all_optional_fields(self):
        """
        Test Case ID: services_TC_M_P_016
        Title: Price with all optional fields filled
        """
        from django.utils import timezone
        now = timezone.now()
        later = now + timezone.timedelta(days=30)

        price = Price.objects.create(
            item=self.item,
            amount=Decimal('123.45'),
            currency='GBP',
            frequency=Price.FrequencyChoices.ANNUALLY,
            description="Full package annual price.",
            is_active=True,
            valid_from=now,
            valid_until=later,
            min_quantity=2,
            max_quantity=10,
            discount_percentage=Decimal('15.00')
        )
        self.assertEqual(price.currency, 'GBP')
        self.assertEqual(price.frequency, Price.FrequencyChoices.ANNUALLY)
        self.assertEqual(price.description, "Full package annual price.")
        self.assertTrue(price.is_active)
        self.assertEqual(price.valid_from, now)
        self.assertEqual(price.valid_until, later)
        self.assertEqual(price.min_quantity, 2)
        self.assertEqual(price.max_quantity, 10)
        self.assertEqual(price.discount_percentage, Decimal('15.00'))
        self.assertIsNotNone(price.pk)
