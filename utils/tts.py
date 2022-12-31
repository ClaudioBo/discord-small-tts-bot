import base64

import requests
from gtts import gTTS

available_voices = {
    "tiktok": [
        ["es_002", "Spanish - Male"],
        ["es_mx_002", "Spanish MX - Male"],
        ["en_us_rocket", "Rocket"],
        ["en_us_ghostface", "Ghost Face"],
        ["en_us_c3po", "C3PO"],
        ["en_us_stitch", "Stitch"],
        ["en_us_stormtrooper", "Stormtrooper"],
        ["en_us_006", "English US - Male 1"],
        ["en_us_007", "English US - Male 2"],
        ["en_us_009", "English US - Male 3"],
        ["en_us_010", "English US - Male 4"],
        ["en_us_001", "English US - Female (Int. 1)"],
        ["en_us_002", "English US - Female (Int. 2)"],
        ["br_005", "Portuguese BR - Male"],
        ["br_001", "Portuguese BR - Female 1"],
        ["br_003", "Portuguese BR - Female 2"],
        ["br_004", "Portuguese BR - Female 3"],
        ["jp_006", "Japanese - Male"],
        ["jp_001", "Japanese - Female 1"],
        ["jp_003", "Japanese - Female 2"],
        ["jp_005", "Japanese - Female 3"],
        ["en_male_narration", "narrator"],
        ["en_male_funny", "wacky"],
        ["en_female_emotional", "peaceful"],
        # ["en_us_chewbacca", "Chewbacca"],
        # ["en_male_m03_sunshine_soon", "Sunshine Soon"],
        # ["en_female_f08_warmy_breeze", "Warmy Breeze"],
        # ["en_male_m03_lobby", "Tenor"],
        # ["en_female_f08_salut_damour", "Alto"],
        # ["en_au_001", "English AU - Female"],
        # ["en_au_002", "English AU - Male"],
        # ["en_uk_001", "English UK - Male 1"],
        # ["en_uk_003", "English UK - Male 2"],
        # ["fr_001", "French - Male 1"],
        # ["fr_002", "French - Male 2"],
        # ["de_001", "German - Female"],
        # ["de_002", "German - Male"],
        # ["id_001", "Indonesian - Female"],
        # ["kr_002", "Korean - Male 1"],
        # ["kr_003", "Korean - Female"],
        # ["kr_004", "Korean - Male 2"],
    ],
    "gtts": [
        ["es.es", "Spanish (Spain)"],
        ["es.com", "Spanish (United States)"],
        ["es.com.mx", "Spanish (Mexico)"],
        ["en.com", "English (United States)"],
    ],
}


def generate_gtts(language: str, text):
    lang, tld = language.split(".", 1)
    tts = gTTS(text=text, lang=lang, tld=tld)
    tts.save("tts.mp3")


# Thanks for the tiktok voices: https://github.com/oscie57/tiktok-voice
def generate_tiktok(session_id, text, voice="es_mx_002"):
    text = text.replace("+", "mas")
    text = text.replace(" ", "+")
    text = text.replace("&", "y")

    headers = {"User-Agent": "com.zhiliaoapp.musically/2022600030 (Linux; U; Android 7.1.2; es_ES; SM-G988N; Build/NRD90M;tt-ok/3.12.13.1)", "Cookie": f"sessionid={session_id}"}
    url = f"https://api16-normal-useast5.us.tiktokv.com/media/api/text/speech/invoke/?text_speaker={voice}&req_text={text}&speaker_map_type=0&aid=1233"

    r = requests.post(url, headers=headers)
    try:
        if r.json()["message"] == "Couldn't load speech. Try again.":
            return False
    except:
        return False

    vstr = [r.json()["data"]["v_str"]][0]
    b64d = base64.b64decode(vstr)
    with open("tts.mp3", "wb") as out:
        out.write(b64d)

    return True
