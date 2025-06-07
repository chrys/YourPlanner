from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from template_app.models import Template, TemplateImage, TemplateService
from services.models import Service
from users.models import Professional
import tempfile
from PIL import Image
import io

User = get_user_model()


class TemplateViewsTest(TestCase):
    """Test cases for the Template views."""
    
    def setUp(self):
        # Create a client
        self.client = Client()
        
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
            description='Test template description',
            is_active=True
        )
        
        # Create a template service
        self.template_service = TemplateService.objects.create(
            template=self.template,
            service=self.service1,
            position=1
        )
        
        # Create a temporary image for testing
        self.image = self._create_test_image()
        
        # Create a template image
        self.template_image = TemplateImage.objects.create(
            template=self.template,
            image=self.image,
            alt_text='Test image',
            is_default=True
        )
        
        # Login the user
        self.client.login(username='testprofessional', password='testpassword')
    
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
    
    def test_template_list_view(self):
        """Test the template list view."""
        # Get the template list page
        response = self.client.get(reverse('template_app:template_list'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the template is in the context
        self.assertIn('templates', response.context)
        self.assertEqual(len(response.context['templates']), 1)
        self.assertEqual(response.context['templates'][0], self.template)
        
        # Check that the template title is in the response
        self.assertContains(response, 'Test Template')
    
    def test_template_detail_view(self):
        """Test the template detail view."""
        # Get the template detail page
        response = self.client.get(
            reverse('template_app:template_detail', kwargs={'slug': self.template.slug})
        )
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the template is in the context
        self.assertIn('template', response.context)
        self.assertEqual(response.context['template'], self.template)
        
        # Check that the template service is in the context
        self.assertIn('template_services', response.context)
        self.assertEqual(len(response.context['template_services']), 1)
        self.assertEqual(response.context['template_services'][0], self.template_service)
        
        # Check that the template image is in the context
        self.assertIn('template_images', response.context)
        self.assertEqual(len(response.context['template_images']), 1)
        self.assertEqual(response.context['template_images'][0], self.template_image)
        
        # Check that the template title and description are in the response
        self.assertContains(response, 'Test Template')
        self.assertContains(response, 'Test template description')
    
    def test_template_create_view_get(self):
        """Test the template create view (GET request)."""
        # Get the template create page
        response = self.client.get(reverse('template_app:template_create'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the form is in the context
        self.assertIn('form', response.context)
        self.assertIn('image_formset', response.context)
        self.assertIn('service_formset', response.context)
        
        # Check that the page contains the form fields
        self.assertContains(response, 'Title')
        self.assertContains(response, 'Description')
        self.assertContains(response, 'Is active')
    
    def test_template_create_view_post(self):
        """Test the template create view (POST request)."""
        # Create a new image for the template
        image = self._create_test_image()
        
        # Create the form data
        form_data = {
            'title': 'New Template',
            'description': 'New template description',
            'is_active': True,
            
            # Image formset data
            'images-TOTAL_FORMS': '1',
            'images-INITIAL_FORMS': '0',
            'images-MIN_NUM_FORMS': '0',
            'images-MAX_NUM_FORMS': '1000',
            'images-0-image': image,
            'images-0-is_default': True,
            'images-0-alt_text': 'New image',
            'images-0-position': 0,
            
            # Service formset data
            'services-TOTAL_FORMS': '1',
            'services-INITIAL_FORMS': '0',
            'services-MIN_NUM_FORMS': '0',
            'services-MAX_NUM_FORMS': '1000',
            'services-0-service': self.service2.id,
            'services-0-position': 0,
        }
        
        # Submit the form
        response = self.client.post(
            reverse('template_app:template_create'),
            data=form_data,
            follow=True
        )
        
        # Check that the template was created
        self.assertEqual(Template.objects.count(), 2)
        
        # Get the newly created template
        new_template = Template.objects.get(title='New Template')
        
        # Check that the template has the correct data
        self.assertEqual(new_template.description, 'New template description')
        self.assertEqual(new_template.professional, self.professional)
        self.assertTrue(new_template.is_active)
        
        # Check that the template has an image
        self.assertEqual(new_template.images.count(), 1)
        self.assertTrue(new_template.images.first().is_default)
        
        # Check that the template has a service
        self.assertEqual(new_template.template_services.count(), 1)
        self.assertEqual(new_template.template_services.first().service, self.service2)
        
        # Check that the response redirects to the template detail page
        self.assertRedirects(
            response,
            reverse('template_app:template_detail', kwargs={'slug': new_template.slug})
        )
    
    def test_template_update_view_get(self):
        """Test the template update view (GET request)."""
        # Get the template update page
        response = self.client.get(
            reverse('template_app:template_update', kwargs={'slug': self.template.slug})
        )
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the form is in the context
        self.assertIn('form', response.context)
        self.assertIn('image_formset', response.context)
        self.assertIn('service_formset', response.context)
        
        # Check that the form is populated with the template data
        self.assertEqual(response.context['form'].instance, self.template)
        
        # Check that the page contains the template data
        self.assertContains(response, 'Test Template')
        self.assertContains(response, 'Test template description')
    
    def test_template_update_view_post(self):
        """Test the template update view (POST request)."""
        # Create the form data
        form_data = {
            'title': 'Updated Template',
            'description': 'Updated template description',
            'is_active': True,
            
            # Image formset data
            'images-TOTAL_FORMS': '1',
            'images-INITIAL_FORMS': '1',
            'images-MIN_NUM_FORMS': '0',
            'images-MAX_NUM_FORMS': '1000',
            'images-0-id': self.template_image.id,
            'images-0-template': self.template.id,
            'images-0-is_default': True,
            'images-0-alt_text': 'Updated image',
            'images-0-position': 0,
            
            # Service formset data
            'services-TOTAL_FORMS': '1',
            'services-INITIAL_FORMS': '1',
            'services-MIN_NUM_FORMS': '0',
            'services-MAX_NUM_FORMS': '1000',
            'services-0-id': self.template_service.id,
            'services-0-template': self.template.id,
            'services-0-service': self.service2.id,
            'services-0-position': 0,
        }
        
        # Submit the form
        response = self.client.post(
            reverse('template_app:template_update', kwargs={'slug': self.template.slug}),
            data=form_data,
            follow=True
        )
        
        # Refresh the template from the database
        self.template.refresh_from_db()
        
        # Check that the template was updated
        self.assertEqual(self.template.title, 'Updated Template')
        self.assertEqual(self.template.description, 'Updated template description')
        
        # Refresh the template image from the database
        self.template_image.refresh_from_db()
        
        # Check that the template image was updated
        self.assertEqual(self.template_image.alt_text, 'Updated image')
        
        # Refresh the template service from the database
        self.template_service.refresh_from_db()
        
        # Check that the template service was updated
        self.assertEqual(self.template_service.service, self.service2)
        
        # Check that the response redirects to the template detail page
        self.assertRedirects(
            response,
            reverse('template_app:template_detail', kwargs={'slug': self.template.slug})
        )
    
    def test_template_delete_view_get(self):
        """Test the template delete view (GET request)."""
        # Get the template delete page
        response = self.client.get(
            reverse('template_app:template_delete', kwargs={'slug': self.template.slug})
        )
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the template is in the context
        self.assertIn('template', response.context)
        self.assertEqual(response.context['template'], self.template)
        
        # Check that the page contains the confirmation message
        self.assertContains(response, 'Are you sure you want to delete the template')
        self.assertContains(response, 'Test Template')
    
    def test_template_delete_view_post(self):
        """Test the template delete view (POST request)."""
        # Submit the form
        response = self.client.post(
            reverse('template_app:template_delete', kwargs={'slug': self.template.slug}),
            follow=True
        )
        
        # Check that the template was deleted
        self.assertEqual(Template.objects.count(), 0)
        
        # Check that the template image was deleted
        self.assertEqual(TemplateImage.objects.count(), 0)
        
        # Check that the template service was deleted
        self.assertEqual(TemplateService.objects.count(), 0)
        
        # Check that the response redirects to the template list page
        self.assertRedirects(response, reverse('template_app:template_list'))
    
    def test_template_views_require_login(self):
        """Test that the template views require login."""
        # Logout the user
        self.client.logout()
        
        # Try to access the template list page
        response = self.client.get(reverse('template_app:template_list'))
        
        # Check that the response redirects to the login page
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('template_app:template_list')}"
        )
        
        # Try to access the template detail page
        response = self.client.get(
            reverse('template_app:template_detail', kwargs={'slug': self.template.slug})
        )
        
        # Check that the response redirects to the login page
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('template_app:template_detail', kwargs={'slug': self.template.slug})}"
        )
        
        # Try to access the template create page
        response = self.client.get(reverse('template_app:template_create'))
        
        # Check that the response redirects to the login page
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('template_app:template_create')}"
        )
        
        # Try to access the template update page
        response = self.client.get(
            reverse('template_app:template_update', kwargs={'slug': self.template.slug})
        )
        
        # Check that the response redirects to the login page
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('template_app:template_update', kwargs={'slug': self.template.slug})}"
        )
        
        # Try to access the template delete page
        response = self.client.get(
            reverse('template_app:template_delete', kwargs={'slug': self.template.slug})
        )
        
        # Check that the response redirects to the login page
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('template_app:template_delete', kwargs={'slug': self.template.slug})}"
        )
    
    def test_template_views_require_professional(self):
        """Test that the template views require a professional profile."""
        # Create a user without a professional profile
        user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        
        # Login the user
        self.client.login(username='testuser', password='testpassword')
        
        # Try to access the template list page
        response = self.client.get(reverse('template_app:template_list'))
        
        # Check that the response redirects to the profile page
        self.assertRedirects(response, reverse('users:profile'))
        
        # Try to access the template create page
        response = self.client.get(reverse('template_app:template_create'))
        
        # Check that the response redirects to the profile page
        self.assertRedirects(response, reverse('users:profile'))
    
    def test_template_views_require_ownership(self):
        """Test that the template views require ownership of the template."""
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
        
        # Create a template for the other professional
        other_template = Template.objects.create(
            professional=other_professional,
            title='Other Template',
            description='Other template description'
        )
        
        # Try to access the other professional's template detail page
        response = self.client.get(
            reverse('template_app:template_detail', kwargs={'slug': other_template.slug})
        )
        
        # Check that the response is forbidden
        self.assertEqual(response.status_code, 403)
        
        # Try to access the other professional's template update page
        response = self.client.get(
            reverse('template_app:template_update', kwargs={'slug': other_template.slug})
        )
        
        # Check that the response is forbidden
        self.assertEqual(response.status_code, 403)
        
        # Try to access the other professional's template delete page
        response = self.client.get(
            reverse('template_app:template_delete', kwargs={'slug': other_template.slug})
        )
        
        # Check that the response is forbidden
        self.assertEqual(response.status_code, 403)

