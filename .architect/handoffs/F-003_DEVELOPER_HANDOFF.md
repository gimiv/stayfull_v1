# Developer Handoff: F-003 Dynamic Commerce Engine

**Priority**: P1 - Revenue Generator
**Effort**: 80 hours (~10 days)
**Status**: ⏳ READY FOR IMPLEMENTATION
**Specification**: `.architect/features/F-003_DYNAMIC_COMMERCE_ENGINE.md`
**Standards**: `.architect/DEVELOPMENT_STANDARDS.md`
**Dependencies**: F-002 (AI Onboarding) MUST be complete - provides initial data

---

## 🎯 What You're Building

**Dynamic Commerce Engine = The Shopify for Hotels**

Transform hotel onboarding data into a **live, bookable website** in seconds.

### The Vision

**Industry Standard:**
- Hotel website: 3-6 months, $5,000-$15,000
- Booking engine: Separate platform, monthly fees, complex integration
- Content creation: Manual, time-consuming, rarely updated

**Stayfull:**
- ✅ Complete website + booking engine: **Generated during 10-minute onboarding**
- ✅ Single source of truth: Admin changes → Website updates instantly
- ✅ AI-generated content: Things To Do, Events, enhanced descriptions
- ✅ Professional SEO: Meta tags, sitemaps, schema markup
- ✅ Stripe payments: Integrated, PCI-compliant, commission routing

### The Litmus Test

> "Can a consumer purchase a room tonight?"

If YES → Ship it. Everything else is polish.

---

## 📊 Implementation Phases

### Phase 1: Website Foundation (10 hours)

**Goal**: Create database models and URL routing for hotel websites.

**Models to Create:**

```python
# apps/website/models.py

class WebsiteConfig(models.Model):
    """
    Website configuration for a hotel.
    Two-stage publishing: Draft → Published
    """
    hotel = models.OneToOneField('hotels.Hotel', on_delete=models.CASCADE, related_name='website_config')

    # Two-stage publishing
    draft_config = models.JSONField(default=dict, help_text="Unpublished changes")
    published_config = models.JSONField(default=dict, help_text="Live website configuration")

    # Publishing metadata
    published_at = models.DateTimeField(null=True, blank=True)
    published_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)

    # Version control (last 10 changes)
    version_history = models.JSONField(default=list, help_text="Last 10 published versions")

    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    # Custom domain (future)
    custom_domain = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'website_configs'

    def publish(self):
        """Publish draft to live site with version control."""
        # Save current published version to history
        if self.published_config:
            self.version_history.insert(0, {
                'config': self.published_config,
                'published_at': self.published_at.isoformat() if self.published_at else None,
                'published_by': self.published_by.username if self.published_by else None
            })
            # Keep only last 10 versions
            self.version_history = self.version_history[:10]

        # Promote draft to published
        self.published_config = self.draft_config.copy()
        self.published_at = timezone.now()
        self.save()

    def revert_to_version(self, version_index: int):
        """Revert to a previous version."""
        if 0 <= version_index < len(self.version_history):
            old_version = self.version_history[version_index]
            self.draft_config = old_version['config'].copy()
            self.save()
```

```python
# apps/website/models.py

class ThingsToDoItem(models.Model):
    """
    AI-generated local attraction (museums, restaurants, activities).
    Auto-updated monthly via cron job.
    """
    hotel = models.ForeignKey('hotels.Hotel', on_delete=models.CASCADE, related_name='things_to_do')

    # Content
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=[
        ('museum', 'Museums & Culture'),
        ('outdoor', 'Outdoor & Nature'),
        ('food', 'Food & Drink'),
        ('nightlife', 'Nightlife & Entertainment'),
        ('shopping', 'Shopping'),
        ('family', 'Family Activities'),
    ])

    # Location
    address = models.CharField(max_length=255, blank=True)
    distance_miles = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    # External data
    google_place_id = models.CharField(max_length=255, blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    price_level = models.IntegerField(null=True, help_text="1-4 ($-$$$$)")
    website_url = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    # Images
    image_url = models.URLField(blank=True, help_text="Google Places photo or stock image")

    # Metadata
    season = models.CharField(max_length=20, choices=[
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('fall', 'Fall'),
        ('winter', 'Winter'),
        ('year_round', 'Year Round'),
    ], default='year_round')

    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Display order")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'things_to_do_items'
        ordering = ['order', '-rating', 'name']
        indexes = [
            models.Index(fields=['hotel', 'category', 'is_active']),
        ]


class Event(models.Model):
    """
    AI-generated local event (concerts, festivals, sports).
    Auto-updated monthly via cron job.
    """
    hotel = models.ForeignKey('hotels.Hotel', on_delete=models.CASCADE, related_name='events')

    # Content
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=[
        ('concert', 'Concerts & Music'),
        ('festival', 'Festivals'),
        ('sports', 'Sports'),
        ('theater', 'Theater & Arts'),
        ('food', 'Food & Wine'),
        ('community', 'Community Events'),
    ])

    # Dates
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)

    # Location
    venue_name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    distance_miles = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    # External data
    source = models.CharField(max_length=50, choices=[
        ('ticketmaster', 'Ticketmaster'),
        ('eventbrite', 'Eventbrite'),
        ('google', 'Google Events'),
        ('manual', 'Manual Entry'),
    ])
    external_id = models.CharField(max_length=255, blank=True)
    ticket_url = models.URLField(blank=True)
    price_range = models.CharField(max_length=100, blank=True, help_text="e.g., '$50-$150'")

    # Images
    image_url = models.URLField(blank=True)

    # Metadata
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        ordering = ['start_date', 'start_time']
        indexes = [
            models.Index(fields=['hotel', 'start_date', 'is_active']),
            models.Index(fields=['hotel', 'is_featured']),
        ]

    @property
    def is_past(self):
        """Check if event has already happened."""
        end_date = self.end_date or self.start_date
        return end_date < timezone.now().date()
```

**Create Django App:**

```bash
python manage.py startapp website
# Move to apps/website/
# Add 'apps.website' to INSTALLED_APPS
```

**URL Routing:**

```python
# apps/website/urls.py

from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    # Public website routes
    path('<slug:hotel_slug>/', views.homepage, name='homepage'),
    path('<slug:hotel_slug>/rooms/', views.rooms, name='rooms'),
    path('<slug:hotel_slug>/offers/', views.offers, name='offers'),
    path('<slug:hotel_slug>/things-to-do/', views.things_to_do, name='things_to_do'),
    path('<slug:hotel_slug>/events/', views.events, name='events'),
    path('<slug:hotel_slug>/amenities/', views.amenities, name='amenities'),
    path('<slug:hotel_slug>/dining/', views.dining, name='dining'),
    path('<slug:hotel_slug>/shop/', views.shop, name='shop'),
    path('<slug:hotel_slug>/reviews/', views.reviews, name='reviews'),
    path('<slug:hotel_slug>/location/', views.location, name='location'),

    # Booking flow
    path('<slug:hotel_slug>/book/', views.booking_start, name='booking_start'),
    path('<slug:hotel_slug>/book/rooms/', views.booking_select_room, name='booking_select_room'),
    path('<slug:hotel_slug>/book/details/', views.booking_guest_details, name='booking_guest_details'),
    path('<slug:hotel_slug>/book/payment/', views.booking_payment, name='booking_payment'),
    path('<slug:hotel_slug>/book/confirmation/<uuid:reservation_id>/', views.booking_confirmation, name='booking_confirmation'),
]
```

```python
# config/urls.py (main project urls)

urlpatterns = [
    ...
    path('', include('apps.website.urls')),  # Public hotel websites
]
```

**Tests:**

- [ ] WebsiteConfig model creates correctly
- [ ] publish() method saves version history
- [ ] revert_to_version() restores old config
- [ ] ThingsToDoItem and Event models create correctly
- [ ] URL routing works for hotel slug
- [ ] Organization isolation maintained

---

### Phase 2: Component System (12 hours)

**Goal**: Build 11 website components with visibility logic.

**Component Structure:**

```python
# apps/website/services/component_renderer.py

class ComponentRenderer:
    """
    Renders website components based on published_config.

    Components only show if they have content (except Hero + Rooms = always visible).
    """

    COMPONENTS = [
        {'id': 'hero', 'name': 'Hero Section', 'always_visible': True},
        {'id': 'intro', 'name': 'Introduction', 'always_visible': False},
        {'id': 'rooms', 'name': 'Rooms & Suites', 'always_visible': True},
        {'id': 'offers', 'name': 'Special Offers', 'always_visible': False},
        {'id': 'things_to_do', 'name': 'Things To Do', 'always_visible': False},
        {'id': 'events', 'name': 'Local Events', 'always_visible': False},
        {'id': 'amenities', 'name': 'Amenities', 'always_visible': False},
        {'id': 'dining', 'name': 'Dining', 'always_visible': False},
        {'id': 'shop', 'name': 'Shop', 'always_visible': False},
        {'id': 'reviews', 'name': 'Guest Reviews', 'always_visible': False},
        {'id': 'location', 'name': 'Location', 'always_visible': False},
    ]

    def __init__(self, hotel, config):
        self.hotel = hotel
        self.config = config

    def get_visible_components(self):
        """Return list of components that should be visible."""
        visible = []

        for component in self.COMPONENTS:
            if component['always_visible']:
                visible.append(component)
            elif self.has_content(component['id']):
                visible.append(component)

        return visible

    def has_content(self, component_id):
        """Check if component has content to display."""
        if component_id == 'intro':
            return bool(self.config.get('intro_text'))

        elif component_id == 'offers':
            # Check if hotel has active offers
            return self.hotel.offers.filter(is_active=True).exists()

        elif component_id == 'things_to_do':
            # Always visible (AI-generated during onboarding)
            return self.hotel.things_to_do.filter(is_active=True).exists()

        elif component_id == 'events':
            # Always visible (AI-generated during onboarding)
            return self.hotel.events.filter(is_active=True, start_date__gte=timezone.now().date()).exists()

        elif component_id == 'amenities':
            return bool(self.hotel.amenities)

        elif component_id == 'dining':
            return bool(self.config.get('dining_description'))

        elif component_id == 'shop':
            return self.hotel.merchandise.filter(is_active=True).exists()

        elif component_id == 'reviews':
            return self.hotel.reviews.filter(is_approved=True).exists()

        elif component_id == 'location':
            return bool(self.hotel.address)

        return False

    def render_component(self, component_id, context=None):
        """Render a specific component's HTML."""
        context = context or {}
        context['hotel'] = self.hotel
        context['config'] = self.config

        template_name = f'website/components/{component_id}.html'
        return render_to_string(template_name, context)
```

**Component Templates:**

Create these templates:

```
apps/website/templates/website/components/
├── hero.html                    # Hero section (image/video, CTA)
├── intro.html                   # Hotel introduction text
├── rooms.html                   # Room types carousel
├── offers.html                  # Special offers
├── things_to_do.html            # AI-generated attractions
├── events.html                  # AI-generated events
├── amenities.html               # Hotel amenities grid
├── dining.html                  # Dining information
├── shop.html                    # Merchandise (if applicable)
├── reviews.html                 # Guest reviews
└── location.html                # Map + address
```

**Example Component Template:**

```html
<!-- apps/website/templates/website/components/hero.html -->

{% load static %}

<section class="hero relative h-screen">
  {% if config.hero_type == 'video' %}
    <video autoplay muted loop class="absolute inset-0 w-full h-full object-cover">
      <source src="{{ config.hero_video_url }}" type="video/mp4">
    </video>
  {% elif config.hero_type == 'slideshow' %}
    <div class="hero-slideshow absolute inset-0">
      {% for image in config.hero_images %}
        <img src="{{ image.url }}" alt="{{ image.alt }}" class="absolute inset-0 w-full h-full object-cover">
      {% endfor %}
    </div>
  {% else %}
    <img src="{{ config.hero_image_url }}" alt="{{ hotel.name }}" class="absolute inset-0 w-full h-full object-cover">
  {% endif %}

  <!-- Overlay -->
  <div class="absolute inset-0 bg-black bg-opacity-40"></div>

  <!-- Content -->
  <div class="relative z-10 h-full flex items-center justify-center text-center text-white px-4">
    <div>
      <h1 class="text-5xl md:text-7xl font-bold mb-4">{{ hotel.name }}</h1>
      <p class="text-xl md:text-2xl mb-8">{{ config.hero_tagline|default:hotel.tagline }}</p>
      <a href="{% url 'website:booking_start' hotel.slug %}" class="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded-lg text-lg transition">
        Book Now
      </a>
    </div>
  </div>
</section>
```

**Tests:**

- [ ] ComponentRenderer identifies visible components correctly
- [ ] Hero + Rooms always show
- [ ] Other components show only with content
- [ ] All 11 component templates render without errors
- [ ] Component ordering matches config

---

### Phase 3: Website Manager (Admin Interface) (14 hours)

**Goal**: Build admin interface for hotel owners to manage their website.

**Views:**

```python
# apps/website/views.py (admin views)

@login_required
@organization_required
def website_manager(request):
    """
    Website management interface.
    Left panel: Settings tabs
    Right panel: Live preview
    """
    hotel = get_object_or_404(Hotel, organization=request.user.staff.organization)
    config, created = WebsiteConfig.objects.get_or_create(hotel=hotel)

    # If config was just created, initialize from onboarding data
    if created:
        config.draft_config = initialize_website_config(hotel)
        config.save()

    context = {
        'hotel': hotel,
        'config': config,
        'themes': get_available_themes(),
        'components': ComponentRenderer.COMPONENTS,
    }

    return render(request, 'website/admin/manager.html', context)


@login_required
@organization_required
@require_http_methods(["POST"])
def save_draft(request):
    """Save changes to draft (not published)."""
    hotel = get_object_or_404(Hotel, organization=request.user.staff.organization)
    config = hotel.website_config

    # Update draft_config with posted data
    updated_config = json.loads(request.body)
    config.draft_config.update(updated_config)
    config.save()

    return JsonResponse({'success': True, 'message': 'Draft saved'})


@login_required
@organization_required
@require_http_methods(["POST"])
def publish_website(request):
    """Publish draft to live website."""
    hotel = get_object_or_404(Hotel, organization=request.user.staff.organization)
    config = hotel.website_config

    # Publish (saves version history)
    config.published_by = request.user
    config.publish()

    return JsonResponse({
        'success': True,
        'message': 'Website published!',
        'published_at': config.published_at.isoformat()
    })


@login_required
@organization_required
def preview_draft(request):
    """Preview draft website (not published)."""
    hotel = get_object_or_404(Hotel, organization=request.user.staff.organization)
    config = hotel.website_config

    # Use draft_config instead of published_config
    renderer = ComponentRenderer(hotel, config.draft_config)

    context = {
        'hotel': hotel,
        'config': config.draft_config,
        'components': renderer.get_visible_components(),
        'is_preview': True,
    }

    return render(request, 'website/preview.html', context)
```

**Website Manager Template:**

```html
<!-- apps/website/templates/website/admin/manager.html -->

{% extends "base.html" %}

{% block content %}
<div class="flex h-screen bg-gray-50">
  <!-- Left Panel: Settings -->
  <div class="w-1/2 bg-white border-r overflow-y-auto">
    <div class="p-6">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold">Website Manager</h1>
        <div class="space-x-2">
          <button
            id="save-draft-btn"
            class="px-4 py-2 border rounded hover:bg-gray-50"
            hx-post="{% url 'website:save_draft' %}"
            hx-include="#config-form"
          >
            Save Draft
          </button>
          <button
            id="publish-btn"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            hx-post="{% url 'website:publish_website' %}"
            hx-confirm="Publish changes to live website?"
          >
            Publish
          </button>
        </div>
      </div>

      <!-- Tabs -->
      <div class="tabs mb-6">
        <button class="tab active" data-tab="general">General</button>
        <button class="tab" data-tab="theme">Theme</button>
        <button class="tab" data-tab="components">Components</button>
        <button class="tab" data-tab="seo">SEO</button>
      </div>

      <!-- Tab Content -->
      <form id="config-form">
        {% csrf_token %}

        <!-- General Tab -->
        <div id="general-tab" class="tab-content active">
          <h2 class="text-lg font-semibold mb-4">General Settings</h2>

          <div class="mb-4">
            <label class="block text-sm font-medium mb-2">Hero Type</label>
            <select name="hero_type" class="w-full border rounded p-2">
              <option value="image" {% if config.draft_config.hero_type == 'image' %}selected{% endif %}>Single Image</option>
              <option value="slideshow" {% if config.draft_config.hero_type == 'slideshow' %}selected{% endif %}>Slideshow</option>
              <option value="video" {% if config.draft_config.hero_type == 'video' %}selected{% endif %}>Video</option>
            </select>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium mb-2">Hero Tagline</label>
            <input
              type="text"
              name="hero_tagline"
              value="{{ config.draft_config.hero_tagline }}"
              class="w-full border rounded p-2"
              placeholder="Experience luxury on the coast"
            >
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium mb-2">Introduction Text</label>
            <textarea
              name="intro_text"
              rows="4"
              class="w-full border rounded p-2"
              placeholder="Welcome to..."
            >{{ config.draft_config.intro_text }}</textarea>
          </div>
        </div>

        <!-- Theme Tab -->
        <div id="theme-tab" class="tab-content hidden">
          <h2 class="text-lg font-semibold mb-4">Theme Settings</h2>

          <div class="mb-4">
            <label class="block text-sm font-medium mb-2">Select Theme</label>
            <div class="grid grid-cols-2 gap-4">
              {% for theme in themes %}
                <div class="border rounded p-4 cursor-pointer hover:border-blue-500 {% if config.draft_config.theme == theme.id %}border-blue-500{% endif %}">
                  <img src="{{ theme.preview_image }}" alt="{{ theme.name }}" class="mb-2 rounded">
                  <h3 class="font-medium">{{ theme.name }}</h3>
                </div>
              {% endfor %}
            </div>
          </div>
        </div>

        <!-- Components Tab -->
        <div id="components-tab" class="tab-content hidden">
          <h2 class="text-lg font-semibold mb-4">Component Order</h2>
          <p class="text-sm text-gray-600 mb-4">Drag to reorder sections</p>

          <div id="component-list" class="space-y-2">
            {% for component in components %}
              <div class="component-item border rounded p-3 cursor-move flex justify-between items-center" data-component-id="{{ component.id }}">
                <span>{{ component.name }}</span>
                <span class="text-sm text-gray-500">
                  {% if component.always_visible %}
                    <span class="text-green-600">Always Visible</span>
                  {% else %}
                    <span class="text-gray-400">Auto-hide if empty</span>
                  {% endif %}
                </span>
              </div>
            {% endfor %}
          </div>
        </div>

        <!-- SEO Tab -->
        <div id="seo-tab" class="tab-content hidden">
          <h2 class="text-lg font-semibold mb-4">SEO Settings</h2>

          <div class="mb-4">
            <label class="block text-sm font-medium mb-2">Meta Title (60 chars max)</label>
            <input
              type="text"
              name="meta_title"
              value="{{ config.meta_title }}"
              maxlength="60"
              class="w-full border rounded p-2"
            >
            <p class="text-xs text-gray-500 mt-1">{{ config.meta_title|length }}/60 characters</p>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium mb-2">Meta Description (160 chars max)</label>
            <textarea
              name="meta_description"
              maxlength="160"
              rows="3"
              class="w-full border rounded p-2"
            >{{ config.meta_description }}</textarea>
            <p class="text-xs text-gray-500 mt-1">{{ config.meta_description|length }}/160 characters</p>
          </div>
        </div>
      </form>
    </div>
  </div>

  <!-- Right Panel: Live Preview -->
  <div class="w-1/2 bg-gray-100 overflow-y-auto">
    <div class="sticky top-0 bg-white border-b p-4 flex justify-between items-center">
      <h2 class="font-semibold">Preview</h2>
      <div class="space-x-2">
        <button id="desktop-preview" class="px-3 py-1 border rounded bg-blue-600 text-white">Desktop</button>
        <button id="mobile-preview" class="px-3 py-1 border rounded">Mobile</button>
      </div>
    </div>

    <iframe
      id="preview-iframe"
      src="{% url 'website:preview_draft' %}"
      class="w-full h-full bg-white"
      style="min-height: calc(100vh - 60px);"
    ></iframe>
  </div>
</div>

<script>
  // Auto-update preview on changes
  const form = document.getElementById('config-form');
  const iframe = document.getElementById('preview-iframe');

  form.addEventListener('input', debounce(() => {
    // Save draft
    htmx.trigger('#save-draft-btn', 'click');

    // Reload preview
    iframe.contentWindow.location.reload();
  }, 1000));

  // Tab switching
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const tabName = tab.dataset.tab;

      // Update active tab
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      // Show tab content
      document.querySelectorAll('.tab-content').forEach(content => content.classList.add('hidden'));
      document.getElementById(`${tabName}-tab`).classList.remove('hidden');
    });
  });

  // Mobile preview toggle
  document.getElementById('mobile-preview').addEventListener('click', () => {
    iframe.style.maxWidth = '375px';
    iframe.style.margin = '0 auto';
  });

  document.getElementById('desktop-preview').addEventListener('click', () => {
    iframe.style.maxWidth = '100%';
    iframe.style.margin = '0';
  });
</script>
{% endblock %}
```

**Tests:**

- [ ] Website Manager loads for authenticated hotel owner
- [ ] Save Draft updates draft_config
- [ ] Publish button publishes draft to live
- [ ] Preview iframe shows draft website
- [ ] Desktop/Mobile toggle works
- [ ] Tab switching works
- [ ] Component reordering saves correctly

---

### Phase 4: Booking Engine (16 hours)

**Goal**: Build 4-step booking flow with real-time availability.

**Booking Models:**

```python
# apps/bookings/models.py

class Reservation(models.Model):
    """
    Guest reservation (created via booking engine or admin).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relationships
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE)
    hotel = models.ForeignKey('hotels.Hotel', on_delete=models.CASCADE, related_name='reservations')
    room_type = models.ForeignKey('hotels.RoomType', on_delete=models.PROTECT, related_name='reservations')
    room = models.ForeignKey('hotels.Room', on_delete=models.SET_NULL, null=True, blank=True, related_name='reservations')

    # Guest info
    guest_name = models.CharField(max_length=200)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)
    guest_country = models.CharField(max_length=2, help_text="ISO country code")

    # Stay details
    check_in = models.DateField()
    check_out = models.DateField()
    num_guests = models.IntegerField()
    num_adults = models.IntegerField(default=1)
    num_children = models.IntegerField(default=0)

    # Pricing
    nightly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    num_nights = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    taxes = models.DecimalField(max_digits=10, decimal_places=2)
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Payment
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_paid = models.BooleanField(default=False)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2)

    # Status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ], default='pending')

    # Confirmation
    confirmation_code = models.CharField(max_length=10, unique=True, editable=False)

    # Special requests
    special_requests = models.TextField(blank=True)

    # Metadata
    source = models.CharField(max_length=50, choices=[
        ('website', 'Hotel Website'),
        ('admin', 'Manual Entry'),
        ('ota', 'OTA'),
    ], default='website')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reservations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'hotel', 'check_in']),
            models.Index(fields=['confirmation_code']),
            models.Index(fields=['guest_email']),
        ]

    def save(self, *args, **kwargs):
        if not self.confirmation_code:
            self.confirmation_code = self.generate_confirmation_code()
        super().save(*args, **kwargs)

    def generate_confirmation_code(self):
        """Generate unique 10-character confirmation code."""
        import random
        import string
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            if not Reservation.objects.filter(confirmation_code=code).exists():
                return code


class Payment(models.Model):
    """
    Payment record (linked to Stripe Payment Intent).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relationships
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='payments')

    # Stripe
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True)

    # Amount
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    # Status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ], default='pending')

    # Metadata
    payment_method = models.CharField(max_length=50, blank=True)
    last4 = models.CharField(max_length=4, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
```

**Booking Views:**

```python
# apps/bookings/views.py

def booking_start(request, hotel_slug):
    """
    Step 1: Select dates and number of guests.
    """
    hotel = get_object_or_404(Hotel, slug=hotel_slug)

    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        num_adults = int(request.POST.get('num_adults', 1))
        num_children = int(request.POST.get('num_children', 0))

        # Store in session
        request.session['booking'] = {
            'check_in': check_in,
            'check_out': check_out,
            'num_adults': num_adults,
            'num_children': num_children,
        }

        return redirect('website:booking_select_room', hotel_slug=hotel.slug)

    context = {
        'hotel': hotel,
        'min_date': timezone.now().date().isoformat(),
    }

    return render(request, 'bookings/step1_dates.html', context)


def booking_select_room(request, hotel_slug):
    """
    Step 2: Select room type.
    Shows available rooms for selected dates with real-time pricing.
    """
    hotel = get_object_or_404(Hotel, slug=hotel_slug)
    booking_data = request.session.get('booking', {})

    if not booking_data:
        return redirect('website:booking_start', hotel_slug=hotel.slug)

    check_in = datetime.fromisoformat(booking_data['check_in']).date()
    check_out = datetime.fromisoformat(booking_data['check_out']).date()
    num_guests = booking_data['num_adults'] + booking_data['num_children']

    # Get available room types
    available_rooms = get_available_room_types(
        hotel=hotel,
        check_in=check_in,
        check_out=check_out,
        num_guests=num_guests
    )

    if request.method == 'POST':
        room_type_id = request.POST.get('room_type_id')

        # Update session
        request.session['booking']['room_type_id'] = room_type_id
        request.session.modified = True

        return redirect('website:booking_guest_details', hotel_slug=hotel.slug)

    context = {
        'hotel': hotel,
        'available_rooms': available_rooms,
        'check_in': check_in,
        'check_out': check_out,
        'num_nights': (check_out - check_in).days,
    }

    return render(request, 'bookings/step2_rooms.html', context)


def booking_guest_details(request, hotel_slug):
    """
    Step 3: Collect guest information.
    """
    hotel = get_object_or_404(Hotel, slug=hotel_slug)
    booking_data = request.session.get('booking', {})

    if not booking_data or 'room_type_id' not in booking_data:
        return redirect('website:booking_start', hotel_slug=hotel.slug)

    if request.method == 'POST':
        # Store guest info in session
        booking_data.update({
            'guest_name': request.POST.get('guest_name'),
            'guest_email': request.POST.get('guest_email'),
            'guest_phone': request.POST.get('guest_phone'),
            'guest_country': request.POST.get('guest_country'),
            'special_requests': request.POST.get('special_requests', ''),
        })

        request.session['booking'] = booking_data
        request.session.modified = True

        return redirect('website:booking_payment', hotel_slug=hotel.slug)

    context = {
        'hotel': hotel,
        'booking_data': booking_data,
    }

    return render(request, 'bookings/step3_details.html', context)


def booking_payment(request, hotel_slug):
    """
    Step 4: Payment with Stripe.
    Creates Payment Intent and shows Stripe Elements.
    """
    hotel = get_object_or_404(Hotel, slug=hotel_slug)
    booking_data = request.session.get('booking', {})

    if not booking_data or 'guest_email' not in booking_data:
        return redirect('website:booking_start', hotel_slug=hotel.slug)

    # Calculate pricing
    check_in = datetime.fromisoformat(booking_data['check_in']).date()
    check_out = datetime.fromisoformat(booking_data['check_out']).date()
    num_nights = (check_out - check_in).days

    room_type = RoomType.objects.get(id=booking_data['room_type_id'])

    # Get rate (base rate for MVP)
    nightly_rate = room_type.base_rate
    subtotal = nightly_rate * num_nights

    # Calculate taxes (from hotel settings)
    tax_rate = hotel.tax_rate or Decimal('0.10')
    taxes = subtotal * tax_rate

    total = subtotal + taxes

    # Calculate deposit (from hotel payment policy)
    deposit_percent = hotel.deposit_percent or Decimal('50')
    deposit_amount = total * (deposit_percent / Decimal('100'))
    balance_due = total - deposit_amount

    # Create Stripe Payment Intent
    payment_intent = create_payment_intent(
        hotel=hotel,
        amount=deposit_amount,
        guest_email=booking_data['guest_email'],
        metadata={
            'hotel_id': str(hotel.id),
            'room_type_id': str(room_type.id),
            'check_in': booking_data['check_in'],
            'check_out': booking_data['check_out'],
        }
    )

    context = {
        'hotel': hotel,
        'room_type': room_type,
        'booking_data': booking_data,
        'subtotal': subtotal,
        'taxes': taxes,
        'total': total,
        'deposit_amount': deposit_amount,
        'balance_due': balance_due,
        'num_nights': num_nights,
        'nightly_rate': nightly_rate,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'client_secret': payment_intent.client_secret,
    }

    return render(request, 'bookings/step4_payment.html', context)


@require_http_methods(["POST"])
def booking_confirmation(request, hotel_slug, reservation_id):
    """
    Booking confirmation page (after successful payment).
    """
    hotel = get_object_or_404(Hotel, slug=hotel_slug)
    reservation = get_object_or_404(Reservation, id=reservation_id, hotel=hotel)

    # Send confirmation emails/SMS
    send_confirmation_to_guest(reservation)
    send_notification_to_hotel(reservation)

    # Clear booking session
    if 'booking' in request.session:
        del request.session['booking']

    context = {
        'hotel': hotel,
        'reservation': reservation,
    }

    return render(request, 'bookings/confirmation.html', context)
```

**Availability Service:**

```python
# apps/bookings/services/availability.py

def get_available_room_types(hotel, check_in, check_out, num_guests):
    """
    Get available room types with real-time pricing.

    Logic:
    1. Find room types that can accommodate num_guests
    2. Check if any rooms of that type are available
    3. Calculate pricing for the date range
    4. Return sorted by price
    """
    room_types = hotel.room_types.filter(
        max_occupancy__gte=num_guests,
        is_active=True
    )

    available = []

    for room_type in room_types:
        # Check availability
        total_rooms = room_type.rooms.filter(is_active=True).count()
        booked_rooms = get_booked_rooms_count(room_type, check_in, check_out)

        available_count = total_rooms - booked_rooms

        if available_count > 0:
            # Calculate pricing
            num_nights = (check_out - check_in).days
            nightly_rate = room_type.base_rate  # MVP: Use base rate
            subtotal = nightly_rate * num_nights

            available.append({
                'room_type': room_type,
                'available_count': available_count,
                'nightly_rate': nightly_rate,
                'subtotal': subtotal,
            })

    # Sort by price (lowest first)
    available.sort(key=lambda x: x['subtotal'])

    return available


def get_booked_rooms_count(room_type, check_in, check_out):
    """
    Count how many rooms of this type are booked for the date range.

    A room is unavailable if there's ANY overlap with existing reservations.
    """
    from apps.bookings.models import Reservation

    overlapping = Reservation.objects.filter(
        room_type=room_type,
        status__in=['confirmed', 'checked_in'],
        check_in__lt=check_out,
        check_out__gt=check_in
    ).count()

    return overlapping
```

**Tests:**

- [ ] Step 1: Date selection validates dates
- [ ] Step 2: Shows only available room types
- [ ] Step 3: Collects guest information
- [ ] Step 4: Creates Stripe Payment Intent
- [ ] Availability calculation correct
- [ ] Overlapping reservations handled
- [ ] Session data persists across steps
- [ ] Confirmation emails send

---

### Phase 5: Payment Integration (Stripe Connect) (10 hours)

**Goal**: Integrate Stripe Connect for payment processing.

**Critical Architecture**: Stayfull = Merchant of Record, hotels = sub-accounts.

**Stripe Service:**

```python
# apps/payments/services/stripe_service.py

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment_intent(hotel, amount, guest_email, metadata):
    """
    Create Stripe Payment Intent with Connect routing.

    Flow:
    1. Guest pays Stayfull (platform)
    2. Commission deducted automatically
    3. Net amount transferred to hotel sub-account
    """

    # Calculate commission
    commission_rate = settings.STAYFULL_COMMISSION_RATE  # e.g., 0.15 = 15%
    commission = amount * Decimal(str(commission_rate))
    hotel_amount = amount - commission

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Stripe uses cents
            currency=hotel.currency.lower(),

            # Route to hotel sub-account
            transfer_data={
                'destination': hotel.stripe_account_id,
                'amount': int(hotel_amount * 100),
            },

            # Platform fee (commission)
            application_fee_amount=int(commission * 100),

            # Metadata
            metadata=metadata,

            # Receipt email
            receipt_email=guest_email,

            # Description
            description=f"Reservation at {hotel.name}",
        )

        return intent

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise


def create_connected_account(hotel_owner_email, hotel_name, country='US'):
    """
    Create Stripe Connect account for hotel.
    Called during hotel onboarding.
    """
    try:
        account = stripe.Account.create(
            type='express',
            country=country,
            email=hotel_owner_email,
            capabilities={
                'card_payments': {'requested': True},
                'transfers': {'requested': True},
            },
            business_type='company',
            company={
                'name': hotel_name,
            },
        )

        return account.id

    except stripe.error.StripeError as e:
        logger.error(f"Stripe account creation error: {e}")
        raise


def create_account_link(stripe_account_id, return_url, refresh_url):
    """
    Create Stripe Connect onboarding link.
    Hotel owner completes onboarding on Stripe's hosted page.
    """
    try:
        link = stripe.AccountLink.create(
            account=stripe_account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type='account_onboarding',
        )

        return link.url

    except stripe.error.StripeError as e:
        logger.error(f"Stripe account link error: {e}")
        raise


def handle_webhook(payload, sig_header):
    """
    Handle Stripe webhooks (payment confirmations, etc.).
    """
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        raise ValueError("Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise ValueError("Invalid signature")

    # Handle event types
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_payment_success(payment_intent)

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_payment_failure(payment_intent)

    return True


def handle_payment_success(payment_intent):
    """
    Payment succeeded - create reservation and send confirmations.
    """
    from apps.bookings.models import Reservation, Payment
    from apps.bookings.services.notifications import send_confirmation_to_guest, send_notification_to_hotel

    metadata = payment_intent['metadata']

    # Create reservation
    reservation = Reservation.objects.create(
        hotel_id=metadata['hotel_id'],
        room_type_id=metadata['room_type_id'],
        # ... (populate from metadata)
        status='confirmed',
        deposit_paid=True,
    )

    # Create payment record
    Payment.objects.create(
        organization=reservation.organization,
        reservation=reservation,
        stripe_payment_intent_id=payment_intent['id'],
        stripe_charge_id=payment_intent.get('latest_charge'),
        amount=Decimal(str(payment_intent['amount'])) / 100,
        currency=payment_intent['currency'].upper(),
        status='succeeded',
        payment_method=payment_intent.get('payment_method_types', ['card'])[0],
    )

    # Send notifications
    send_confirmation_to_guest(reservation)
    send_notification_to_hotel(reservation)

    logger.info(f"Reservation {reservation.confirmation_code} created from payment {payment_intent['id']}")
```

**Webhook Endpoint:**

```python
# apps/payments/views.py

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json

@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """
    Stripe webhook endpoint.
    Receives payment confirmations, failures, etc.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        handle_webhook(payload, sig_header)
        return HttpResponse(status=200)
    except ValueError as e:
        logger.error(f"Webhook error: {e}")
        return HttpResponse(status=400)
```

**Environment Variables:**

```bash
# Add to .env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STAYFULL_COMMISSION_RATE=0.15  # 15%
```

**Tests:**

- [ ] Payment Intent created correctly
- [ ] Commission calculated correctly
- [ ] Transfer to hotel sub-account works
- [ ] Connected account creation works
- [ ] Webhook signature verification works
- [ ] payment_intent.succeeded creates reservation
- [ ] payment_intent.failed handled gracefully

---

### Phase 6: SEO Infrastructure (8 hours)

**Goal**: Implement SEO features for hotel websites.

**SEO Service:**

```python
# apps/website/services/seo_service.py

class SEOService:
    """
    Generate SEO meta tags, sitemaps, and structured data.
    """

    def generate_meta_tags(self, hotel, page_type='homepage'):
        """
        Generate SEO meta tags for different page types.
        """
        if page_type == 'homepage':
            title = f"{hotel.name} | {hotel.type.title()} Hotel in {hotel.address.get('city')}, {hotel.address.get('state')}"
            description = f"Experience {hotel.name}, a {hotel.type} hotel in {hotel.address.get('city')}. "

            # Add amenities
            amenities = hotel.amenities[:3] if hotel.amenities else []
            if amenities:
                description += ", ".join(amenities) + ". "

            description += "Book direct and save."

        elif page_type == 'rooms':
            title = f"Rooms & Suites | {hotel.name}"
            description = f"Explore our {hotel.room_types.count()} room types at {hotel.name}. "

            # Add room type names
            room_names = [rt.name for rt in hotel.room_types.all()[:3]]
            if room_names:
                description += ", ".join(room_names) + " and more."

        elif page_type == 'things_to_do':
            title = f"Things To Do in {hotel.address.get('city')} | {hotel.name}"
            description = f"Discover the best attractions near {hotel.name}. Museums, dining, nightlife, and more."

        # Truncate to limits
        title = title[:60]
        description = description[:160]

        return {
            'title': title,
            'description': description,
            'og_title': title,
            'og_description': description,
            'og_image': hotel.hero_image_url if hasattr(hotel, 'hero_image_url') else '',
            'og_url': f"https://app.stayfull.com/{hotel.slug}",
            'canonical_url': f"https://app.stayfull.com/{hotel.slug}",
        }

    def generate_sitemap(self, hotel):
        """
        Generate sitemap.xml for hotel website.
        """
        from django.urls import reverse

        urls = [
            {'loc': reverse('website:homepage', args=[hotel.slug]), 'priority': '1.0'},
            {'loc': reverse('website:rooms', args=[hotel.slug]), 'priority': '0.9'},
            {'loc': reverse('website:things_to_do', args=[hotel.slug]), 'priority': '0.7'},
            {'loc': reverse('website:events', args=[hotel.slug]), 'priority': '0.7'},
            {'loc': reverse('website:amenities', args=[hotel.slug]), 'priority': '0.6'},
            {'loc': reverse('website:location', args=[hotel.slug]), 'priority': '0.6'},
        ]

        # Add individual room type pages
        for room_type in hotel.room_types.all():
            urls.append({
                'loc': reverse('website:room_detail', args=[hotel.slug, room_type.slug]),
                'priority': '0.8'
            })

        return urls

    def generate_schema_markup(self, hotel):
        """
        Generate Schema.org JSON-LD structured data.
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "Hotel",
            "name": hotel.name,
            "description": hotel.description,
            "url": f"https://app.stayfull.com/{hotel.slug}",
            "telephone": hotel.phone,
            "email": hotel.email,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": hotel.address.get('street'),
                "addressLocality": hotel.address.get('city'),
                "addressRegion": hotel.address.get('state'),
                "postalCode": hotel.address.get('zip'),
                "addressCountry": hotel.address.get('country'),
            },
            "priceRange": self.get_price_range(hotel),
        }

        # Add amenities
        if hotel.amenities:
            schema["amenityFeature"] = [
                {"@type": "LocationFeatureSpecification", "name": amenity}
                for amenity in hotel.amenities[:10]
            ]

        # Add rating if available
        if hasattr(hotel, 'average_rating') and hotel.average_rating:
            schema["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": str(hotel.average_rating),
                "reviewCount": str(hotel.review_count)
            }

        return schema

    def get_price_range(self, hotel):
        """Get price range symbol ($$-$$$$)."""
        min_rate = hotel.room_types.aggregate(min_rate=Min('base_rate'))['min_rate']

        if not min_rate:
            return "$$"

        if min_rate < 100:
            return "$"
        elif min_rate < 200:
            return "$$"
        elif min_rate < 350:
            return "$$$"
        else:
            return "$$$$"
```

**Sitemap View:**

```python
# apps/website/views.py

from django.contrib.sitemaps import Sitemap
from django.shortcuts import render

def sitemap_xml(request, hotel_slug):
    """Generate sitemap.xml for hotel website."""
    hotel = get_object_or_404(Hotel, slug=hotel_slug)

    seo_service = SEOService()
    urls = seo_service.generate_sitemap(hotel)

    return render(request, 'website/sitemap.xml', {'urls': urls}, content_type='application/xml')


def robots_txt(request, hotel_slug):
    """Generate robots.txt for hotel website."""
    hotel = get_object_or_404(Hotel, slug=hotel_slug)

    content = f"""User-agent: *
Allow: /

Sitemap: https://app.stayfull.com/{hotel.slug}/sitemap.xml
"""

    return HttpResponse(content, content_type='text/plain')
```

**Base Template with SEO:**

```html
<!-- apps/website/templates/website/base.html -->

{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- SEO Meta Tags -->
    <title>{{ seo.title }}</title>
    <meta name="description" content="{{ seo.description }}">
    <link rel="canonical" href="{{ seo.canonical_url }}">

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="{{ seo.og_title }}">
    <meta property="og:description" content="{{ seo.og_description }}">
    <meta property="og:image" content="{{ seo.og_image }}">
    <meta property="og:url" content="{{ seo.og_url }}">

    <!-- Schema.org JSON-LD -->
    <script type="application/ld+json">
    {{ schema|json_script:"schema-data" }}
    </script>

    <!-- Favicon -->
    <link rel="icon" href="{% static 'favicon.ico' %}">

    <!-- Styles -->
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">

    {% block extra_head %}{% endblock %}
</head>
<body class="font-sans antialiased">
    {% block content %}{% endblock %}
</body>
</html>
```

**Tests:**

- [ ] Meta tags generate correctly for each page type
- [ ] Titles truncated to 60 chars
- [ ] Descriptions truncated to 160 chars
- [ ] Sitemap.xml generates valid XML
- [ ] Schema.org markup validates
- [ ] robots.txt allows all crawlers

---

### Phase 7: AI Content Generation (10 hours)

**Goal**: Auto-generate Things To Do and Events during onboarding.

**Things To Do Generator:**

```python
# apps/website/services/ai_content_generator.py

import openai
from django.conf import settings
import googlemaps
import requests

openai.api_key = settings.OPENAI_API_KEY
gmaps = googlemaps.Client(key=settings.GOOGLE_PLACES_API_KEY)


class ThingsToDoGenerator:
    """
    Generate "Things To Do" content based on hotel location.
    Uses GPT-4o + Google Places API.
    """

    def generate(self, hotel):
        """
        Generate 10-15 Things To Do items.

        Steps:
        1. Research with GPT-4o
        2. Enrich with Google Places API
        3. Save to database
        """
        season = self.get_current_season()
        location = f"{hotel.address['city']}, {hotel.address['state']}"

        # Step 1: Research with GPT-4o
        prompt = f"""
        Generate 15 must-visit attractions for {location} during {season}.

        Requirements:
        - 3 museums/culture
        - 3 outdoor/nature
        - 3 food/dining
        - 3 nightlife/entertainment
        - 3 shopping

        Format as JSON array:
        [
          {{
            "name": "Museum of Art",
            "category": "museum",
            "description": "World-class art museum with...",
            "why_visit": "Perfect for art lovers..."
          }},
          ...
        ]
        """

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        attractions = json.loads(response.choices[0].message.content).get('attractions', [])

        # Step 2: Enrich with Google Places
        enriched = []

        for attraction in attractions:
            places_result = self.google_places_search(
                query=f"{attraction['name']} {location}",
                location=hotel.get_coordinates()
            )

            if places_result:
                enriched.append({
                    **attraction,
                    'google_place_id': places_result['place_id'],
                    'address': places_result.get('formatted_address'),
                    'rating': places_result.get('rating'),
                    'price_level': places_result.get('price_level'),
                    'website_url': places_result.get('website'),
                    'phone': places_result.get('formatted_phone_number'),
                    'image_url': self.get_place_photo(places_result.get('photos', [{}])[0].get('photo_reference')),
                    'distance_miles': self.calculate_distance(hotel, places_result['geometry']['location']),
                })
            else:
                enriched.append(attraction)

        # Step 3: Save to database
        self.save_to_database(hotel, enriched)

        return enriched

    def google_places_search(self, query, location):
        """Search Google Places API."""
        result = gmaps.places(
            query=query,
            location=location,
            radius=50000  # 50km
        )

        if result['results']:
            place = result['results'][0]

            # Get place details
            details = gmaps.place(place['place_id'], fields=[
                'name', 'formatted_address', 'rating', 'price_level',
                'website', 'formatted_phone_number', 'photos', 'geometry'
            ])

            return details.get('result')

        return None

    def get_place_photo(self, photo_reference):
        """Get photo URL from Google Places."""
        if not photo_reference:
            return ''

        return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_reference}&key={settings.GOOGLE_PLACES_API_KEY}"

    def calculate_distance(self, hotel, destination):
        """Calculate distance in miles."""
        from geopy.distance import geodesic

        hotel_coords = (hotel.address['latitude'], hotel.address['longitude'])
        dest_coords = (destination['lat'], destination['lng'])

        distance_km = geodesic(hotel_coords, dest_coords).kilometers
        distance_miles = distance_km * 0.621371

        return round(distance_miles, 1)

    def get_current_season(self):
        """Determine current season."""
        month = timezone.now().month

        if month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        elif month in [9, 10, 11]:
            return 'fall'
        else:
            return 'winter'

    def save_to_database(self, hotel, items):
        """Save items to database."""
        from apps.website.models import ThingsToDoItem

        for i, item in enumerate(items):
            ThingsToDoItem.objects.create(
                hotel=hotel,
                name=item['name'],
                description=item['description'],
                category=item['category'],
                address=item.get('address', ''),
                distance_miles=item.get('distance_miles'),
                google_place_id=item.get('google_place_id', ''),
                rating=item.get('rating'),
                price_level=item.get('price_level'),
                website_url=item.get('website_url', ''),
                phone=item.get('phone', ''),
                image_url=item.get('image_url', ''),
                season='year_round',
                is_active=True,
                order=i,
            )
```

**Events Generator:**

```python
# apps/website/services/ai_content_generator.py

class EventsGenerator:
    """
    Generate local events using Ticketmaster/Eventbrite APIs + GPT-4o enhancement.
    """

    def generate(self, hotel):
        """
        Generate 5-10 upcoming events.

        Steps:
        1. Fetch events from Ticketmaster
        2. Enhance descriptions with GPT-4o
        3. Save to database
        """
        location = f"{hotel.address['city']}, {hotel.address['state']}"

        # Step 1: Fetch from Ticketmaster
        events = self.fetch_ticketmaster_events(
            city=hotel.address['city'],
            state_code=hotel.address['state'],
            radius=25,  # miles
            size=10
        )

        # Step 2: Enhance with GPT-4o
        enhanced = []

        for event in events:
            enhanced_description = self.enhance_event_description(event)

            enhanced.append({
                **event,
                'description': enhanced_description,
            })

        # Step 3: Save to database
        self.save_to_database(hotel, enhanced)

        return enhanced

    def fetch_ticketmaster_events(self, city, state_code, radius, size):
        """Fetch events from Ticketmaster API."""
        api_key = settings.TICKETMASTER_API_KEY

        url = "https://app.ticketmaster.com/discovery/v2/events.json"
        params = {
            'apikey': api_key,
            'city': city,
            'stateCode': state_code,
            'radius': radius,
            'unit': 'miles',
            'size': size,
            'sort': 'date,asc',
        }

        response = requests.get(url, params=params)
        data = response.json()

        events = []

        for item in data.get('_embedded', {}).get('events', []):
            events.append({
                'name': item['name'],
                'category': self.map_category(item['classifications'][0]['segment']['name']),
                'description': item.get('info', ''),
                'start_date': item['dates']['start']['localDate'],
                'start_time': item['dates']['start'].get('localTime'),
                'venue_name': item['_embedded']['venues'][0]['name'],
                'address': item['_embedded']['venues'][0]['address'].get('line1', ''),
                'ticket_url': item['url'],
                'price_range': self.format_price_range(item.get('priceRanges', [])),
                'image_url': self.get_best_image(item['images']),
                'source': 'ticketmaster',
                'external_id': item['id'],
            })

        return events

    def enhance_event_description(self, event):
        """Enhance event description with GPT-4o."""
        prompt = f"""
        Write a 2-sentence description for this event that makes guests want to attend:

        Event: {event['name']}
        Category: {event['category']}
        Venue: {event['venue_name']}

        Make it exciting and informative.
        """

        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Cheaper for simple tasks
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )

        return response.choices[0].message.content.strip()

    def map_category(self, segment):
        """Map Ticketmaster segment to our category."""
        mapping = {
            'Music': 'concert',
            'Sports': 'sports',
            'Arts & Theatre': 'theater',
            'Film': 'theater',
            'Miscellaneous': 'community',
        }

        return mapping.get(segment, 'community')

    def format_price_range(self, price_ranges):
        """Format price range."""
        if not price_ranges:
            return ''

        min_price = price_ranges[0].get('min', 0)
        max_price = price_ranges[0].get('max', 0)

        return f"${int(min_price)}-${int(max_price)}"

    def get_best_image(self, images):
        """Get highest quality image."""
        if not images:
            return ''

        # Sort by width (highest first)
        sorted_images = sorted(images, key=lambda x: x.get('width', 0), reverse=True)

        return sorted_images[0]['url']

    def save_to_database(self, hotel, events):
        """Save events to database."""
        from apps.website.models import Event

        for event in events:
            Event.objects.create(
                hotel=hotel,
                name=event['name'],
                description=event['description'],
                category=event['category'],
                start_date=event['start_date'],
                start_time=event.get('start_time'),
                venue_name=event['venue_name'],
                address=event['address'],
                source=event['source'],
                external_id=event['external_id'],
                ticket_url=event['ticket_url'],
                price_range=event['price_range'],
                image_url=event['image_url'],
                is_active=True,
            )
```

**Integrate with Onboarding:**

```python
# apps/ai_agent/services/nora_agent.py

def complete_onboarding(self, context):
    """
    Called when onboarding is complete.
    Generates hotel + AI content.
    """
    # ... (existing hotel creation code)

    # Generate AI content
    things_to_do_generator = ThingsToDoGenerator()
    things_to_do_generator.generate(hotel)

    events_generator = EventsGenerator()
    events_generator.generate(hotel)

    # Initialize website config
    from apps.website.models import WebsiteConfig
    config = WebsiteConfig.objects.create(
        hotel=hotel,
        draft_config=self.build_initial_config(context),
    )

    # Publish immediately (onboarding generates live site)
    config.publish()
```

**Tests:**

- [ ] Things To Do generates 10-15 items
- [ ] Google Places API enriches data
- [ ] Events fetches from Ticketmaster
- [ ] GPT-4o enhances descriptions
- [ ] Items save to database correctly
- [ ] Integration with onboarding works

---

### Phase 8: Integration & Testing (10 hours)

**Goal**: Integrate all phases and test end-to-end.

**Integration Checklist:**

- [ ] **Onboarding → Website**: Completing onboarding generates live website
- [ ] **Website → Booking**: Click "Book Now" starts booking flow
- [ ] **Booking → Payment**: Payment flow creates reservation
- [ ] **Payment → Confirmation**: Successful payment sends emails/SMS
- [ ] **Admin → Website**: Changes in Website Manager update live site after publish
- [ ] **AI Content**: Things To Do and Events display correctly
- [ ] **SEO**: Meta tags, sitemaps, schema markup present

**End-to-End Test:**

```python
# apps/website/tests/test_e2e.py

from django.test import TestCase, Client
from apps.hotels.models import Hotel, RoomType, Room
from apps.website.models import WebsiteConfig, ThingsToDoItem, Event
from apps.bookings.models import Reservation
from decimal import Decimal
import stripe

class EndToEndTest(TestCase):
    """
    End-to-end test: Onboarding → Website → Booking → Payment → Confirmation
    """

    def test_full_journey(self):
        # 1. Onboarding creates hotel with AI content
        hotel = self.create_hotel()
        self.assertEqual(hotel.things_to_do.count(), 15)
        self.assertEqual(hotel.events.count(), 10)

        # 2. Website config created and published
        config = hotel.website_config
        self.assertIsNotNone(config.published_config)

        # 3. Public website loads
        response = self.client.get(f'/{hotel.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, hotel.name)

        # 4. Booking flow: Step 1 (dates)
        response = self.client.post(f'/{hotel.slug}/book/', {
            'check_in': '2025-12-01',
            'check_out': '2025-12-03',
            'num_adults': 2,
            'num_children': 0,
        })
        self.assertEqual(response.status_code, 302)  # Redirect to step 2

        # 5. Booking flow: Step 2 (select room)
        response = self.client.post(f'/{hotel.slug}/book/rooms/', {
            'room_type_id': hotel.room_types.first().id,
        })
        self.assertEqual(response.status_code, 302)  # Redirect to step 3

        # 6. Booking flow: Step 3 (guest details)
        response = self.client.post(f'/{hotel.slug}/book/details/', {
            'guest_name': 'John Doe',
            'guest_email': 'john@example.com',
            'guest_phone': '+1234567890',
            'guest_country': 'US',
        })
        self.assertEqual(response.status_code, 302)  # Redirect to step 4

        # 7. Payment page loads with Stripe client secret
        response = self.client.get(f'/{hotel.slug}/book/payment/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'client_secret')

        # 8. Simulate successful Stripe payment
        # (In real test, use Stripe test mode)
        payment_intent = stripe.PaymentIntent.create(
            amount=10000,  # $100
            currency='usd',
            metadata={'hotel_id': str(hotel.id)},
        )

        # Trigger webhook
        self.simulate_webhook('payment_intent.succeeded', payment_intent)

        # 9. Reservation created
        reservation = Reservation.objects.get(guest_email='john@example.com')
        self.assertEqual(reservation.status, 'confirmed')
        self.assertTrue(reservation.deposit_paid)

        # 10. Confirmation emails sent
        from django.core import mail
        self.assertEqual(len(mail.outbox), 2)  # Guest + Hotel
```

**Performance Tests:**

- [ ] Homepage loads in <2 seconds
- [ ] Booking flow completes in <10 seconds
- [ ] SEO score >90 (Google Lighthouse)
- [ ] Mobile responsive score >95

**Deploy:**

- [ ] Push to Railway
- [ ] Set environment variables (Stripe, OpenAI, Google, Ticketmaster)
- [ ] Run migrations
- [ ] Test in staging
- [ ] Smoke test production

---

## 🔑 Critical Implementation Notes

### 1. Stayfull = Merchant of Record (ALWAYS)

**This is non-negotiable architecture:**

- ✅ Stayfull owns all payment processing
- ✅ Hotels are **sub-accounts** in Stripe Connect
- ✅ Commission flows through platform automatically
- ❌ Hotels CANNOT use their own payment processor

**Why**: Revenue model, PCI compliance, fraud prevention.

### 2. Two-Stage Publishing (Draft → Published)

**Users cannot accidentally update live websites:**

- ✅ All changes save to `draft_config`
- ✅ "Publish" button required to go live
- ✅ Version history allows reversion
- ❌ No auto-publishing

### 3. Component Visibility Logic

**Show components only if they have content:**

- ✅ Hero + Rooms: Always visible
- ✅ Things To Do + Events: Always visible (AI-generated)
- ✅ Others: Show only if has content
- ❌ Do not show empty sections

### 4. SEO is Core (Not Future)

**Every hotel website must have:**

- ✅ Meta tags (title, description)
- ✅ Open Graph tags
- ✅ Schema.org JSON-LD
- ✅ Sitemap.xml
- ✅ robots.txt

**Why**: Without SEO, no traffic. No traffic = no bookings.

### 5. AI Content Generation is Onboarding (Not Future)

**Things To Do and Events generate during onboarding:**

- ✅ 10-15 Things To Do items
- ✅ 5-10 upcoming Events
- ✅ Auto-update monthly (cron job)
- ❌ Not a "future feature" - it's core MVP

**Why**: Content = SEO = Traffic = Bookings.

### 6. Multi-Tenancy Security

**ALWAYS filter by Organization:**

```python
# ✅ Correct
hotels = Hotel.objects.filter(organization=request.user.staff.organization)

# ❌ WRONG - Data leakage!
hotels = Hotel.objects.all()
```

See `.architect/DEVELOPMENT_STANDARDS.md` Section 1.

### 7. Design References

**Public Website (Consumer-Facing):**
- Follow **Airbnb** patterns
- Visual, card-based, warm palette
- Large images, minimal text

**Admin Interface (Website Manager):**
- Follow **Stripe Dashboard** patterns
- Clean, minimal, professional
- System font, blue primary, 8px grid

See `.architect/DEVELOPMENT_STANDARDS.md` Section 2.

---

## 📚 Key Reference Files

**Full Specification (READ THIS FIRST):**
`.architect/features/F-003_DYNAMIC_COMMERCE_ENGINE.md`

**Development Standards:**
`.architect/DEVELOPMENT_STANDARDS.md`

**F-002 Integration:**
`.architect/features/F-002_AI_ONBOARDING_AGENT.md` (provides onboarding data)

**F-001 Models (You'll Query These):**
- `apps/hotels/models.py` - Hotel, RoomType, Room
- `apps/core/models.py` - Organization, Staff

---

## ✅ Definition of Done

**Functional:**
- [ ] Hotel website generates from onboarding data
- [ ] All 11 components render correctly
- [ ] Booking flow works end-to-end
- [ ] Stripe payment creates reservation
- [ ] Confirmation emails/SMS send
- [ ] Things To Do + Events display
- [ ] SEO meta tags present
- [ ] Sitemap.xml generates

**Technical:**
- [ ] Two-stage publishing works (draft → published)
- [ ] Version control saves last 10 changes
- [ ] Component visibility logic correct
- [ ] Stripe Connect integration working
- [ ] Commission routing correct
- [ ] AI content generation works
- [ ] Google Places API enriches data
- [ ] Ticketmaster API fetches events
- [ ] Test coverage >80%

**UX:**
- [ ] Website Manager easy to use
- [ ] Live preview updates in real-time
- [ ] Desktop/Mobile preview toggle works
- [ ] Booking flow: <10 seconds, <5 clicks
- [ ] Mobile responsive (all pages)
- [ ] SEO score >90 (Lighthouse)
- [ ] Page load <2 seconds

**Deployment:**
- [ ] Deployed to Railway
- [ ] Environment variables configured
- [ ] Migrations run
- [ ] Staging tested
- [ ] Documentation complete

---

## 🚨 IMPORTANT: Start After F-002

**DO NOT START F-003 until F-002 is complete!**

F-003 requires:
- ✅ Onboarding generates hotel data
- ✅ Hotel, RoomType, Room models populated
- ✅ NoraContext with completed task_state
- ✅ Organization multi-tenancy working

**When F-002 is done:**
1. Read full spec: `.architect/features/F-003_DYNAMIC_COMMERCE_ENGINE.md`
2. Read standards: `.architect/DEVELOPMENT_STANDARDS.md`
3. Set up API keys (Stripe, Google Places, Ticketmaster)
4. Start with Phase 1 (Website Foundation)
5. Ask architect if you have questions

---

## 💡 Tips for Success

**Ask Architect When:**
- ⚠️ Payment processing question (Stripe Connect is complex)
- ⚠️ SEO best practice question
- ⚠️ AI content generation issue
- ⚠️ Multi-tenancy security concern
- ⚠️ Performance issue

**Don't Need to Ask:**
- ✅ Following Airbnb/Stripe patterns
- ✅ Writing tests
- ✅ Styling per design standards
- ✅ Fixing obvious bugs

**Resources:**
- Stripe Connect Docs: https://stripe.com/docs/connect
- Google Places API: https://developers.google.com/maps/documentation/places
- Ticketmaster API: https://developer.ticketmaster.com/
- Schema.org Hotel: https://schema.org/Hotel
- Airbnb: https://airbnb.com (reference for consumer UI)
- Stripe Dashboard: https://dashboard.stripe.com (reference for admin UI)

---

## 🎯 Target Completion

**Estimated Effort**: 80 hours (~10 days)

**Breakdown:**
- Phase 1 (Website Foundation): 10 hours
- Phase 2 (Component System): 12 hours
- Phase 3 (Website Manager): 14 hours
- Phase 4 (Booking Engine): 16 hours
- Phase 5 (Payment Integration): 10 hours
- Phase 6 (SEO Infrastructure): 8 hours
- Phase 7 (AI Content Generation): 10 hours
- Phase 8 (Integration & Testing): 10 hours

**Recommended Approach:**
- Phases 1-2: Can work in parallel with F-002 Phase 6
- Phases 3-8: Start after F-002 is complete

---

**This is the REVENUE GENERATOR. Make it fast, beautiful, and conversion-optimized. 🚀**

**Questions? Ask the architect. Ready? Let's ship!**
