from decimal import Decimal
from django.core.management.base import BaseCommand,CommandError
from django.conf import settings
from django.contrib.auth.models import Group,Permission
from core.models import Program,Case,Campaign,Donation
class Command(BaseCommand):
    help='Create fictional presentation records and permission groups; never creates a password.'
    def handle(self,*args,**kwargs):
        if not settings.DEMO_MODE: raise CommandError('Demo mode is required.')
        records=[('education','Education & opportunity','Support access to learning, materials, and practical skills.'),('health','Health & wellbeing','Coordinate assistance for people facing barriers to essential care.'),('community','Community support','Help communities respond to immediate needs and build resilience.')]
        for slug,title,summary in records:
            Program.objects.get_or_create(slug=slug,defaults={'title':title,'summary':summary,'description':summary+' Every project follows a documented path from need assessment to delivery and a privacy-conscious impact update.','published':True})
        images={'education':('classroom.png','An educator helping two adult learners'), 'health':('health.png','A healthcare worker speaking with a community member'), 'community':('community.png','Community members discussing a shared plan')}
        for slug,(filename,alt) in images.items():
            Program.objects.filter(slug=slug,image_path='').update(image_path='core/'+filename,image_alt=alt,image_caption='Program illustration')
        program=Program.objects.get(slug='education')
        case,_=Case.objects.get_or_create(reference='DEMO-EDU-001',defaults={'program':program,'title':'Back-to-school essentials','community':'Lomé, Togo','required':Decimal('310'),'private_notes':'Fictional record. No actual beneficiary personal data.'})
        campaign,_=Campaign.objects.get_or_create(case=case,defaults={'title':'A supported start to the school year','published':True})
        Donation.objects.get_or_create(reference='DEMO-SEED-001',defaults={'campaign':campaign,'amount':Decimal('245')})
        groups={'Field officer':['view_case','verify_case'],'Program manager':['view_case','approve_case','publish_impact'],'Finance':['view_case','view_donation','view_expense','record_expense'],'Presentation manager':['view_case','verify_case','approve_case','record_expense','publish_impact']}
        for name,codes in groups.items():
            group,_=Group.objects.get_or_create(name=name)
            group.permissions.set(Permission.objects.filter(content_type__app_label='core',codename__in=codes))
        self.stdout.write(self.style.SUCCESS('Fictional demo records and permission groups ready.'))
