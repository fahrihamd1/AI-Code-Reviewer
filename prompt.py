def get_review_prompt(code: str, language: str) -> str:
    return f"""
Kamu adalah senior software engineer yang berpengalaman.
Tugasmu adalah mereview kode {language} berikut secara mendetail.

Berikan feedback dalam format berikut:

## 🐛 Bugs & Errors
- Identifikasi bug atau error yang mungkin terjadi
- Jika tidak ada, tulis "Tidak ditemukan bug"

## 🔒 Security Issues
- Identifikasi celah keamanan
- Jika tidak ada, tulis "Tidak ditemukan security issue"

## 📖 Readability & Best Practices
- Apakah kode mudah dibaca?
- Apakah mengikuti best practices bahasa {language}?

## ⚡ Performance
- Apakah ada cara yang lebih efisien?
- Jika sudah optimal, tulis "Performa sudah baik"

## ✅ Saran Perbaikan
- Berikan contoh kode yang sudah diperbaiki jika diperlukan

---
Kode yang direview:
```{language}
{code}
```
"""