"""
برنامه ای ساده برای نشان دادن اوقات شرعی برای منطقه تجریش تهران - ایران.  شما میتوانید به سادگی موقعیت
مکانی (محله، شهر و کشور) را از داخل برنامه تغییر دهید.  همچنین وضعیت آب و هوا و درجه حرارت روز به همراه درجه حرارت واقعی که با توجه به شرایط احساس میشود نمایش
داده میشود.  DLord
"""

from datetime import date
from io import BytesIO

import certifi
import pycurl
import FreeSimpleGUI as sg
import requests
from art import text2art
from persiantools.jdatetime import JalaliDate, digits

SCRIPT_VERSION = "2.0"
WINDOW_TITLE = f"Islamic Prayer Times Farsi by DLord (v{SCRIPT_VERSION})"

# ابنجا میتوانید نام منطقه، شهر و کشور مورد نظر خودتان را تغییر دهید
AREA = "Tajrish"  # میتوانید وارد نکنید و بصورت "" خالی بگذارید
CITY = "Tehran"
COUNTRY = "Iran"


def get_date() -> str:
    """Get todays date and retuen formated string."""
    return date.today().strftime("%A %d-%b-%y")


def get_jalali_date() -> str:
    """Get todays date based on Jalali Calendar and return formated string."""
    months = {
        "1": "فروردین",
        "2": "اردیبهشت",
        "3": "خرداد",
        "4": "تیر",
        "5": "مرداد",
        "6": "شهریور",
        "7": "مهر",
        "8": "آبان",
        "9": "آذر",
        "10": "دی",
        "11": "بهمن",
        "12": "اسفند",
    }
    days = {
        "Shanbeh": "شنبه",
        "Yekshanbeh": "یکشنبه",
        "Doshanbeh": "دوشنبه",
        "Seshanbeh": "سه شنبه",
        "Chaharshanbeh": "چهارشنبه",
        "Panjshanbeh": "پنج شنبه",
        "Jomeh": "جمعه",
    }
    jdate = str([JalaliDate.today()])[12:-2]
    jlist = jdate.replace(" ", "").split(",")
    todayJ = days[jlist[3]] + ", " + jlist[2] + " " + months[jlist[1]] + " " + jlist[0]
    return digits.en_to_fa(todayJ)


def ascii_art() -> str:
    """Print an ascii art with random font of author's name."""
    author = "DLord"
    return text2art(author, font="random-medium")


def get_weather(loc) -> str:
    """Get weather data for the Area if present, otherwise for the City"""
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(pycurl.TIMEOUT, 4)
    c.setopt(c.URL, f"https://wttr.in/{loc}?format=%l:+%c+%t+(%f)")
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CAINFO, certifi.where())
    try:
        c.perform()
        c.close()
        body = (buffer.getvalue()).decode("utf-8")
    except pycurl.error:
        body = "اطلاعات هواشناسی در دسترس نیست"
    return digits.en_to_fa(body)


def main():
    try:
        response = requests.get(
            f"http://api.aladhan.com/v1/timingsByAddress?address={AREA}%2C+{CITY}%2C+{COUNTRY}&method=7&midnightMode=1",
            timeout=10,
        )
        response.raise_for_status()
        timings = response.json()["data"]["timings"]
        header1_date = f"{get_jalali_date()}"
        header2_location = (
            f"\n{CITY} ({AREA}) - {COUNTRY} : موقعیت"
            if AREA != ""
            else f"\n{CITY} - {COUNTRY} : موقعیت"
        )
        header3_weather = (
            f"\n {get_weather(AREA)}\n\n"
            if AREA != ""
            else f"\n {get_weather(CITY)}\n\n"
        )
        body = digits.en_to_fa(
            f"\nاذان صبح: {timings['Fajr']}\nطلوع آفتاب: {timings['Sunrise']}\nاذان ظهر: {timings['Dhuhr']}\nاذان عصر: {timings['Asr']}\nغروب آفتاب: {timings['Sunset']}\nاذان مغرب: {timings['Maghrib']}\nاذان عشاء: {timings['Isha']}\nنیمه شب شرعی: {timings['Midnight']}\n\n\n"
        )
        output_text = (
            header1_date + header2_location + header3_weather + body + ascii_art()
        )
        sg.theme("DarkGrey5")
        layout = [
            [sg.Text(output_text, font=("Cascadia Code", 12))],
            [sg.Button("Close")],
        ]
        window = sg.Window(
            WINDOW_TITLE,
            layout,
            element_justification="c",
            text_justification="c",
        )
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == "Close":
                break
        window.close()
    except (requests.exceptions.RequestException, ValueError) as e:
        sg.theme("DarkGrey5")
        sg.Window(
            title="Error",
            layout=[
                [sg.Text(("Connenction error...!"), font=("Cascadia Code", 12))],
                [sg.Button("  Exit  ")],
            ],
            element_justification="c",
            text_justification="c",
        ).read()

if __name__ == "__main__":
    main()

