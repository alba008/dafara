import tempfile
from io import BytesIO
from PIL import Image
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from .models import Program, ProgramPhoto
from .forms import ProgramForm


def picture():
    buf=BytesIO()
    Image.new('RGB',(60,40),'green').save(buf,'PNG')
    return SimpleUploadedFile('photo.png',buf.getvalue(),content_type='image/png')

class ProgramPhotoTests(TestCase):
    def test_management_upload_and_public_gallery(self):
        with tempfile.TemporaryDirectory() as folder, override_settings(MEDIA_ROOT=folder):
            program=Program.objects.create(title='Water',slug='water',summary='Water',description='Water',published=True)
            url=f'/management/records/programs/{program.pk}/edit/'
            self.assertEqual(self.client.get(url).status_code,302)
            user=get_user_model().objects.create_superuser('owner','owner@example.com','testpass')
            self.client.force_login(user)
            response=self.client.post(url,{
                'title':'Water','slug':'water','summary':'Water','description':'Water','published':'on',
                'image':picture(),'image_alt':'A water source','image_caption':'Water access',
                'photos-TOTAL_FORMS':'1','photos-INITIAL_FORMS':'0',
                'photos-MIN_NUM_FORMS':'0','photos-MAX_NUM_FORMS':'24',
                'photos-0-image':picture(),'photos-0-alt':'Community water','photos-0-caption':'Our water project','photos-0-order':'0',
            })
            self.assertEqual(response.status_code,302, response.content.decode())
            program.refresh_from_db()
            self.assertTrue(program.image.name.endswith('.jpg'))
            self.assertEqual(ProgramPhoto.objects.count(),1)
            response=self.client.get('/programs/water/')
            self.assertContains(response,program.image.url)
            self.assertContains(response,'Our water project')
            # Resaving without a new upload keeps both stored photos.
            response=self.client.get(url)
            self.assertEqual(response.status_code,200)
            self.assertContains(response,'multipart/form-data')
            self.client.logout()
            self.assertEqual(self.client.post(url,{}).status_code,302)

    def test_invalid_upload_rejected(self):
        form=ProgramForm({'title':'Water','slug':'water','summary':'Water','description':'Water'},
            {'image':SimpleUploadedFile('bad.html',b'<script>alert(1)</script>',content_type='text/html')})
        self.assertFalse(form.is_valid())
        self.assertIn('image',form.errors)

    def test_shared_photos_replace_static_illustrations(self):
        with tempfile.TemporaryDirectory() as folder, override_settings(MEDIA_ROOT=folder):
            environment=Program.objects.create(title='Environmental Protection',slug='environment',summary='Nature',description='Nature',published=True,image=picture(),image_alt='Tree planting')
            ProgramPhoto.objects.create(program=environment,image=picture(),alt='Community planting',caption='Planting together')
            response=self.client.get('/')
            self.assertContains(response,environment.image.url)
            self.assertNotContains(response,'core/community.png')
            response=self.client.get('/programs/')
            self.assertContains(response,'Planting together')
            self.assertNotContains(response,'core/classroom.png')
            environment.published=False
            environment.save()
            self.assertNotContains(self.client.get('/'),environment.image.url)

    def test_shared_photos_mix_environment_and_education(self):
        from .context import brand
        with tempfile.TemporaryDirectory() as folder, override_settings(MEDIA_ROOT=folder):
            environment=Program.objects.create(title='Environment',slug='environment',published=True,image=picture())
            education=Program.objects.create(title='Education',slug='education',published=True,image=picture())
            extra=ProgramPhoto.objects.create(program=environment,image=picture(),alt='Planting')
            selected=brand(None)
            self.assertEqual(selected['site_hero']['url'],environment.image.url)
            self.assertEqual(selected['site_story']['url'],education.image.url)
            self.assertEqual(selected['site_involve']['url'],extra.image.url)
            environment.published=False
            environment.save()
            self.assertEqual(brand(None)['site_hero']['url'],education.image.url)
