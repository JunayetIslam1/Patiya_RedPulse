# Patiya RedPulse - Blood Donor Directory

A simple, fast, and trustworthy blood donation platform for Patiya, Chattogram, Bangladesh.

## 🎯 Objective

Create a direct connection system between blood seekers and donors without any middleman complexity. This platform is designed for emergency use with mobile-first approach.

## ✨ Features

### For Blood Seekers
- **Search donors** by blood group, district, and upazila (with a Patiya union autocomplete)
- **View donor eligibility** status (auto-calculated, gender-aware: 90 days for men, 120 for women)
- **Direct calling, WhatsApp, and copy-to-clipboard** for every contact number
- **Submit blood requests** for emergency situations — emergencies are always pinned to the top of the list
- **Blood Compatibility Checker** — an interactive ABO/Rh reference at `/compatibility/`
- **Live blood-group availability chart** on the homepage

### For Donors
- **Simple registration** with minimal required fields
- **Automatic eligibility tracking** (gender-aware donation gap)
- **Availability status control** (Available/Not Available)
- **Life-Saver recognition badges** (Bronze/Silver/Gold) based on donation history
- **Profile management** with update capabilities

### Platform-wide
- **Bilingual: English and বাংলা**, switchable from the navbar, powered by Django's i18n framework
- **Light/Dark mode** toggle (persisted per device)
- **Emergency SOS** floating action button
- **Referral program** — every donor gets a unique referral link; registrations through it are credited, with Community Builder/Champion recognition
- **"I'm Responding"** — a donor can mark interest in a specific request with one click, visible to everyone viewing that request
- **"Near Me" distance search** — optional browser geolocation sorts donors by actual distance, no paid maps API involved
- **Donor profile photos**
- **Self-service donation logging** — donors can record their own past donations from the dashboard
- **Emergency contact / hospital directory** — a small, admin-managed list, seeded only with officially-sourced numbers (999, DGHS 16263, Patiya Upazila Health Complex)
- **FAQ and Awareness articles**
- **Printable personal emergency card**
- **Auto-expiring requests** — requests more than 2 days past their need-by date quietly drop out of the active list (not deleted)
- **Basic PWA support** — installable, works offline for previously-visited pages

### For Admins
- **Dashboard statistics** with real-time counts
- **Donor management** (block/unblock functionality)
- **Request management** (delete fake/spam requests)
- **Django admin panel** for full database access

## 🛠️ Technology Stack

- **Backend:** Django 4.2+ (Python)
- **Database:** SQLite3 (production-ready)
- **Frontend:** Bootstrap 5 + a custom design system (`static/css/style.css`)
- **i18n:** Django's built-in translation framework (English + Bangla, `locale/bn`)
- **Authentication:** Django built-in system
- **Security:** CSRF protection, password hashing

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone/Download the project**
   ```bash
   cd patiya_redpulse
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create your own superuser (admin account)**
   ```bash
   python manage.py createsuperuser
   ```
   No demo/default account ships with this project — you'll be prompted to
   set your own username, email, and password interactively.

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## 🔧 Configuration

### Settings to Customize

1. **Secret Key** - Change `SECRET_KEY` in `settings.py` for production
2. **Debug Mode** - Set `DEBUG = False` in production
3. **Allowed Hosts** - Add your domain/IP to `ALLOWED_HOSTS`
4. **Database** - Currently uses SQLite3 (suitable for this use case)

### Creating an Admin User

After running `python manage.py createsuperuser`, you can:
1. Login to Django admin at `/admin/`
2. Access the custom admin panel at `/admin-panel/`
3. Manage donors and requests from the dashboard

## 📱 Mobile-First Design

The platform is optimized for:
- Low-end Android phones
- Slow internet connections
- Touch interfaces
- Small screens
- Emergency situations

## 🔐 Security Features

- Django authentication system
- Password hashing (PBKDF2)
- CSRF protection on all forms
- Server-side validation
- No raw SQL queries
- XSS protection

## 🩸 Donor Eligibility Logic

The system automatically calculates, per Bangladesh Red Crescent / DGHS
guidance:
- Days since last donation
- Eligibility status (90-day minimum gap for men, 120 days for women)
- Visual indicators for eligible/not eligible donors

## 🌐 Language Support

The site is fully usable in English and বাংলা (Bangla). To add or update
translated strings after editing a template:
```bash
django-admin makemessages -l bn --no-wrap
# edit locale/bn/LC_MESSAGES/django.po
django-admin compilemessages
```

**Eligible Donors:** Green badge with checkmark
**Not Eligible:** Yellow badge with countdown days

## 📞 Direct Contact System

- Phone numbers are publicly visible
- One-click calling using `tel:` protocol
- No OTP or SMS verification
- Direct connection between seeker and donor

## 🏥 Emergency Handling

- Emergency requests highlighted in red
- Pulsing animation for visual attention
- Emergency badge on request cards
- Admin dashboard shows emergency count

## 🌍 Location Coverage

Designed specifically for:
- **Country:** Bangladesh
- **Primary Area:** Patiya, Chattogram
- **District/Upazila system** for precise location

## 📊 Database Schema

### Donor Model
- User account (Django User)
- Personal information (name, age, gender)
- Blood group and location
- Last donation date and eligibility
- Contact information (mobile required, email optional)

### BloodRequest Model
- Patient information
- Required blood group and bags
- Hospital details
- Emergency level and required date
- Contact information

## 🚀 Production Deployment

For production deployment:

1. **Security**
   - Change SECRET_KEY
   - Set DEBUG = False
   - Configure ALLOWED_HOSTS
   - Use HTTPS

2. **Performance**
   - Use a production web server (Gunicorn, uWSGI)
   - Configure static file serving
   - Set up database backups

3. **Monitoring**
   - Set up error logging
   - Monitor server resources
   - Regular database maintenance

## 🤝 Contributing

This is a humanitarian project. To contribute:
1. Test the platform thoroughly
2. Report bugs and issues
3. Suggest improvements
4. Help spread awareness
5. Register as a donor

## ⚠️ Important Disclaimers

1. **Medical Responsibility:** This platform only connects donors and seekers. Medical verification is the responsibility of the parties involved.

2. **Identity Verification:** Always verify donor identity and blood compatibility before transfusion.

3. **Emergency Situations:** For life-threatening emergencies, contact the nearest hospital immediately.

4. **Data Privacy:** Phone numbers are publicly visible. Register only if you consent to this.

5. **Humanitarian Use:** This platform is for genuine blood donation needs only.

## 📞 Support

For technical support or questions:
- Check the admin panel for user management
- Review Django admin for database access
- Monitor the platform for fake/spam content

## 📄 License

This project is created for humanitarian purposes. Use it to save lives in Patiya and beyond.

---

**Built with ❤️ for the people of Patiya, Chattogram.**

*Saving lives through direct connection.*