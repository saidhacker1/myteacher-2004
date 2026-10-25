#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BM OS 2004 V1 - AI va ovoz orqali boshqariladigan veb-muhit (bitta fayl, faqat standart kutubxona).

Ishga tushirish:  python3 2004.py        ->  http://127.0.0.1:2004
Tekshirish:       python3 2004.py --self-test
"""
import argparse, collections, hmac, http.client, http.server, json, os, re, secrets, socket
import sys, tempfile, threading, time, urllib.request, webbrowser
from datetime import datetime

PORT, HOST, VERSION, MAX_BODY = 2004, "127.0.0.1", "1.0", 65536
DATA_DIR = os.environ.get("BMOS_HOME") or os.path.join(os.path.expanduser("~"), ".bm_os_2004")
MODEL = os.environ.get("BMOS_MODEL", "gemini-2.5-flash")
GEMINI = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent"
LANGS = ("uz", "en", "ru")
DEFAULTS = {"lang": "uz", "mode": "voice", "sound": True, "volume": 80, "font": 2,
            "contrast": False, "demo": True, "onboarded": False}

# ---------------------------------------------------------------- tarjimalar
T = {
"uz": dict(title="BM OS 2004", wel="Xush kelibsiz! Men ovoz va matn orqali boshqariladigan AI yordamchingizman. Keling, sozlab olamiz.",
 lang="Til", mode="Boshqaruv rejimi", voice="Ovozli", text="Matnli", audio="Ovoz va mikrofon", mic_t="Mikrofonni tekshirish",
 spk_t="Ovozni tekshirish", sound="Ovozli javob", volume="Ovoz balandligi", ok_mic="Mikrofon ishlayapti.",
 no_mic="Mikrofon yoki nutqni aniqlash mavjud emas. Matnli rejimda davom eting.", ok_tts="Ovoz tekshiruvi: eshitilyaptimi?",
 no_tts="Brauzer ovoz chiqarishni qoʻllamaydi. Javoblar matn koʻrinishida.", api="AI kaliti (ixtiyoriy)",
 api_h="Gemini API kaliti faqat shu qurilmada saqlanadi. Kalitsiz mahalliy demo rejimi toʻliq ishlaydi.", save="Saqlash",
 delete="Kalitni oʻchirish", demo="Faqat mahalliy demo", saved="Saqlandi.", bad_key="Kalit formati notoʻgʻri.", acc="Qulaylik",
 big="Shrift +", small="Shrift −", contrast="Yuqori kontrast", finish="Yakunlash", next="Keyingi", back="Orqaga",
 ph="Buyruq yozing…", send="Yuborish", listen="Tinglash", stop_l="Tinglashni toʻxtatish", listening="Tinglayapman…", idle="Tayyor",
 repeat="Takrorlash", mute="Ovozni toʻxtatish", settings="Sozlamalar", help="Yordam", close="Yopish",
 hello="Salom! Men BM OS yordamchisiman. Sizga qanday yordam beray?", time="Soat {t}.", date="Bugun {d}.",
 net_ok="Internet mavjud.", net_no="Internet yoʻq.", unk="Buyruqni tushunmadim. «Buyruqlar roʻyxati» deb ayting.",
 helptxt="Men soat, sana, sozlamalar, ovoz, shrift, mikrofon va internet holati bilan yordam beraman. «Buyruqlar roʻyxati» deng.",
 cmds="Buyruqlar: Salom; Yordam ber; Soat nechchi; Bugungi sana; Sozlamalarni och; Ovozni yoq yoki oʻchir; Ovoz balandligini oshir yoki kamaytir; Shriftni kattalashtir yoki kichraytir; Mikrofon holatini tekshir; Internet holatini tekshir; Ekrandagi matnni oʻqib ber; Oxirgi javobni takrorla; Dasturdan chiq.",
 vol="Ovoz balandligi {v}%.", dir_q="Oshiraymi yoki kamaytiraymi?", snd_on="Ovoz yoqildi.", snd_off="Ovoz oʻchirildi.",
 font="Shrift oʻlchami: {v}/5.", con_on="Yuqori kontrast yoqildi.", con_off="Yuqori kontrast oʻchirildi.", read="Ekrandagi matn: {t}",
 none="Takrorlash uchun javob yoʻq.", exit_q="Dasturdan chiqishni tasdiqlaysizmi?", bye="BM OS yopildi. Oynani yopishingiz mumkin.",
 err="Xatolik", ai_err="AI xizmati hozir javob bermadi. Mahalliy buyruqlar ishlaydi.", rate="Juda koʻp soʻrov. Biroz kuting.",
 deny="Mikrofonga ruxsat berilmadi.", empty="Matn yoʻq.", you="Siz", ai="BM OS", mode_demo="Demo rejim", mode_ai="AI rejim"),
"en": dict(title="BM OS 2004", wel="Welcome! I am your AI assistant controlled by voice or text. Let's set things up.",
 lang="Language", mode="Control mode", voice="Voice", text="Text", audio="Audio and microphone", mic_t="Test microphone",
 spk_t="Test sound", sound="Spoken replies", volume="Volume", ok_mic="The microphone works.",
 no_mic="Microphone or speech recognition is unavailable. Please continue in text mode.", ok_tts="Sound test: can you hear this?",
 no_tts="This browser cannot speak. Replies stay as text.", api="AI key (optional)",
 api_h="The Gemini API key is stored only on this device. Without a key, the local demo mode works fully.", save="Save",
 delete="Delete key", demo="Local demo only", saved="Saved.", bad_key="Invalid key format.", acc="Accessibility",
 big="Font +", small="Font −", contrast="High contrast", finish="Finish", next="Next", back="Back",
 ph="Type a command…", send="Send", listen="Listen", stop_l="Stop listening", listening="Listening…", idle="Ready",
 repeat="Repeat", mute="Stop speech", settings="Settings", help="Help", close="Close",
 hello="Hello! I am the BM OS assistant. How can I help?", time="It is {t}.", date="Today is {d}.",
 net_ok="Internet is available.", net_no="No internet.", unk="I did not understand. Say “list of commands”.",
 helptxt="I can help with time, date, settings, sound, font size, microphone and internet status. Say “list of commands”.",
 cmds="Commands: Hello; Help; What time is it; Today's date; Open settings; Sound on or off; Volume up or down; Font bigger or smaller; Check microphone; Check internet; Read the screen; Repeat last answer; Exit program.",
 vol="Volume {v}%.", dir_q="Increase or decrease?", snd_on="Sound is on.", snd_off="Sound is off.",
 font="Font size: {v}/5.", con_on="High contrast is on.", con_off="High contrast is off.", read="Screen text: {t}",
 none="No answer to repeat.", exit_q="Do you confirm exiting the program?", bye="BM OS closed. You can close this window.",
 err="Error", ai_err="The AI service did not respond. Local commands still work.", rate="Too many requests. Please wait.",
 deny="Microphone permission was denied.", empty="No text.", you="You", ai="BM OS", mode_demo="Demo mode", mode_ai="AI mode"),
"ru": dict(title="BM OS 2004", wel="Добро пожаловать! Я ИИ-помощник с голосовым и текстовым управлением. Давайте всё настроим.",
 lang="Язык", mode="Режим управления", voice="Голосовой", text="Текстовый", audio="Звук и микрофон", mic_t="Проверить микрофон",
 spk_t="Проверить звук", sound="Голосовые ответы", volume="Громкость", ok_mic="Микрофон работает.",
 no_mic="Микрофон или распознавание речи недоступны. Продолжайте в текстовом режиме.", ok_tts="Проверка звука: слышно?",
 no_tts="Браузер не умеет озвучивать. Ответы будут текстом.", api="Ключ ИИ (необязательно)",
 api_h="Ключ Gemini API хранится только на этом устройстве. Без ключа локальный демо-режим работает полностью.", save="Сохранить",
 delete="Удалить ключ", demo="Только локальное демо", saved="Сохранено.", bad_key="Неверный формат ключа.", acc="Доступность",
 big="Шрифт +", small="Шрифт −", contrast="Высокий контраст", finish="Завершить", next="Далее", back="Назад",
 ph="Введите команду…", send="Отправить", listen="Слушать", stop_l="Остановить прослушивание", listening="Слушаю…", idle="Готово",
 repeat="Повторить", mute="Остановить речь", settings="Настройки", help="Помощь", close="Закрыть",
 hello="Здравствуйте! Я помощник BM OS. Чем помочь?", time="Сейчас {t}.", date="Сегодня {d}.",
 net_ok="Интернет доступен.", net_no="Интернета нет.", unk="Я не понял. Скажите «список команд».",
 helptxt="Я помогаю со временем, датой, настройками, звуком, шрифтом, микрофоном и интернетом. Скажите «список команд».",
 cmds="Команды: Привет; Помоги; Который час; Какая сегодня дата; Открой настройки; Включи или выключи звук; Громкость больше или меньше; Шрифт больше или меньше; Проверь микрофон; Проверь интернет; Прочитай экран; Повтори последний ответ; Выход.",
 vol="Громкость {v}%.", dir_q="Увеличить или уменьшить?", snd_on="Звук включён.", snd_off="Звук выключен.",
 font="Размер шрифта: {v}/5.", con_on="Высокий контраст включён.", con_off="Высокий контраст выключен.", read="Текст на экране: {t}",
 none="Нет ответа для повтора.", exit_q="Подтвердите выход из программы?", bye="BM OS закрыт. Можно закрыть окно.",
 err="Ошибка", ai_err="ИИ-сервис не ответил. Локальные команды работают.", rate="Слишком много запросов. Подождите.",
 deny="Доступ к микрофону запрещён.", empty="Текста нет.", you="Вы", ai="BM OS", mode_demo="Демо-режим", mode_ai="Режим ИИ"),
}
MONTHS = {"uz": "yanvar fevral mart aprel may iyun iyul avgust sentabr oktyabr noyabr dekabr".split(),
          "ru": "января февраля марта апреля мая июня июля августа сентября октября ноября декабря".split()}

# ---------------------------------------------------------------- buyruqlarni aniqlash
def norm(t):
    t = t.lower()
    for c in "ʻʼ’‘`´":
        t = t.replace(c, "'")
    return re.sub(r"[^\w' ]+", " ", t).strip()

RULES = [(k, re.compile(p)) for k, p in [
 ("exit", r"dasturdan chiq|\bexit\b|\bquit\b|выход|выйти|закрой программ"),
 ("cmds", r"buyruqlar|commands|список команд|команды"),
 ("settings", r"sozlamalar|settings|настройк"),
 ("stop", r"to'xtat|\bstop\b|стоп|хватит"),
 ("mic", r"mikrofon|microphone|микрофон"),
 ("net", r"internet|интернет|tarmoq|network"),
 ("vol", r"balandlig|volume|громкост"),
 ("snd", r"\bovozni\b|\bsound\b|\bmute\b|\bunmute\b|звук"),
 ("font", r"shrift|\bfont\b|text size|шрифт"),
 ("contrast", r"kontrast|contrast|контраст"),
 ("read", r"ekrandagi|read (the )?screen|прочита[йи] (экран|текст)|o'qib ber"),
 ("repeat", r"takrorla|repeat|повтор"),
 ("time", r"soat nech|\bvaqt|what time|time is it|который час|сколько времени|current time"),
 ("date", r"\bsana|\bdate\b|какое сегодня|какое число|\btoday"),
 ("help", r"yordam|\bhelp\b|помо[гщ]"),
 ("greet", r"salom|assalom|hello|\bhi\b|привет|здравствуй")]]
UP = re.compile(r"oshir|ko'tar|katta|\bup\b|louder|increase|raise|bigger|larger|громче|прибав|увелич|больше")
DOWN = re.compile(r"kamayt|pasaytir|tushir|kichray|kichik|\bdown\b|quieter|lower|decrease|reduce|smaller|тише|убав|уменьш|меньше")
ON = re.compile(r"\byoq\b|yoqish|yoqing|\bon\b|unmute|включ|вкл")
OFF = re.compile(r"o'chir|\boff\b|\bmute\b|выключ|выкл|отключ")

def detect(text):
    n = norm(text)
    for name, rx in RULES:
        if rx.search(n):
            return name, n
    return None, n

def fmt_date(lang, d):
    if lang == "en":
        return d.strftime("%B %d, %Y")
    return "%d %s %d" % (d.day, MONTHS[lang][d.month - 1], d.year)

def internet_ok():
    for ip in ("1.1.1.1", "8.8.8.8"):
        try:
            socket.create_connection((ip, 53), timeout=3).close()
            return True
        except OSError:
            pass
    return False

# ---------------------------------------------------------------- ilova holati
class App:
    def __init__(self, data_dir=DATA_DIR, verbose=False):
        self.dir, self.verbose = data_dir, verbose
        self.token = secrets.token_urlsafe(32)
        self.lock = threading.Lock()
        self.hist, self.hits = [], collections.deque()
        os.makedirs(self.dir, mode=0o700, exist_ok=True)
        self.sfile, self.kfile = os.path.join(self.dir, "settings.json"), os.path.join(self.dir, "key.txt")
        self.s = self.load_settings()
        self.key = self.load_key()

    @staticmethod
    def clean(d, base):
        out = dict(base)
        if not isinstance(d, dict):
            return out
        if d.get("lang") in LANGS: out["lang"] = d["lang"]
        if d.get("mode") in ("voice", "text"): out["mode"] = d["mode"]
        for k in ("sound", "contrast", "demo", "onboarded"):
            if isinstance(d.get(k), bool): out[k] = d[k]
        for k, lo, hi in (("volume", 0, 100), ("font", 1, 5)):
            v = d.get(k)
            if isinstance(v, int) and not isinstance(v, bool): out[k] = max(lo, min(hi, v))
        return out

    def write(self, path, text):
        tmp = path + ".tmp"
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
        try: os.chmod(path, 0o600)
        except OSError: pass

    def load_settings(self):
        try:
            with open(self.sfile, encoding="utf-8") as f:
                return self.clean(json.load(f), DEFAULTS)
        except (OSError, ValueError):
            return dict(DEFAULTS)

    def load_key(self):
        try:
            with open(self.kfile, encoding="utf-8") as f:
                k = f.read().strip()
        except OSError:
            k = ""
        k = k or os.environ.get("GEMINI_API_KEY", "").strip()
        return k if re.fullmatch(r"[A-Za-z0-9_\-]{20,128}", k) else ""

    def update(self, patch):
        with self.lock:
            self.s = self.clean({**self.s, **(patch if isinstance(patch, dict) else {})}, self.s)
            self.write(self.sfile, json.dumps(self.s, ensure_ascii=False))
            return dict(self.s)

    def set_key(self, k):
        k = (k or "").strip()
        if k and not re.fullmatch(r"[A-Za-z0-9_\-]{20,128}", k):
            return False
        with self.lock:
            self.key = k
            if k: self.write(self.kfile, k)
            elif os.path.exists(self.kfile): os.remove(self.kfile)
        return True

    def state(self):
        return {**self.s, "has_key": bool(self.key), "ai": bool(self.key) and not self.s["demo"], "v": VERSION}

    def allow(self):
        now = time.time()
        with self.lock:
            while self.hits and now - self.hits[0] > 60: self.hits.popleft()
            if len(self.hits) >= 120: return False
            self.hits.append(now)
            return True

    def ask_ai(self, text, lang):
        sysmsg = {"uz": "Sen BM OS yordamchisisan, qoʻli bilan ishlay olmaydigan odamlarga yordam berasan. Oʻzbek tilida, qisqa va aniq javob ber.",
                  "en": "You are the BM OS assistant helping people who cannot use their hands. Reply briefly and clearly in English.",
                  "ru": "Ты помощник BM OS для людей, которые не могут пользоваться руками. Отвечай кратко и ясно по-русски."}[lang]
        contents = self.hist[-8:] + [{"role": "user", "parts": [{"text": text}]}]
        body = json.dumps({"system_instruction": {"parts": [{"text": sysmsg}]}, "contents": contents}).encode()
        req = urllib.request.Request(GEMINI % MODEL, body, {"Content-Type": "application/json", "x-goog-api-key": self.key}, method="POST")
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read(1000000))
        ans = d["candidates"][0]["content"]["parts"][0]["text"].strip()
        self.hist += [{"role": "user", "parts": [{"text": text}]}, {"role": "model", "parts": [{"text": ans}]}]
        self.hist = self.hist[-16:]
        return ans

    def command(self, text):
        lang = self.s["lang"]
        t = T[lang]
        text = (text or "").strip()[:500]
        reply, acts = None, []
        intent, n = detect(text) if text else (None, "")
        if intent == "greet": reply = t["hello"]
        elif intent == "help": reply = t["helptxt"]
        elif intent == "cmds": reply = t["cmds"]
        elif intent == "time": reply = t["time"].format(t=datetime.now().strftime("%H:%M"))
        elif intent == "date": reply = t["date"].format(d=fmt_date(lang, datetime.now()))
        elif intent == "net": reply = t["net_ok"] if internet_ok() else t["net_no"]
        elif intent == "settings": reply, acts = t["settings"], ["settings"]
        elif intent == "mic": reply, acts = t["mic_t"], ["mic"]
        elif intent == "read": reply, acts = t["read"].split(":")[0], ["read"]
        elif intent == "repeat": reply, acts = t["repeat"], ["repeat"]
        elif intent == "stop": reply, acts = t["mute"], ["stop"]
        elif intent == "exit": reply, acts = t["exit_q"], ["exit"]
        elif intent == "snd":
            on, off = bool(ON.search(n)), bool(OFF.search(n))
            v = (not self.s["sound"]) if on == off else on
            self.update({"sound": v})
            reply = t["snd_on"] if v else t["snd_off"]
        elif intent == "vol":
            m = re.search(r"\b(\d{1,3})\b", n)
            up, down = bool(UP.search(n)), bool(DOWN.search(n))
            if m: v = int(m.group(1))
            elif up != down: v = self.s["volume"] + (20 if up else -20)
            else: v = None
            if v is None: reply = t["dir_q"]
            else:
                self.update({"volume": max(0, min(100, v))})
                reply = t["vol"].format(v=self.s["volume"])
        elif intent == "font":
            up, down = bool(UP.search(n)), bool(DOWN.search(n))
            if up == down: reply = t["dir_q"]
            else:
                self.update({"font": self.s["font"] + (1 if up else -1)})
                reply = t["font"].format(v=self.s["font"])
        elif intent == "contrast":
            self.update({"contrast": not self.s["contrast"]})
            reply = t["con_on"] if self.s["contrast"] else t["con_off"]
        elif not text: reply = t["unk"]
        elif self.state()["ai"]:
            try: reply = self.ask_ai(text, lang)
            except Exception:  # kalit va tafsilotlar hech qachon chiqarilmaydi
                reply = t["ai_err"]
        else: reply = t["unk"]
        return {"reply": reply, "actions": acts, "state": self.state()}

# ---------------------------------------------------------------- veb-server
PAGE = r"""<!doctype html><html lang="uz"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BM OS 2004</title><style nonce="__N__">
:root{--bg:#0f1115;--fg:#eef1f6;--mut:#9aa4b5;--card:#181c24;--ac:#5aa9ff;--bd:#2b3240;--fs:20px}
body.hc{--bg:#000;--fg:#fff;--mut:#fff;--card:#000;--ac:#ffe600;--bd:#fff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:var(--fs)/1.5 system-ui,Segoe UI,Roboto,sans-serif}
#app{max-width:820px;margin:0 auto;padding:16px;display:flex;flex-direction:column;gap:14px;min-height:100vh}
header{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--bd);padding-bottom:8px}
h1{font-size:1.3em;margin:0}#badge{color:var(--mut);font-size:.8em}
#log{flex:1;min-height:40vh;max-height:60vh;overflow:auto;background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:12px}
.m{margin:0 0 10px;padding:8px 12px;border-radius:10px;border:1px solid var(--bd);white-space:pre-wrap;overflow-wrap:anywhere}
.u{background:transparent}.a{border-color:var(--ac)}.m b{display:block;font-size:.7em;color:var(--mut)}
#state{min-height:1.5em;color:var(--ac)}#state.on::before{content:"● ";animation:p 1s infinite}@keyframes p{50%{opacity:.2}}
.row{display:flex;gap:8px;flex-wrap:wrap}input[type=text],input[type=password],select{flex:1;min-width:0;font:inherit;padding:10px;border-radius:10px;border:2px solid var(--bd);background:var(--card);color:var(--fg)}
button{font:inherit;padding:10px 16px;border-radius:10px;border:2px solid var(--ac);background:var(--card);color:var(--fg);cursor:pointer}
button:hover{background:var(--ac);color:#000}:focus-visible{outline:4px solid var(--ac);outline-offset:2px}
fieldset{border:1px solid var(--bd);border-radius:12px;display:flex;flex-direction:column;gap:10px;padding:14px}legend{padding:0 8px;color:var(--ac)}
label{display:flex;gap:10px;align-items:center}input[type=range]{flex:1}[hidden]{display:none!important}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style></head><body><div id="app">
<header><h1 id="ttl">BM OS 2004</h1><span id="badge"></span></header>
<p id="wintro" data-t="wel" hidden></p>
<section id="main" class="col"><div id="log" role="log" aria-live="polite" tabindex="0"></div>
<div id="state" role="status" aria-live="assertive"></div>
<div class="row"><input id="inp" type="text" autocomplete="off" maxlength="500" data-p="ph"><button id="send" data-t="send"></button><button id="mic" data-t="listen"></button></div>
<div class="row"><button id="rep" data-t="repeat"></button><button id="stp" data-t="mute"></button><button id="set" data-t="settings"></button><button id="hlp" data-t="help"></button></div></section>
<section id="cfg" hidden>
<fieldset id="f0"><legend data-t="lang"></legend><select id="lang"><option value="uz">Oʻzbekcha</option><option value="en">English</option><option value="ru">Русский</option></select></fieldset>
<fieldset id="f1"><legend data-t="mode"></legend><select id="modeSel"><option value="voice" data-t="voice"></option><option value="text" data-t="text"></option></select></fieldset>
<fieldset id="f2"><legend data-t="audio"></legend><div class="row"><button id="tmic" data-t="mic_t"></button><button id="tspk" data-t="spk_t"></button></div>
<label><input type="checkbox" id="sndChk"><span data-t="sound"></span></label><label><span data-t="volume"></span><input type="range" id="volR" min="0" max="100" step="10"></label></fieldset>
<fieldset id="f3"><legend data-t="api"></legend><p data-t="api_h"></p><div class="row"><input type="password" id="key" autocomplete="off" spellcheck="false" maxlength="128"><button id="ksave" data-t="save"></button><button id="kdel" data-t="delete"></button></div>
<label><input type="checkbox" id="demoChk"><span data-t="demo"></span></label></fieldset>
<fieldset id="f4"><legend data-t="acc"></legend><div class="row"><button id="fbig" data-t="big"></button><button id="fsm" data-t="small"></button></div>
<label><input type="checkbox" id="conChk"><span data-t="contrast"></span></label></fieldset>
<div class="row"><button id="back" data-t="back"></button><button id="next"></button></div></section></div>
<script nonce="__N__">
(()=>{"use strict";
const TOKEN=__TOKEN__,I=__I18N__,LC={uz:"uz-UZ",en:"en-US",ru:"ru-RU"},$=i=>document.getElementById(i);
let S=null,T=null,last="",rec=null,listening=false,step=0,showCfg=false,greeted=false;
const SR=window.SpeechRecognition||window.webkitSpeechRecognition,TTS=window.speechSynthesis;
async function api(p,b){const r=await fetch(p,{method:b===undefined?"GET":"POST",headers:{"X-BM-Token":TOKEN,"Content-Type":"application/json"},body:b===undefined?undefined:JSON.stringify(b)});
 const j=await r.json().catch(()=>({}));if(!r.ok)throw new Error(j.error||("HTTP "+r.status));return j}
function apply(s){S=s;T=I[s.lang];document.documentElement.lang=s.lang;document.title=T.title;
 document.documentElement.style.setProperty("--fs",[16,20,24,30,36][s.font-1]+"px");document.body.classList.toggle("hc",s.contrast);
 document.querySelectorAll("[data-t]").forEach(e=>e.textContent=T[e.dataset.t]);
 document.querySelectorAll("[data-p]").forEach(e=>{e.placeholder=T[e.dataset.p];e.setAttribute("aria-label",T[e.dataset.p])});
 $("badge").textContent=s.ai?T.mode_ai:T.mode_demo;$("mic").textContent=listening?T.stop_l:T.listen;
 $("lang").value=s.lang;$("modeSel").value=s.mode;$("sndChk").checked=s.sound;$("volR").value=s.volume;$("demoChk").checked=s.demo;$("conChk").checked=s.contrast;
 $("mic").hidden=!SR;view()}
function view(){const w=!S.onboarded,c=w||showCfg;$("main").hidden=c;$("cfg").hidden=!c;$("wintro").hidden=!(w&&step===0);
 for(let i=0;i<5;i++)$("f"+i).hidden=w&&i!==step;$("back").hidden=!(w&&step>0);
 $("next").textContent=w?(step===4?T.finish:T.next):T.close;if(!c&&!greeted){greeted=true;say(T.hello)}}
function speak(t,force){if(!TTS||!(force||S.sound))return false;TTS.cancel();const u=new SpeechSynthesisUtterance(t);u.lang=LC[S.lang];u.volume=S.volume/100;TTS.speak(u);return true}
function add(who,t){const d=document.createElement("div");d.className="m "+(who===T.you?"u":"a");const b=document.createElement("b");b.textContent=who;d.append(b,document.createTextNode(t));$("log").append(d);$("log").scrollTop=1e9}
function say(t,force){last=t;add(T.ai,t);speak(t,force)}
function st(t,on){$("state").textContent=t;$("state").classList.toggle("on",!!on)}
async function save(p){try{apply((await api("/api/settings",p)).state)}catch(e){say(T.err+": "+e.message)}}
async function send(text){text=(text||"").trim();if(!text)return;add(T.you,text);$("inp").value="";
 try{const j=await api("/api/command",{text});apply(j.state);
  const a=j.actions||[];if(a.includes("read")){const x=$("log").innerText.trim();say(x?x.slice(-600):T.empty,true);return}
  if(a.includes("repeat")){last?say(last,true):add(T.ai,T.none);return}
  if(a.includes("stop")){stopAll();add(T.ai,j.reply);return}
  say(j.reply);
  if(a.includes("settings")){showCfg=true;view()}
  if(a.includes("mic"))checkMic();
  if(a.includes("exit")&&confirm(T.exit_q)){await api("/api/exit",{});stopAll();say(T.bye)}
 }catch(e){say(T.err+": "+e.message)}}
function stopAll(){if(TTS)TTS.cancel();if(rec)try{rec.stop()}catch(e){}}
async function checkMic(){if(!SR||!navigator.mediaDevices){say(T.no_mic);return}
 try{const s=await navigator.mediaDevices.getUserMedia({audio:true});s.getTracks().forEach(t=>t.stop());say(T.ok_mic)}catch(e){say(T.deny)}}
function toggleListen(){if(!SR){say(T.no_mic);return}
 if(listening){stopAll();return}
 rec=new SR();rec.lang=LC[S.lang];rec.interimResults=false;rec.maxAlternatives=1;
 rec.onstart=()=>{listening=true;$("mic").textContent=T.stop_l;st(T.listening,true)};
 rec.onend=()=>{listening=false;$("mic").textContent=T.listen;st(T.idle,false)};
 rec.onerror=e=>{st("",false);if(e.error==="not-allowed"||e.error==="service-not-allowed")say(T.deny);else if(e.error!=="no-speech"&&e.error!=="aborted")say(T.err+": "+e.error)};
 rec.onresult=e=>send(e.results[0][0].transcript);
 try{if(TTS)TTS.cancel();rec.start()}catch(e){say(T.err+": "+e.message)}}
$("send").onclick=()=>send($("inp").value);$("inp").onkeydown=e=>{if(e.key==="Enter")send($("inp").value)};
$("mic").onclick=toggleListen;$("rep").onclick=()=>send(T.repeat);$("stp").onclick=()=>{stopAll()};
$("set").onclick=()=>{showCfg=true;view()};$("hlp").onclick=()=>send(T.help);
$("lang").onchange=e=>save({lang:e.target.value});$("modeSel").onchange=e=>save({mode:e.target.value});
$("sndChk").onchange=e=>save({sound:e.target.checked});$("volR").onchange=e=>save({volume:+e.target.value});
$("demoChk").onchange=e=>save({demo:e.target.checked});$("conChk").onchange=e=>save({contrast:e.target.checked});
$("fbig").onclick=()=>save({font:Math.min(5,S.font+1)});$("fsm").onclick=()=>save({font:Math.max(1,S.font-1)});
$("tmic").onclick=checkMic;$("tspk").onclick=()=>{if(!speak(T.ok_tts,true))say(T.no_tts);else add(T.ai,T.ok_tts)};
$("ksave").onclick=async()=>{try{await api("/api/key",{key:$("key").value});$("key").value="";await save({demo:false});add(T.ai,T.saved)}catch(e){add(T.ai,T.bad_key)}};
$("kdel").onclick=async()=>{try{await api("/api/key",{key:""});await save({demo:true})}catch(e){}};
$("back").onclick=()=>{step=Math.max(0,step-1);view()};
$("next").onclick=()=>{if(!S.onboarded){if(step<4){step++;view()}else save({onboarded:true})}else{showCfg=false;view()}};
document.addEventListener("keydown",e=>{if(e.altKey&&e.key==="m"){e.preventDefault();toggleListen()}
 else if(e.altKey&&e.key==="r"){e.preventDefault();send(T.repeat)}else if(e.altKey&&e.key==="s"){e.preventDefault();stopAll()}
 else if(e.altKey&&e.key==="o"){e.preventDefault();showCfg=true;view()}
 else if(e.key==="Escape"){stopAll();if(S.onboarded&&showCfg){showCfg=false;view()}}});
api("/api/state").then(j=>apply(j.state)).catch(e=>{document.body.textContent="BM OS: "+e.message});
})();
</script></body></html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    server_version, sys_version = "BMOS2004", ""
    def log_message(self, *a):
        if self.server.app.verbose:
            sys.stderr.write("%s %s\n" % (self.command, self.path.split("?")[0]))

    def send_all(self, code, body, ctype, extra=None):
        self.send_response(code)
        for k, v in {"Content-Type": ctype, "Content-Length": str(len(body)), "Cache-Control": "no-store",
                     "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer", "X-Frame-Options": "DENY",
                     "Cross-Origin-Opener-Policy": "same-origin", "Cross-Origin-Resource-Policy": "same-origin",
                     "Permissions-Policy": "camera=(), geolocation=(), microphone=(self)", "Connection": "close",
                     **(extra or {})}.items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD": self.wfile.write(body)

    def js(self, code, obj):
        self.send_all(code, json.dumps(obj, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def host_ok(self):
        port = self.server.server_address[1]
        ok = {"127.0.0.1:%d" % port, "localhost:%d" % port}
        if self.headers.get("Host", "") not in ok:
            return False
        o = self.headers.get("Origin")
        return o is None or o in {"http://" + h for h in ok}

    def auth_ok(self):
        return hmac.compare_digest(self.headers.get("X-BM-Token", ""), self.server.app.token)

    def do_GET(self):
        try:
            if not self.host_ok(): return self.js(403, {"error": "forbidden"})
            p = self.path.split("?")[0]
            if p == "/":
                nonce = secrets.token_urlsafe(16)
                html = (PAGE.replace("__N__", nonce).replace("__TOKEN__", json.dumps(self.server.app.token))
                        .replace("__I18N__", json.dumps(T, ensure_ascii=False).replace("</", "<\\/"))).encode()
                csp = ("default-src 'none'; script-src 'nonce-%s'; style-src 'nonce-%s'; connect-src 'self'; "
                       "img-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'" % (nonce, nonce))
                return self.send_all(200, html, "text/html; charset=utf-8", {"Content-Security-Policy": csp})
            if p == "/favicon.ico": return self.send_all(204, b"", "image/x-icon")
            if p == "/api/state":
                if not self.auth_ok(): return self.js(403, {"error": "forbidden"})
                return self.js(200, {"state": self.server.app.state()})
            self.js(404, {"error": "not found"})
        except Exception:
            self.js(500, {"error": "server error"})

    do_HEAD = do_GET

    def do_POST(self):
        app = self.server.app
        try:
            if not self.host_ok() or not self.auth_ok(): return self.js(403, {"error": "forbidden"})
            if not app.allow(): return self.js(429, {"error": T[app.s["lang"]]["rate"]})
            if not self.headers.get("Content-Type", "").startswith("application/json"): return self.js(415, {"error": "json only"})
            n = int(self.headers.get("Content-Length") or 0)
            if n < 0 or n > MAX_BODY: return self.js(413, {"error": "too large"})
            try:
                d = json.loads(self.rfile.read(n) or b"{}")
                assert isinstance(d, dict)
            except Exception:
                return self.js(400, {"error": "bad json"})
            p = self.path.split("?")[0]
            if p == "/api/command":
                return self.js(200, app.command(d.get("text", "") if isinstance(d.get("text", ""), str) else ""))
            if p == "/api/settings":
                app.update({k: v for k, v in d.items() if k in DEFAULTS})
                return self.js(200, {"state": app.state()})
            if p == "/api/key":
                k = d.get("key", "")
                if not isinstance(k, str) or not app.set_key(k): return self.js(400, {"error": "bad key"})
                return self.js(200, {"state": app.state()})
            if p == "/api/exit":
                self.js(200, {"ok": True})
                threading.Thread(target=self.server.shutdown, daemon=True).start()
                return
            self.js(404, {"error": "not found"})
        except Exception:
            self.js(500, {"error": "server error"})

def make_server(app, port):
    srv = http.server.ThreadingHTTPServer((HOST, port), Handler)
    srv.daemon_threads, srv.app = True, app
    return srv

# ---------------------------------------------------------------- self-test
def self_test():
    ok = 0
    def check(c, name):
        nonlocal ok
        print(("OK   " if c else "FAIL ") + name)
        if not c: sys.exit(1)
        ok += 1
    keys = set(T["uz"])
    check(all(set(T[l]) == keys for l in LANGS), "tarjimalar to'liq (uz/en/ru)")
    for txt, want in [("Salom, BM OS.", "greet"), ("Soat nechchi?", "time"), ("Bugungi sanani ayt", "date"), ("Sozlamalarni och", "settings"),
                      ("Internet holatini tekshir", "net"), ("Mikrofon holatini tekshir", "mic"), ("Oxirgi javobni takrorla", "repeat"),
                      ("Dasturdan chiq", "exit"), ("What time is it?", "time"), ("Который час?", "time"), ("Список команд", "cmds"),
                      ("Ekrandagi matnni o‘qib ber", "read"), ("Yordam ber", "help"), ("Ovoz balandligini oshir", "vol")]:
        check(detect(txt)[0] == want, "intent: %s -> %s" % (txt, want))
    with tempfile.TemporaryDirectory() as d:
        app = App(d)
        check(app.command("Shriftni kattalashtir")["state"]["font"] == 3, "shrift kattalashadi")
        check(app.command("Ovoz balandligini kamaytir")["state"]["volume"] == 60, "ovoz balandligi kamayadi")
        check(app.command("Ovozni o'chir")["state"]["sound"] is False, "ovoz o'chadi")
        check(app.command("Shriftni kattalashtir yoki kichraytir")["reply"] == T["uz"]["dir_q"], "noaniq buyruq aniqlashtiriladi")
        check(App(d).s["font"] == 3, "sozlamalar tiklanadi")
        check(app.update({"font": 99, "lang": "xx"})["font"] == 5 and app.s["lang"] == "uz", "noto'g'ri sozlamalar rad etiladi")
        check(not app.set_key("short") and app.set_key("A" * 39), "kalit formati tekshiriladi")
        check("A" * 39 not in json.dumps(app.state()), "kalit holatda ko'rinmaydi")
        if os.name == "posix": check(oct(os.stat(app.kfile).st_mode & 0o777) == "0o600", "kalit fayli 0600")
        srv = make_server(app, 0)
        port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        def req(m, path, body=None, h=None, host=None):
            c = http.client.HTTPConnection(HOST, port, timeout=5)
            hh = {"Host": host or "127.0.0.1:%d" % port, **(h or {})}
            c.request(m, path, body, hh)
            r = c.getresponse(); data = r.read(); c.close()
            return r, data
        r, body = req("GET", "/")
        check(r.status == 200 and "script-src 'nonce-" in r.getheader("Content-Security-Policy") and app.key not in body.decode(), "sahifa + CSP")
        tok = re.search(rb'const TOKEN="([^"]+)"', body).group(1).decode()
        H = {"X-BM-Token": tok, "Content-Type": "application/json"}
        check(req("GET", "/", host="evil.com")[0].status == 403, "begona Host rad etiladi")
        check(req("POST", "/api/command", b"{}", {"Content-Type": "application/json"})[0].status == 403, "tokensiz so'rov rad etiladi")
        check(req("POST", "/api/command", b"{}", {**H, "Origin": "http://evil.com"})[0].status == 403, "begona Origin rad etiladi")
        check(req("POST", "/api/command", b"{bad", H)[0].status == 400, "noto'g'ri JSON rad etiladi")
        check(req("POST", "/api/command", b"x" * (MAX_BODY + 1), H)[0].status == 413, "katta so'rov rad etiladi")
        r, b = req("POST", "/api/command", json.dumps({"text": "Soat nechchi?"}).encode(), H)
        check(r.status == 200 and re.search(r"\d\d:\d\d", json.loads(b)["reply"]), "HTTP orqali soat buyrug'i")
        r, b = req("POST", "/api/command", json.dumps({"text": "<script>"}).encode(), H)
        check(json.loads(b)["reply"] == T["uz"]["unk"], "noma'lum buyruq: AI kalitsiz aniqlashtirish")
        check(req("POST", "/api/exit", b"{}", H)[0].status == 200, "chiqish buyrug'i")
    print("Barcha %d tekshiruv o'tdi." % ok)

def main():
    ap = argparse.ArgumentParser(description="BM OS 2004 V1")
    ap.add_argument("--self-test", action="store_true"); ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--verbose", action="store_true"); a = ap.parse_args()
    if a.self_test: return self_test()
    app = App(verbose=a.verbose)
    try:
        srv = make_server(app, PORT)
    except OSError as e:
        sys.exit("Port %d band yoki ochib bo'lmadi: %s" % (PORT, e))
    url = "http://localhost:%d" % PORT
    print("BM OS 2004 ishga tushdi: %s  (to'xtatish: Ctrl+C)" % url)
    if not a.no_browser:
        try: webbrowser.open(url)
        except Exception: pass
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
    finally: srv.server_close()

if __name__ == "__main__":
    main()
