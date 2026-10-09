from django import forms
from .models import Enquiry
class EnquiryForm(forms.ModelForm):
    class Meta:
        model=Enquiry
        fields=['name','email','message']
class DemoDonationForm(forms.Form):
    amount=forms.DecimalField(min_value=1,max_value=100000,max_digits=12,decimal_places=2)

from .models import Program,Case,Campaign
class ProgramForm(forms.ModelForm):
    def clean_image(self):
        return public_photo(self.cleaned_data.get("image"))

    class Meta:
        model=Program
        fields=['title','slug','summary','description','image','image_alt','image_caption','published']
class CaseForm(forms.ModelForm):
    class Meta:
        model=Case
        fields=['reference','program','title','community','required','private_notes']
class CampaignForm(forms.ModelForm):
    class Meta:
        model=Campaign
        fields=['title','case','published']

from io import BytesIO
from uuid import uuid4
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.forms import inlineformset_factory
from .models import ProgramPhoto


def public_photo(upload):
    if not upload or not hasattr(upload, 'content_type'):
        return upload
    if upload.size > 5 * 1024 * 1024:
        raise forms.ValidationError("Choose a picture smaller than 5 MB.")
    try:
        upload.seek(0)
        with Image.open(upload) as original:
            if original.format not in ('JPEG', 'PNG', 'WEBP'):
                raise ValueError('Unsupported image')
            if original.width * original.height > 25000000:
                raise ValueError('Image too large')
            original.load()
            picture = ImageOps.exif_transpose(original).convert('RGB')
            picture.thumbnail((2000, 2000))
            output = BytesIO()
            picture.save(output, format='JPEG', quality=85, optimize=True)
        return ContentFile(output.getvalue(), name=uuid4().hex + '.jpg')
    except Exception:
        raise forms.ValidationError("Use a valid JPEG, PNG or WebP picture under 25 megapixels.")
    finally:
        upload.seek(0)


class ProgramPhotoForm(forms.ModelForm):
    class Meta:
        model = ProgramPhoto
        fields = ['image', 'alt', 'caption', 'order']
    def clean_image(self):
        return public_photo(self.cleaned_data.get('image'))

ProgramPhotoFormSet = inlineformset_factory(
    Program, ProgramPhoto, form=ProgramPhotoForm,
    extra=3, can_delete=True, max_num=24, validate_max=True,
)
