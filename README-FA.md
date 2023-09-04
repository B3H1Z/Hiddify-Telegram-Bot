

<p align="center">
  <a href="https://github.com/B3H1Z/Hiddify-Telegram-Bot" target="_blank" rel="noopener noreferrer">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/B3H1Z/Hiddify-Telegram-Bot/blob/main/Screenshots/icon.png?raw=True">
      <img width="200" height="200" src="https://github.com/B3H1Z/Hiddify-Telegram-Bot/blob/main/Screenshots/icon.png?raw=True">
    </picture>
  </a>
</p>
<p align="center">
	<a href="./README.md">
	English
	</a>
	|
	<a href="./README-FA.md">
	فارسی
	</a>
<br>
  <a href="https://t.me/HidyBotGroup">گروه تلگرام</a>

</p>

<h1 align="center"/>هیدی بات</h1>

با استفاده از این ربات می‌توانید پنل هیدیفای خود را از طریق تلگرام مدیریت کنید.

این ربات را **در همان سرور** پنل هیدیفای خود نصب کنید.

> ما در نسخه آزمایشی (BETA) هستیم و در حال بهبود آن هستیم. لطفاً اگر باگ یا مشکلی دیدید، با ما در ارتباط باشید.

لطفاً توجه داشته باشید که این ربات <b>رسمی نیست</b> و ارتباطی با تیم هیدیفای ندارد.

بعضی از ویژگی‌ها عبارتند از:
-  افزودن کاربران
-  حذف کاربران
-  ویرایش کاربران
-  نمایش لیست کاربران
-  جستجوی کاربران (بر اساس نام، تنظیمات، UUID)
-  نمایش اطلاعات کاربران (نام، ترافیک، تاریخ و غیره)
-  نمایش پیکربندی‌ها و لینک‌های اشتراک کاربر
-  دریافت پشتیبان از پنل شما
-  نمایش وضعیت سرور (رم، پردازنده، دیسک)

## نصب 
برای نصب ربات دستور زیر را اجرا کنید:
 
```bash
sudo bash -c "$(curl -Lfo- https://raw.githubusercontent.com/B3H1Z/Hiddify-Telegram-Bot/main/install.sh)"
```
<br>

مطمئن شوید که اطلاعات زیر را آماده دارید:
1. `شناسه تلگرام ادمین` : آن را از ربات[ User Info Bot](https://t.me/userinfobot) بگیرید (مثال: `123456789`)
2. `توکن ربات ادمین` : آن را از ربات [BotFather](https://t.me/BotFather) بگیرید (
   مثال: `1234567890:ABCdEfGhIjKlMnOpQrStUvWxYz`)
3. `آدرس پنل هیدیفای` : آدرس پنل هیدیفای خود را وارد کنید (
   مثال: `https://panel.example.com/7frgemkvtE0/78854985-68dp-425c-989b-7ap0c6kr9bd4`) <b>دقیقاً مانند این الگو!</b>
4. `زبان ربات` : گزینه‌ها `en` و `fa` می‌باشند [پیش‌فرض `fa`]
5. `توکن ربات کاربران(اختیاری)` : آن را از ربات [BotFather](https://t.me/BotFather) بگیرید (
   مثال: `1234567890:ABCdEfGhIjKlMnOpQrStUvWxYz`)

حالا می‌توانید با ارسال دستور `/start` از ربات در تلگرام استفاده کنید.


## دستورات
 به‌روزرسانی ربات
```bash
cd /opt/Hiddify-Telegram-Bot/ && curl -fsSL -o /opt/Hiddify-Telegram-Bot/update.sh https://raw.githubusercontent.com/B3H1Z/Hiddify-Telegram-Bot/main/update.sh && chmod +x /opt/Hiddify-Telegram-Bot/update.sh && bash /opt/Hiddify-Telegram-Bot/update.sh
```
 راه‌اندازی مجدد ربات
```bash
cd /opt/Hiddify-Telegram-Bot/ && chmod +x restart.sh && ./restart.sh
```
 متوقف کردن ربات

```bash
pkill -9 -f hiddifyTelegramBot.py
```
 دریافت لاگ های ربات
```bash
cat /opt/Hiddify-Telegram-Bot/Logs/hidyBot.log
```
 اطلاعات پیکربندی ربات
```bash
cat /opt/Hiddify-Telegram-Bot/config.json
```
 تغییر پیکربندی ربات
```bash
cd /opt/Hiddify-Telegram-Bot/ && python3 config.py && chmod +x restart.sh && ./restart.sh
```
 نصب مجدد ربات
```bash
cd /opt/ && rm -rf /opt/Hiddify-Telegram-Bot/ && sudo bash -c "$(curl -Lfo- https://raw.githubusercontent.com/B3H1Z/Hiddify-Telegram-Bot/main/install.sh)"
```
## اسکرین شات‌ها
#### ربات کاربران 
- <img src="https://github.com/B3H1Z/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-u-1.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/B3H1Z/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-u-2.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/B3H1Z/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-u-3.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/B3H1Z/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-u-4.jpg?raw=True" width=35% height=35%>
#### ربات ادمین
- <img src="https://github.com/B3H1Z/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-a-1.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/B3H1Z/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-a-2.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/B3H1Z/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-a-6.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/B3H1Z/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-a-8.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/B3H1Z/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-a-5.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/B3H1Z/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-a-3.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/B3H1Z/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-a-4.jpg?raw=True" width=35% height=35%>
- <img src="https://github.com/B3H1Z/Hiddify-Telegram-Bot/blob/main/Screenshots/scr-a-7.jpg?raw=True" width=35% height=35%>