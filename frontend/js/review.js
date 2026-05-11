const FRIEND_COLORS = [
  '#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981',
  '#3b82f6', '#ef4444', '#14b8a6', '#f97316', '#84cc16',
];

let _uid = 0;

function reviewPage() {
  return {
    phase: 'items',          // 'items' | 'charges'
    currentIndex: 0,
    editingCurrent: false,
    items: [],
    extras: { vat: null, service_charge: null, discount: null },
    friends: [],
    imagePath: null,
    error: '',
    submitting: false,

    async init() {
      requireAuth();
      const raw = sessionStorage.getItem('parsedBill');
      if (!raw) { window.location.href = '/upload.html'; return; }
      const parsed = JSON.parse(raw);
      this.imagePath = parsed.image_path || null;
      this.items = (parsed.items || []).map(it => ({
        ...it,
        _id: ++_uid,
        friend_ids: [],
        amount: parseFloat(it.amount || 0).toFixed(2),
      }));
      this.extras = parsed.extras || { vat: null, service_charge: null, discount: null };
      try { this.friends = await API.get('/friends/'); } catch (_) {}
    },

    currentItem() {
      return this.items[this.currentIndex] || null;
    },

    friendColor(idx) {
      return FRIEND_COLORS[idx % FRIEND_COLORS.length];
    },

    toggleFriend(item, friendId) {
      if (!item) return;
      const i = item.friend_ids.indexOf(friendId);
      if (i === -1) item.friend_ids.push(friendId);
      else item.friend_ids.splice(i, 1);
    },

    nextItem() {
      this.editingCurrent = false;
      if (this.currentIndex < this.items.length - 1) {
        this.currentIndex++;
      } else {
        this.phase = 'charges';
      }
    },

    prevItem() {
      this.editingCurrent = false;
      if (this.currentIndex > 0) this.currentIndex--;
    },

    skipItem() {
      // Clear any assigned friends and move on
      if (this.currentItem()) this.currentItem().friend_ids = [];
      this.nextItem();
    },

    removeCurrentItem() {
      this.items.splice(this.currentIndex, 1);
      if (this.currentIndex >= this.items.length) {
        this.currentIndex = Math.max(0, this.items.length - 1);
      }
      this.editingCurrent = false;
    },

    addManualItem() {
      const item = { _id: ++_uid, description: '', amount: '0.00', is_manual: true, friend_ids: [] };
      this.items.push(item);
      this.currentIndex = this.items.length - 1;
      this.editingCurrent = true;
    },

    ensureExtra(key) {
      if (!this.extras[key]) {
        this.extras[key] = { type: 'percent', value: '' };
      }
    },

    setExtra(key, value) {
      if (!this.extras[key]) this.extras[key] = { type: 'percent', value: '' };
      this.extras[key] = { ...this.extras[key], value: value === '' ? '' : Number(value) };
    },

    // ── Totals ──────────────────────────────────────
    subtotal() {
      return this.items.reduce((s, it) => s + (parseFloat(it.amount) || 0), 0);
    },

    _resolveExtra(key) {
      const e = this.extras[key];
      if (!e || e.value === '' || e.value === null) return 0;
      const sub = this.subtotal();
      return e.type === 'percent' ? sub * Number(e.value) / 100 : Number(e.value);
    },

    vatAmount()      { return this._resolveExtra('vat'); },
    serviceAmount()  { return this._resolveExtra('service_charge'); },
    discountAmount() { return this._resolveExtra('discount'); },

    grandTotal() {
      return this.subtotal() + this.vatAmount() + this.serviceAmount() - this.discountAmount();
    },

    unassignedCount() {
      return this.items.filter(it => it.friend_ids.length === 0).length;
    },

    // ── Submit ───────────────────────────────────────
    async submit() {
      this.error = '';
      for (const item of this.items) {
        if (!item.description.trim()) { this.error = 'All items need a description.'; return; }
        if (parseFloat(item.amount) <= 0 || isNaN(parseFloat(item.amount))) {
          this.error = `"${item.description}" needs a valid amount.`; return;
        }
      }

      const cleanExtras = {};
      for (const key of ['vat', 'service_charge', 'discount']) {
        const e = this.extras[key];
        cleanExtras[key] = (e && e.value !== '' && e.value !== null && Number(e.value) > 0)
          ? { type: e.type || 'percent', value: Number(e.value) }
          : null;
      }

      this.submitting = true;
      try {
        const payload = {
          image_path: this.imagePath,
          items: this.items.map(it => ({
            description: it.description.trim(),
            amount: parseFloat(it.amount),
            is_manual: Boolean(it.is_manual),
            friend_ids: it.friend_ids,
          })),
          extras: cleanExtras,
        };
        const { bill_id } = await API.post('/bills/', payload);
        sessionStorage.removeItem('parsedBill');
        window.location.href = `/summary.html?bill_id=${bill_id}`;
      } catch (e) {
        this.error = e.message;
      } finally {
        this.submitting = false;
      }
    },
  };
}
