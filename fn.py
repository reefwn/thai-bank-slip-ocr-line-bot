import pytesseract
import re

from collections import namedtuple
from pytesseract import Output

SPECIAL_CHARACTERS = "!#$%^&*()-+?_=,<>/|"
THA="tha"
ENG="eng"
THA_ENG="tha+eng"


def get_img_size(bank):
    sizes = {
        "BAY": (1080, 2268),
        "BBL": (1080, 2589),
        "GOV": (1080, 2037),
        "KBANK": (984, 1402),
        "KTB": (996, 1258),
        "SCB": (1080, 2540),
        "TMB": (1500, 3100)
    }

    return sizes[bank]


def get_ocr_locations(bank):
    OCRLocation = namedtuple("OCRLocation", ["id", "bbox"])
    locations = {
        "BAY": [
            OCRLocation("from", (500, 310, 510, 60)),
            OCRLocation("to", (500, 525, 510, 60)),
            OCRLocation("amount", (500, 705, 400, 60)),
            OCRLocation("date", (320, 165, 205, 40)),
            OCRLocation("time", (525, 165, 145, 40)),
            OCRLocation("ref", (75, 960, 305, 60))
        ],
        "BBL": [
            OCRLocation("from", (400, 1340, 400, 50)),
            OCRLocation("to", (400, 1580, 500, 50)),
            OCRLocation("amount", (400, 1100, 320, 90)),
            OCRLocation("date", (350, 940, 220, 50)),
            OCRLocation("time", (580, 940, 150, 50)),
            OCRLocation("ref", (70, 2370, 650, 50))
        ],
        "GOV": [
            OCRLocation("from", (400, 1340, 400, 50)),
            OCRLocation("to", (400, 1580, 500, 50)),
            OCRLocation("amount", (400, 1100, 320, 90)),
            OCRLocation("date", (350, 940, 220, 50)),
            OCRLocation("time", (580, 940, 150, 50)),
            OCRLocation("ref", (70, 2370, 650, 50))
        ],
        "KBANK": [
            OCRLocation("from", (220, 240, 420, 50)),
            OCRLocation("to", (220, 550, 420, 50)),
            OCRLocation("amount", (210, 985, 320, 50)),
            OCRLocation("date", (60, 100, 195, 50)),
            OCRLocation("time", (255, 100, 160, 50)),
            OCRLocation("ref", (220, 865, 400, 50))
        ],
        "KTB": [
            OCRLocation("from", (180, 480, 500, 50)),
            OCRLocation("to", (180, 680, 500, 50)),
            OCRLocation("amount", (560, 900, 320, 50)),
            OCRLocation("date", (600, 1050, 230, 50)),
            OCRLocation("time", (865, 1050, 100, 50)),
            OCRLocation("ref", (330, 360, 350, 50))
        ],
        "SCB": [
            OCRLocation("from", (350, 670, 700, 70)),
            OCRLocation("to", (350, 880, 700, 70)),
            OCRLocation("amount", (650, 1320, 370, 70)),
            OCRLocation("date", (340, 415, 250, 70)),
            OCRLocation("time", (620, 415, 120, 70)),
            OCRLocation("ref", (355, 490, 565, 70))
        ],
        "TMB": [
            OCRLocation("from", (500, 1280, 935, 70)),
            OCRLocation("to", (500, 1665, 935, 100)),
            OCRLocation("amount", (550, 740, 320, 120)),
            OCRLocation("date", (950, 1880, 270, 90)),
            OCRLocation("time", (1220, 1880, 215, 90)),
            OCRLocation("ref", (900, 2070, 535, 90))
        ]
    }

    return locations[bank]


def get_rois(img):
    d = pytesseract.image_to_data(img, output_type=Output.DICT)
    n_boxes = len(d["level"])

    duplicates = []
    count = 0
    rois = []

    p = 10

    for i in range(n_boxes):
        (x, y, w, h) = (d["left"][i], d["top"][i], d["width"][i], d["height"][i])

        if x != 0 and y != 0 and w != img.shape[0] and h != img.shape[1] and "{}{}".format(w, h) not in duplicates:
            duplicates.append("{}{}".format(w, h))
            count += 1
            roi = img[y-p:y+h+p, x-p:x+w+p]
            rois.append(roi)

    return rois


def gov_ocr(rois):
    ref = ""
    date = ""
    time = ""
    from_ = ""
    to = ""
    amount = ""

    for i in range(len(rois)):
        # ref
        if i == 6:
            txt = pytesseract.image_to_string(rois[i], lang=ENG)
            if any(c in SPECIAL_CHARACTERS for c in txt):
                refs = txt.split(" ")
                for r in refs:
                    if not any(c in SPECIAL_CHARACTERS for c in r):
                        ref = r.strip()
            else:
                ref = txt.strip()
        # date time
        if i == 7:
            text = pytesseract.image_to_string(rois[i], lang=THA_ENG)
            datetime = text.split(" ")
            date = " ".join(datetime[:3]).strip()
            time = " ".join(datetime[3:]).strip()
        # from
        if i == 14:
            txt = pytesseract.image_to_string(rois[i], lang=THA_ENG)
            t = txt.split("\n")
            if len(t[0].split(" ")) > 2:
                names = t[0].split(" ")
                from_ = " ".join(names[-2:])
            else:
                from_ = t[0].strip()
        # to
        if i == 22 or i == 24:
            txt = pytesseract.image_to_string(rois[i], lang=THA_ENG)
            if to == "" and not any(c in SPECIAL_CHARACTERS for c in txt):
                if len(txt.split(" ")) > 2:
                    names = txt.split(" ")
                    to = " ".join(names[-2:])
                else:
                    to = txt.strip()
        # amount
        if i == len(rois) - 2 or i == len(rois) - 1:
            txt = pytesseract.image_to_string(rois[i], lang=THA_ENG)
            txt_int = re.findall(r'[0-9]+', txt)
            if len(txt_int) > 0:
                amount = txt if amount == "" else amount

    return [ref, date, time, from_, to, amount]


def scb_ocr(rois):
    ref = ""
    date = ""
    time = ""
    from_ = ""
    to = ""
    amount = ""

    for i in range(len(rois)):
    # ref
        if i == 10 or i == 12 or i == 13:
            if ref == "":
                txt = pytesseract.image_to_string(rois[i], lang="eng")
                if any(c in SPECIAL_CHARACTERS for c in txt):
                    refs = txt.split(" ")
                    for r in refs:
                        if not any(c in SPECIAL_CHARACTERS for c in r):
                            ref = r.strip().replace(" ", "")
                elif ":" in txt:
                    idx = txt.index(":")
                    ref = "".join(txt[idx+1:]).strip()
                else:
                    ref = txt.strip().replace(" ", "")
        # date time
        if i == 4:
            text = pytesseract.image_to_string(rois[i], lang=THA_ENG)
            datetime = text.split("-")
            date = datetime[0].strip()
            time = datetime[1].strip()
        # from
        if i == 13 or i == 14 or i == 15:
            if from_ == "":
                txt = pytesseract.image_to_string(rois[i], lang=THA_ENG)
                if not any(c in SPECIAL_CHARACTERS for c in txt):
                    t = txt.split(" ")
                    if (len(t) >= 2):
                        from_ = " ".join(t[-2:]).strip()
                    else:
                        from_ = t[0].strip()
        # to
        if i == 20 or i == 22 or i == 25:
            if to == "":
                txt = pytesseract.image_to_string(rois[i], lang=THA_ENG)
                if len(txt.split(" ")) > 2:
                    names = txt.split(" ")
                    if "@" in names:
                        at_idx = names.index("@")
                        to = " ".join(names[at_idx+1:]).strip()
                    else:
                        to = " ".join(names[-2:]).strip()
                else:
                    to = txt.strip()
        # amount
        if i == len(rois) - 5:
            txt = pytesseract.image_to_string(rois[i], lang=THA_ENG)
            txt_int = re.findall(r'[0-9]+', txt)
            if len(txt_int) > 0:
                amount = txt if amount == "" else amount

    return [ref, date, time, from_, to, amount]
