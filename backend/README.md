# Backend

## Folder Structure Overview

### api/
Berisi layer **HTTP interface** aplikasi (route/controller).  
Menangani request–response, validasi input, dan pemanggilan service/domain.  
Tidak berisi logika bisnis berat.

---

### database/
Mengatur **koneksi database**, session, migrasi, dan inisialisasi ORM.  
Menjadi satu-satunya pintu interaksi langsung dengan database engine.

---

### domains/
Berisi **inti logika bisnis (business logic)** per domain/fitur.  
Mendefinisikan aturan, proses, dan perilaku utama sistem (misal: transcript, legal AI, auth, user).  
Tidak bergantung pada framework atau mekanisme eksekusi.

---

### integrations/
Berisi adapter untuk **layanan eksternal** seperti LLM API, WhisperX, storage, payment, atau third-party service lainnya.  
Digunakan oleh domain atau worker sebagai dependency.

---

### workers/
Berisi **background job / async task** untuk proses berat dan non-blocking  
(seperti transkripsi audio, fine-tuning model, summarization, indexing).  
Biasanya dijalankan via queue atau scheduler, bukan request HTTP langsung.

---

### utils/
Berisi **helper umum** dan fungsi pendukung yang reusable lintas domain  
(seperti formatter, logger, file helper, error handler).  
Tidak menyimpan logika bisnis spesifik.

---

### test/
Berisi seluruh **unit test, integration test, dan e2e test**.  
Strukturnya mencerminkan folder aplikasi untuk memastikan coverage dan maintainability.





## Setup

1. Aktifkan virtual environment:
   ```
   .venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Jalankan server:
   ```
   uvicorn main:app --reload
   ```

Server akan berjalan di `http://localhost:8000`

## Environment Variables

Pastikan file `.env` dikonfigurasi dengan:
- `DATABASE_URL` - URL koneksi database
- `ZOOM_WEBHOOK_SECRET` - Secret key dari Zoom webhook
- `ZOOM_CLIENT_ID` & `ZOOM_CLIENT_SECRET` - Kredensial Zoom
- (Opsional) `LLM_API_KEY` - API key untuk LLM service

## API Documentation

Setelah server berjalan, akses dokumentasi API di:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Kontribusi

Saat menambah fitur baru:
1. Buat endpoint baru di folder `api/`
2. Tambahkan logic di folder `services/`
3. Definisikan model di folder `models/` (jika perlu database)
4. Buat schema validasi di folder `schemas/`
5. Tambahkan test di folder `test/`
