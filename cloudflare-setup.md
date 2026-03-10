# 🔵 Cloudflare Tunnel Setup Guide

## Step 2: Login ke Cloudflare

Jalankan command ini di terminal VM:

```bash
cloudflared tunnel login
```

Ini akan:
1. Open browser dengan URL authorization Cloudflare
2. Pilih domain yang akan digunakan (atau signup dulu jika belum punya)
3. Authorize cloudflared
4. Download certificate ke `~/.cloudflared/cert.pem`

**PENTING:** Ini akan membuka browser. Karena Anda SSH ke VM, copy URL yang muncul dan buka di browser lokal Anda.

---

## Step 3: Create Tunnel

Setelah login berhasil, create tunnel:

```bash
# Create tunnel dengan nama "botzoom-api"
cloudflared tunnel create botzoom-api
```

Output akan seperti:
```
Tunnel credentials written to /home/cak-seno/.cloudflared/xxxxx-xxxx-xxxx.json
Created tunnel botzoom-api with id xxxxx-xxxx-xxxx-xxxx
```

**Simpan Tunnel ID** yang muncul!

---

## Step 4: Configure Tunnel

Create config file:

```bash
mkdir -p ~/.cloudflared
nano ~/.cloudflared/config.yml
```

Isi dengan (ganti `TUNNEL_ID` dengan ID dari step 3):

```yaml
tunnel: TUNNEL_ID
credentials-file: /home/cak-seno/.cloudflared/TUNNEL_ID.json

ingress:
  # Route traffic ke backend FastAPI
  - hostname: api-botzoom.your-domain.com
    service: http://localhost:8000
  
  # Catch-all rule (required)
  - service: http_status:404
```

**Ganti:**
- `TUNNEL_ID` - dari step 3
- `api-botzoom.your-domain.com` - subdomain yang Anda mau

---

## Step 5: Route DNS

Buat DNS record yang point ke tunnel:

```bash
cloudflared tunnel route dns botzoom-api api-botzoom.your-domain.com
```

Ganti `api-botzoom.your-domain.com` dengan subdomain pilihan Anda.

Ini akan otomatis buat CNAME record di Cloudflare DNS.

---

## Step 6: Run Tunnel (Test Dulu)

Test run tunnel:

```bash
cloudflared tunnel run botzoom-api
```

Jika sukses, akses: `https://api-botzoom.your-domain.com/`

Seharusnya muncul response dari FastAPI backend!

---

## Step 7: Install as Service (Auto-Start)

Install sebagai systemd service agar jalan otomatis:

```bash
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
sudo systemctl status cloudflared
```

---

## ✅ Selesai!

Backend sekarang bisa diakses dari:
- `https://api-botzoom.your-domain.com`

Update frontend Vercel untuk pakai URL ini:

```javascript
// frontend/.env.production
VITE_API_URL=https://api-botzoom.your-domain.com
```

---

## 🔍 Monitoring

Cek status tunnel:
```bash
cloudflared tunnel list
cloudflared tunnel info botzoom-api
```

Cek logs:
```bash
sudo journalctl -u cloudflared -f
```

---

## ⚡ Alternatif: Quick Tunnel (Tanpa Domain)

Jika tidak punya domain Cloudflare, pakai Quick Tunnel:

```bash
cloudflared tunnel --url http://localhost:8000
```

Ini akan generate random URL seperti:
`https://random-name.trycloudflare.com`

Tapi URL ini temporary dan berubah setiap restart.

