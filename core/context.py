from itertools import zip_longest
from django.conf import settings
from .models import Program


def brand(request):
    result = {'demo_mode': settings.DEMO_MODE}
    programs = {
        program.slug: program
        for program in Program.objects.filter(
            slug__in=['environment', 'education'], published=True
        ).prefetch_related('photos')
    }
    collections = []
    for slug in ['environment', 'education']:
        program = programs.get(slug)
        pictures = []
        if program:
            if program.image:
                pictures.append({
                    'url': program.image.url,
                    'alt': program.image_alt if program.image_alt and 'illustrat' not in program.image_alt.lower() else program.title,
                    'caption': '' if program.image_caption == 'Program illustration' else program.image_caption,
                })
            for photo in program.photos.all():
                pictures.append({'url': photo.image.url, 'alt': photo.alt, 'caption': photo.caption})
        collections.append(pictures)
    # Alternate the two programs, keeping the first two photographs distinct.
    pictures = [photo for pair in zip_longest(*collections) for photo in pair if photo]
    if pictures:
        result.update(
            site_hero=pictures[0],
            site_story=pictures[1 % len(pictures)],
            site_involve=pictures[2 % len(pictures)],
        )
    return result
