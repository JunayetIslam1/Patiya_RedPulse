from django.db import migrations


def seed_hospitals(apps, schema_editor):
    Hospital = apps.get_model('blood_requests', 'Hospital')
    # Only officially-sourced numbers are seeded here. The Patiya Upazila
    # Health Complex number is published on the government's own site
    # (health.patiya.chittagong.gov.bd, "জরুরি কল"). The two national
    # hotlines are well-known, government-run services. Everything else —
    # private hospitals, clinics, blood banks — should be added by the
    # site owner via Django admin once they've personally verified the
    # number, rather than shipped here as a guess.
    entries = [
        dict(
            name='জাতীয় জরুরি সেবা (National Emergency Service)',
            phone='999',
            address='সারা বাংলাদেশ',
            has_blood_bank=False,
            is_24_7=True,
            notes='Police, fire, and medical emergency — free, 24/7.',
            display_order=1,
        ),
        dict(
            name='স্বাস্থ্য বাতায়ন (Health Helpline, DGHS)',
            phone='16263',
            address='সারা বাংলাদেশ',
            has_blood_bank=False,
            is_24_7=True,
            notes='Government health advice hotline, 24/7.',
            display_order=2,
        ),
        dict(
            name='পটিয়া উপজেলা স্বাস্থ্য কমপ্লেক্স',
            phone='01730324451',
            address='পটিয়া, চট্টগ্রাম',
            has_blood_bank=False,
            is_24_7=False,
            notes='সরকারি হাসপাতাল — Source: health.patiya.chittagong.gov.bd',
            display_order=3,
        ),
    ]
    for e in entries:
        Hospital.objects.get_or_create(name=e['name'], defaults=e)


def remove_seed(apps, schema_editor):
    Hospital = apps.get_model('blood_requests', 'Hospital')
    Hospital.objects.filter(display_order__in=[1, 2, 3]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('blood_requests', '0004_hospital'),
    ]

    operations = [
        migrations.RunPython(seed_hospitals, remove_seed),
    ]
