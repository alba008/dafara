from decimal import Decimal
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Sum
from .models import Case, Donation, Allocation, Expense, ImpactUpdate, AuditEvent
@transaction.atomic
def advance(user,case_id,action,amount=None,description='',evidence=''):
    case=Case.objects.select_for_update().get(pk=case_id)
    permission={'verify':'verify_case','approve':'approve_case','allocate':'approve_case','expense':'record_expense','complete':'approve_case','publish':'publish_impact'}.get(action)
    if not permission or not user.has_perm('core.'+permission): raise PermissionDenied
    if action in ['verify','approve','complete']:
        expected={'verify':'submitted','approve':'verified','complete':'in_progress'}[action]
        if case.status!=expected: raise ValidationError('This action is not available at the current stage.')
        if action=='complete' and case.spent<case.required: raise ValidationError('Record the funded delivery before completing the case.')
        case.status={'verify':'verified','approve':'approved','complete':'completed'}[action]
        case.save(update_fields=['status'])
    elif action=='allocate':
        if case.status not in ['approved','in_progress']: raise ValidationError('Approve the case before allocating funds.')
        remaining=case.required-case.allocated
        for donation in Donation.objects.select_for_update().filter(campaign__case=case,status='demo_confirmed').order_by('id'):
            used=donation.allocations.aggregate(v=Sum('amount'))['v'] or Decimal('0')
            value=min(donation.amount-used,remaining)
            if value>0:
                Allocation.objects.create(donation=donation,case=case,amount=value)
                remaining-=value
        if case.allocated==0: raise ValidationError('No confirmed contributions are available.')
        case.status='in_progress'; case.save(update_fields=['status'])
    elif action=='expense':
        if case.status!='in_progress': raise ValidationError('Allocate funds before recording delivery.')
        try: value=Decimal(str(amount))
        except Exception: raise ValidationError('Enter a valid amount.')
        if not value.is_finite() or value<=0 or value.as_tuple().exponent < -2 or value>case.allocated-case.spent: raise ValidationError('Expense must be positive and within the unspent allocation, with at most two decimals.')
        if not description.strip() or not evidence.strip(): raise ValidationError('Description and evidence reference are required.')
        expense=Expense(case=case,amount=value,description=description,evidence_reference=evidence,recorded_by=user)
        expense.full_clean(); expense.save()
    elif action=='publish':
        if case.status!='completed': raise ValidationError('Complete the case before publishing the result.')
        if not case.updates.filter(published=True).exists():
            ImpactUpdate.objects.create(case=case,title=case.title+' — delivery completed',body=f'Assistance was delivered in {case.community}. ${case.spent:,.2f} was recorded against approved expenses. Beneficiary identities and evidence remain private.',published=True)
    AuditEvent.objects.create(actor=user,case=case,action=action,details='Case workflow')
    return case
