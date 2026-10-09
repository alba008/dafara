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
