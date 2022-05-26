from collections import namedtuple

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
    OCRLocation = namedtuple('OCRLocation', ['id', 'bbox'])
    locations = {
        "BAY": [
            OCRLocation('from', (500, 310, 510, 60)),
            OCRLocation('to', (500, 525, 510, 60)),
            OCRLocation('amount', (500, 705, 400, 60)),
            OCRLocation('date', (320, 165, 205, 40)),
            OCRLocation('time', (525, 165, 145, 40)),
            OCRLocation('ref', (75, 960, 305, 60))
        ],
        "BBL": [
            OCRLocation('from', (400, 1340, 400, 50)),
            OCRLocation('to', (400, 1580, 500, 50)),
            OCRLocation('amount', (400, 1100, 320, 90)),
            OCRLocation('date', (350, 940, 220, 50)),
            OCRLocation('time', (580, 940, 150, 50)),
            OCRLocation('ref', (70, 2370, 650, 50))
        ],
        "GOV": [
            OCRLocation('from', (400, 1340, 400, 50)),
            OCRLocation('to', (400, 1580, 500, 50)),
            OCRLocation('amount', (400, 1100, 320, 90)),
            OCRLocation('date', (350, 940, 220, 50)),
            OCRLocation('time', (580, 940, 150, 50)),
            OCRLocation('ref', (70, 2370, 650, 50))
        ],
        "KBANK": [
            OCRLocation('from', (220, 240, 420, 50)),
            OCRLocation('to', (220, 550, 420, 50)),
            OCRLocation('amount', (210, 985, 320, 50)),
            OCRLocation('date', (60, 100, 195, 50)),
            OCRLocation('time', (255, 100, 160, 50)),
            OCRLocation('ref', (220, 865, 400, 50))
        ],
        "KTB": [
            OCRLocation('from', (180, 480, 500, 50)),
            OCRLocation('to', (180, 680, 500, 50)),
            OCRLocation('amount', (560, 900, 320, 50)),
            OCRLocation('date', (600, 1050, 230, 50)),
            OCRLocation('time', (865, 1050, 100, 50)),
            OCRLocation('ref', (330, 360, 350, 50))
        ],
        "SCB": [
            OCRLocation('from', (350, 670, 700, 70)),
            OCRLocation('to', (350, 880, 700, 70)),
            OCRLocation('amount', (650, 1320, 370, 70)),
            OCRLocation('date', (340, 415, 250, 70)),
            OCRLocation('time', (620, 415, 120, 70)),
            OCRLocation('ref', (355, 490, 565, 70))
        ],
        "TMB": [
            OCRLocation('from', (500, 1280, 935, 70)),
            OCRLocation('to', (500, 1665, 935, 100)),
            OCRLocation('amount', (550, 740, 320, 120)),
            OCRLocation('date', (950, 1880, 270, 90)),
            OCRLocation('time', (1220, 1880, 215, 90)),
            OCRLocation('ref', (900, 2070, 535, 90))
        ]
    }

    return locations[bank]