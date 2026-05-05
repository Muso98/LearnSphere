import re
import os

translations = {
    "Kelajak Ta'limini": "Образование Будущего",
    "Bugun Boshqaring": "Управляйте Сегодня",
    "LearnSphere - bu sun'iy intellekt yordamida o'quv jarayonini tahlil qiluvchi va boshqaruvchi innovatsion platforma.": "LearnSphere - инновационная платформа, анализирующая и управляющая процессом обучения с помощью искусственного интеллекта.",
    "Kabinetga o'tish": "Перейти в кабинет",
    "Jurnalga o'tish": "Перейти в журнал",
    "Boshqaruv Paneli": "Панель управления",
    "Kirish": "Вход",
    "Ko'proq ma'lumot": "Подробнее",
    "Mening Qobiliyatlarim (AI)": "Мои способности (AI)",
    "Tanqidiy Fikrlash": "Критическое мышление",
    "Ijodkorlik": "Креативность",
    "Muloqot": "Коммуникация",
    "Jamoaviy": "Командная работа",
    "Moslashuvchanlik": "Адаптивность",
    "Ball": "Балл",
    "Ma'lumotlar yo'q": "Нет данных",
    "O'qituvchingiz hali sizning Soft Skills ko'rsatkichlaringizni kiritmagan.": "Ваш преподаватель еще не ввел ваши показатели Soft Skills.",
    "AI Powered": "На базе ИИ",
    "LearnSphere Dashboard": "Панель LearnSphere",
    "Maktab faoliyati bir qarashda": "Деятельность школы с одного взгляда",
    "AI Tahlil": "AI Анализ",
    "O'quvchilarning o'zlashtirishini sun'iy intellekt yordamida chuqur tahlil qiling va bashorat qiling.": "Глубоко анализируйте и прогнозируйте успеваемость учащихся с помощью ИИ.",
    "Ota-onalar Nazorati": "Родительский контроль",
    "Farzandlaringizning baholarini va davomatini onlayn kuzatib boring.": "Следите за оценками и посещаемостью ваших детей онлайн.",
    "Elektron Jurnal": "Электронный журнал",
    "O'qituvchilar uchun qulay va tezkor baholash tizimi. Qog'ozbozlikdan xalos bo'ling.": "Удобная и быстрая система оценивания для учителей. Избавьтесь от бумажной волокиты.",
    "Profil": "Профиль",
    "Foydalanuvchi Profili": "Профиль пользователя",
    "Rasmni o'zgartirish": "Сменить фото",
    "Ism": "Имя",
    "Familiya": "Фамилия",
    "Telefon": "Телефон",
    "Bio": "О себе",
    "Sinf": "Класс",
    "Farzandlar": "Дети",
    "Farzandlar biriktirilmagan.": "Дети не прикреплены.",
    "Qo'yilgan baholar": "Поставленные оценки",
    "Saqlash": "Сохранить",
    "Bekor qilish": "Отмена",
    "AI Tahlil: Qobiliyatlar Xaritasi": "AI Анализ: Карта способностей",
    "Xulosa": "Заключение",
    "Tanqidiy fikrlash": "Критическое мышление",
    "Ijodkorlik": "Креативность",
    "Muloqot": "Коммуникация",
    "Jamoaviy ishlash": "Командная работа",
    "Moslashuvchanlik": "Адаптивность",
    "So'nggi yangilanish": "Последнее обновление",
    "O'qituvchi": "Учитель",
    "O'quvchi Ko'rsatkichlari": "Показатели ученика",
    "Bildirishnomalar": "Уведомления",
    "Yangi": "Новый",
    "Sizda yangi bildirishnomalar yo'q.": "У вас нет новых уведомлений.",
    "AI Assistant": "AI Ассистент",
    "Teacher": "Учитель",
    "Parent": "Родитель",
    "Student": "Ученик",
    "New Chat": "Новый чат",
    "Recent Conversations": "Недавние диалоги",
    "No conversations yet": "Пока нет диалогов",
    "Select or start a new conversation": "Выберите или начните новый диалог",
    "Start a conversation with your AI assistant": "Начните диалог с вашим AI ассистентом",
    "Type your message...": "Введите сообщение...",
    "Send": "Отправить",
    "AI is thinking...": "AI думает...",
    "Zamonaviy Ta'lim Platformasi": "Современная образовательная платформа",
}

po_path = 'locale/ru/LC_MESSAGES/django.po'

if not os.path.exists(po_path):
    print(f"Error: {po_path} not found!")
    exit(1)

with open(po_path, 'r', encoding='utf-8') as f:
    content = f.read()

def replace_func(match):
    msgid = match.group(1)
    if msgid in translations:
        return f'msgid "{msgid}"\nmsgstr "{translations[msgid]}"'
    return match.group(0)

# Pattern to find empty msgstr for specific msgid
new_content = re.sub(r'msgid "(.*?)"\nmsgstr ""', replace_func, content)

with open(po_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Successfully updated {po_path} with {len(translations)} potential translations.")
