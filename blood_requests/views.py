from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, Value, IntegerField
from django.http import Http404
from django.utils import timezone
from datetime import timedelta
from .forms import BloodRequestForm
from .models import BloodRequest, Hospital, RequestResponse
from .content import FAQS, ARTICLES
from accounts.models import Donor

BLOOD_GROUPS_ORDER = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']


def home(request):
    total_donors = Donor.objects.filter(is_active=True).count()
    available_donors = Donor.objects.filter(is_active=True, availability_status='Available').count()
    total_requests = BloodRequest.objects.filter(is_active=True).count()
    emergency_requests = BloodRequest.objects.filter(is_active=True, emergency_level='Emergency').count()

    group_counts = {
        bg: Donor.objects.filter(is_active=True, availability_status='Available', blood_group=bg).count()
        for bg in BLOOD_GROUPS_ORDER
    }
    max_group_count = max(group_counts.values()) if group_counts else 0
    blood_group_breakdown = [
        {
            'group': bg,
            'count': count,
            'percent': round((count / max_group_count) * 100) if max_group_count else 0,
        }
        for bg, count in group_counts.items()
    ]

    context = {
        'total_donors': total_donors,
        'available_donors': available_donors,
        'total_requests': total_requests,
        'emergency_requests': emergency_requests,
        'blood_group_breakdown': blood_group_breakdown,
        'title': 'Patiya RedPulse - Blood Donor Directory'
    }
    return render(request, 'blood_requests/home.html', context)


def submit_blood_request(request):
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.is_active = True
            blood_request.save()
            
            messages.success(request, 'Blood request submitted successfully! We will review it shortly.')
            return redirect('blood_requests_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = BloodRequestForm()
    
    context = {
        'form': form,
        'title': 'Submit Blood Request'
    }
    return render(request, 'blood_requests/submit_request.html', context)


def compatibility_guide(request):
    context = {
        'title': 'Blood Compatibility Checker',
        'blood_groups': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
    }
    return render(request, 'blood_requests/compatibility.html', context)


def blood_requests_list(request):
    # রিকোয়েস্ট তৈরি হওয়ার সময় থেকে ২ দিন (৪৮ ঘণ্টা) পার হয়ে গেলে তা অটোমেটিক ফিল্টার আউট হয়ে যাবে
    cutoff_datetime = timezone.now() - timedelta(days=2)
    
    requests = BloodRequest.objects.filter(
        is_active=True, 
        request_date__gte=cutoff_datetime
    ).annotate(
        _priority=Case(
            When(emergency_level='Emergency', then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        )
    ).order_by('_priority', '-request_date')

    my_responses = set()
    donor = getattr(request.user, 'donor', None) if request.user.is_authenticated else None
    if donor is not None:
        my_responses = set(RequestResponse.objects.filter(donor=donor).values_list('request_id', flat=True))

    context = {
        'requests': requests,
        'my_responses': my_responses,
        'title': 'Blood Requests'
    }
    return render(request, 'blood_requests/requests_list.html', context)


@login_required
def respond_to_request(request, request_id):
    blood_request = get_object_or_404(BloodRequest, id=request_id, is_active=True)
    donor = getattr(request.user, 'donor', None)
    if donor is None:
        messages.error(request, 'Only registered donors can respond to a request.')
        return redirect('blood_requests_list')

    _, created = RequestResponse.objects.get_or_create(
        request=blood_request, donor=donor,
        defaults={'responder_name': donor.full_name, 'responder_phone': donor.mobile_number}
    )
    if created:
        messages.success(request, "Thanks! You're marked as responding — the requester can see your interest.")
    else:
        messages.info(request, "You've already marked yourself as responding to this request.")
    return redirect('blood_requests_list')


def hospital_directory(request):
    context = {
        'hospitals': Hospital.objects.all(),
        'title': 'Emergency Contacts & Hospitals',
    }
    return render(request, 'blood_requests/hospitals.html', context)


def faq(request):
    context = {'faqs': FAQS, 'title': 'Frequently Asked Questions'}
    return render(request, 'blood_requests/faq.html', context)


def awareness_list(request):
    context = {'articles': ARTICLES, 'title': 'Awareness'}
    return render(request, 'blood_requests/awareness_list.html', context)


def awareness_detail(request, slug):
    article = next((a for a in ARTICLES if a['slug'] == slug), None)
    if article is None:
        raise Http404
    context = {'article': article, 'title': article['title']}
    return render(request, 'blood_requests/awareness_detail.html', context)


def offline_page(request):
    return render(request, 'blood_requests/offline.html', {'title': 'Offline'})


def service_worker(request):
    from django.conf import settings
    from django.http import HttpResponse
    import os
    path = os.path.join(settings.BASE_DIR, 'static', 'service-worker.js')
    with open(path, 'rb') as f:
        content = f.read()
    response = HttpResponse(content, content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    return response


@login_required
def close_blood_request(request, request_id):
    """রক্ত দেওয়া হয়ে গেলে বা রিকোয়েস্ট সম্পন্ন হলে এটি সচল তালিকা থেকে বাদ দেবে"""
    blood_request = get_object_or_404(BloodRequest, id=request_id)
    blood_request.is_active = False
    blood_request.save()
    
    messages.success(request, 'রক্তের অনুরোধটি সফলভাবে সম্পন্ন ও তালিকা থেকে সরানো হয়েছে।')
    return redirect('blood_requests_list')