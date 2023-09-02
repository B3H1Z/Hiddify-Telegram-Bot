from config import LANG

# Response Messages Template
MESSAGES = {
    'EN': {
        'WELCOME': "Welcome to Users Bot",
        'INFO_USER': '📄Your Subscription Info',
        'INFO_USAGE': '📊Usage:',
        'INFO_REMAINING_DAYS': '⏳Remaining Days:',
        'INFO_ID': '🔑UUID:',
        'OF': 'of',
        'GB': 'GB',
        'DAY_EXPIRE': 'Days',
        'CONFIRM_SUBSCRIPTION_QUESTION': 'Is this your subscription?',
        'NAME': 'Name:',
        'CANCEL_SUBSCRIPTION': 'Subscription not confirmed',
        'SUBSCRIPTION_CONFIRMED': 'Your subscription has been confirmed. Now you can get your subscription status.',
        'WAIT': 'Please wait...',
        'UNKNOWN_ERROR': 'Unknown error!',
        'ENTER_SUBSCRIPTION_INFO': 'Please enter your subscription info\n One of the configs, uuid or subscription link',
        'SUBSCRIPTION_INFO_NOT_FOUND': 'Subscription info not found!',
        'SUBSCRIPTION_UNLINKED': 'Subscription unlinked!',
        'USER_NAME': '👤Name:',
        'PLANS_LIST': '📋Plans List:',
        'PLANS_NOT_FOUND': 'Plans not found!',
        'PLAN_ADD_NAME': 'Please enter your name:',
        'SUBSCRIPTION_SUCCESS_ADDED': 'Your subscription has been successfully added.',
        'PLAN_INFO': '📄Plan Info:',
        'PLAN_SIZE': 'Size:',
        'PLAN_DAYS': 'Days:',
        'PLAN_PRICE': 'Price:',
        'TOMAN': 'T',
        'REQUEST_SEND_SCREENSHOT': 'Please send your payment receipt.',
        'ERROR_TYPE_SEND_SCREENSHOT': 'Please send your payment receipt as a photo!',
        'REQUEST_SEND_NAME': 'Please send your name.',
        'NO_SUBSCRIPTION': 'You have no subscription!',
        'WAIT_FOR_ADMIN_CONFIRMATION': '✅Your subscription is waiting for confirmation by the admin.\nPlease wait...',
        'NEW_PAYMENT_RECEIVED': 'New payment received',
        'PAYMENT_ASK_TO_CONFIRM': 'Do you want to confirm this payment?',
        'REQUEST_SEND_TO_QR': 'Please send your config or subscription link:',
        'REQUEST_SEND_TO_QR_ERROR': 'Please send your config or subscription!',
        'USER_CONFIGS_LIST': '📋Your Configs:',
        'USER_CONFIGS_NOT_FOUND': 'Configs not found!',
        'ERROR_CONFIG_NOT_FOUND': 'Config not found!',
        'ERROR_INVALID_COMMAND': 'Invalid command!',
        'ALREADY_SUBSCRIBED': 'You are already subscribed!',
        'ERROR_INVALID_NUMBER': 'Invalid number!',
        'CANCELED': 'Cancelled!',

    },
    'FA': {
        'WELCOME': "به ربات کاربران خوش آمدید",
        'INFO_USER': '📄اطلاعات اشتراک شما',
        'INFO_USAGE': '📊میزان استفاده:',
        'INFO_REMAINING_DAYS': '⏳زمان باقی مانده:',
        'INFO_ID': '🔑شناسه:',
        'OF': 'از',
        'GB': 'گیگ',
        'DAY_EXPIRE': 'روز',
        'CONFIRM_SUBSCRIPTION_QUESTION': 'آیا این اشتراک شماست؟',
        'NAME': 'نام:',
        'CANCEL_SUBSCRIPTION': 'اشتراک تایید نشد',
        'SUBSCRIPTION_CONFIRMED': 'اشتراک شما تایید شد. حالا میتوانید وضعیت اشتراک خود را دریافت کنید.',
        'WAIT': 'لطفا صبر کنید...',
        'UNKNOWN_ERROR': 'خطای ناشناخته!',
        'ENTER_SUBSCRIPTION_INFO': 'لطفا اطلاعات اشتراک خود را وارد کنید\n یکی از کانفیگ ها، uuid یا لینک اشتراک',
        'SUBSCRIPTION_INFO_NOT_FOUND': 'اطلاعات اشتراک یافت نشد!',
        'USER_NOT_FOUND': 'کاربر یافت نشد.',
        'SUBSCRIPTION_UNLINKED': 'اشتراک لغو شد!',
        'USER_NAME': '👤نام:',
        'PLANS_LIST': '📋لیست پلن ها:',
        'PLANS_NOT_FOUND': 'پلنی یافت نشد!',
        'PLAN_ADD_NAME': 'لطفا نام خود را وارد کنید:',
        'SUBSCRIPTION_SUCCESS_ADDED': 'اشتراک شما با موفقیت اضافه شد.',
        'PLAN_INFO': '📋اطلاعات پلن انتخاب شده',
        'PLAN_INFO_SIZE': 'حجم پلن:',
        'PLAN_INFO_PRICE': 'قیمت پلن:',
        'PLAN_INFO_DAYS': 'زمان پلن:',
        'TOMAN': 'تومان',
        'REQUEST_SEND_SCREENSHOT': '⬇️لطفا رسید پرداخت خود را در زیر این پیام ارسال کنید:',
        'ERROR_TYPE_SEND_SCREENSHOT': '⬇️لطفا رسید پرداخت خود را به صورت عکس ارسال کنید:',
        'REQUEST_SEND_NAME': '⬇️لطفا نام خود را ارسال کنید:',
        'NO_SUBSCRIPTION': 'شما هیچ اشتراکی ندارید!',
        'WAIT_FOR_ADMIN_CONFIRMATION': '✅اشتراک شما در انتظار تایید توسط ادمین است.\nلطفا صبر کنید.',
        'NEW_PAYMENT_RECEIVED': "پرداخت جدیدی ثبت شد",
        'PAYMENT_ASK_TO_CONFIRM': 'آیا شما این پرداخت را تایید میکنید؟',
        'REQUEST_SEND_TO_QR': 'لطفا کانفیگ یا لینک اشتراک خود را ارسال کنید:',
        'REQUEST_SEND_TO_QR_ERROR': 'متن ارسالی معتبر نیست\nلطفا کانفیگ یا لینک اشتراک خود را به صورت متنی ارسال کنید!',
        'USER_CONFIGS_LIST': '📋لیست کانفیگ های شما',
        'USER_CONFIGS_NOT_FOUND': 'کانفیگی یافت نشد!',
        'ERROR_CONFIG_NOT_FOUND': 'کانفیگ یافت نشد!',
        'ERROR_INVALID_COMMAND': 'دستور نامعتبر!',
        'ALREADY_SUBSCRIBED': 'اشتراک شما قبلا اضافه شده است.',
        'ERROR_INVALID_NUMBER': 'لطفا مقداری عددی وارد کنید!',
        'CANCELED': 'لغو شد',
    }

}
MESSAGES = MESSAGES[LANG]
