import uuid
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Sum,Q
from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.http import require_POST
from .models import Program,Case,Campaign,Donation,ImpactUpdate,Expense,AuditEvent,Allocation
from .forms import EnquiryForm,DemoDonationForm
from .services import advance

def home(request):
    return render(request,'core/home.html',{'programs':Program.objects.filter(published=True),'campaigns':Campaign.objects.filter(published=True,case__program__published=True).select_related('case__program').order_by('-id')[:3],'updates':ImpactUpdate.objects.filter(published=True,case__program__published=True).select_related('case__program').order_by('-created_at')[:3]})
def programs(request): return render(request,'core/programs.html',{'programs':Program.objects.filter(published=True)})
def program(request,slug):
    obj=get_object_or_404(Program,slug=slug,published=True)
    return render(request,'core/program.html',{'program':obj,'campaigns':Campaign.objects.filter(case__program=obj,published=True).select_related('case')})
def impact(request): return render(request,'core/impact.html',{'updates':ImpactUpdate.objects.filter(published=True,case__program__published=True).select_related('case__program'),'expenses':Expense.objects.filter(case__updates__published=True,case__program__published=True).distinct().aggregate(v=Sum('amount'))['v'] or 0})
def mission(request): return render(request,'core/mission.html')
def about(request): return render(request,'core/about.html')
def enquiry(request,kind):
    form=EnquiryForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        item=form.save(commit=False); item.kind=kind; item.save()
        messages.success(request,'Your enquiry has been saved for review.'); return redirect(request.path)
    return render(request,'core/enquiry.html',{'form':form,'kind':kind})
def donate(request):
    campaigns=Campaign.objects.filter(published=True,case__program__published=True).select_related('case__program')
    form=DemoDonationForm(request.POST or None)
    if request.method=='POST':
        if not settings.DEMO_MODE: raise PermissionDenied('Live payment processing is not configured.')
        campaign=get_object_or_404(campaigns,pk=request.POST.get('campaign'))
        if form.is_valid():
            donation=Donation.objects.create(campaign=campaign,amount=form.cleaned_data['amount'],reference='DEMO-'+uuid.uuid4().hex[:12].upper())
            return render(request,'core/receipt.html',{'donation':donation})
    return render(request,'core/donate.html',{'campaigns':campaigns,'form':form})
@login_required
@permission_required('core.view_case',raise_exception=True)
def dashboard(request):
    cases=Case.objects.select_related('program').order_by('-id')
    query=request.GET.get('q','').strip()
    if query: cases=cases.filter(Q(reference__icontains=query)|Q(title__icontains=query)|Q(program__title__icontains=query))
    stage=request.GET.get('stage','')
    if stage in dict(Case.STATES): cases=cases.filter(status=stage)
    return render(request,'core/dashboard.html',{'cases':cases,'selected':cases.first(),'stages':Case.STATES,'donations':Donation.objects.aggregate(v=Sum('amount'))['v'] or 0,'allocated':Allocation.objects.aggregate(v=Sum('amount'))['v'] or 0,'spent':Expense.objects.aggregate(v=Sum('amount'))['v'] or 0,'updates':ImpactUpdate.objects.filter(published=True).count(),'events':AuditEvent.objects.select_related('actor','case').order_by('-id')[:5]})
@login_required
@permission_required('core.view_case',raise_exception=True)
def case_detail(request,pk):
    case=get_object_or_404(Case,pk=pk)
    return render(request,'core/case.html',{'case':case,'events':case.auditevent_set.select_related('actor').order_by('-id'),'expenses':case.expenses.all()})
@login_required
@require_POST
def action(request,pk):
    if not settings.DEMO_MODE: raise PermissionDenied('Presentation workflow is disabled outside demo mode.')
    get_object_or_404(Case,pk=pk)
    try:
        advance(request.user,pk,request.POST.get('action'),request.POST.get('amount'),request.POST.get('description',''),request.POST.get('evidence',''))
        messages.success(request,'Case updated. The action is recorded in its audit history.')
    except ValidationError as exc: messages.error(request,' '.join(exc.messages))
    return redirect('case',pk=pk)

from .forms import ProgramForm,CaseForm,CampaignForm,ProgramPhotoFormSet
from django.db import transaction
from django.http import Http404
RECORDS={
    'programs':(Program,ProgramForm,'program','Programs'),
    'cases':(Case,CaseForm,'case','Cases'),
    'campaigns':(Campaign,CampaignForm,'campaign','Campaigns'),
    'donations':(Donation,None,'donation','Donations'),
    'expenses':(Expense,None,'expense','Expenses'),
    'updates':(ImpactUpdate,None,'impactupdate','Impact updates'),
}
def record_config(user,kind,action='view'):
    if kind not in RECORDS: raise Http404
    model,form,code,title=RECORDS[kind]
    if not user.has_perm('core.'+action+'_'+code): raise PermissionDenied
    return model,form,code,title
@login_required
def records(request,kind):
    model,form,code,title=record_config(request.user,kind)
    rows=[]
    for item in model.objects.order_by('-pk')[:100]:
        if kind=='programs': label=item.title; detail='Published' if item.published else 'Draft'
        elif kind=='cases': label=item.reference+' · '+item.title; detail=item.get_status_display()
        elif kind=='campaigns': label=item.title; detail='Published' if item.published else 'Draft'
        elif kind=='donations': label=item.reference; detail='$'+str(item.amount)
        elif kind=='expenses': label=item.description; detail='$'+str(item.amount)
        else: label=item.title; detail='Published' if item.published else 'Draft'
        rows.append({'pk':item.pk,'label':label,'detail':detail,'case_id':getattr(item,'case_id',None)})
    return render(request,'core/records.html',{'kind':kind,'title':title,'rows':rows,'can_add':form is not None and request.user.has_perm('core.add_'+code),'can_edit':form is not None and kind!='cases' and request.user.has_perm('core.change_'+code)})
@login_required
def record_form(request,kind,pk=None):
    model,form,code,title=record_config(request.user,kind,'change' if pk else 'add')
    if form is None or (pk and kind=='cases'): raise Http404
    item=get_object_or_404(model,pk=pk) if pk else None
    fields=form(request.POST or None,request.FILES or None,instance=item)
    gallery = ProgramPhotoFormSet(request.POST or None, request.FILES or None, instance=fields.instance, prefix='photos') if kind=='programs' else None
    if request.method=='POST':
        valid=fields.is_valid()
        gallery_valid=gallery.is_valid() if gallery is not None else True
        if valid and gallery_valid:
            with transaction.atomic():
                saved=fields.save()
                if gallery is not None:
                    gallery.instance=saved
                    gallery.save()
            messages.success(request,'Saved successfully.');return redirect('records',kind=kind)
    return render(request,'core/record_form.html',{'form':fields,'gallery':gallery,'title':title,'kind':kind,'editing':item is not None})
