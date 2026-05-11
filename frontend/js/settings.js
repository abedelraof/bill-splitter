function settingsPage() {
  return {
    currentPreview: null,
    newKey: '',
    email: '',
    error: '',
    loading: true,
    saving: false,

    async init() {
      requireAuth();
      try {
        const [settings, me] = await Promise.all([API.get('/settings/'), API.get('/auth/me')]);
        this.currentPreview = settings.claude_key_preview;
        this.email = me.email;
      } catch (e) {
        showToast(e.message, true);
      } finally {
        this.loading = false;
      }
    },

    async saveKey() {
      this.error = '';
      const key = this.newKey.trim();
      if (!key) return;
      if (!key.startsWith('sk-')) { this.error = "API key must start with 'sk-'"; return; }
      this.saving = true;
      try {
        await API.put('/settings/claude-key', { claude_api_key: key });
        const settings = await API.get('/settings/');
        this.currentPreview = settings.claude_key_preview;
        this.newKey = '';
        showToast('API key saved!');
      } catch (e) {
        this.error = e.message;
      } finally {
        this.saving = false;
      }
    },

    logout() {
      localStorage.removeItem('token');
      window.location.href = '/index.html';
    },
  };
}
