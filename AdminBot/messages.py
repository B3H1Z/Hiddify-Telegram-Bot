from config import LANG

# Response Messages Template
MESSAGES = {
    'EN': {
        'WELCOME': "Welcome to Hiddify Management Bot",
        'ERROR_INVALID_NUMBER': "❌Only numbers are allowed!",
        'ERROR_USER_NOT_FOUND': "❌User not found",
        'ERROR_INVALID_COMMAND': "❌Invalid command",
        'ERROR_UNKNOWN': "❌Unknown error",
        'ERROR_CONFIG_NOT_FOUND': '❌Config not found',
        'ERROR_PLAN_NOT_FOUND': '❌Plan not found',
        'SUCCESS_USER_DELETED': "✅User deleted",
        'SUCCESS_USER_EDITED': "✅User edited",
        'SUCCESS_USER_ADDED': "✅User added",
        'SUCCESS_USER_USAGE_EDITED': "✅Usage limit edited to:",
        'SUCCESS_USER_DAYS_EDITED': "✅Days edited to:",
        'SUCCESS_USER_NAME_EDITED': "✅Name edited to:",
        'SUCCESS_USER_COMMENT_EDITED': "✅Comment edited to:",
        'SUCCESS_ADD_USER': "✅User added",
        'SUCCESS_SEARCH_USER': "✅User found",
        'SUCCESS_SEND_MSG_USERS': "✅Message sent to users",
        'WAIT': "Please wait...",
        'CANCELED': "❌Canceled",
        'CANCEL_ADD_USER': "❌Add User Canceled",
        'ADD_USER_NAME': "Please enter the name of the user: ",
        'ADD_USER_COMMENT': "Please enter the comment of the user: ",
        'ADD_USER_USAGE_LIMIT': "Please enter the usage limit of the user (GB): ",
        'ADD_USER_DAYS': "Please enter the days of package: ",
        'ENTER_NEW_USAGE_LIMIT': "Please enter new usage limit (GB): ",
        'ENTER_NEW_DAYS': "Please enter new limit: ",
        'ENTER_NEW_NAME': "Please enter new name: ",
        'ENTER_NEW_COMMENT': "Please enter new comment: ",
        'RESET_USAGE': "✅Usage limit reset",
        'RESET_DAYS': "✅Days reset",
        'ADD_USER_CONFIRM': "Please confirm the information:",
        'ERROR_NOT_ADMIN': "❌You are not admin!",
        'NEW_USER_INFO': "[New User Info]",
        'EDITED_USER_INFO': "[User Info Updated]",
        'EXPIRED_USERS_LIST': '[EXPIRED USERS LIST]',
        'GB': 'GB',
        'DAY_EXPIRE': 'Days',
        'INFO_USAGE': '📊Usage:',
        'OF': 'of',
        'INFO_REMAINING_DAYS': '📆Remaining Days:',
        'INFO_LAST_CONNECTION': '📶Last Connection:',
        'INFO_COMMENT': '📝Comment:',
        'INFO_USER': '👤Name:',
        'HEADER_USERS_LIST': '👤Users List',
        'HEADER_USERS_LIST_MSG': 'ℹ️You can see the list of users and their information here.',
        'NUM_USERS': '🟢Number of users: ',
        'NUM_USERS_ONLINE': '🔵Online users: ',
        'SEARCH_USER': 'Please select the search method',
        'SEARCH_USER_NAME': 'Please enter the name of the user: ',
        'SEARCH_USER_UUID': 'Please enter the UUID of the user: ',
        'SEARCH_USER_CONFIG': 'Please enter one of the config of the user: ',
        'SEARCH_RESULT': '[Search Result]',
        'MONTH': 'Months',
        'WEEK': 'Weeks',
        'DAY': 'Days',
        'HOUR': 'Hours',
        'MINUTE': 'Minutes',
        'ONLINE': 'Online',
        'AGO': "ago",
        'NEVER': 'Never',
        'TOMAN': 'T',
        'ERROR_CLIENT_TOKEN': '❌Client bot is not set!',
        'USERS_BOT_ADD_PLAN': 'Please complete the following information to add a plan',
        'USERS_BOT_ADD_PLAN_DAYS': 'Please enter the days of Plan: ',
        'USERS_BOT_ADD_PLAN_USAGE': 'Please enter the usage limit(GB) of the Plan: ',
        'USERS_BOT_ADD_PLAN_PRICE': 'Please enter the price(TOMAN) of the Plan: ',
        'USERS_BOT_ADD_PLAN_CONFIRM': 'Please confirm the information:',
        'USERS_BOT_ADD_PLAN_SUCCESS': '✅Plan added',
        'USERS_BOT_OWNER_INFO_NOT_FOUND': 'Owner info not found!\nPlease set it first.',
        'USERS_BOT_OWNER_INFO_ADD_USERNAME': 'Please enter the username of the support bot: ',
        'USERS_BOT_OWNER_INFO_ADD_CARD_NUMBER': 'Please enter the card number: ',
        'USERS_BOT_OWNER_INFO_ADD_CARD_NAME': 'Please enter the name of the card owner: ',
        'USERS_BOT_SEND_MSG_USERS': 'Please enter the message you want to send to users:',
        'USERS_BOT_PLANS_LIST': '📋Plans List',
        'USERS_BOT_SELECT_PLAN_TO_DELETE': 'Please select the plan you want to delete:',
        'USERS_BOT_PLAN_DELETED': '✅Plan deleted',
        'SUCCESS_UPDATE_DATA': '✅Data updated',
        'USERS_BOT_SETTINGS': '⚙️Users Bot Settings',
        'USERS_BOT_SETTINGS_HYPERLINK': 'Set Hyperlink visibility when user request subscription info',
        'USERS_BOT_ORDER_NUMBER_REQUEST': 'Please enter the order number:',
        'ERROR_INVALID_USERNAME': '❌Invalid username\nUsername must start with @',
        'ERROR_INVALID_CARD_NUMBER': '❌Invalid card number',
        'PAYMENT_CONFIRMED': '✅Payment confirmed',
        'PAYMENT_NOT_CONFIRMED': '❌Payment not confirmed',
        'ERROR_PAYMENT_ALREADY_CONFIRMED': '❌Payment already confirmed',
        'ERROR_PAYMENT_ALREADY_REJECTED': '❌Payment already rejected',
        'PAYMENT_CONFIRMED_ADMIN': '✅Payment confirmed',
        'PAYMENT_NOT_CONFIRMED_ADMIN': '❌Payment not confirmed',
        'ERROR_PAYMENT_NOT_FOUND': '❌Payment not found',
        'ERROR_ORDER_NOT_FOUND': '❌Order not found',
        'ORDER_ID': 'Order number:',
        'USER_TIME_EXPIRED': '⚠️EXPIRED',
        'PAYMENT_ASK_CHANGE_STATUS': 'Do you want to change the status of the payment?',
        'PAYMENT_ACCEPT_STATUS_CONFIRMED': '🟢Confirmed',
        'PAYMENT_ACCEPT_STATUS_NOT_CONFIRMED': '🔴Not Confirmed',
        'PAYMENT_ACCEPT_STATUS_WAITING': '🟡Waiting',
        'PAYMENT_ACCEPT_STATUS': 'Status:',
        'CREATED_AT': 'Created:',


    },
    'FA': {
        'WELCOME': "به ربات مدیریت هیدیفای خوش آمدید.",
        'ERROR_INVALID_NUMBER': "❌تنها اعداد مجاز هستند!",
        'ERROR_USER_NOT_FOUND': "❌کاربر یافت نشد",
        'ERROR_INVALID_COMMAND': "❌فرمان نامعتبر",
        'ERROR_UNKNOWN': "❌خطای ناشناخته",
        'ERROR_CONFIG_NOT_FOUND': '❌کانفیگ یافت نشد',
        'ERROR_PLAN_NOT_FOUND': '❌پلن یافت نشد',
        'SUCCESS_USER_DELETED': "✅کاربر حذف شد",
        'SUCCESS_USER_EDITED': "✅کاربر ویرایش شد",
        'SUCCESS_USER_ADDED': "✅کاربر اضافه شد",
        'SUCCESS_USER_USAGE_EDITED': "✅محدودیت استفاده کاربر ویرایش شد به:",
        'SUCCESS_USER_DAYS_EDITED': "✅روزها ویرایش شد به:",
        'SUCCESS_USER_NAME_EDITED': "✅نام ویرایش شد به:",
        'SUCCESS_USER_COMMENT_EDITED': "✅یادداشت ویرایش شد به:",
        'SUCCESS_ADD_USER': "✅کاربر اضافه شد",
        'SUCCESS_SEARCH_USER': "✅کاربر یافت شد",
        'SUCCESS_SEND_MSG_USERS': "✅پیام به کاربران ارسال شد",
        'WAIT': "لطفاً منتظر بمانید...",
        'CANCELED': "❌لغو شد",
        'CANCEL_ADD_USER': "❌افزودن کاربر لغو شد",
        'ADD_USER_NAME': "لطفاً نام کاربر را وارد کنید: ",
        'ADD_USER_COMMENT': "لطفاً نظر کاربر را وارد کنید: ",
        'ADD_USER_USAGE_LIMIT': "لطفاً محدودیت استفاده کاربر (GB) را وارد کنید: ",
        'ADD_USER_DAYS': "لطفاً تعداد روز بسته‌ی کاربر را وارد کنید: ",
        'ENTER_NEW_USAGE_LIMIT': "لطفاً محدودیت استفاده جدید (GB) را وارد کنید: ",
        'ENTER_NEW_DAYS': "لطفاً محدودیت جدید را وارد کنید: ",
        'ENTER_NEW_NAME': "لطفاً نام جدید را وارد کنید: ",
        'ENTER_NEW_COMMENT': "لطفاً یادداشت جدید را وارد کنید: ",
        'RESET_USAGE': "✅محدودیت استفاده بازنشانی شد",
        'RESET_DAYS': "✅روزها بازنشانی شد",
        'ADD_USER_CONFIRM': "لطفاً اطلاعات را تأیید کنید:",
        'ERROR_NOT_ADMIN': "❌شما ادمین نیستید!",
        'NEW_USER_INFO': "[اطلاعات کاربر جدید]",
        'EDITED_USER_INFO': "[اطلاعات کاربر به‌روزرسانی شد]",
        'EXPIRED_USERS_LIST': "[لیست کاربران منقضی شده]",
        'GB': 'گیگابایت',
        'DAY_EXPIRE': 'روز دیگر',
        'INFO_USAGE': '📊مصرف:',
        'OF': 'از',
        'INFO_REMAINING_DAYS': '📆انقضا:',
        'INFO_LAST_CONNECTION': '📶آخرین اتصال:',
        'INFO_COMMENT': '📝یادداشت:',
        'INFO_USER': '👤کاربر:',
        'HEADER_USERS_LIST': '👤لیست کاربران',
        'HEADER_USERS_LIST_MSG': 'ش️ما می‌توانید لیست کاربران و اطلاعات آن‌ها را اینجا مشاهده کنید',
        'NUM_USERS': '🟢تعداد کاربران: ',
        'NUM_USERS_ONLINE': '🔵کاربران آنلاین: ',
        'SEARCH_USER': 'لطفاً روش جستجو را انتخاب کنید',
        'SEARCH_USER_NAME': 'لطفاً نام کاربر را وارد کنید: ',
        'SEARCH_USER_UUID': 'لطفاً UUID کاربر را وارد کنید: ',
        'SEARCH_USER_CONFIG': 'لطفاً یکی از کانفیگ های کاربر را وارد کنید: ',
        'SEARCH_RESULT': '[نتیجه جستجو]',
        'MONTH': 'ماه',
        'WEEK': 'هفته',
        'DAY': 'روز',
        'HOUR': 'ساعت',
        'MINUTE': 'دقیقه',
        'ONLINE': 'آنلاین',
        'AGO': 'پیش',
        'NEVER': 'هرگز',
        'TOMAN': 'تومان',
        'ERROR_CLIENT_TOKEN': '❌ربات کاربران تنظیم نشده',
        'USERS_BOT_ADD_PLAN': 'لطفا اطلاعات زیر را برای افزودن پلن وارد کنید',
        'USERS_BOT_ADD_PLAN_DAYS': 'لطفا زمان(تعداد روزهای) پلن را وارد کنید',
        'USERS_BOT_ADD_PLAN_USAGE': 'لطفا محدودیت استفاده(گیگابایت) پلن را وارد کنید',
        'USERS_BOT_ADD_PLAN_PRICE': 'لطفا قیمت(تومان) پلن را وارد کنید',
        'USERS_BOT_ADD_PLAN_CONFIRM': 'لطفا اطلاعات زیر را تایید کنید',
        'USERS_BOT_ADD_PLAN_SUCCESS': '✅پلن با موفقیت افزوده شد',
        'USERS_BOT_OWNER_INFO_NOT_FOUND': '❌اطلاعات مالک یافت نشد \n لطفا ابتدا آن را تنظیم کنید.',
        'USERS_BOT_OWNER_INFO_ADD_USERNAME': 'لطفا نام کاربری تلگرام پشتیبان را وارد کنید\nلطفا همراه با @ وارد کنید\nمثال: @example',
        'USERS_BOT_OWNER_INFO_ADD_CARD_NUMBER': 'لطفا شماره 16 رقمی کارت بانکی جهت واریز را وارد کنید',
        'USERS_BOT_OWNER_INFO_ADD_CARD_NAME': 'لطفا نام صاحب حساب بانکی جهت واریز را وارد کنید',
        'USERS_BOT_SEND_MSG_USERS': 'لطفا پیام خود را برای ارسال به کاربران وارد کنید:',
        'USERS_BOT_PLANS_LIST': '📋لیست پلن های موجود',
        'USERS_BOT_SELECT_PLAN_TO_DELETE': 'لطفا پلن مورد نظر را برای حذف انتخاب کنید',
        'USERS_BOT_PLAN_DELETED': '✅پلن با موفقیت حذف شد',
        'USERS_BOT_SETTINGS': '⚙️تنظیمات ربات کاربران',
        'USERS_BOT_SETTINGS_HYPERLINK': 'تنظیم نمایش Hyperlink صفحه هیدیفای روی نام کاربر هنگام دریافت اطلاعات اشتراک',
        'USERS_BOT_ORDER_NUMBER_REQUEST': 'لطفا شماره سفارش را وارد کنید:',
        'SUCCESS_UPDATE_DATA': '✅اطلاعات با موفقیت به روز شد',
        'ERROR_INVALID_USERNAME': '❌نام کاربری نامعتبر است\n نام کاربری باید با @ شروع شود',
        'ERROR_INVALID_CARD_NUMBER': '❌شماره کارت نامعتبر است\nشماره کارت باید 16 رقمی باشد',
        'PAYMENT_CONFIRMED': '✅پرداخت شما تایید شد\n از طریق دکمه [📊وضعیت اشتراک] میتوانید به اطلاعات اشتراک خود دسترسی داشته باشید.',
        'PAYMENT_NOT_CONFIRMED': '❌پرداخت شما تایید نشد!\nلطفا اگر اشتباهی صورت گرفته با پشتیبانی در تماس باشید.',
        'ERROR_PAYMENT_ALREADY_CONFIRMED': '❌پرداخت قبلا تایید شده است',
        'ERROR_PAYMENT_ALREADY_REJECTED': '❌پرداخت قبلا رد شده است',
        'PAYMENT_CONFIRMED_ADMIN': '✅پرداخت با موفقیت تایید شد',
        'PAYMENT_NOT_CONFIRMED_ADMIN': '❌پرداخت تایید نشد',
        'ERROR_ORDER_NOT_FOUND': '❌سفارش یافت نشد',
        'ERROR_PAYMENT_NOT_FOUND': '❌پرداخت یافت نشد',
        'ORDER_ID': 'شماره سفارش',
        'USER_TIME_EXPIRED': '⚠️منقضی',
        'PAYMENT_ASK_CHANGE_STATUS': 'آیا میخواهید وضعیت سفارش را تغییر دهید؟',
        'PAYMENT_ACCEPT_STATUS_CONFIRMED': '🟢تایید شده',
        'PAYMENT_ACCEPT_STATUS_NOT_CONFIRMED': '🔴رد شده',
        'PAYMENT_ACCEPT_STATUS_WAITING': '🟡در انتظار تایید',
        'PAYMENT_ACCEPT_STATUS': 'وضعیت:',
        'CREATED_AT': 'تاریخ ایجاد:',


    }

}
MESSAGES = MESSAGES[LANG]
