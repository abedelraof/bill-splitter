function dashboardPage() {
  return {
    friends: [],
    bills: [],
    newFriendName: '',
    editingId: null,
    editName: '',

    async init() {
      requireAuth();
      await Promise.all([this.loadFriends(), this.loadBills()]);
    },

    async loadFriends() {
      try { this.friends = await API.get('/friends/'); } catch (e) { showToast(e.message, true); }
    },

    async loadBills() {
      try { this.bills = await API.get('/bills/'); } catch (e) { /* silent */ }
    },

    async addFriend() {
      const name = this.newFriendName.trim();
      if (!name) return;
      try {
        const f = await API.post('/friends/', { name });
        this.friends.push(f);
        this.newFriendName = '';
      } catch (e) { showToast(e.message, true); }
    },

    startEdit(f) {
      this.editingId = f.id;
      this.editName = f.name;
    },

    async saveEdit(id) {
      const name = this.editName.trim();
      if (!name) return;
      try {
        const updated = await API.put(`/friends/${id}`, { name });
        const idx = this.friends.findIndex(f => f.id === id);
        if (idx !== -1) this.friends[idx] = updated;
        this.editingId = null;
      } catch (e) { showToast(e.message, true); }
    },

    async deleteFriend(id) {
      try {
        await API.delete(`/friends/${id}`);
        this.friends = this.friends.filter(f => f.id !== id);
      } catch (e) { showToast(e.message, true); }
    },

    formatDate(iso) {
      return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    },

    logout() {
      localStorage.removeItem('token');
      window.location.href = '/index.html';
    },
  };
}
