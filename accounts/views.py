from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import DonorRegistrationForm, DonorUpdateForm, LogDonationForm
from .models import Donor, DonationHistory

def register_donor(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.donor.referred_by:
                messages.success(request, f"Registration successful! You were referred by {user.donor.referred_by.full_name} — thank you both for growing the donor community.")
            else:
                messages.success(request, 'Registration successful! Welcome to Patiya RedPulse.')
            return redirect('dashboard') # রেজিস্ট্রেশনের পর ড্যাশবোর্ডে যাবে
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        # Feature: referral program — capture ?ref=CODE from a shared link
        # and silently prefill the (hidden) referral_code field.
        ref_code = request.GET.get('ref', '').strip().upper()
        initial = {'referral_code': ref_code} if ref_code else {}
        form = DonorRegistrationForm(initial=initial)

    referrer = None
    ref_code = request.GET.get('ref', '').strip().upper()
    if ref_code:
        referrer = Donor.objects.filter(referral_code=ref_code).first()

    context = {
        'form': form,
        'title': 'Donor Registration',
        'referrer': referrer,
    }
    return render(request, 'accounts/register.html', context)

@login_required
def dashboard(request):
    """ইউজার ড্যাশবোর্ড যা রক্তদানের ইতিহাস এবং এলিজিবিলিটি দেখাবে"""
    try:
        donor = request.user.donor
        donations = donor.donations.all() # এটি DonationHistory থেকে ডাটা আনবে

        if request.method == 'POST':
            log_form = LogDonationForm(request.POST)
            if log_form.is_valid():
                DonationHistory.objects.create(
                    donor=donor,
                    donation_date=log_form.cleaned_data['donation_date'],
                    hospital_name=log_form.cleaned_data.get('hospital_name', ''),
                    note=log_form.cleaned_data.get('note', ''),
                )
                # Keep last_donation_date in sync if this is the most recent one.
                if log_form.cleaned_data['donation_date'] >= donor.last_donation_date:
                    donor.last_donation_date = log_form.cleaned_data['donation_date']
                    donor.save()
                messages.success(request, 'Donation logged — thank you for saving a life!')
                return redirect('dashboard')
            else:
                for field, errors in log_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
        else:
            log_form = LogDonationForm()

        referral_link = request.build_absolute_uri(f"/accounts/register/?ref={donor.referral_code}")

        context = {
            'donor': donor,
            'donations': donations,
            'log_form': log_form,
            'referral_link': referral_link,
            'title': 'Donor Dashboard'
        }
        return render(request, 'accounts/dashboard.html', context)
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found.')
        return redirect('register')

@login_required
def profile(request):
    try:
        donor = request.user.donor
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        form = DonorUpdateForm(request.POST, request.FILES, instance=donor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = DonorUpdateForm(instance=donor)
    
    context = {
        'form': form,
        'donor': donor,
        'title': 'My Profile'
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def emergency_card(request):
    """Feature: a print-friendly personal emergency card showing the
    donor's blood group and the platform's verified emergency numbers, so
    it can be printed and kept in a wallet."""
    try:
        donor = request.user.donor
    except Donor.DoesNotExist:
        messages.error(request, 'Donor profile not found.')
        return redirect('home')

    from blood_requests.models import Hospital
    context = {
        'donor': donor,
        'hospitals': Hospital.objects.filter(display_order__lte=3),
        'title': 'Emergency Card',
    }
    return render(request, 'accounts/emergency_card.html', context)


def donor_list(request):
    blood_group = request.GET.get('blood_group', '')
    district = request.GET.get('district', '')
    upazila = request.GET.get('upazila', '')
    near_lat = request.GET.get('lat', '')
    near_lng = request.GET.get('lng', '')

    donors = Donor.objects.filter(is_active=True) # সব ডোনার দেখাবে ফিল্টারিং এর জন্য
    
    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    if district:
        donors = donors.filter(district__icontains=district)
    if upazila:
        donors = donors.filter(upazila__icontains=upazila)

    donors = list(donors)

    # Feature: "Near Me" distance-based sort. Uses the browser's geolocation
    # (opt-in button) rather than any paid mapping API. Donors who haven't
    # set a location are kept, just sorted to the end.
    sorted_by_distance = False
    if near_lat and near_lng:
        try:
            lat = float(near_lat)
            lng = float(near_lng)
            for d in donors:
                d.distance_km = d.distance_km_from(lat, lng)
            donors.sort(key=lambda d: (d.distance_km is None, d.distance_km if d.distance_km is not None else 0))
            sorted_by_distance = True
        except (TypeError, ValueError):
            pass

    context = {
        'donors': donors,
        'blood_groups': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        'selected_blood_group': blood_group,
        'selected_district': district,
        'selected_upazila': upazila,
        'sorted_by_distance': sorted_by_distance,
        'title': 'Find Blood Donors'
    }
    return render(request, 'accounts/donor_list.html', context)
