# 🔧 Hướng Dẫn Setup - Caro AI

*Hướng dẫn cài đặt và chạy project Caro AI.*

---

## ⚡ Quick Start (5 phút)

### Windows

```bash
# 1. Vào thư mục project
cd Caro_AI

# 2. Tạo virtual environment cho Python 3.12
py -3.12 -m venv venv

# 3. Kích hoạt venv
venv\Scripts\activate

# 4. Cài đặt dependencies
pip install -r requirements.txt

# 5. Chạy game
python src/main.py
```

### macOS/Linux

```bash
# 1. Vào thư mục project
cd Caro_AI

# 2. Tạo virtual environment cho Python 3.12
python3.12 -m venv venv

# 3. Kích hoạt venv
source venv/bin/activate

# 4. Cài đặt dependencies
pip install -r requirements.txt

# 5. Chạy game
python src/main.py
```

---

## ✅ Yêu Cầu

- **Python 3.12** (bắt buộc)
- **pip** (kèm theo Python)

### Kiểm Tra Python Version

```bash
# Kiểm tra Python 3.12
py -3.12 --version         # Windows
python3.12 --version       # macOS/Linux

# Phải là 3.12.x
```

---

## 📋 Chi Tiết Các Bước

### Bước 1: Kiểm Tra Python 3.12

```bash
# Windows
py -3.12 --version

# macOS/Linux
python3.12 --version
```

**Nếu không có Python 3.12:**
- Tải từ https://www.python.org/downloads/
- Chọn version 3.12.x
- Cài đặt (nhớ tick "Add to PATH")

### Bước 2: Tạo Virtual Environment

⚠️ **Dùng đúng** Python 3.12 (không phải `python` thôi):

**Windows:**
```bash
py -3.12 -m venv venv
```

**macOS/Linux:**
```bash
python3.12 -m venv venv
```

❌ **Không nên dùng** (có thể dùng Python 3.13+):
```bash
python -m venv venv
```

### Bước 3: Kích Hoạt Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

Bạn sẽ thấy `(venv)` ở đầu dòng lệnh.

### Bước 4: Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

**Hiện tại bao gồm:**
- `pygame==2.6.1` - Game render

### Bước 5: Chạy Game

```bash
python src/main.py
```

---

## 🎮 Điều Khiển Game

- **Click**: Đặt quân (nếu là Human)
- **R**: Restart game
- **M**: Về menu
- **Close**: Thoát game

---

## 🐛 Lỗi Thường Gặp

### "Python 3.12 không tìm thấy"

```bash
# Kiểm tra Python hiện có
py --list-paths          # Windows
python3 --version        # macOS/Linux

# Cài lại venv với đúng version:
py -3.12 -m venv venv         # Windows
python3.12 -m venv venv       # macOS/Linux
```

### "No module named 'pygame'"

```bash
# 1. Kiểm tra venv đã activate? (phải thấy (venv) ở terminal)
venv\Scripts\activate

# 2. Cài lại
pip install -r requirements.txt
```

### "No module named 'game'"

```bash
# Phải ở thư mục project root
cd Caro_AI
python src/main.py
```

---

## ✅ Verification Checklist

```bash
# ✓ Python 3.12 có?
py -3.12 --version              # Windows
python3.12 --version            # macOS/Linux

# ✓ Venv activated? (thấy (venv) ở terminal)

# ✓ Pygame cài xong?
python -c "import pygame; print('OK')"

# ✓ Game chạy?
python src/main.py
```

---

## 🔄 Hủy Kích Hoạt Virtual Environment

Khi xong:

```bash
deactivate
```

---

## 📖 Tiếp Theo

- ✅ Setup xong? → Chạy: `python src/main.py`
- 📖 Muốn hiểu game? → `README_ARCHITECTURE.md`
- 🤖 Muốn phát triển AI? → `AI_DEVELOPMENT_GUIDE.md`

---

**Done! 🚀**
