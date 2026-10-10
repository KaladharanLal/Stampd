// Stampd Global Client Logic
document.addEventListener('alpine:init', () => {
  // Global Store for current user session and notifications
  Alpine.store('auth', {
    user: localStorage.getItem('stampd_user') || 'nobi',
    users: [
      { username: 'nobi', name: 'Nobi K.', accent: '#ff8a3d' },
      { username: 'maya', name: 'Maya Sen', accent: '#40bcf4' },
      { username: 'arjun', name: 'Arjun Varma', accent: '#00e054' },
      { username: 'clara', name: 'Clara Croft', accent: '#ec4899' },
    ],
    switchUser(u) {
      this.user = u;
      localStorage.setItem('stampd_user', u);
      window.location.reload();
    }
  });

  // Global Log Modal state
  Alpine.store('logModal', {
    isOpen: false,
    slug: '',
    name: '',
    country: '',
    date: new Date().toISOString().split('T')[0],
    rating: 4.5,
    hoverRating: 0,
    review: '',
    tags: [],
    availableTags: ['mountains', 'beaches', 'city', 'food', 'heritage', 'nature', 'nightlife', 'adventure', 'spiritual', 'offbeat'],
    wouldReturn: true,
    isSubmitting: false,
    successStamp: null,

    open(slug = '', name = '', country = '') {
      this.slug = slug;
      this.name = name;
      this.country = country;
      this.date = new Date().toISOString().split('T')[0];
      this.rating = 4.5;
      this.hoverRating = 0;
      this.review = '';
      this.tags = [];
      this.wouldReturn = true;
      this.isSubmitting = false;
      this.successStamp = null;
      this.isOpen = true;
    },

    toggleTag(t) {
      if (this.tags.includes(t)) {
        this.tags = this.tags.filter(x => x !== t);
      } else {
        this.tags.push(t);
      }
    },

    setRating(val) {
      this.rating = val;
    },

    async submit() {
      if (!this.slug) {
        window.showToast('Please select a destination', 'error');
        return;
      }
      this.isSubmitting = true;
      try {
        const currentUser = Alpine.store('auth').user;
        const res = await fetch('/api/visits', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            destination_slug: this.slug,
            visited_on: this.date,
            rating: this.rating,
            review: this.review,
            tags: this.tags,
            would_return: this.wouldReturn,
            username: currentUser
          })
        });
        const data = await res.json();
        if (data.success) {
          this.successStamp = data.visit.stamp;
          window.showToast(`Stamped! Logged visit to ${this.name || this.slug}`, 'success');
          // If on destination page or profile, refresh after a moment
          setTimeout(() => {
            if (window.location.pathname.includes('/destinations/') || window.location.pathname.includes('/profile')) {
              window.location.reload();
            }
          }, 1800);
        } else {
          window.showToast(data.detail || 'Failed to log visit', 'error');
        }
      } catch (err) {
        console.error(err);
        window.showToast('Network error while logging visit', 'error');
      } finally {
        this.isSubmitting = false;
      }
    },

    close() {
      this.isOpen = false;
      this.successStamp = null;
    }
  });

  // Global Toast store
  Alpine.store('toast', {
    show: false,
    message: '',
    type: 'success',
    timeout: null,
    trigger(msg, type = 'success') {
      this.message = msg;
      this.type = type;
      this.show = true;
      if (this.timeout) clearTimeout(this.timeout);
      this.timeout = setTimeout(() => {
        this.show = false;
      }, 3200);
    }
  });
});

// Global Helpers
window.showToast = (msg, type = 'success') => {
  if (window.Alpine && Alpine.store('toast')) {
    Alpine.store('toast').trigger(msg, type);
  }
};

window.openLogModal = (slug, name, country) => {
  if (window.Alpine && Alpine.store('logModal')) {
    Alpine.store('logModal').open(slug, name, country);
  }
};

window.toggleBucket = async (slug, btnElement = null) => {
  const currentUser = localStorage.getItem('stampd_user') || 'nobi';
  try {
    const res = await fetch(`/api/bucket/${slug}?username=${currentUser}`, { method: 'POST' });
    const data = await res.json();
    if (data.in_bucket) {
      window.showToast('Added to your Bucket List! 📌', 'success');
      if (btnElement) {
        btnElement.classList.add('text-accent');
      }
    }
  } catch (err) {
    window.showToast('Could not update bucket list', 'error');
  }
};
