import os
import re

def update_translations(lang, translations):
    po_path = f'locale/{lang}/LC_MESSAGES/django.po'
    if not os.path.exists(po_path):
        print(f"Error: {po_path} not found!")
        return

    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into header and entries
    parts = re.split(r'\n\n', content)
    header = parts[0]
    
    # Parse existing entries
    existing_entries = {}
    for entry in parts[1:]:
        if not entry.strip(): continue
        match = re.search(r'msgid "(.*?)"\nmsgstr "(.*?)"', entry, re.DOTALL)
        if match:
            msgid = match.group(1).replace('"\n"', '')
            msgstr = match.group(2).replace('"\n"', '')
            existing_entries[msgid] = msgstr

    # Update with our translations
    for msgid, msgstr in translations.items():
        existing_entries[msgid] = msgstr

    # Rebuild file content
    new_content = header + "\n"
    for msgid, msgstr in sorted(existing_entries.items()):
        new_content += f'\nmsgid "{msgid}"\nmsgstr "{msgstr}"\n'

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Successfully rebuilt {po_path} with {len(existing_entries)} entries.")

ru_translations = {
    "Kelajak Ta'limini": "Образование Будущего",
    "Bugun Boshqaring": "Управляйте Сегодня",
    "LearnSphere - bu sun'iy intellekt yordamida o'quv jarayonini tahlil qiluvchi va boshqaruvchi innovatsion platforma.": "LearnSphere - инновационная платформа, анализирующая и управляющая процессом обучения с помощью искусственного интеллекта.",
    "LearnSphere Boshqaruv Paneli": "Панель управления LearnSphere",
    "Maktab faoliyati bir qarashda": "Деятельность школы с одного взгляда",
    "AI Tahlil": "AI Анализ",
    "O'quvchilarning o'zlashtirishini sun'iy intellekt yordamida chuqur tahlil qiling va bashorat qiling.": "Глубоко анализируйте и прогнозируйте успеваемость учащихся с помощью ИИ.",
    "Ota-onalar Nazorati": "Родительский контроль",
    "Farzandlaringizning baholarini va davomatini onlayn kuzatib boring.": "Следите за оценками и посещаемостью ваших детей онлайн.",
    "Elektron Jurnal": "Электронный журнал",
    "O'qituvchilar uchun qulay va tezkor baholash tizimi. Qog'ozbozlikdan xalos bo'ling.": "Удобная и быстрая система оценивания для учителей. Избавьтесь от бумажной волокиты.",
    "Mening Qobiliyatlarim (AI)": "Мои способности (AI)",
    "Tanqidiy Fikrlash": "Критическое мышление",
    "Ijodkorlik": "Креативность",
    "Muloqot": "Коммуникация",
    "Jamoaviy": "Командная работа",
    "Moslashuvchanlik": "Адаптивность",
    "Ball": "Балл",
    "Ma'lumotlar yo'q": "Нет данных",
    "O'qituvchingiz hali sizning Soft Skills ko'rsatkichlaringizni kiritmagan.": "Ваш преподаватель еще не ввел ваши показатели Soft Skills.",
    "AI tizimida": "На базе ИИ",
    "Zamonaviy Ta'lim Platformasi": "Современная образовательная платформа",
    "Foydalanuvchilar": "Пользователи",
    "Sinflar": "Классы",
    "Fanlar": "Предметы",
    "Baholar": "Оценки",
    "O'qituvchilar": "Учителя",
    "Davomat": "Посещаемость",
    "Do'kon": "Магазин",
    "Dashboard": "Дашборд",
    "Admin Panel": "Админ панель",
    "Jadval Boshqaruvi": "Управление расписанием",
    "O'qituvchi Biriktiruvi": "Прикрепление учителей",
    "Hisobotlar": "Отчеты",
    "Bosh sahifa": "Главная страница",
    "Asosiy sahifa": "Главная страница",
    "Vazifalar": "Задания",
    "Kutubxona": "Библиотека",
    "Testlar": "Тесты",
    "Bildirishnomalar": "Уведомления",
    "Profil": "Профиль",
    "Majlislar": "Собрания",
    "Reyting": "Рейтинг",
    "Xabarlar": "Сообщения",
    "Barcha huquqlar himoyalangan.": "Все права защищены.",
    "Mening Profilim": "Мой профиль",
    "Profil boshqaruvi": "Управление профилем",
    "Chiqish": "Выйти",
    "Kirish": "Войти",
    "Yuklanmoqda...": "Загрузка...",
    "Muvaffaqiyatli saqlandi!": "Успешно сохранено!",
    "Xatolik yuz berdi!": "Произошла ошибка!",
    "Tarmoq xatosi!": "Сетевая ошибка!",
    "Hech narsa tanlanmagan!": "Ничего не выбрано!",
    "ni o'chirishga ishonchingiz komilmi?": " вы уверены, что хотите удалить?",
    "Muvaffaqiyatli o'chirildi!": "Успешно удалено!",
    "Yangi": "Новый",
    "chat": "чат",
}

en_translations = {
    "Kelajak Ta'limini": "Future Education",
    "Bugun Boshqaring": "Manage Today",
    "LearnSphere - bu sun'iy intellekt yordamida o'quv jarayonini tahlil qiluvchi va boshqaruvchi innovatsion platforma.": "LearnSphere is an innovative platform that analyzes and manages the learning process using artificial intelligence.",
    "LearnSphere Boshqaruv Paneli": "LearnSphere Control Panel",
    "Maktab faoliyati bir qarashda": "School activity at a glance",
    "AI Tahlil": "AI Analysis",
    "O'quvchilarning o'zlashtirishini sun'iy intellekt yordamida chuqur tahlil qiling va bashorat qiling.": "Deeply analyze and predict student achievement using AI.",
    "Ota-onalar Nazorati": "Parental Control",
    "Farzandlaringizning baholarini va davomatini onlayn kuzatib boring.": "Track your children's grades and attendance online.",
    "Elektron Jurnal": "Electronic Journal",
    "O'qituvchilar uchun qulay va tezkor baholash tizimi. Qog'ozbozlikdan xalos bo'ling.": "Convenient and fast grading system for teachers. Get rid of paperwork.",
    "Mening Qobiliyatlarim (AI)": "My Abilities (AI)",
    "Tanqidiy Fikrlash": "Critical Thinking",
    "Ijodkorlik": "Creativity",
    "Muloqot": "Communication",
    "Jamoaviy": "Teamwork",
    "Moslashuvchanlik": "Adaptability",
    "Ball": "Score",
    "Ma'lumotlar yo'q": "No data",
    "O'qituvchingiz hali sizning Soft Skills ko'rsatkichlaringizni kiritmagan.": "Your teacher has not entered your Soft Skills indicators yet.",
    "AI tizimida": "AI Powered",
    "Zamonaviy Ta'lim Platformasi": "Modern Education Platform",
    "Foydalanuvchilar": "Users",
    "Sinflar": "Classes",
    "Fanlar": "Subjects",
    "Baholar": "Grades",
    "O'qituvchilar": "Teachers",
    "Davomat": "Attendance",
    "Do'kon": "Shop",
    "Dashboard": "Dashboard",
    "Admin Panel": "Admin Panel",
    "Jadval Boshqaruvi": "Schedule Management",
    "O'qituvchi Biriktiruvi": "Teacher Assignment",
    "Hisobotlar": "Reports",
    "Bosh sahifa": "Home",
    "Asosiy sahifa": "Home",
    "Vazifalar": "Assignments",
    "Kutubxona": "Library",
    "Testlar": "Quizzes",
    "Bildirishnomalar": "Notifications",
    "Profil": "Profile",
    "Majlislar": "Meetings",
    "Reyting": "Leaderboard",
    "Xabarlar": "Messages",
    "Barcha huquqlar himoyalangan.": "All rights reserved.",
    "Mening Profilim": "My Profile",
    "Profil boshqaruvi": "Profile Management",
    "Chiqish": "Logout",
    "Kirish": "Login",
    "Yuklanmoqda...": "Loading...",
}

update_translations('ru', ru_translations)
update_translations('en', en_translations)
