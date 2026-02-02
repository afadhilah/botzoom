## Frontend Folder Structure (`src/`)

### asset/
Berisi **aset statis** seperti gambar, ikon, font, ilustrasi, dan file media lainnya.  
Tidak mengandung logika aplikasi.

---

### components/
Berisi **UI components reusable** yang bersifat umum dan tidak terikat fitur tertentu  
(contoh: Button, Modal, Table, Input, Dropdown).

---

### features/
Berisi **implementasi per fitur (feature-based structure)**.  
Setiap fitur dapat memiliki komponen, logic, API call, dan state sendiri  
(contoh: auth, transcript, legal-ai).

---

### lib/
Berisi **library internal dan konfigurasi global**  
(seperti axios instance, API client, auth handler, constants, config).  
Digunakan lintas fitur.

---

### pages/
Berisi **halaman (page-level components)** yang terhubung langsung dengan routing.  
Setiap file merepresentasikan satu route utama aplikasi.

---

### router/
Berisi **konfigurasi routing aplikasi** (Vue Router).  
Mengatur mapping URL ke halaman, route guard, dan middleware frontend.

---

### services/
Berisi **abstraksi komunikasi ke backend atau external service**  
(seperti API call, WebSocket handler, atau SDK wrapper).  
Tidak mengandung state UI.

---

### stores/
Berisi **state management global** (Pinia / Vuex).  
Digunakan untuk menyimpan state lintas halaman seperti auth, user, dan app state.
