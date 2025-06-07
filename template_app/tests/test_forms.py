from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from template_app.forms import TemplateForm, TemplateImageForm, TemplateServiceForm
from template_app.models import Template
from services.models import Service
from users.models import Professional
from PIL import Image
import io

User = get_user_model()


class TemplateFormTest(TestCase):
    """Test cases for the Template form."""
    
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
    
    def test_template_form_valid_data(self):
        """Test that the template form is valid with valid data."""
        form = TemplateForm(
            data={
                'title': 'Test Template',
                'description': 'Test template description',
                'is_active': True
            },
            professional=self.professional
        )
        
        self.assertTrue(form.is_valid())
    
    def test_template_form_missing_title(self):
        """Test that the template form is invalid without a title."""
        form = TemplateForm(
            data={
                'description': 'Test template description',
                'is_active': True
            },
            professional=self.professional
        )
        
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_template_form_save_with_professional(self):
        """Test that the template form saves with the provided professional."""
        form = TemplateForm(
            data={
                'title': 'Test Template',
                'description': 'Test template description',
                'is_active': True
            },
            professional=self.professional
        )
        
        self.assertTrue(form.is_valid())
        template = form.save()
        
        self.assertEqual(template.professional, self.professional)
        self.assertEqual(template.title, 'Test Template')
        self.assertEqual(template.description, 'Test template description')
        self.assertTrue(template.is_active)


class TemplateImageFormTest(TestCase):
    """Test cases for the TemplateImage form."""
    
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
        
        # Create a test image
        self.image = self._create_test_image()
    
    def _create_test_image(self):
        """Create a test image for testing."""
        # Create a temporary image file
        image = Image.new('RGB', (100, 100), color='red')
        image_file = io.BytesIO()
        image.save(image_file, 'JPEG')
        image_file.seek(0)
        
        return SimpleUploadedFile(
            name='test_image.jpg',
            content=image_file.read(),
            content_type='image/jpeg'
        )
    
    def test_template_image_form_valid_data(self):
        """Test that the template image form is valid with valid data."""
        form = TemplateImageForm(
            data={
                'is_default': True,
                'alt_text': 'Test image',
                'position': 0
            },
            files={
                'image': self.image
            }
        )
        
        self.assertTrue(form.is_valid())
    
    def test_template_image_form_missing_image(self):
        """Test that the template image form is invalid without an image."""
        form = TemplateImageForm(
            data={
                'is_default': True,
                'alt_text': 'Test image',
                'position': 0
            }
        )
        
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)


class TemplateServiceFormTest(TestCase):
    """Test cases for the TemplateService form."""
    
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
        
        # Create another professional and service
        self.other_user = User.objects.create_user(
            username='otherprofessional',
            email='other@example.com',
            password='otherpassword'
        )
        
        self.other_professional = Professional.objects.create(
            user=self.other_user,
            title='Other Professional',
            specialization='Other Specialization'
        )
        
        self.other_service = Service.objects.create(
            professional=self.other_professional,
            title='Other Service',
            description='Other service description'
        )
        
        # Create a template
        self.template = Template.objects.create(
            professional=self.professional,
            title='Test Template',
            description='Test template description'
        )
    
    def test_template_service_form_valid_data(self):
        """Test that the template service form is valid with valid data."""
        form = TemplateServiceForm(
            data={
                'service': self.service.id,
                'position': 0
            },
            professional=self.professional
        )
        
        self.assertTrue(form.is_valid())
    
    def test_template_service_form_missing_service(self):
        """Test that the template service form is invalid without a service."""
        form = TemplateServiceForm(
            data={
                'position': 0
            },
            professional=self.professional
        )
        
        self.assertFalse(form.is_valid())
        self.assertIn('service', form.errors)
    
    def test_template_service_form_filters_services_by_professional(self):
        """Test that the template service form filters services by professional."""
        form = TemplateServiceForm(professional=self.professional)
        
        # Check that only the professional's services are in the queryset
        self.assertIn(self.service, form.fields['service'].queryset)
        self.assertNotIn(self.other_service, form.fields['service'].queryset)

