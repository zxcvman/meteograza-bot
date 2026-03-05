import os, logging, httpx
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = os.getenv("BOT_TOKEN", "8742820412:AAHrQ59ppcc4YY85Bg7tOQAhSD7-Vh1cDiE")

CITIES = {
    "москва":(55.7558,37.6173,"ЦФО"),"воронеж":(51.6717,39.2106,"ЦФО"),
    "тула":(54.2043,37.6184,"ЦФО"),"рязань":(54.6269,39.6916,"ЦФО"),
    "тверь":(56.8589,35.9176,"ЦФО"),"владимир":(56.1291,40.4067,"ЦФО"),
    "иваново":(57.0005,40.9739,"ЦФО"),"ярославль":(57.6261,39.8845,"ЦФО"),
    "кострома":(57.7677,40.9268,"ЦФО"),"калуга":(54.5293,36.2754,"ЦФО"),
    "брянск":(53.2521,34.3717,"ЦФО"),"орел":(52.9651,36.0785,"ЦФО"),
    "курск":(51.7304,36.1921,"ЦФО"),"белгород":(50.5957,36.5879,"ЦФО"),
    "липецк":(52.6031,39.5708,"ЦФО"),"тамбов":(52.7212,41.4523,"ЦФО"),
    "смоленск":(54.7818,32.0401,"ЦФО"),"подольск":(55.4311,37.5444,"ЦФО"),
    "балашиха":(55.7960,37.9383,"ЦФО"),"химки":(55.8896,37.4297,"ЦФО"),
    "мытищи":(55.9116,37.7307,"ЦФО"),"люберцы":(55.6783,37.8938,"ЦФО"),
    "коломна":(55.0847,38.7764,"ЦФО"),"серпухов":(54.9167,37.4167,"ЦФО"),
    "электросталь":(55.7833,38.4500,"ЦФО"),"дмитров":(56.3447,37.5236,"ЦФО"),
    "орехово-зуево":(55.8074,38.9882,"ЦФО"),"зеленоград":(55.9878,37.1965,"ЦФО"),
    "санкт-петербург":(59.9311,30.3609,"СЗФО"),"архангельск":(64.5401,40.5433,"СЗФО"),
    "мурманск":(68.9792,33.0925,"СЗФО"),"петрозаводск":(61.7849,34.3469,"СЗФО"),
    "вологда":(59.2239,39.8978,"СЗФО"),"псков":(57.8136,28.3496,"СЗФО"),
    "великий новгород":(58.5213,31.2752,"СЗФО"),"сыктывкар":(61.6688,50.8364,"СЗФО"),
    "ухта":(63.5603,53.7155,"СЗФО"),"воркута":(67.4983,64.0339,"СЗФО"),
    "нарьян-мар":(67.6381,53.0069,"СЗФО"),"череповец":(59.1335,37.9077,"СЗФО"),
    "калининград":(54.7104,20.5103,"СЗФО"),"апатиты":(67.5678,33.4014,"СЗФО"),
    "северодвинск":(64.5669,39.8311,"СЗФО"),"мончегорск":(67.9380,32.9208,"СЗФО"),
    "ростов-на-дону":(47.2357,39.7015,"ЮФО"),"краснодар":(45.0448,38.9760,"ЮФО"),
    "волгоград":(48.7080,44.5133,"ЮФО"),"астрахань":(46.3497,48.0408,"ЮФО"),
    "сочи":(43.5855,39.7231,"ЮФО"),"новороссийск":(44.7239,37.7684,"ЮФО"),
    "таганрог":(47.2088,38.9357,"ЮФО"),"армавир":(44.9894,41.1220,"ЮФО"),
    "элиста":(46.3074,44.2680,"ЮФО"),"майкоп":(44.6098,40.1069,"ЮФО"),
    "симферополь":(44.9521,34.1024,"ЮФО"),"севастополь":(44.6166,33.5254,"ЮФО"),
    "керчь":(45.3572,36.4692,"ЮФО"),"анапа":(44.8953,37.3162,"ЮФО"),
    "геленджик":(44.5618,38.0773,"ЮФО"),"батайск":(47.1369,39.7561,"ЮФО"),
    "шахты":(47.7085,40.2150,"ЮФО"),"новочеркасск":(47.4182,40.0936,"ЮФО"),
    "волжский":(48.7892,44.7631,"ЮФО"),"камышин":(50.0944,45.3981,"ЮФО"),
    "ставрополь":(45.0440,41.9686,"СКФО"),"владикавказ":(43.0248,44.6811,"СКФО"),
    "махачкала":(42.9849,47.5047,"СКФО"),"грозный":(43.3178,45.6980,"СКФО"),
    "нальчик":(43.4846,43.6074,"СКФО"),"черкесск":(44.2291,42.0665,"СКФО"),
    "назрань":(43.2261,44.7669,"СКФО"),"пятигорск":(44.0490,43.0597,"СКФО"),
    "кисловодск":(43.9050,42.7183,"СКФО"),"ессентуки":(44.0459,42.8643,"СКФО"),
    "минеральные воды":(44.2088,43.1414,"СКФО"),"дербент":(42.0598,48.2896,"СКФО"),
    "хасавюрт":(43.2500,46.5833,"СКФО"),"буйнакск":(42.8167,47.1167,"СКФО"),
    "нижний новгород":(56.2965,43.9361,"ПФО"),"казань":(55.7887,49.1221,"ПФО"),
    "самара":(53.2028,50.1408,"ПФО"),"уфа":(54.7388,55.9721,"ПФО"),
    "пермь":(58.0105,56.2502,"ПФО"),"саратов":(51.5924,46.0335,"ПФО"),
    "тольятти":(53.5303,49.3461,"ПФО"),"ижевск":(56.8527,53.2048,"ПФО"),
    "ульяновск":(54.3282,48.3866,"ПФО"),"оренбург":(51.7879,55.1076,"ПФО"),
    "пенза":(53.2007,45.0046,"ПФО"),"киров":(58.6036,49.6680,"ПФО"),
    "чебоксары":(56.1439,47.2489,"ПФО"),"набережные челны":(55.7435,52.4066,"ПФО"),
    "нижнекамск":(55.6386,51.8279,"ПФО"),"альметьевск":(54.9024,52.2979,"ПФО"),
    "йошкар-ола":(56.6344,47.8677,"ПФО"),"саранск":(54.1838,45.1749,"ПФО"),
    "балаково":(51.9944,47.7791,"ПФО"),"энгельс":(51.5022,46.1222,"ПФО"),
    "стерлитамак":(53.6254,55.9477,"ПФО"),"октябрьский":(54.4833,53.4667,"ПФО"),
    "березники":(59.4091,56.8131,"ПФО"),"соликамск":(59.6447,56.7750,"ПФО"),
    "орск":(51.2354,58.6238,"ПФО"),"новотроицк":(51.2000,58.3167,"ПФО"),
    "димитровград":(54.2167,49.6333,"ПФО"),
    "екатеринбург":(56.8519,60.6122,"УФО"),"челябинск":(55.1644,61.4368,"УФО"),
    "тюмень":(57.1553,65.5880,"УФО"),"сургут":(61.2500,73.4167,"УФО"),
    "нефтеюганск":(61.1008,72.5994,"УФО"),"нижневартовск":(60.9384,76.5638,"УФО"),
    "ханты-мансийск":(61.0069,69.0102,"УФО"),"новый уренгой":(66.0846,76.6819,"УФО"),
    "ноябрьск":(63.2000,75.4500,"УФО"),"нижний тагил":(57.9100,59.9822,"УФО"),
    "магнитогорск":(53.4113,58.9937,"УФО"),"курган":(55.4507,65.3410,"УФО"),
    "первоуральск":(56.9044,59.9437,"УФО"),"каменск-уральский":(56.4143,61.9178,"УФО"),
    "серов":(59.6003,60.5800,"УФО"),"салехард":(66.5333,66.6167,"УФО"),
    "ишим":(56.1124,69.4892,"УФО"),"тобольск":(58.1975,68.2537,"УФО"),
    "шадринск":(56.0858,63.6336,"УФО"),"копейск":(55.1073,61.6182,"УФО"),
    "златоуст":(55.1723,59.6605,"УФО"),"миасс":(55.0507,60.1073,"УФО"),
    "новосибирск":(54.9885,82.9207,"СФО"),"омск":(54.9885,73.3242,"СФО"),
    "красноярск":(56.0184,92.8672,"СФО"),"барнаул":(53.3548,83.7697,"СФО"),
    "иркутск":(52.2855,104.2890,"СФО"),"кемерово":(55.3904,86.0479,"СФО"),
    "новокузнецк":(53.7557,87.1099,"СФО"),"томск":(56.4977,84.9744,"СФО"),
    "улан-удэ":(51.8272,107.6064,"СФО"),"чита":(52.0315,113.5010,"СФО"),
    "абакан":(53.7154,91.4293,"СФО"),"горно-алтайск":(51.9581,85.9603,"СФО"),
    "кызыл":(51.7191,94.4378,"СФО"),"норильск":(69.3558,88.1893,"СФО"),
    "братск":(56.1513,101.6340,"СФО"),"ангарск":(52.5378,103.8884,"СФО"),
    "бийск":(52.5406,85.1630,"СФО"),"рубцовск":(51.5000,81.2000,"СФО"),
    "прокопьевск":(53.8857,86.7218,"СФО"),"ленинск-кузнецкий":(54.6603,86.1716,"СФО"),
    "белово":(54.4228,86.3031,"СФО"),"северск":(56.6028,84.8869,"СФО"),
    "ачинск":(56.2694,90.4997,"СФО"),"канск":(56.2044,95.7072,"СФО"),
    "минусинск":(53.7099,91.6918,"СФО"),"черемхово":(53.1458,103.0700,"СФО"),
    "усолье-сибирское":(52.7559,103.6442,"СФО"),"шелехов":(52.2122,104.1008,"СФО"),
    "хабаровск":(48.4827,135.0840,"ДФО"),"владивосток":(43.1332,131.9113,"ДФО"),
    "якутск":(62.0280,129.7325,"ДФО"),"благовещенск":(50.2897,127.5270,"ДФО"),
    "южно-сахалинск":(46.9591,142.7381,"ДФО"),"петропавловск-камчатский":(53.0452,158.6536,"ДФО"),
    "магадан":(59.5681,150.8083,"ДФО"),"комсомольск-на-амуре":(50.5500,137.0000,"ДФО"),
    "биробиджан":(48.7949,132.9212,"ДФО"),"находка":(42.8217,132.8730,"ДФО"),
    "уссурийск":(43.7985,131.9474,"ДФО"),"анадырь":(64.7348,177.4993,"ДФО"),
    "нерюнгри":(56.6599,124.7150,"ДФО"),"мирный":(62.5358,113.9588,"ДФО"),
    "тында":(55.1552,124.7216,"ДФО"),"свободный":(51.3648,128.1292,"ДФО"),
    "белогорск":(50.9167,128.4667,"ДФО"),"арсеньев":(44.1639,133.2719,"ДФО"),
    "холмск":(47.0451,142.0325,"ДФО"),"корсаков":(46.6378,142.7842,"ДФО"),
    "елизово":(53.1858,158.3806,"ДФО"),"верхоянск":(67.5500,133.3833,"ДФО"),
    "оймякон":(63.4611,142.7736,"ДФО"),
}

ALIASES = {
    "мск":"москва","питер":"санкт-петербург","спб":"санкт-петербург",
    "нск":"новосибирск","екб":"екатеринбург","нн":"нижний новгород",
    "рнд":"ростов-на-дону","крд":"краснодар","влд":"владивосток",
    "хбр":"хабаровск","пкк":"петропавловск-камчатский","нур":"новый уренгой",
    "мурм":"мурманск","кзн":"казань","смр":"самара","чел":"челябинск",
}

WMO = {
    0:"☀️ Ясно",1:"🌤 Преим. ясно",2:"⛅ Перем. облачность",3:"☁️ Пасмурно",
    45:"🌫 Туман",48:"🌫 Гололёдный туман",51:"🌦 Морось слабая",53:"🌦 Морось",
    55:"🌧 Морось сильная",56:"🌨 Ледяная морось",57:"🌨 Ледяная морось сильная",
    61:"🌧 Дождь слабый",63:"🌧 Дождь",65:"🌧 Дождь сильный",
    66:"🌨 Ледяной дождь",67:"🌨 Ледяной дождь сильный",
    71:"❄️ Снег слабый",73:"❄️ Снег",75:"❄️ Снег сильный",77:"🌨 Снежная крупа",
    80:"🌦 Ливень слабый",81:"🌦 Ливень",82:"⛈ Ливень сильный",
    85:"🌨 Снегопад",86:"🌨 Снегопад сильный",
    95:"⛈ Гроза",96:"⛈ Гроза с градом",99:"⛈ Гроза с крупным градом",
}
DIRS = ["С","СВ","В","ЮВ","Ю","ЮЗ","З","СЗ"]

def wmo(c): return WMO.get(c,f"Код {c}")
def wdir(d): return DIRS[round(d/45)%8]

def find_city(q):
    q = q.lower().strip()
    q = ALIASES.get(q, q)
    if q in CITIES: return q.title(), CITIES[q]
    for k,v in CITIES.items():
        if k.startswith(q): return k.title(), v
    for k,v in CITIES.items():
        if q in k: return k.title(), v
    return None, None

def cape_label(c):
    if c<300: return "стабильно"
    if c<1000: return "слабая нестабильность"
    if c<2500: return "умеренная нестабильность"
    if c<4000: return "⚠️ высокая нестабильность"
    return "🔴 экстремальная нестабильность"

def li_label(li):
    if li is None: return ""
    if li>=0: return "стабильно"
    if li>=-2: return "слабо неустойчиво"
    if li>=-4: return "неустойчиво"
    if li>=-6: return "⚠️ сильно неустойчиво"
    return "🔴 экстрем. нестабильность"

def gust_label(g):
    if g<40: return "слабый"
    if g<60: return "умеренный"
    if g<80: return "сильный"
    if g<100: return "💨 шквал"
    return "🔴 ураганный"

def uv_label(u):
    if u<3: return "низкий"
    if u<6: return "умеренный"
    if u<8: return "⚠️ высокий"
    if u<11: return "⚠️ очень высокий"
    return "🔴 экстремальный"

def comfort(t,rh):
    td = t-(100-rh)/5
    ti = 0.4*(t+td)+4.8
    if ti<15: return "🥶 Прохладно"
    if ti<21: return "😊 Комфортно"
    if ti<27: return "😅 Тепло"
    return "🥵 Жарко и душно"

def wind_chill(t,ws):
    if t>10 or ws<5: return None
    return round(13.12+0.6215*t-11.37*(ws**0.16)+0.3965*t*(ws**0.16),1)

def heat_index(t,rh):
    if t<27: return None
    hi=-8.78469475556+1.61139411*t+2.3385248*rh-0.14611605*t*rh\
       -0.01230809*t**2-0.01642482*rh**2+0.00221173*t**2*rh\
       +0.00072546*t*rh**2-0.00000358*t**2*rh**2
    return round(hi,1)

async def fetch(lat,lon):
    url=(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
         f"&current=temperature_2m,apparent_temperature,relative_humidity_2m,"
         f"weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m,"
         f"pressure_msl,precipitation,cloud_cover,visibility,uv_index,"
         f"dew_point_2m,snow_depth,wet_bulb_temperature_2m,cape"
         f"&hourly=temperature_2m,weather_code,wind_speed_10m,wind_gusts_10m,"
         f"precipitation_probability,cape,lifted_index,wind_speed_80m,"
         f"cloud_cover,freezing_level_height,precipitation,snowfall,"
         f"relative_humidity_2m,visibility,uv_index"
         f"&daily=weather_code,temperature_2m_max,temperature_2m_min,"
         f"precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max,"
         f"sunrise,sunset,uv_index_max,snowfall_sum,precipitation_sum"
         f"&timezone=auto&forecast_days=7")
    async with httpx.AsyncClient(timeout=20) as c:
        r=await c.get(url)
        return r.json()

def fmt_current(data,city):
    cur=data["current"]
    daily=data.get("daily",{})
    t=cur["temperature_2m"]; at=cur["apparent_temperature"]
    rh=cur["relative_humidity_2m"]; code=cur["weather_code"]
    ws=cur["wind_speed_10m"]; wd=cur["wind_direction_10m"]
    wg=cur.get("wind_gusts_10m") or 0; pres=cur["pressure_msl"]
    prec=cur.get("precipitation") or 0; cloud=cur.get("cloud_cover") or 0
    vis=cur.get("visibility") or 0; uv=cur.get("uv_index") or 0
    dp=cur.get("dew_point_2m"); snow=cur.get("snow_depth") or 0
    wb=cur.get("wet_bulb_temperature_2m"); cape=cur.get("cape") or 0
    mmhg=round(pres*0.750064)
    vis_s=f"{vis/1000:.0f} км" if vis>=1000 else f"{vis:.0f} м"
    wc=wind_chill(t,ws); hi=heat_index(t,rh)
    now=datetime.now().strftime("%d.%m.%Y %H:%M")
    lines=[
        f"🌍 *{city}*  |  {now}","",
        f"{wmo(code)}",
        f"🌡 *{t:+.1f}°C*  (ощущ. {at:+.1f}°C)  {comfort(t,rh)}","",
        f"💧 *Влага и давление*",
        f"   Влажность: {rh}%" + (f"  |  Точка росы: {dp:+.1f}°C" if dp else ""),
        f"   Давление: {round(pres)} гПа  /  {mmhg} мм рт.ст.",
    ]
    if wb: lines.append(f"   Влажный термометр: {wb:+.1f}°C")
    if prec>0: lines.append(f"   Осадки: {prec:.1f} мм")
    if snow>0: lines.append(f"   ❄️ Снежный покров: {snow:.0f} см")
    lines+=[
        "","💨 *Ветер*",
        f"   {wdir(wd)} ({round(wd)}°)  |  {ws:.0f} км/ч",
        f"   Порывы: {wg:.0f} км/ч  — {gust_label(wg)}",
    ]
    if wc: lines.append(f"   Охлаждение ветром: {wc:+.1f}°C")
    if hi: lines.append(f"   Индекс жары: {hi:+.1f}°C")
    lines+=[
        "","☁️ *Атмосфера*",
        f"   Облачность: {cloud}%  |  Видимость: {vis_s}",
        f"   UV: {uv:.0f} — {uv_label(uv)}",
    ]
    if daily.get("sunrise"):
        try:
            sr=datetime.fromisoformat(daily["sunrise"][0]).strftime("%H:%M")
            ss=datetime.fromisoformat(daily["sunset"][0]).strftime("%H:%M")
            lines.append(f"   🌅 {sr}  |  🌇 {ss}")
        except: pass
    if cape>200:
        lines+=["","⚡ *Нестабильность*",f"   CAPE: {cape:.0f} Дж/кг — {cape_label(cape)}"]
    if daily.get("temperature_2m_max"):
        mx=daily["temperature_2m_max"][0]; mn=daily["temperature_2m_min"][0]
        pp=(daily.get("precipitation_probability_max") or [0])[0] or 0
        lines+=["",f"📈 Сегодня: {mn:+.0f}°C ... {mx:+.0f}°C"+(f"  💧{pp:.0f}%" if pp>10 else "")]
    return "\n".join(lines)

def fmt_forecast(data,city):
    d=data["daily"]; n=len(d["time"])
    lines=[f"📅 *Прогноз 7 дней — {city}*",""]
    for i in range(min(7,n)):
        dt=datetime.strptime(d["time"][i],"%Y-%m-%d")
        day=["Сегодня","Завтра"][i] if i<2 else dt.strftime("%a %d.%m").capitalize()
        code=d["weather_code"][i]; mx=d["temperature_2m_max"][i]; mn=d["temperature_2m_min"][i]
        pp=(d.get("precipitation_probability_max") or [0]*7)[i] or 0
        wmax=(d.get("wind_speed_10m_max") or [0]*7)[i] or 0
        gmax=(d.get("wind_gusts_10m_max") or [0]*7)[i] or 0
        snow=(d.get("snowfall_sum") or [0]*7)[i] or 0
        psum=(d.get("precipitation_sum") or [0]*7)[i] or 0
        uv=(d.get("uv_index_max") or [0]*7)[i] or 0
        line=f"*{day}*  {wmo(code)}\n  🌡 {mn:+.0f}...{mx:+.0f}°C"
        ex=[]
        if pp>15: ex.append(f"💧{pp:.0f}%")
        if psum>0.5: ex.append(f"{psum:.1f}мм")
        if snow>0.5: ex.append(f"❄️{snow:.1f}мм")
        if wmax>30: ex.append(f"💨{wmax:.0f}км/ч")
        if gmax>60: ex.append(f"⚠️пор.{gmax:.0f}")
        if uv>5: ex.append(f"☀️UV{uv:.0f}")
        if ex: line+="  |  "+"  ".join(ex)
        lines.append(line)
    return "\n".join(lines)

def fmt_alerts(data,city):
    h=data["hourly"]; n=len(h["time"]); now=datetime.now()
    si=0
    for i,t in enumerate(h["time"]):
        try:
            if datetime.fromisoformat(t)>=now: si=i; break
        except: pass
    events=[]; seen=set()
    for off in range(min(168,n-si)):
        hi=si+off
        if hi>=n: break
        code=(h.get("weather_code") or [])[hi] or 0
        gust=(h.get("wind_gusts_10m") or [])[hi] or 0
        cape=(h.get("cape") or [])[hi] or 0
        ws=(h.get("wind_speed_10m") or [])[hi] or 0
        ws80=(h.get("wind_speed_80m") or [])[hi] or 0
        li=(h.get("lifted_index") or [])[hi]
        pp=(h.get("precipitation_probability") or [])[hi] or 0
        shear=abs((ws80 or ws)-ws)
        try: dt=datetime.fromisoformat(h["time"][hi])
        except: continue
        lbl=("сегодня " if off<24 else "завтра " if off<48 else dt.strftime("%d.%m "))+dt.strftime("%H:%M")
        def add(icon,name,desc):
            k=name+dt.strftime("%Y%m%d")
            if k not in seen:
                seen.add(k)
                events.append((icon,name,desc,lbl))
        if code>=95: add("⛈","Гроза"+(" с градом" if code>=96 else ""),f"WMO {code}"+(f", CAPE {cape:.0f}" if cape else ""))
        if gust>=100: add("🌀","Ураганный ветер",f"Порывы {gust:.0f} км/ч")
        elif gust>=80: add("💨","Шквал",f"Порывы {gust:.0f} км/ч")
        elif gust>=60 and code<95: add("💨","Шквалистый ветер",f"Порывы {gust:.0f} км/ч")
        if cape>=1500 and shear>=20 and gust>=50:
            add("🌀","Шкваловый ворот",f"CAPE {cape:.0f}, сдвиг {shear:.0f} км/ч")
        if cape>=2000 and shear>=25 and li is not None and li<-4:
            add("🌪","Суперячейка"+(" (мезоциклон)" if cape>=3000 else ""),f"CAPE {cape:.0f}, LI {li:.1f}")
        if cape>=2500 and shear>=35 and li is not None and li<-6:
            add("🌪","⚠️ Условия для смерча",f"CAPE {cape:.0f}, LI {li:.1f}")
        if gust>=90: add("🌀","Ураган/Шторм",f"Порывы {gust:.0f} км/ч")
        if code in(75,77,86) and pp>=40: add("❄️","Сильный снегопад",f"WMO {code}, {pp}%")
        if code in(65,82) and pp>=40: add("🌧","Сильный ливень",f"WMO {code}, {pp}%")
        if code in(45,48) and off<48: add("🌫️","Туман"+(" замерзающий" if code==48 else ""),"Ограниченная видимость")
        if code in(66,67): add("🧊","Ледяной дождь",f"WMO {code}, риск гололёда")
    lines=[f"⚠️ *Опасные явления — {city}*",""]
    if not events:
        lines.append("✅ Опасных явлений на 7 дней не прогнозируется")
    else:
        lines.append(f"_Найдено: {len(events)} событий_\n")
        for icon,name,desc,lbl in events[:12]:
            lines.append(f"{icon} *{name}*\n   🕒 {lbl}\n   _{desc}_\n")
        if len(events)>12: lines.append(f"_...и ещё {len(events)-12} событий_")
    return "\n".join(lines)

def fmt_atmo(data,city):
    h=data["hourly"]; now=datetime.now(); si=0
    for i,t in enumerate(h["time"]):
        try:
            if datetime.fromisoformat(t)>=now: si=i; break
        except: pass
    cape=(h.get("cape") or [])[si] or 0
    li=(h.get("lifted_index") or [])[si]
    ws=(h.get("wind_speed_10m") or [])[si] or 0
    ws80=(h.get("wind_speed_80m") or [])[si] or 0
    frz=(h.get("freezing_level_height") or [])[si]
    shear=abs((ws80 or ws)-ws)
    cloud=(h.get("cloud_cover") or [])[si] or 0
    vis=(h.get("visibility") or [])[si] or 0
    lines=[
        f"🔬 *Атмосфера — {city}*","",
        f"⚡ *Нестабильность*",
        f"   CAPE: *{cape:.0f} Дж/кг* — {cape_label(cape)}",
    ]
    if li is not None: lines.append(f"   Lifted Index: *{li:.1f}°C* — {li_label(li)}")
    lines+=[
        "","💨 *Профиль ветра*",
        f"   На 10м: {ws:.0f} км/ч",
        f"   На 80м: {ws80:.0f} км/ч",
        f"   Сдвиг 10→80м: {shear:.0f} км/ч",
    ]
    if frz: lines.append(f"   Нулевая изотерма: {frz:.0f} м")
    lines+=[
        "","☁️ *Облачность и видимость*",
        f"   Облачность: {cloud}%",
        f"   Видимость: {vis/1000:.1f} км" if vis>=1000 else f"   Видимость: {vis:.0f} м",
    ]
    warns=[]
    if cape>=1500 or (li is not None and li<-4): warns.append("Повышенный риск конвекции")
    if shear>=20 and cape>=1000: warns.append("Организованные грозы возможны")
    if cape>=2500 and li is not None and li<-5: warns.append("⚠️ Условия для суперячеек")
    if warns: lines+=["","⚠️ *Внимание:*"]+[f"   • {w}" for w in warns]
    return "\n".join(lines)

def main_kb():
    return ReplyKeyboardMarkup([
        ["🌤 Погода","📅 Прогноз 7 дней"],
        ["⚠️ Опасные явления","🔬 Атмосфера"],
        ["📍 Геолокация","🏙 Города"],
    ],resize_keyboard=True)

def cities_kb():
    return ReplyKeyboardMarkup([
        ["Москва","Санкт-Петербург"],
        ["Новосибирск","Екатеринбург"],
        ["Казань","Нижний Новгород"],
        ["Краснодар","Ростов-на-Дону"],
        ["Владивосток","Хабаровск"],
        ["Сочи","Мурманск"],
        ["Норильск","Якутск"],
        ["Оймякон","Воркута"],
        ["⬅️ Назад",""],
    ],resize_keyboard=True)

user_state={}

async def do_city(update,mode,q):
    name,info=find_city(q)
    if not info:
        await update.message.reply_text(
            f"❌ Город «{q}» не найден.\n"
            f"Попробуй: Москва, Питер, Екб, Казань, Сочи, Владивосток...")
        return
    msg=await update.message.reply_text("⏳ Получаю данные...")
    try:
        data=await fetch(info[0],info[1])
        if mode=="weather": text=fmt_current(data,name)
        elif mode=="forecast": text=fmt_forecast(data,name)
        elif mode=="alerts": text=fmt_alerts(data,name)
        elif mode=="atmo": text=fmt_atmo(data,name)
        else: text=fmt_current(data,name)
        await msg.edit_text(text,parse_mode="Markdown")
    except Exception as e:
        logger.error(e)
        await msg.edit_text(f"❌ Ошибка: {e}")

async def cmd_start(u:Update,ctx:ContextTypes.DEFAULT_TYPE):
    n=u.effective_user.first_name or "друг"
    await u.message.reply_text(
        f"👋 Привет, *{n}*!\n\n"
        f"🌩 *МетеоГроза* — погода по всей России\n\n"
        f"*Что умею:*\n"
        f"🌤 Подробная текущая погода\n"
        f"📅 Прогноз на 7 дней\n"
        f"⚠️ Опасные явления: гроза, шквал, смерч,\n"
        f"   суперячейка, снегопад, ледяной дождь\n"
        f"🔬 Атмосфера: CAPE, Lifted Index, сдвиг ветра\n"
        f"📍 Погода по геолокации\n\n"
        f"*Как пользоваться:*\n"
        f"Просто напиши название города 👇\n"
        f"Например: *Москва* или *Сочи* или *Оймякон*\n\n"
        f"Доступно *{len(CITIES)}+ городов* России",
        parse_mode="Markdown",reply_markup=main_kb())

async def cmd_weather(u,ctx):
    uid=u.effective_user.id
    if not ctx.args: user_state[uid]={"mode":"weather"}; await u.message.reply_text("🌤 Напиши город:"); return
    await do_city(u,"weather"," ".join(ctx.args))

async def cmd_forecast(u,ctx):
    uid=u.effective_user.id
    if not ctx.args: user_state[uid]={"mode":"forecast"}; await u.message.reply_text("📅 Напиши город:"); return
    await do_city(u,"forecast"," ".join(ctx.args))

async def cmd_alerts(u,ctx):
    uid=u.effective_user.id
    if not ctx.args: user_state[uid]={"mode":"alerts"}; await u.message.reply_text("⚠️ Напиши город:"); return
    await do_city(u,"alerts"," ".join(ctx.args))

async def cmd_atmo(u,ctx):
    uid=u.effective_user.id
    if not ctx.args: user_state[uid]={"mode":"atmo"}; await u.message.reply_text("🔬 Напиши город:"); return
    await do_city(u,"atmo"," ".join(ctx.args))

async def handle_location(u:Update,ctx):
    loc=u.message.location
    msg=await u.message.reply_text("⏳ Определяю по геолокации...")
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r=await c.get("https://nominatim.openstreetmap.org/reverse",
                params={"lat":loc.latitude,"lon":loc.longitude,"format":"json","accept-language":"ru"},
                headers={"User-Agent":"MeteoGrozaBot/1.0"})
            geo=r.json()
        addr=geo.get("address",{})
        cn=addr.get("city") or addr.get("town") or addr.get("village") or "Ваша точка"
        data=await fetch(loc.latitude,loc.longitude)
        await msg.edit_text(fmt_current(data,cn),parse_mode="Markdown")
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")

async def handle_text(u:Update,ctx):
    text=u.message.text.strip(); uid=u.effective_user.id
    if text=="🏙 Города":
        await u.message.reply_text("Выбери город:",reply_markup=cities_kb()); return
    if text=="⬅️ Назад":
        await u.message.reply_text("Главное меню:",reply_markup=main_kb()); return
    if text=="📍 Геолокация":
        kb=ReplyKeyboardMarkup([[KeyboardButton("📍 Отправить",request_location=True)],["⬅️ Назад"]],resize_keyboard=True)
        await u.message.reply_text("Нажми кнопку:",reply_markup=kb); return
    modes={"🌤 Погода":"weather","📅 Прогноз 7 дней":"forecast","⚠️ Опасные явления":"alerts","🔬 Атмосфера":"atmo"}
    if text in modes:
        user_state[uid]={"mode":modes[text]}
        await u.message.reply_text("Напиши название города:"); return
    mode=user_state.pop(uid,{}).get("mode","weather")
    await do_city(u,mode,text)

def main():
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",cmd_start))
    app.add_handler(CommandHandler("help",lambda u,c: u.message.reply_text(
        "Команды:\n/weather Город\n/forecast Город\n/alerts Город\n/atmo Город\n\nИли просто напиши город",parse_mode="Markdown")))
    app.add_handler(CommandHandler("weather",cmd_weather))
    app.add_handler(CommandHandler("forecast",cmd_forecast))
    app.add_handler(CommandHandler("alerts",cmd_alerts))
    app.add_handler(CommandHandler("atmo",cmd_atmo))
    app.add_handler(MessageHandler(filters.LOCATION,handle_location))
    app.add_handler(MessageHandler(filters.TEXT&~filters.COMMAND,handle_text))
    logger.info("✅ МетеоГроза бот запущен — %d городов",len(CITIES))
    app.run_polling(drop_pending_updates=True)

if __name__=="__main__":
    main()
