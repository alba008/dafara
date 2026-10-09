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
    class Meta:
        model=Program
        fields=['title','slug','summary','description','image_path','image_alt','image_caption','published']
class CaseForm(forms.ModelForm):
    class Meta:
        model=Case
        fields=['reference','program','title','community','required','private_notes']
class CampaignForm(forms.ModelForm):
    class Meta:
        model=Campaign
        fields=['title','case','published']
