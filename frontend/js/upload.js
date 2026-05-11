const MAX_UPLOAD_BYTES = 3 * 1024 * 1024; // 3MB target before upload
const MAX_DIMENSION = 1800;               // max px on longest side

async function compressImage(file) {
  return new Promise((resolve) => {
    const img = new window.Image();
    img.onload = () => {
      let { width, height } = img;

      // Scale down if needed
      if (Math.max(width, height) > MAX_DIMENSION) {
        const ratio = MAX_DIMENSION / Math.max(width, height);
        width = Math.round(width * ratio);
        height = Math.round(height * ratio);
      }

      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      canvas.getContext('2d').drawImage(img, 0, 0, width, height);

      // Try decreasing quality until under size limit
      const tryQuality = (quality) => {
        canvas.toBlob((blob) => {
          if (blob.size <= MAX_UPLOAD_BYTES || quality <= 0.3) {
            resolve(new File([blob], 'bill.jpg', { type: 'image/jpeg' }));
          } else {
            tryQuality(quality - 0.1);
          }
        }, 'image/jpeg', quality);
      };

      tryQuality(0.85);
    };
    img.src = URL.createObjectURL(file);
  });
}

function uploadPage() {
  return {
    selectedFile: null,
    preview: null,
    loading: false,
    error: '',
    noKey: false,

    async init() {
      requireAuth();
      try {
        const settings = await API.get('/settings/');
        this.noKey = !settings.has_claude_key;
      } catch (e) { /* ignore */ }
    },

    triggerUpload() {
      document.getElementById('bill-input').click();
    },

    onFileSelected(event) {
      const file = event.target.files[0];
      if (!file) return;
      this.selectedFile = file;
      this.preview = URL.createObjectURL(file);
      this.error = '';
    },

    async parseBill() {
      if (!this.selectedFile) return;
      this.loading = true;
      this.error = '';
      try {
        const compressed = await compressImage(this.selectedFile);
        const data = await API.uploadFile('/bills/parse', compressed);
        sessionStorage.setItem('parsedBill', JSON.stringify(data));
        window.location.href = '/review.html';
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },

    skipToManual() {
      sessionStorage.setItem('parsedBill', JSON.stringify({ image_path: null, items: [], extras: { vat: null, service_charge: null, discount: null } }));
      window.location.href = '/review.html';
    },
  };
}
