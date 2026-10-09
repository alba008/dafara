from django.contrib import admin
from .models import Program,Case,Campaign,Donation,Allocation,Expense,ImpactUpdate,Enquiry,AuditEvent
admin.site.site_header='Dafara · Organization management'
@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display=['title','published']; prepopulated_fields={'slug':['title']}
@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display=['reference','title','program','status']; readonly_fields=['status']
@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin): list_display=['title','case','published']
class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self,request): return False
    def has_change_permission(self,request,obj=None): return False
    def has_delete_permission(self,request,obj=None): return False
for model in [Donation,Allocation,Expense,AuditEvent]: admin.site.register(model,ReadOnlyAdmin)
admin.site.register(ImpactUpdate)
admin.site.register(Enquiry)
