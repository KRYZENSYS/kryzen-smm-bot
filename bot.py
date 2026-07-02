"""
KRYZEN SMM Telegram Bot
Python aiogram 3 — 6 ta API key bilan avtomatik nakrutka
Bepul hosting uchun tayyor (Render, Railway, Replit, VPS)
"""
import os
import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ============================================================
# 1. SOZLAMALAR (Environment variables dan o'qiladi)
# ============================================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8901775999:AAGTn78lxr4kaTWgJeFcc9kNf3JYiJOJapU")
API_URL = os.getenv("API_URL", "https://bepulsmm.x404.uz/bot.php")

# 6 ta API key — vergul bilan ajratilgan yoki default
API_KEYS_STR = os.getenv(
    "API_KEYS",
    "e2b16fe27ef30908fa8374c01608a47d,"
    "317f89e6dbf34deff9da1bc44262d84d,"
    "ab2ba39c0876c0086f78bfdc130ea919,"
    "7e35240dcb1f13476f547e60e198f4ff,"
    "fa288572bb927d33533f068187f9cf6f,"
    "e525a59cf0c20342b172710173558705"
)
API_KEYS = [k.strip() for k in API_KEYS_STR.split(",") if k.strip()]

# API kalitlarni boshqarish
CURRENT_KEY_INDEX = 0
REQUEST_COUNTER = 0
REQUEST_LIMIT_PER_KEY = int(os.getenv("REQUEST_LIMIT_PER_KEY", "20"))

# Admin va kanal sozlamalari
ADMIN_ID = int(os.getenv("ADMIN_ID", "5372581382"))
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL", "@MatchingWorldHub")
AUTO_SERVICE_ID = os.getenv("AUTO_SERVICE_ID", "42")
AUTO_QUANTITY = int(os.getenv("AUTO_QUANTITY", "50"))
AUTO_INTERVAL = int(os.getenv("AUTO_INTERVAL", "10"))  # sekund

# Avto-xizmat holati
AUTO_BOOST_ACTIVE = False

# ============================================================
# 2. LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================
# 3. BOT VA DISPATCHER
# ============================================================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ============================================================
# 4. SMM XIZMATLAR RO'YXATI
# ============================================================
SERVICES = {
    "12": {"name": "TikTok Video Ko'rishlar", "min": 100, "max": 300},
    "26": {"name": "Telegram Post Ko'rishlar", "min": 10, "max": 200},
    "36": {"name": "Telegram Obunachi", "min": 10, "max": 10},
    "37": {"name": "Telegram Post Reaksiya", "min": 10, "max": 10},
    "39": {"name": "Instagram Reels Ko'rishlar", "min": 100, "max": 100},
    "40": {"name": "Instagram Reels Like", "min": 10, "max": 10},
    "41": {"name": "TikTok Reels Prasmotr", "min": 100, "max": 100},
    "42": {"name": "UZB Telegram Obunachi (50ta)", "min": 50, "max": 50},
}

# ============================================================
# 5. FSM HOLATLARI
# ============================================================
class OrderState(StatesGroup):
    waiting_for_link = State()
    waiting_for_quantity = State()

# ============================================================
# 6. API KALITLARNI BOSHQARISH
# ============================================================
def get_current_api_key() -> str:
    """Joriy API kalitni qaytaradi, limitga yetganda keyingisiga o'tadi."""
    global CURRENT_KEY_INDEX, REQUEST_COUNTER

    active_key = API_KEYS[CURRENT_KEY_INDEX]
    REQUEST_COUNTER += 1

    logger.info(
        f"🔑 Kalit: {CURRENT_KEY_INDEX + 1}/{len(API_KEYS)} | "
        f"So'rovlar: {REQUEST_COUNTER}/{REQUEST_LIMIT_PER_KEY}"
    )

    if REQUEST_COUNTER >= REQUEST_LIMIT_PER_KEY:
        REQUEST_COUNTER = 0
        CURRENT_KEY_INDEX = (CURRENT_KEY_INDEX + 1) % len(API_KEYS)
        logger.info(f"🔄 Limitga erishildi → {CURRENT_KEY_INDEX + 1}-kalitga o'tildi")

    return active_key

async def send_api_request(params: dict) -> dict | None:
    """API ga so'rov yuboradi."""
    params['key'] = get_current_api_key()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, data=params, timeout=30) as response:
                if response.status == 200:
                    return await response.json(content_type=None)
                logger.error(f"API status: {response.status}")
                return None
    except Exception as e:
        logger.error(f"API xatolik: {e}")
        return None

# ============================================================
# 7. AVTOMATIK NAKRUTKA LOOP
# ============================================================
async def auto_boost_loop():
    """Har AUTO_INTERVAL sekundda yangi invite link yaratadi va buyurtma beradi."""
    global AUTO_BOOST_ACTIVE
    logger.info(f"🤖 Avto-loop tayyor (interval: {AUTO_INTERVAL}s, kanal: {TARGET_CHANNEL})")

    while True:
        if AUTO_BOOST_ACTIVE:
            try:
                logger.info("🔗 Yangi invite link yaratilmoqda...")
                chat_invite_link = await bot.create_chat_invite_link(
                    chat_id=TARGET_CHANNEL,
                    creates_join_request=False
                )
                new_link = chat_invite_link.invite_link
                logger.info(f"Yangi link: {new_link}")

                api_params = {
                    "action": "add",
                    "service": AUTO_SERVICE_ID,
                    "link": new_link,
                    "quantity": AUTO_QUANTITY,
                }
                res = await send_api_request(api_params)

                if res and "order" in res:
                    order_id = res['order']
                    logger.info(f"✅ Avto-buyurtma #{order_id}")
                    admin_text = (
                        f"🤖 <b>Avtomatik buyurtma berildi</b>\n\n"
                        f"🆔 <b>Buyurtma ID</b> <code>{order_id</code>\n"
                        f"🔗 <b>Link</b> {new_link}\n"
                        f"📊 <b>Miqdor</b> {AUTO_QUANTITY} ta\n"
                        f"🔑 <b>Faol kalit</b> {CURRENT_KEY_INDEX + 1}/{len(API_KEYS)}\n"
                        f"🕒 <b>Interval</b> Har {AUTO_INTERVAL} soniyada"
                    )
                    try:
                        await bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML")
                    except Exception as e:
                        logger.error(f"Adminga xabar yuborishda xatolik: {e}")
                else:
                    error_msg = res.get("error", "Noma'lum xatolik") if isinstance(res, dict) else "API ulanish xatosi"
                    logger.error(f"❌ Avto-buyurtma xatosi: {error_msg}")
                    try:
                        await bot.send_message(
                            chat_id=ADMIN_ID,
                            text=f"❌ <b>Avto-buyurtmada xatolik</b>\n<code>{error_msg</code>",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
            except Exception as e:
                logger.error(f"Avto-loop xatosi: {e}")

        await asyncio.sleep(AUTO_INTERVAL)

# ============================================================
# 8. KEYBOARD FUNKSIYALARI
# ============================================================
def main_menu():
    kb = [
        [types.KeyboardButton(text="🎁 Bepul Xizmatlar"), types.KeyboardButton(text="💰 Balansni tekshirish")],
        [types.KeyboardButton(text="📋 Buyurtmalar holati")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def services_keyboard():
    keyboard = []
    for s_id, s_info in SERVICES.items():
        keyboard.append([InlineKeyboardButton(text=s_info['name'], callback_data=f"srv_{s_id}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def admin_inline_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text="🟢 Yoqish", callback_data="admin_auto_on"),
            InlineKeyboardButton(text="🔴 O'chirish", callback_data="admin_auto_off"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ============================================================
# 9. HANDLERLAR
# ============================================================
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    """Start komandasi — admin va oddiy foydalanuvchi uchun alohida."""
    if message.from_user.id == ADMIN_ID:
        status_text = "🟢 Yoqilgan" if AUTO_BOOST_ACTIVE else "🔴 O'chirilgan"
        await message.answer(
            f"Salom, <b>Admin</b>!\n\n"
            f"🤖 <b>Avto-xizmat holati</b> {status_text}\n"
            f"Kanal: <code>{TARGET_CHANNEL</code>\n"
            f"Xizmat: <code>{AUTO_SERVICE_ID</code> | Miqdor: {AUTO_QUANTITY}\n"
            f"Interval: {AUTO_INTERVAL}s | API kalitlar: {len(API_KEYS)} ta",
            parse_mode="HTML",
            reply_markup=admin_inline_keyboard()
        )
    else:
        await message.answer(
            f"Xush kelibsiz, {message.from_user.full_name}!\n"
            f"Bu bot orqali bepul SMM xizmatlaridan foydalanishingiz mumkin.",
            reply_markup=main_menu()
        )

@dp.callback_query(F.data == "admin_auto_on")
async def inline_turn_on(callback: types.CallbackQuery):
    """Avto-xizmatni yoqish (faqat admin)."""
    global AUTO_BOOST_ACTIVE
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    if AUTO_BOOST_ACTIVE:
        await callback.answer("🤖 Avto-xizmat allaqachon yoqilgan!", show_alert=True)
        return
    AUTO_BOOST_ACTIVE = True
    await callback.message.edit_text(
        f"Salom, <b>Admin</b>!\n\n🤖 <b>Avto-xizmat holati</b> 🟢 Yoqilgan\n"
        f"Kanal: <code>{TARGET_CHANNEL</code>\n"
        f"Xizmat: <code>{AUTO_SERVICE_ID</code> | Miqdor: {AUTO_QUANTITY}\n"
        f"Interval: {AUTO_INTERVAL}s",
        parse_mode="HTML",
        reply_markup=admin_inline_keyboard()
    )
    await callback.answer("✅ Ishga tushirildi!")

@dp.callback_query(F.data == "admin_auto_off")
async def inline_turn_off(callback: types.CallbackQuery):
    """Avto-xizmatni o'chirish (faqat admin)."""
    global AUTO_BOOST_ACTIVE
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    if not AUTO_BOOST_ACTIVE:
        await callback.answer("🤖 Avto-xizmat allaqachon o'chirilgan!", show_alert=True)
        return
    AUTO_BOOST_ACTIVE = False
    await callback.message.edit_text(
        f"Salom, <b>Admin</b>!\n\n🤖 <b>Avto-xizmat holati</b> 🔴 O'chirilgan\n"
        f"Avtomatik nakrutka tizimi to'xtatildi.",
        parse_mode="HTML",
        reply_markup=admin_inline_keyboard()
    )
    await callback.answer("🛑 To'xtatildi!")

@dp.message(F.text == "💰 Balansni tekshirish")
async def check_balance(message: types.Message):
    res = await send_api_request({"action": "balance"})
    if res and "balance" in res:
        await message.answer(
            f"💳 API balans: <b>{res['balance']</b> so'm\n"
            f"(Eslatma: Buyurtmalar mutlaqo bepul!)",
            parse_mode="HTML"
        )
    else:
        await message.answer("❌ Balansni olishda xatolik yuz berdi.")

@dp.message(F.text == "🎁 Bepul Xizmatlar")
async def show_services(message: types.Message):
    await message.answer("Quyidagi bepul xizmatlardan birini tanlang:", reply_markup=services_keyboard())

@dp.callback_query(F.data.startswith("srv_"))
async def select_service(callback: types.CallbackQuery, state: FSMContext):
    service_id = callback.data.split("_")[1]
    service = SERVICES.get(service_id)
    if not service:
        await callback.answer("❌ Xizmat topilmadi", show_alert=True)
        return
    await state.update_data(service_id=service_id, min_q=service['min'], max_q=service['max'])
    await callback.message.edit_text(
        f"Siz tanladingiz: <b>{service['name']</b>\n\n"
        f"🔗 Iltimos, kanal/profil yoki post havolasini yuboring:",
        parse_mode="HTML"
    )
    await state.set_state(OrderState.waiting_for_link)
    await callback.answer()

@dp.message(OrderState.waiting_for_link)
async def get_link(message: types.Message, state: FSMContext):
    await state.update_data(link=message.text)
    data = await state.get_data()
    await message.answer(
        f"Miqdorni kiriting:\n"
        f"Eng kam: <b>{data['min_q']</b> | Eng ko'p: <b>{data['max_q']</b>",
        parse_mode="HTML"
    )
    await state.set_state(OrderState.waiting_for_quantity)

@dp.message(OrderState.waiting_for_quantity)
async def get_quantity(message: types.Message, state: FSMContext):
    quantity_text = message.text
    data = await state.get_data()
    if not quantity_text.isdigit():
        await message.answer("❌ Iltimos, faqat raqam kiriting!")
        return
    quantity = int(quantity_text)
    if quantity < data['min_q'] or quantity > data['max_q']:
        await message.answer(f"❌ Miqdor {data['min_q']} va {data['max_q']} oralig'ida bo'lishi kerak!")
        return

    await message.answer("🔄 Buyurtma yuborilmoqda, iltimos kuting...")
    api_params = {
        "action": "add",
        "service": data['service_id'],
        "link": data['link'],
        "quantity": quantity,
    }
    res = await send_api_request(api_params)
    await state.clear()

    if res and "order" in res:
        await message.answer(
            f"✅ Buyurtma muvaffaqiyatli qabul qilindi!\n"
            f"🆔 Buyurtma ID: <code>{res['order']</code>",
            parse_mode="HTML",
            reply_markup=main_menu()
        )
    else:
        error_msg = res.get("error", "Noma'lum xatolik") if isinstance(res, dict) else "API bilan aloqa uzildi"
        await message.answer(f"❌ Xatolik yuz berdi: {error_msg}", reply_markup=main_menu())

@dp.message(F.text == "📋 Buyurtmalar holati")
async def order_status_prompt(message: types.Message):
    await message.answer("⏳ Buyurtmalar ro'yxati olinmoqda...")
    res = await send_api_request({"action": "orders"})
    if res and isinstance(res, list):
        if len(res) == 0:
            await message.answer("Sizda hali buyurtmalar mavjud emas.")
            return
        text = "📋 <b>Oxirgi buyurtmalaringiz</b>\n\n"
        for order in res[:5]:
            text += (
                f"🆔 <b>ID</b> {order.get('order')} | "
                f"<b>Xizmat</b> {order.get('service')}\n"
                f"📊 <b>Status</b> {order.get('status')} | "
                f"<b>Miqdor</b> {order.get('quantity')}\n"
                f"🔗 <b>Link</b> <code>{order.get('link')</code>\n"
                f"------------------------\n"
            )
        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer("❌ Buyurtmalar ro'yxatini olib bo'lmadi.")

# ============================================================
# 10. BOTNI ISHGA TUSHIRISH
# ============================================================
async def main():
    logger.info("🚀 Bot ishga tushmoqda...")
    logger.info(f"📊 API kalitlar: {len(API_KEYS)} ta")
    logger.info(f"👤 Admin ID: {ADMIN_ID}")
    logger.info(f"📢 Kanal: {TARGET_CHANNEL}")
    asyncio.create_task(auto_boost_loop())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
