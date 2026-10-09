from django.db import migrations

def clean(apps,schema_editor):
    Program=apps.get_model('core','Program')
    for program in Program.objects.all():
        text=program.description.replace(' Program details in this presentation are proposals for owner review.','')
        caption=program.image_caption
        if caption=='AI-generated illustration. Not a photograph of Dafara activities or beneficiaries.': caption='Program illustration'
        if text!=program.description or caption!=program.image_caption:
            program.description=text;program.image_caption=caption;program.save(update_fields=['description','image_caption'])

class Migration(migrations.Migration):
    dependencies=[('core','0002_program_image_alt_program_image_caption_and_more')]
    operations=[migrations.RunPython(clean,migrations.RunPython.noop)]
