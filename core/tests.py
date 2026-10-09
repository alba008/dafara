from decimal import Decimal
from django.test import TestCase,override_settings
from django.contrib.auth.models import User,Permission
from django.core.management import call_command
from django.core.exceptions import PermissionDenied,ValidationError
from .models import Case,Donation,Expense,AuditEvent
from .services import advance
@override_settings(DEMO_MODE=True)
class WorkflowTests(TestCase):
    def setUp(self):
        call_command('seed_demo',verbosity=0)
        self.case=Case.objects.get(reference='DEMO-EDU-001')
        self.manager=User.objects.create_user('manager',password='test-only-password')
        self.manager.user_permissions.set(Permission.objects.filter(content_type__app_label='core'))
    def test_complete_funding_delivery_and_public_update(self):
        advance(self.manager,self.case.pk,'verify'); advance(self.manager,self.case.pk,'approve')
        advance(self.manager,self.case.pk,'allocate'); advance(self.manager,self.case.pk,'allocate')
        self.assertEqual(self.case.allocated,Decimal('245'))
        with self.assertRaises(ValidationError): advance(self.manager,self.case.pk,'expense','246','School materials','DEMO-R1')
        response=self.client.post('/donate/',{'campaign':self.case.campaign.pk,'amount':'65'})
        self.assertContains(response,'No funds were charged')
        advance(self.manager,self.case.pk,'allocate')
        self.assertEqual(self.case.allocated,Decimal('310'))
        advance(self.manager,self.case.pk,'expense','310','Tuition and books','DEMO-R1')
        advance(self.manager,self.case.pk,'complete'); advance(self.manager,self.case.pk,'publish'); advance(self.manager,self.case.pk,'publish')
        self.assertEqual(self.case.updates.count(),1)
        self.assertContains(self.client.get('/impact/'),'delivery completed')
        self.assertNotContains(self.client.get('/impact/'),self.case.private_notes)
        self.assertEqual(AuditEvent.objects.filter(case=self.case).count(),9)
    def test_permissions_and_order(self):
        outsider=User.objects.create_user('outsider')
        with self.assertRaises(PermissionDenied): advance(outsider,self.case.pk,'verify')
        with self.assertRaises(ValidationError): advance(self.manager,self.case.pk,'approve')
        self.assertEqual(self.client.get('/management/').status_code,302)
        self.client.force_login(outsider)
        self.assertEqual(self.client.get('/management/').status_code,403)
        self.assertEqual(self.client.post(f'/management/cases/{self.case.pk}/action/',{'action':'verify'}).status_code,403)
        self.client.force_login(self.manager)
        self.assertEqual(self.client.get('/management/').status_code,200)
        self.assertContains(self.client.get(f'/management/cases/{self.case.pk}/'),'Verify this case')
        self.assertContains(self.client.get('/management/?q=DEMO-EDU'),self.case.reference)
        self.assertContains(self.client.get('/management/?stage=completed'),'No cases match this search')
    def test_public_pages_and_private_program(self):
        for url in ['/','/programs/','/programs/education/','/programs/health/','/programs/community/','/impact/','/about/','/contact/','/volunteer/','/donate/','/login/']:
            self.assertEqual(self.client.get(url).status_code,200,url)
        p=self.case.program; p.published=False; p.save()
        self.assertEqual(self.client.get('/programs/education/').status_code,404)
        self.assertNotContains(self.client.get('/donate/'),self.case.campaign.title)
    def test_donation_validation_and_live_block(self):
        count=Donation.objects.count()
        self.client.post('/donate/',{'campaign':self.case.campaign.pk,'amount':'-1'})
        self.assertEqual(Donation.objects.count(),count)
        with override_settings(DEMO_MODE=False):
            self.assertEqual(self.client.post('/donate/',{'campaign':self.case.campaign.pk,'amount':'65'}).status_code,403)
    def test_csrf(self):
        from django.test import Client
        c=Client(enforce_csrf_checks=True)
        self.assertEqual(c.post('/donate/',{'campaign':self.case.campaign.pk,'amount':'65'}).status_code,403)
    def test_operations_pages_and_creation(self):
        self.client.force_login(self.manager)
        for kind in ['programs','cases','campaigns','donations','expenses','updates']:
            self.assertEqual(self.client.get('/management/records/'+kind+'/').status_code,200)
        self.assertNotContains(self.client.get('/management/'),'href="/admin/')
        response=self.client.post('/management/records/cases/new/',{'reference':'TEST-NEW-01','program':self.case.program_id,'title':'New assistance request','community':'Lomé','required':'200','private_notes':'Restricted'})
        self.assertEqual(response.status_code,302)
        self.assertEqual(Case.objects.get(reference='TEST-NEW-01').status,'submitted')
        outsider=User.objects.create_user('viewer')
        self.client.force_login(outsider)
        self.assertEqual(self.client.get('/management/records/programs/').status_code,403)
        self.assertEqual(self.client.post('/management/records/cases/new/',{}).status_code,403)
