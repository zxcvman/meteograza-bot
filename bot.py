import os
import asyncio
import logging
import httpx
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN", "8742820412:AAHrQ59ppcc4YY85Bg7tOQAhSD7-Vh1cDiE")

# ─── База городов России ───────────────────────────────
CITIES = {
    "москва": (55.7558, 37.6173), "санкт-петербург": (59.9311, 30.3609),
    "питер": (59.9311, 30.3609), "спб": (59.9311, 30.3609),
    "новосибирск": (54.9885, 82.9207), "екатеринбург": (56.8519, 60.6122),
    "нижний новгород": (56.2965, 43.9361), "казань": (55.7887, 49.1221),
    "челябинск": (55.1644, 61.4368), "омск": (54.9885, 73.3242),
    "самара": (53.2028, 50.1408), "ростов-на-дону": (47.2357, 39.7015),
    "уфа": (54.7388, 55.9721), "красноярск": (56.0184, 92.8672),
    "воронеж": (51.6717, 39.2106), "пермь": (58.0105, 56.2502),
    "волгоград": (48.7080, 44.5133), "краснодар": (45.0448, 38.9760),
    "саратов": (51.5924, 46.0335), "тюмень": (57.1553, 65.5880),
    "тольятти": (53.5303, 49.3461), "ижевск": (56.8527, 53.2048),
    "барнаул": (53.3548, 83.7697), "хабаровск": (48.4827, 135.0840),
    "ульяновск": (54.3282, 48.3866), "иркутск": (52.2855, 104.2890),
    "владивосток": (43.1332, 131.9113), "ярославль": (57.6261, 39.8845),
    "томск": (56.4977, 84.9744), "оренбург": (51.7879, 55.1076),
    "кемерово": (55.3904, 86.0479), "новокузнецк": (53.7557, 87.1099),
    "рязань": (54.6269, 39.6916), "астрахань": (46.3497, 48.0408),
    "набережные челны": (55.7435, 52.4066), "пенза": (53.2007, 45.0046),
    "липецк": (52.6031, 39.5708), "тула": (54.2043, 37.6184),
    "киров": (58.6036, 49.6680), "чебоксары": (56.1439, 47.2489),
    "улан-удэ": (51.8272, 107.6064), "иваново": (57.0005, 40.9739),
    "брянск": (53.2521, 34.3717), "нижний тагил": (57.9100, 59.9822),
    "магнитогорск": (53.4113, 58.9937), "курск": (51.7304, 36.1921),
    "тверь": (56.8589, 35.9176), "ставрополь": (45.0440, 41.9686),
    "белгород": (50.5957, 36.5879), "сочи": (43.5855, 39.7231),
    "мурманск": (68.9792, 33.0925), "архангельск": (64.5401, 40.5433),
    "якутск": (62.0280, 129.7325), "петрозаводск": (61.7849, 34.3469),
    "владикавказ": (43.0248, 44.6811), "чита": (52.0315, 113.5010),
    "сургут": (61.2500, 73.4167), "нефтеюганск": (61.1008, 72.5994),
    "нижневартовск": (60.9384, 76.5638), "ханты-мансийск": (61.0069, 69.0102),
    "новый уренгой": (66.0846, 76.6819), "норильск": (69.3558, 88.1893),
    "южно-сахалинск": (46.9591, 142.7381), "петропавловск-камчатский": (53.0452, 158.6536),
    "магадан": (59.5681, 150.8083), "анадырь": (64.7348, 177.4993),
    "владимир": (56.1291, 40.4067), "орел": (52.9651, 36.0785),
    "смоленск": (54.7818, 32.0401), "калуга": (54.5293, 36.2754),
    "кострома": (57.7677, 40.9268), "вологда": (59.2239, 39.8978),
    "псков": (57.8136, 28.3496), "великий новгород": (58.5213, 31.2752),
    "мурманск": (68.9792, 33.0925), "сыктывкар": (61.6688, 50.8364),
    "нальчик": (43.4846, 43.6074), "махачкала": (42.9849, 47.5047),
    "грозный": (43.3178, 45.6980), "элиста": (46.3074, 44.2680),
    "майкоп": (44.6098, 40.1069), "черкесск": (44.2291, 42.0665),
    "назрань": (43.2261, 44.7669), "абакан": (53.7154, 91.4293),
    "горно-алтайск": (51.9581, 85.9603), "кызыл": (51.7191, 94.4378),
    "биробиджан": (48.7949, 132.9212), "благовещенск": (50.2897, 127.5270),
    "комсомольск-на-амуре": (50.5500, 137.0000), "находка": (42.8217, 132.8730),
    "уссурийск": (43.7985, 131.9474), "воркута": (67.4983, 64.0339),
    "ухта": (63.5603, 53.7155), "усинск": (65.9997, 57.5389),
    "тобольск": (58.1975, 68.2537), "ишим": (56.1124, 69.4892),
    "курган": (55.4507, 65.3410), "шадринск": (56.0858, 63.6336),
    "орск": (51.2354, 58.6238), "нижнекамск": (55.6386, 51.8279),
    "альметьевск": (54.9024, 52.2979), "серов": (59.6003, 60.5800),
    "каменск-уральский": (56.4143, 61.9178), "первоуральск": (56.9044, 59.9437),
}

# ─── WMO коды ─────────────────────────────────────────
WMO = {
    0:"☀️ Ясно", 1:"🌤 Преим. ясно", 2:"⛅ Переменная облачность",
    3:"☁️ Пасмурно", 45:"🌫 Туман", 48:"🌫 Гололёдный туман",
    51:"🌦 Морось слабая", 53:"🌦 Морось умеренная", 55:"🌧 Морось сильная",
    61:"🌧 Дождь слабый", 63:"🌧 Дождь умеренный", 65:"🌧 Дождь сильный",
    66:"🌨 Ледяной дождь", 67:"🌨 Сильный ледяной дождь",
    71:"❄️ Снег слабый", 73:"❄️ Снег умеренный", 75:"❄️ Снег сильный",
    77:"🌨 Снежная крупа", 80:"🌦 Ливень слабый", 81:"🌦 Ливень умеренный",
    82:"⛈ Ливень сильный", 85:"🌨 Снегопад слабый", 86:"🌨 Снегопад сильный",
    95:"⛈ Гроза", 96:"⛈ Гроза с градом", 99:"⛈ Гроза с сильным градом",
}

DIRS = ["С","СВ","В","ЮВ","Ю","ЮЗ","З","СЗ"]

def wmo_name(c): return WMO.get(c, f"Код {c}")
def wind_dir(d): return DIRS[round(d/45)%8]
def tcolor(t):
    if t <= -20: return "🔵"
    if t <= -5:  return "🔵"
    if t <= 5:   return "🟡"
    if t <= 20:  return "🟢"
    if t <= 30:  return "🟠"
    return "🔴"

def find_city(name: str):
    name = name.lower().strip()
    if name in CITIES:
        return name.title(), CITIES[name]
    # Частичное совпадение
    for k, v in CITIES.items():
        if name in k or k in name:
            return k.title(), v
    return None, None

async def fetch_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,apparent_temperature,relative_humidity_2m,"
        f"weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m,"
        f"pressure_msl,precipitation,cloud_cover,visibility,uv_index,"
        f"dew_point_2m,snow_depth,wet_bulb_temperature_2m,cape"
        f"&hourly=temperature_2m,weather_code,wind_speed_10m,wind_gusts_10m,"
        f"precipitation_probability,cape,lifted_index,wind_speed_80m,"
        f"cloud_cover,freezing_level_height"
        f"&daily=weather_code,temperature_2m_max,temperature_2m_min,"
        f"precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max,"
        f"sunrise,sunset,uv_index_max,snowfall_sum"
        f"&timezone=auto&forecast_days=7"
    )
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(url)
        return r.json()

def cape_label(cape):
    if cape < 300: return "Стабильно"
    if cape < 1000: return "Слабая"
    if cape < 2500: return "Умеренная"
    if cape < 4000: return "Высокая"
    return "Экстремальная"

def li_label(li):
    if li is None: return ""
    if li >= 0: return "Стабильно"
    if li >= -2: return "Слабо неустойчиво"
    if li >= -4: return "Неустойчиво"
    if li >= -6: return "Сильно неустойчиво"
    return "Экстремальная нестабильность"

def gust_label(g):
    if g < 40: return "Слабый"
    if g < 60: return "Умеренный"
    if g < 80: return "Сильный"
    if g < 100: return "Шквал"
    return "⚠️ Ураганный"

def format_current(data, city_name):
    cur = data["current"]
    daily = data["daily"]
    t = cur["temperature_2m"]
    at = cur["apparent_temperature"]
    rh = cur["relative_humidity_2m"]
    code = cur["weather_code"]
    ws = cur["wind_speed_10m"]
    wd = cur["wind_direction_10m"]
    wg = cur.get("wind_gusts_10m", 0)
    pres = cur["pressure_msl"]
    prec = cur.get("precipitation", 0)
    cloud = cur.get("cloud_cover", 0)
    vis = cur.get("visibility", 0)
    uv = cur.get("uv_index", 0)
    dp = cur.get("dew_point_2m")
    snow = cur.get("snow_depth", 0)
    wb = cur.get("wet_bulb_temperature_2m")
    cape = cur.get("cape", 0)
    gust_cat = gust_label(wg)

    vis_str = f"{vis/1000:.0f} км" if vis >= 1000 else f"{vis:.0f} м"
    mm_hg = round(pres * 0.750064)

    lines = [
        f"🌍 *{city_name}*",
        f"🕒 {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        "",
        f"{wmo_name(code)}",
        f"{tcolor(t)} *{t:+.1f}°C* (ощущ. {at:+.1f}°C)",
        "",
        "📊 *Текущие условия*",
        f"💧 Влажность: {rh}% | Точка росы: {dp:+.1f}°C" if dp is not None else f"💧 Влажность: {rh}%",
        f"🌡 Давление: {round(pres)} гПа / {mm_hg} мм рт.ст.",
        f"👁 Видимость: {vis_str} | ☁️ Облачность: {cloud}%",
    ]
    if wb:
        lines.append(f"🌡 Влажный термометр: {wb:+.1f}°C")
    if snow and snow > 0:
        lines.append(f"❄️ Снежный покров: {snow:.0f} см")
    lines += [
        "",
        "💨 *Ветер*",
        f"📍 {wind_dir(wd)} {ws:.0f} км/ч | Порывы: {wg:.0f} км/ч ({gust_cat})",
        "",
        "☀️ *Радиация*",
        f"UV-индекс: {uv:.1f}",
    ]
    if cape > 200:
        lines += [
            "",
            "⚡ *Нестабильность*",
            f"CAPE: {cape:.0f} Дж/кг — {cape_label(cape)}",
        ]
    if daily.get("temperature_2m_max") and daily.get("temperature_2m_min"):
        mx = daily["temperature_2m_max"][0]
        mn = daily["temperature_2m_min"][0]
        lines += ["", f"📈 Сегодня: макс {mx:+.0f}°C / мин {mn:+.0f}°C"]

    return "\n".join(lines)

def format_forecast(data, city_name):
    daily = data["daily"]
    days = len(daily["time"])
    lines = [f"📅 *Прогноз на 7 дней — {city_name}*", ""]
    day_names = ["Сегодня", "Завтра"]
    for i in range(min(7, days)):
        dt = datetime.strptime(daily["time"][i], "%Y-%m-%d")
        if i < 2:
            day = day_names[i]
        else:
            day = dt.strftime("%a %d.%m").capitalize()
        code = daily["weather_code"][i]
        mx = daily["temperature_2m_max"][i]
        mn = daily["temperature_2m_min"][i]
        pp = daily.get("precipitation_probability_max", [0]*7)[i] or 0
        wmax = daily.get("wind_speed_10m_max", [0]*7)[i] or 0
        gmax = daily.get("wind_gusts_10m_max", [0]*7)[i] or 0
        snow = daily.get("snowfall_sum", [0]*7)[i] or 0
        uv = daily.get("uv_index_max", [0]*7)[i] or 0

        line = f"*{day}*: {wmo_name(code)}\n"
        line += f"  🌡 {mn:+.0f}..{mx:+.0f}°C"
        if pp > 15:
            line += f" | 💧 {pp:.0f}%"
        if snow > 0.5:
            line += f" | ❄️ {snow:.1f} мм"
        if wmax > 30:
            line += f" | 💨 {wmax:.0f} км/ч"
        if gmax > 60:
            line += f" *(порывы {gmax:.0f})*"
        if uv > 5:
            line += f" | ☀️ UV {uv:.0f}"
        lines.append(line)

    return "\n".join(lines)

def format_alerts(data, city_name):
    hourly = data["hourly"]
    daily = data["daily"]
    n = len(hourly["time"])

    # Найти текущий час
    now = datetime.now()
    si = 0
    for i, t in enumerate(hourly["time"]):
        if datetime.fromisoformat(t) >= now:
            si = i; break

    events = []
    seen = set()

    for offset in range(min(168, n - si)):
        hi = si + offset
        if hi >= n: break
        code   = (hourly.get("weather_code") or [])[hi] or 0
        gust   = (hourly.get("wind_gusts_10m") or [])[hi] or 0
        cape   = (hourly.get("cape") or [])[hi] or 0
        ws     = (hourly.get("wind_speed_10m") or [])[hi] or 0
        ws80   = (hourly.get("wind_speed_80m") or [])[hi] or 0
        li     = (hourly.get("lifted_index") or [])[hi]
        pp     = (hourly.get("precipitation_probability") or [])[hi] or 0
        shear  = abs((ws80 or ws) - ws)
        t_str  = hourly["time"][hi]
        dt     = datetime.fromisoformat(t_str)

        if offset < 24:
            lbl = f"сегодня {dt.strftime('%H:%M')}"
        elif offset < 48:
            lbl = f"завтра {dt.strftime('%H:%M')}"
        else:
            lbl = dt.strftime("%d.%m %H:%M")

        def add(icon, name, desc, key=None):
            k = key or (name + dt.strftime("%Y%m%d"))
            if k not in seen:
                seen.add(k)
                events.append(f"{icon} *{name}* — {lbl}\n   _{desc}_")

        if code >= 95:
            add("⛈", "Гроза" + (" с градом" if code >= 96 else ""),
                f"WMO {code}, CAPE {cape:.0f} Дж/кг")
        if gust >= 60 and code < 95:
            cat = "Сильный шквал" if gust >= 100 else "Шквал" if gust >= 80 else "Шквалистый ветер"
            add("💨", cat, f"Порывы до {gust:.0f} км/ч")
        if cape >= 1500 and shear >= 20 and gust >= 50:
            add("🌀", "Шкваловый ворот",
                f"CAPE {cape:.0f}, сдвиг {shear:.0f} км/ч")
        if cape >= 2000 and shear >= 25 and li is not None and li < -4:
            add("🌪", "Суперячейка" + (" (мезоциклон)" if cape >= 3000 else ""),
                f"CAPE {cape:.0f}, LI {li:.1f}, сдвиг {shear:.0f} км/ч")
        if cape >= 2500 and shear >= 35 and li is not None and li < -6:
            add("🌪", "Возможен смерч",
                f"Экстрем. нестабильность CAPE {cape:.0f}, LI {li:.1f}")
        if gust >= 90:
            add("🌀", "Ураган/Шторм", f"Порывы {gust:.0f} км/ч")
        if code in (75, 77, 86) and pp >= 40:
            add("❄️", "Сильный снегопад", f"WMO {code}, вероятность {pp}%")
        if code in (65, 82) and pp >= 40:
            add("🌧", "Сильный ливень", f"WMO {code}, вероятность {pp}%")
        if code in (45, 48) and offset < 48:
            add("🌫️", "Туман" + (" (замерзающий)" if code == 48 else ""),
                "Ограниченная видимость")
        if gust >= 60 and cape >= 800:
            add("⚠️", "Грозовой шквал", f"Порывы {gust:.0f} км/ч, CAPE {cape:.0f}")

    lines = [f"⚠️ *Опасные явления — {city_name}*", ""]
    if not events:
        lines.append("✅ Опасных явлений на 7 дней не прогнозируется")
    else:
        lines += events[:15]
        if len(events) > 15:
            lines.append(f"\n_...и ещё {len(events)-15} событий_")
    return "\n".join(lines)

# ─── Handlers ─────────────────────────────────────────
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = ReplyKeyboardMarkup([
        [KeyboardButton("📍 Отправить геолокацию", request_location=True)],
        ["/help"]
    ], resize_keyboard=True)
    await update.message.reply_text(
        "👋 *МетеоГроза Бот*\n\n"
        "Реальная погода по всей России на основе Open-Meteo.\n\n"
        "Команды:\n"
        "🌤 `/weather Москва` — текущая погода\n"
        "📅 `/forecast Казань` — прогноз 7 дней\n"
        "⚠️ `/alerts Сочи` — опасные явления\n"
        "📍 Или просто отправь геолокацию",
        parse_mode="Markdown", reply_markup=kb
    )

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Справка*\n\n"
        "`/weather [город]` — подробная текущая погода\n"
        "`/forecast [город]` — прогноз на 7 дней\n"
        "`/alerts [город]` — прогноз опасных явлений (гроза, шквал, смерч, снегопад...)\n\n"
        "Доступно 120+ городов России.\n"
        "Данные: Open-Meteo (обновляются каждый час)",
        parse_mode="Markdown"
    )

async def cmd_weather(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Укажи город: `/weather Москва`", parse_mode="Markdown")
        return
    city_input = " ".join(ctx.args)
    name, coords = find_city(city_input)
    if not coords:
        await update.message.reply_text(f"❌ Город «{city_input}» не найден.\nПопробуй: Москва, Казань, Новосибирск...")
        return
    msg = await update.message.reply_text("⏳ Получаю данные...")
    try:
        data = await fetch_weather(*coords)
        text = format_current(data, name)
        await msg.edit_text(text, parse_mode="Markdown")
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")

async def cmd_forecast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Укажи город: `/forecast Москва`", parse_mode="Markdown")
        return
    city_input = " ".join(ctx.args)
    name, coords = find_city(city_input)
    if not coords:
        await update.message.reply_text(f"❌ Город «{city_input}» не найден.")
        return
    msg = await update.message.reply_text("⏳ Получаю прогноз...")
    try:
        data = await fetch_weather(*coords)
        text = format_forecast(data, name)
        await msg.edit_text(text, parse_mode="Markdown")
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")

async def cmd_alerts(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Укажи город: `/alerts Москва`", parse_mode="Markdown")
        return
    city_input = " ".join(ctx.args)
    name, coords = find_city(city_input)
    if not coords:
        await update.message.reply_text(f"❌ Город «{city_input}» не найден.")
        return
    msg = await update.message.reply_text("⏳ Анализирую опасные явления...")
    try:
        data = await fetch_weather(*coords)
        text = format_alerts(data, name)
        await msg.edit_text(text, parse_mode="Markdown")
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")

async def handle_location(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    msg = await update.message.reply_text("⏳ Определяю погоду по геолокации...")
    try:
        # Reverse geocode через Nominatim
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(
                f"https://nominatim.openstreetmap.org/reverse",
                params={"lat": loc.latitude, "lon": loc.longitude,
                        "format": "json", "accept-language": "ru"},
                headers={"User-Agent": "MeteoGrozaBot/1.0"}
            )
            geo = r.json()
        addr = geo.get("address", {})
        city_name = (addr.get("city") or addr.get("town") or
                     addr.get("village") or addr.get("county") or "Ваша точка")
        data = await fetch_weather(loc.latitude, loc.longitude)
        text = format_current(data, city_name)
        await msg.edit_text(text, parse_mode="Markdown")
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")

async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Просто текст = ищем город"""
    text = update.message.text.strip()
    name, coords = find_city(text)
    if coords:
        msg = await update.message.reply_text("⏳ Получаю данные...")
        try:
            data = await fetch_weather(*coords)
            out = format_current(data, name)
            await msg.edit_text(out, parse_mode="Markdown")
        except Exception as e:
            await msg.edit_text(f"❌ Ошибка: {e}")
    else:
        await update.message.reply_text(
            f"Город «{text}» не найден.\n"
            "Попробуй: `/weather Москва` или просто напиши название города.",
            parse_mode="Markdown"
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("weather", cmd_weather))
    app.add_handler(CommandHandler("forecast", cmd_forecast))
    app.add_handler(CommandHandler("alerts", cmd_alerts))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    logger.info("Бот запущен")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
