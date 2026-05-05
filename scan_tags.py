import os
import re

def get_template_strings():
    strings = set()
    template_dir = 'templates'
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Find {% trans "..." %} or {% trans '...' %}
                    found = re.findall(r'\{% trans ["\'](.*?)["\'] %\}', content)
                    strings.update(found)
    
    # Also check other apps
    for app in ['communication', 'analytics', 'gamification', 'journal', 'homework', 'core']:
        app_template_dir = os.path.join(app, 'templates')
        if os.path.exists(app_template_dir):
            for root, dirs, files in os.walk(app_template_dir):
                for file in files:
                    if file.endswith('.html'):
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            content = f.read()
                            found = re.findall(r'\{% trans ["\'](.*?)["\'] %\}', content)
                            strings.update(found)
    return strings

def check_missing():
    template_strings = get_template_strings()
    
    # Import translations from fix_translations.py (manually defined here for speed)
    defined_ru = [
        "Kelajak Ta'limini", "Bugun Boshqaring", "LearnSphere Boshqaruv Paneli", "Maktab faoliyati bir qarashda",
        "AI Tahlil", "Ota-onalar Nazorati", "Elektron Jurnal", "Mening Qobiliyatlarim (AI)", "Tanqidiy Fikrlash",
        "Ijodkorlik", "Muloqot", "Jamoaviy", "Moslashuvchanlik", "Ball", "Ma'lumotlar yo'q", "AI tizimida",
        "Zamonaviy Ta'lim Platformasi", "Foydalanuvchilar", "Sinflar", "Fanlar", "Baholar", "O'qituvchilar",
        "Davomat", "Do'kon", "Dashboard", "Admin Panel", "Jadval Boshqaruvi", "O'qituvchi Biriktiruvi",
        "Hisobotlar", "Bosh sahifa", "Asosiy sahifa", "Vazifalar", "Kutubxona", "Testlar", "Bildirishnomalar",
        "Profil", "Majlislar", "Reyting", "Xabarlar", "Barcha huquqlar himoyalangan.", "Mening Profilim",
        "Profil boshqaruvi", "Chiqish", "Kirish", "Yuklanmoqda...", "Muvaffaqiyatli saqlandi!", "Xatolik yuz berdi!",
        "Tarmoq xatosi!", "Hech narsa tanlanmagan!", "ni o'chirishga ishonchingiz komilmi?", "Muvaffaqiyatli o'chirildi!",
        "Yangi", "chat", "Jami foydalanuvchilar", "Faol", "Bugungi davomat", "O'rtacha baho",
        "Fanlar bo'yicha o'zlashtirish", "Haftalik davomat tendensiyasi", "Eng yaxshi o'quvchilar",
        "E'tibor talab qiluvchilar", "Oxirgi baholar", "Yangi foydalanuvchilar", "Kelgan", "Kelmagan",
        "Davomat %", "baho", "Hammasi yaxshi!", "Aktiv", "Virtual Majlislar", "Majlis yaratish",
        "Tashkilotchi", "Umumiy majlis", "Qo'shilish", "Rejalashtirilgan majlislar yo'q",
        "Yangi majlislar paydo bo'lganda shu yerda ko'rasiz.", "Ballar Do'koni", "Balansingiz", "ball",
        "Sotib olish", "Ball yetmaydi", "Eng Faol O'quvchilar Reytingi", "Yuqori ball to'plagan o'quvchilar",
        "O'quvchi", "Yutuqlar (Badges)", "Jami Ball", "Sinf Tanlash", "Qobiliyatlar Xaritasi (AI Data)",
        "O'quvchilarning 'Soft Skills' ko'rsatkichlarini kiritish uchun sinfni tanlang.", "Qobiliyatlar",
        "Soft Skills Baholash", "Saqlash", "Bekor qilish", "Xush kelibsiz!",
        "LearnSphere ta'lim platformasiga kirish", "Login yoki parol noto'g'ri.", "Foydalanuvchi nomi",
        "Username", "Parol", "Tizimga Kirish", "Zamonaviy Ta'lim Platformasi", "Barcha huquqlar himoyalangan."
    ]
    
    missing = []
    for s in template_strings:
        if s not in defined_ru:
            missing.append(s)
    
    if missing:
        print("Missing translations for these strings:")
        for m in sorted(missing):
            print(f'"{m}"')
    else:
        print("All template strings are covered!")

check_missing()
