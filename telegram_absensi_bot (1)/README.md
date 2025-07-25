# Telegram Absensi Bot

Bot Telegram untuk mencatat aktivitas harian seperti:
- Makan (1x, max 30 menit)
- Merokok (3x, max 7 menit per sesi)
- Buang air kecil (3x, max 5 menit)
- Buang air besar (1x, max 15 menit)
- Ambil delivery (1x, max 15 menit)
- Kembali ke tempat duduk

## Fitur
- ⏰ Jam aktif: 01:00 - 23:00
- 🔄 Reset otomatis jam 00:00 setiap hari
- 📁 Simpan data ke CSV lokal
- 🛑 Batas frekuensi & durasi tiap aktivitas
- 🔔 Reminder otomatis sebelum batas waktu habis
- ✅ Command: /makan /merokok /toilet /berak /delivery /kembali

## Deploy ke Render
1. Buat akun di https://render.com
2. Fork / upload repo ini ke GitHub
3. Deploy Web Service → pilih repo ini
4. Tambah `Environment Variable`: `TOKEN` = 7878205061:AAGXAFpJQnEdtRK1QnqRERr76lcQtxqX5lc
5. Done! Bot akan aktif 24 jam non-stop

CSV akan otomatis direstart tiap hari pukul 00:00.
