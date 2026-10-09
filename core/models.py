from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
positive=[MinValueValidator(Decimal('0.01'))]
class Program(models.Model):
    title=models.CharField(max_length=100)
    slug=models.SlugField(unique=True)
    summary=models.TextField()
    description=models.TextField()
    image=models.ImageField(upload_to="programs/",blank=True,help_text="Approved public photograph. JPEG, PNG or WebP; up to 5 MB.")
    image_path=models.CharField(max_length=200,blank=True,help_text="Path to an approved image within static assets, for example core/classroom.png.")
    image_alt=models.CharField(max_length=200,blank=True)
    image_caption=models.CharField(max_length=250,blank=True)
    published=models.BooleanField(default=False)
    @property
    def image_url(self):
        if self.image: return self.image.url
        from django.templatetags.static import static
        return static(self.image_path) if self.image_path else ""
    def __str__(self): return self.title

class ProgramPhoto(models.Model):
    program=models.ForeignKey(Program,on_delete=models.CASCADE,related_name="photos")
    image=models.ImageField(upload_to="programs/gallery/")
    alt=models.CharField(max_length=200)
    caption=models.CharField(max_length=250,blank=True)
    order=models.PositiveIntegerField(default=0)
    class Meta:
        ordering=["order","pk"]

class Case(models.Model):
    STATES=[(s,s.title()) for s in ['submitted','verified','approved','in_progress','completed']]
    reference=models.CharField(max_length=30,unique=True)
    program=models.ForeignKey(Program,on_delete=models.PROTECT)
    title=models.CharField(max_length=150)
    community=models.CharField(max_length=100)
    private_notes=models.TextField(blank=True,help_text='Restricted operational notes. Never public.')
    required=models.DecimalField(max_digits=12,decimal_places=2,validators=positive)
    status=models.CharField(max_length=20,choices=STATES,default='submitted')
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        permissions=[('verify_case','Can verify cases'),('approve_case','Can approve cases'),('record_expense','Can record case expenses'),('publish_impact','Can publish impact updates')]
    @property
    def allocated(self): return self.allocations.aggregate(v=models.Sum('amount'))['v'] or Decimal('0')
    @property
    def spent(self): return self.expenses.aggregate(v=models.Sum('amount'))['v'] or Decimal('0')
    def __str__(self): return self.reference+' · '+self.title
class Campaign(models.Model):
    title=models.CharField(max_length=150)
    case=models.OneToOneField(Case,on_delete=models.PROTECT,related_name='campaign')
    published=models.BooleanField(default=False)
    @property
    def raised(self): return self.donations.filter(status='demo_confirmed').aggregate(v=models.Sum('amount'))['v'] or Decimal('0')
    @property
    def progress(self): return min(100,int(self.raised/self.case.required*100))
    def __str__(self): return self.title
class Donation(models.Model):
    campaign=models.ForeignKey(Campaign,on_delete=models.PROTECT,related_name='donations')
    reference=models.CharField(max_length=40,unique=True)
    amount=models.DecimalField(max_digits=12,decimal_places=2,validators=positive)
    status=models.CharField(max_length=30,default='demo_confirmed')
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.reference
class Allocation(models.Model):
    donation=models.ForeignKey(Donation,on_delete=models.PROTECT,related_name='allocations')
    case=models.ForeignKey(Case,on_delete=models.PROTECT,related_name='allocations')
    amount=models.DecimalField(max_digits=12,decimal_places=2,validators=positive)
    created_at=models.DateTimeField(auto_now_add=True)
class Expense(models.Model):
    case=models.ForeignKey(Case,on_delete=models.PROTECT,related_name='expenses')
    amount=models.DecimalField(max_digits=12,decimal_places=2,validators=positive)
    description=models.CharField(max_length=200)
    evidence_reference=models.CharField(max_length=150,help_text='Reference to internally held evidence; no public document upload in MVP.')
    recorded_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    created_at=models.DateTimeField(auto_now_add=True)
class ImpactUpdate(models.Model):
    case=models.ForeignKey(Case,on_delete=models.PROTECT,related_name='updates')
    title=models.CharField(max_length=150)
    body=models.TextField(help_text='Anonymized public wording only; no names or medical details.')
    published=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
class Enquiry(models.Model):
    kind=models.CharField(max_length=20,choices=[('contact','Contact'),('volunteer','Volunteer')])
    name=models.CharField(max_length=100)
    email=models.EmailField()
    message=models.TextField(max_length=2000)
    created_at=models.DateTimeField(auto_now_add=True)
class AuditEvent(models.Model):
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    case=models.ForeignKey(Case,on_delete=models.PROTECT)
    action=models.CharField(max_length=80)
    details=models.CharField(max_length=250,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
