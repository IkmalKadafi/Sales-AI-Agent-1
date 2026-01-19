# Penjelasan Bagian AI dalam Aplikasi

## 🤖 Bagian AI - Lokasi dan Fungsi

### 1. **File Utama AI: `agent_engine.py`**

#### Fungsi `generate_ai_insight()` - Baris 238-370

**INI ADALAH BAGIAN AI UTAMA** yang menghasilkan laporan penjualan dalam bahasa natural (Bahasa Indonesia).

**Cara Kerja:**
```python
def generate_ai_insight(self, summary: Dict[str, Any]) -> str:
    """
    Generate AI-powered daily sales insight
    INI ADALAH BAGIAN AI - Menghasilkan laporan penjualan dalam bahasa natural
    """
```

**Apa yang Dilakukan AI:**
1. **Membaca Data** - Mengambil status penjualan (CRITICAL/WARNING/OK)
2. **Menganalisis Konteks** - Memahami performa vs target, perubahan vs kemarin
3. **Menghasilkan Narasi** - Membuat laporan dalam bahasa Indonesia yang mencakup:
   - 📌 Ringkasan Eksekutif
   - 📊 Metrik Utama
   - ⚠️ Peringatan & Risiko
   - 🧠 Analisis AI (Mengapa ini terjadi)
   - 🎯 Tindakan yang Direkomendasikan

**Contoh Output AI:**
```
🧾 LAPORAN PENJUALAN HARIAN — Rabu, 2026-01-15

📌 Ringkasan Eksekutif
- Portofolio berkinerja jauh di bawah target: 98.3% dari target tercapai
- 4 masalah kritis memerlukan perhatian segera
- Penjualan menurun 18.0% vs kemarin
...
```

### 2. **Jenis AI yang Digunakan**

**Saat ini: Template-Based AI (Tidak Perlu API Key)**
- Menggunakan logika if-else untuk menghasilkan teks
- Menyesuaikan narasi berdasarkan status (CRITICAL/WARNING/OK)
- Memasukkan data real-time (angka penjualan, persentase)
- **Keuntungan**: Gratis, cepat, dapat diprediksi
- **Keterbatasan**: Kurang fleksibel, pola teks terbatas

**Upgrade ke Real LLM (Opsional):**
Bisa diganti dengan API LLM seperti:
- OpenAI GPT-4
- Anthropic Claude
- Google Gemini

Caranya: Ganti fungsi `generate_ai_insight()` dengan panggilan API:
```python
import openai

def generate_ai_insight_real(summary):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Anda adalah analis penjualan senior..."},
            {"role": "user", "content": f"Analisis data ini: {summary}"}
        ]
    )
    return response.choices[0].message.content
```

### 3. **Komponen Lain yang Mendukung AI**

#### Rule-Based Evaluation (`evaluate_rules()`)
Menentukan status berdasarkan aturan:
- R1: Pencapaian Target
- R2: Performa Hari-ke-Hari
- R3: Anomali Tren
- R4: Penyesuaian Akhir Pekan

#### Data Aggregation (`aggregate_findings()`)
Mengumpulkan semua temuan untuk diberikan ke AI

### 4. **Flow Data ke AI**

```
CSV Data 
  ↓
Load & Process (agent_engine.py)
  ↓
Rule Evaluation (R1-R4)
  ↓
Status Classification (OK/WARNING/CRITICAL)
  ↓
🤖 AI Insight Generation ← BAGIAN AI DI SINI
  ↓
Template Rendering (insight.html)
  ↓
Tampilan Web (Browser)
```

### 5. **Dimana Melihat Output AI**

**Di Web Browser:**
1. Buka http://localhost:5000
2. Klik menu "Insight AI"
3. Lihat laporan yang dihasilkan AI

**Contoh Tampilan:**
- Judul: "Laporan Analis Penjualan AI"
- Isi: Teks narasi dalam Bahasa Indonesia
- Format: Markdown yang dirender sebagai HTML

---

## 📝 Ringkasan

**Bagian AI ada di:**
- **File**: `agent_engine.py`
- **Fungsi**: `generate_ai_insight()` (baris 238-370)
- **Jenis**: Template-based (saat ini), bisa upgrade ke LLM
- **Output**: Laporan penjualan harian dalam Bahasa Indonesia
- **Tampilan**: Halaman "Insight AI" di web

**Kenapa Ini Disebut "AI"?**
Karena sistem ini:
1. Menganalisis data secara otomatis
2. Menghasilkan narasi dalam bahasa natural
3. Memberikan rekomendasi berdasarkan pola
4. Menyesuaikan output berdasarkan konteks

Meskipun saat ini menggunakan template, arsitekturnya sudah siap untuk upgrade ke LLM yang lebih canggih!
