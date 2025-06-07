from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from template_app.models import Template, TemplateImage, TemplateService
from services.models import Service
from users.models import Professional

User = get_user_model()


class TemplateModelTest(TestCase):
    """Test cases for the Template model."""
    
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testprofessional',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create a professional
        self.professional = Professional.objects.create(
            user=self.user,
            title='Test Professional',
            specialization='Test Specialization'
        )
        
        # Create a service
        self.service = Service.objects.create(
            professional=self.professional,
            title='Test Service',
            description='Test service description'
        )
        
        # Create a template
        self.template = Template.objects.create(
            professional=self.professional,
            title='Test Template',
            description='Test template description',
            is_active=True
        )
    
    def test_template_creation(self):
        """Test that a template can be created with valid data."""
        self.assertEqual(self.template.title, 'Test Template')
        self.assertEqual(self.template.description, 'Test template description')
        self.assertEqual(self.template.professional, self.professional)
        self.assertTrue(self.template.is_active)
        self.assertEqual(self.template.slug, slugify(f'Test Template-{self.professional.pk}'))
    
    def test_template_string_representation(self):
        """Test the string representation of a template."""
        expected_string = f'Test Template (by {self.professional})'
        self.assertEqual(str(self.template), expected_string)
    
    def test_template_unique_title_per_professional(self):
        """Test that a professional cannot have two templates with the same title."""
        # Try to create another template with the same title for the same professional
        duplicate_template = Template(
            professional=self.professional,
            title='Test Template',
            description='Another description'
        )
        
        with self.assertRaises(ValidationError):
            duplicate_template.full_clean()
    
    def test_template_requires_professional(self):
        """Test that a template must have a professional."""
        template_without_professional = Template(
            title='No Professional Template',
            description='This template has no professional'
        )
        
        with self.assertRaises(ValidationError):
            template_without_professional.save()
    
    def test_template_active_manager(self):
        """Test that the active manager returns only active templates."""
        # Create an inactive template
        Template.objects.create(
            professional=self.professional,
            title='Inactive Template',
            description='This template is inactive',
            is_active=False
        )
        
        # Check that only active templates are returned by the active manager
        active_templates = Template.active.all()
        self.assertEqual(active_templates.count(), 1)
        self.assertEqual(active_templates.first(), self.template)


class TemplateImageModelTest(TestCase):
    """Test cases for the TemplateImage model."""
    
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testprofessional',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create a professional
        self.professional = Professional.objects.create(
            user=self.user,
            title='Test Professional',
            specialization='Test Specialization'
        )
        
        # Create a template
        self.template = Template.objects.create(
            professional=self.professional,
            title='Test Template',
            description='Test template description'
        )
    
    def test_template_image_default_behavior(self):
        """Test that the first image added to a template is set as default."""
        # Create a template image
        image1 = TemplateImage.objects.create(
            template=self.template,
            image='test_image1.jpg',
            alt_text='Test image 1'
        )
        
        # Check that the first image is set as default
        self.assertTrue(image1.is_default)
        
        # Create another template image
        image2 = TemplateImage.objects.create(
            template=self.template,
            image='test_image2.jpg',
            alt_text='Test image 2'
        )
        
        # Check that the second image is not set as default
        self.assertFalse(image2.is_default)
    
    def test_template_image_set_default(self):
        """Test that setting a new image as default unsets the previous default."""
        # Create two template images
        image1 = TemplateImage.objects.create(
            template=self.template,
            image='test_image1.jpg',
            alt_text='Test image 1'
        )
        
        image2 = TemplateImage.objects.create(
            template=self.template,
            image='test_image2.jpg',
            alt_text='Test image 2'
        )
        
        # Set the second image as default
        image2.is_default = True
        image2.save()
        
        # Refresh the first image from the database
        image1.refresh_from_db()
        
        # Check that the first image is no longer default
        self.assertFalse(image1.is_default)
        
        # Check that the second image is now default
        self.assertTrue(image2.is_default)
    
    def test_template_image_string_representation(self):
        """Test the string representation of a template image."""
        # Create a template image
        image = TemplateImage.objects.create(
            template=self.template,
            image='test_image.jpg',
            alt_text='Test image',
            is_default=True
        )
        
        expected_string = f'Image for {self.template.title} (Default)'
        self.assertEqual(str(image), expected_string)
        
        # Create a non-default template image
        non_default_image = TemplateImage.objects.create(
            template=self.template,
            image='non_default_image.jpg',
            alt_text='Non-default image',
            is_default=False
        )
        
        expected_string = f'Image for {self.template.title}'
        self.assertEqual(str(non_default_image), expected_string)


class TemplateServiceModelTest(TestCase):
    """Test cases for the TemplateService model."""
    
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testprofessional',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create a professional
        self.professional = Professional.objects.create(
            user=self.user,
            title='Test Professional',
            specialization='Test Specialization'
        )
        
        # Create services
        self.service1 = Service.objects.create(
            professional=self.professional,
            title='Test Service 1',
            description='Test service 1 description'
        )
        
        self.service2 = Service.objects.create(
            professional=self.professional,
            title='Test Service 2',
            description='Test service 2 description'
        )
        
        # Create a template
        self.template = Template.objects.create(
            professional=self.professional,
            title='Test Template',
            description='Test template description'
        )
        
        # Create a template service
        self.template_service = TemplateService.objects.create(
            template=self.template,
            service=self.service1,
            position=1
        )
    
    def test_template_service_creation(self):
        """Test that a template service can be created with valid data."""
        self.assertEqual(self.template_service.template, self.template)
        self.assertEqual(self.template_service.service, self.service1)
        self.assertEqual(self.template_service.position, 1)
    
    def test_template_service_string_representation(self):
        """Test the string representation of a template service."""
        expected_string = f'{self.service1.title} in {self.template.title}'
        self.assertEqual(str(self.template_service), expected_string)
    
    def test_template_service_unique_constraint(self):
        """Test that a service can only be added once to a template."""
        # Try to create another template service with the same service and template
        with self.assertRaises(Exception):  # Could be IntegrityError or ValidationError
            TemplateService.objects.create(
                template=self.template,
                service=self.service1,
                position=2
            )
    
    def test_template_service_different_professional(self):
        """Test that a service from a different professional cannot be added to a template."""
        # Create another user and professional
        other_user = User.objects.create_user(
            username='otherprofessional',
            email='other@example.com',
            password='otherpassword'
        )
        
        other_professional = Professional.objects.create(
            user=other_user,
            title='Other Professional',
            specialization='Other Specialization'
        )
        
        # Create a service for the other professional
        other_service = Service.objects.create(
            professional=other_professional,
            title='Other Service',
            description='Other service description'
        )
        
        # Try to add the other professional's service to the template
        template_service = TemplateService(
            template=self.template,
            service=other_service,
            position=2
        )
        
        with self.assertRaises(ValidationError):
            template_service.full_clean()
    
    def test_template_service_ordering(self):
        """Test that template services are ordered by position."""
        # Create another template service with a different position
        TemplateService.objects.create(
            template=self.template,
            service=self.service2,
            position=0
        )
        
        # Get all template services for the template
        template_services = TemplateService.objects.filter(template=self.template)
        
        # Check that the services are ordered by position
        self.assertEqual(template_services[0].service, self.service2)
        self.assertEqual(template_services[1].service, self.service1)

