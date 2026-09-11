Sən təcrübəli Python və Telegram Bot mütəxəssisisən. Mənə Python dilində "python-telegram-bot==20.7" və "Flask" kitabxanalarından istifadə edən, Render platformasında host olunmaq üçün uyğun (Flask serveri ilə birgə) tam işlək və səhvsiz bir Telegram bot kodu (`bot.py`) yaz. Botun strukturu və qaydaları aşağıdakı kimi olmalıdır:

1. Başlanğıc və Dillər:
- Bot açılan kimi istifadəçiyə dil seçimi gəlməlidir: Azərbaycan, Türk, Rus, İngilis.
- Dillər seçildikdən sonra məzənnə göstərilməlidir: Adi üzv üçün 1000 xal -> 0.05$ | VIP üzv üçün 1000 xal -> 0.08$.
- Bundan sonra əsas menyu açılmalıdır.

2. Əsas Menyu Düymələri (Inline):
- Çarx
- Balans
- Referal
- Tapşırıqlar
- Vip
- Çıxarış
- Məlumat
- Dil dəyiş
- Rəsmi kanal (https://t.me/+ZMvnUmwWkJ0wZDI0)
- Bot bildirişləri aktivləşdir

3. Çarx Mexanizmi:
- Gündəlik 50 ədəd pulsuz çarx haqqı olmalı, yenilənmə 24 saatdan bir baş verməlidir.
- 50 çarx bitdikdən sonra 10 ədəd hədiyyə/bonus çarx tələb etmək imkanı olmalıdır.
- İstifadəçinin statusuna uyğun olaraq (Adi və ya VIP) xallar avtomatik tənzimlənməlidir:
  * Adi user xalları: 35 xal (20%), 45 xal (20%), 55 xal (20%), 65 xal (10%), Boş 0 xal (20%), Hədiyyə çarx (10%). Hədiyyə çarxda: 2 fırlanma (50%), 3 fırlanma (30%), 5 fırlanma (20%). (Məsələn, 2 fırlanma çıxıbsa və userin 10 çarxı qalıbsa, 12 olmalıdır).
  * VIP user xalları: 60 xal (20%), 80 xal (20%), 100 xal (20%), 120 xal (10%), Boş 0 xal (20%), Hədiyyə çarx (10%). Hədiyyə çarx eyni qaydada.
- 50 çarxı tamamlamaqla qazanılan 10 bonus fırlatma haqqında 4 xal sistemi olsun: 15, 20, 25, 30 xal.
- "Çarxı yenidən fırlat" düyməsi olsun. Bu düyməyə basıldıqda köhnə mesaj silinib yenisi gəlsin, lakin xallar balansda qalsın.

4. Balans Bölməsi:
- Başlıq: "Sizi USDT Bot-da görməkdən məmnunuq"
- Ümumi balans, referaldan əldə olunan balans, referal sayı (adi/vip), status (vip/adi) göstərilsin.

5. Referal Sistemi:
- Referal linki yaratmaq (`https://t.me/BOT_USERNAME?start=USER_ID`).
- Adi və VIP referal sayları, referallardan gələn ümumi gəlir qeyd olunsun.
- Hər 1000 xalı olan referaldan 20 xal onu gətirənə verilsin.
- "Referalları yoxla" düyməsi ilə açılan pəncərədə referalların ID kodu, xalları və onlardan qazanılan xal görünsün.
- Gətirilən referal 5 gün bota daxil olmasa, onun xalı artıq hesablanmasın.

6. Tapşırıqlar Bölməsi:
- Kanallar:
  1. https://t.me/craftbetting
  2. https://t.me/mercvekuponlarr
  3. https://t.me/qizilanaliz
  4. https://t.me/+ZMvnUmwWkJ0wZDI0
- Bütün kanallara qoşulanlara 100 xal verilsin. "Yoxla" düyməsi ilə bot bunu nəzarətdə saxlasın.

7. VIP Bölməsi və Ödənişlər:
- VIP mahiyyəti, yüksək xal və çıxarış limitləri qeyd olunsun.
- Qiymətlər: 7 günlük -> 3$, 15 günlük -> 5$.
- Ödənişlər TRC20 (USDT) ünvanına edilir: `TKf5cMmCqjR76gN62Vim9BaP3G5XL4a7kp`
- Ödəniş qəbzi və ID kodu @usdtqazanadmin ünvanına göndərilməlidir.

8. Çıxarış Bölməsi (Adi və VIP ayrı olmalıdır):
- Adi user üçün:
  * Maksimum 300 000 xal -> 15$ (Şərt: 10 adi üzv və 1 VIP referal)
  * Maksimum 400 000 xal -> 15$ (Şərt: 10 adi üzv referal)
- VIP user üçün:
  * Maksimum 250 000 xal -> 20$ (Şərt: 10 adi üzv referal)
  * Maksimum 300 000 xal -> 25$ (Şərt: 5 adi üzv referal)
- Şərtlər ödəndiydən sonra @usdtqazanadmin hesabına ID kod atılaraq müraciət edilsin.

9. Məlumat, Rəsmi Kanal və Bildirişlər:
- Məlumat: Botun pulsuz olması, referal sistemi, şikayət üçün @usdtqazanadmin və TRC20 izahı.
- Rəsmi kanal: https://t.me/+ZMvnUmwWkJ0wZDI0
- Bildirişlər: User 24 saat botu aktiv etsə əlavə 200 xal verilsin. Çarx olduqda və referaldan 200 xal gəldikdə bildiriş göndərilsin.

Zəhmət olmasa bütün bu detalları nəzərə alaraq təmiz, tam və səhvsiz Python kodu (`bot.py`) tərtib et.
