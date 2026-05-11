function authPage() {
  return {
    tab: 'login',
    email: '',
    password: '',
    error: '',
    loading: false,

    async login() {
      this.error = '';
      if (!this.email || !this.password) { this.error = 'Please enter email and password.'; return; }
      this.loading = true;
      try {
        const data = await API.post('/auth/login', { email: this.email, password: this.password });
        localStorage.setItem('token', data.access_token);
        window.location.href = '/dashboard.html';
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },

    async signup() {
      this.error = '';
      if (!this.email || !this.password) { this.error = 'Please enter email and password.'; return; }
      if (this.password.length < 6) { this.error = 'Password must be at least 6 characters.'; return; }
      this.loading = true;
      try {
        const data = await API.post('/auth/signup', { email: this.email, password: this.password });
        localStorage.setItem('token', data.access_token);
        window.location.href = '/dashboard.html';
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },
  };
}

// Redirect if already logged in
if (localStorage.getItem('token')) {
  window.location.href = '/dashboard.html';
}
