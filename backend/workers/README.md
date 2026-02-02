### workers/
Berisi **background job / async task** untuk proses berat dan non-blocking  
(seperti transkripsi audio, fine-tuning model, summarization, indexing).  
Biasanya dijalankan via queue atau scheduler, bukan request HTTP langsung.