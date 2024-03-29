import json
URL = "https://www.mtgtop8.com/format?f=ST"

ZENDIKAR_RELEASE = "2020-09-25"
KALDHEIM_RELEASE = "2021-02-05"
STRIXHAVEN_RELEASE = "2021-04-23"

data_maps = {
    "id_names": {
        601: "GW Adventures",
        930: "Izzet Mill",
        931: "Sultai Ramp",
        932: "Orzhov Aristocrats",
        934: "Temur Control"
    },

    "archetype_maps": {
        "base_map": {
            "jund": ["jund"],
            "golgari": ["golgari"],
            "aggro": [
                "aggro",
                "red deck wins",
                "weenie",
                "ww",
                "mono green",
                "rdw",
                "devotion to black",
                "agro"
            ],
            "control": ["control", "doom", "4cc", "yorion"],
            "midrange": ["midrange", "mid range"],
            "gyruda": ["gyruda"],
            "winota": ["winota"],
            "mill": ["mill"],
            "ramp": ["ramp", "omnath", "ultimatum", "forsaken monument"],
            "rogue": ["rogue"],
            "flash": ["flash"],
            "adventure": ["adventure"],
            "food": ["food"],
            "reclamation": ["reclamation"],
            "sacrifce": ["sacrifice", "aristocrats"],
            "cycling": ["cycling"],
            "kicker": ["kicker", "kick"],
            "mutate": ["mutate"],
            "stompy": ["stompy"],
            "dragons": ["dragon"]
        },
        "name_map": {
            "5c Sanctum": "control"
        },
        "id_map": {
            2452: "aggro",
            2757: "control",
            2975: "aggro",
            3020: "aggro",
            3024: "aggro",
            3199: "aggro",
            3201: "control",
            3202: "aggro",
            3347: "aggro",
            3390: "control",
            3624: "aggro",
            3626: "control",
            3673: "aggro",
            3678: "aggro"
        }
    },

    "category_maps": {
        "base_map": {
            "mono white": [
                "mono white",
                "mono-white",
                "white weenie",
                "weenie white",
                "ww"
            ],
            "mono blue": ["mono blue", "mono-blue"],
            "mono black": ["mono black", "mono-black", "devotion to black"],
            "mono red": ["mono red", "mono-red", "red deck wins", "rdw"],
            "mono green": ["mono green", "mono-green", "monogreen"],
            "azorius": ["azorius", "uw", "wu"],
            "orzhov": ["orzhov", "wb", "bw"],
            "boros": ["boros", "wr", "rw", "winota"],
            "selesnya": ["selesnya", "wg", "gw"],
            "dimir": ["dimir", "ub"],
            "izzet": ["izzet", "ur"],
            "simic": ["simic", " ug "],
            "rakdos": ["rakdos", "br", "rb"],
            "golgari": ["golgari", "bg", "gb"],
            "gruul": ["gruul", "rg", "grull"],
            "bant": ["bant", "gwu", "guw", "ugw", "uwg", "wgu", "wug"],
            "esper": ["esper", "wub"],
            "grixis": ["grixis"],
            "jund": ["jund"],
            "naya": ["naya"],
            "jeskai": ["jeskai"],
            "sultai": ["sultai"],
            "mardu": ["mardu", "kroxa doom"],
            "temur": ["temur"],
            "abzan": ["abzan"],
            "4-color": ["omnath", "4c"],
            "colorless": ["forsaken monument"],
            "5-color": ["5c"]
        },
        "id_map": {
            360: "gruul",
            1063: "4-color",
            3568: "4-color",
            3625: "mono white"
        }
    },

    "abu_map": {
        "092abu": "266eld",
        "170abu": "262eld",
        "130abu": "254eld",
        "196abu": "250eld",
        "249abu": "258eld",
        "065abu": "010znr",
        "271abu": "078m20",
        "215abu": "027eld" 
    },

    "broken_code_map": {
        "171cmd": "204m21",
        "356eld": "101eld",
        "367eld": "147eld",
        "335eld": "008eld",
        "346eld": "054eld",
        "001unk": "",
        "003ivg": "174grn",
        "004m10": "006m21",
        "00514c": "013m21",
        "021sha": "032m21",
        "036str": "126eld",
        "0496th": "025iko",
        "051m10": "049iko",
        "054m12": "051m21",
        "054m12 ": "051m21",
        "079sta": "103m21",
        "083urs": "096m21",
        "10113m": "109m20",
        "107dar": "241m21",
        "1136th": "159m21",
        "12410m": "124m20",
        "1276th": "171m21",
        "144gui": "248rna",
        "162gui": "257grn",
        "163gui": "259rna",
        "23215m": "245m15",
        "237urs": "063m21",
        "309thb": "076thb",
        "328iko": "162iko",
        "334eld": "001eld",
        "364znr": "215znr",
        "117urs": "021m21",
        "189eld": "187eld",
        "012urs": "042khm",
        "228ths": "256m21",
        "043mor": "071znr",
        "001frf": "001m21",
        "119akh": "107iko",
        "228roe": "247iko",
        "201isd": "199m21",
        "245mrd": "239m21",
        "096isd": "083iko",
        "005jou": "004thb",
        "148rix": "209m21",
        "225ths": "245thb",
        "246ktk": "257iko",
        "165jou": "253m21",
        "175war": "197thb",
        "232ktk": "246iko",
        "235ktk": "249iko",
        "065mh1": "061m21",
        "048zen": "062znr",
        "227ths": "255m21",
        "168zen": "193znr",
        "065som": "102m21",
        "168m11": "177m21",
        "109aer": "188m21",
        "115ori": "103eld",
        "226ths": "254m21",
        "248xln": "233eld",
        "164jou": "252m21",
        "143isd": "145m21",
        "043hou": "064m21",
        "224ths": "244thb",
        "088hou": "140m21",
        "018som": "034thb",
        "145m20": "141thb",
        "190m11": "169iko",
        "229ktk": "243iko",
        "240ktk": "252iko",
        "176war": "207m21",
        "110xln": "107m21",
        "046mbs": "114m21",
        "201chk": "173m21",
        "229ths": "249thb",
        "190som": "234m21",
        "010war": "009iko",
        "079emn": "082m21",
        "010ktk": "019m21",
        "040ori": "043m21",
        "223soi": "199znr",
        "082mbs": "163iko",
        "247ktk": "258iko",
        "147roe": "147m21",
        "078aer": "141m21",
        "016rav": "017m21",
        "231ktk": "244iko",
        "035m19": "031m21",
        "145war": "161m21",
        "041rav": "045iko",
        "133ths": "149thb",
        "168akh": "157iko",
        "245m19": "238m21",
        "242ktk": "254iko",
        "172dis": "246rna",
        "051tsp": "046m21",
        "149dka": "227m20",
        "037ktk": "054khm",
        "075war": "085m21",
        "100kld": "128znr",
        "007ktk": "015m21",
        "093rna": "134m21",
        "205dom": "147khm"
    },

    "rank_map": {
        "base_map":
            {
            22: [
                ("11 pts", 1),
                ("9 pts", 2),
                ("8 pts", 3),
                ("7 pts", 4),
                ("6 pts", 5),
                ("5 pts", 6),
                ("4 pts", 7)
                ],
            30: [
                ("9 pts", 1),
                ("8 pts", 2),
                ("7 pts", 3),
                ("6 pts", 4),
                ("5 pts", 5)
                ],
            300: [
                ("21 pts", 1),
                ("1 pts", 2)
                ],
            408: [
                ("24 pts", 1),
                ("21 pts", 2),
                ("18 pts", 3)
                ]
        },
        "composite_map": {
            "5-8": 5,
            "3-4": 3
            }
    },

    "id_spec_map": {
        "160bng": ("246thb", "Temple of Enlightenment", ""),
        "161bng": ("247thb", "Temple of Malice", ""),
        "088ths": ("099thb", "Gray Merchant of Asphodel", "B"),
        "162bng": ("248thb", "Temple of Plenty", ""),
        "169inv": ("059m21", "Opt", "U"),
        "236ktk": ("255iko", "Swiftwater Cliffs", ""),
        "237ktk": ("256iko", "Thornwood Falls", ""),
        "255xln": ("242thb", "Field of Ruin", ""),
        "232m15": ("248m21", "Radiant Fountain", ""),
        "279leg": ("121thb", "Underworld Dreams", "B"),
        "011dom": ("016m21", "Dub", "W"),
        "310ice": ("280khm", "Snow-Covered Swamp", ""),
        "189dom": ("142iko", "Adventurous Impulse", "G"),
        "076dom": ("082iko", "Dark Bargain", "B"),
        "034isd": ("042znr", "Smite the Monstrous", "W"),
        "108kld": ("110iko", "Cathartic Reunion", "R"),
        "090dom": ("094m21", "Deathbloom Thallid", "B"),
        "307ice": ("278khm", "Snow-Covered Island", ""),
        "308ice": ("283khm", "Snow-Covered Mountain", ""),
        "306ice": ("284khm", "Snow-Covered Forest", ""),
        "309ice": ("277khm", "Snow-Covered Plains", "")
    }
}

FULL_TABLE_COLUMNS = [
    "eventId",
    "name_event",
    "date",
    "deckId",
    "pilotId",
    "name_deck",
    "firstName",
    "lastName",
    "cardId",
    "name",
    "count",
    "color",
    "slot",
    "archetype",
    "category",
    "latest_set"
    ]

SETS = [
    "eld", "thb", "iko", "m21", "znr",
    "war", "rna", "grn", "m20", "mor",
    "frf", "m11", "m12", "m10", "m13",
    "m19", "m14", "m15", "aer", "akh",
    "bng", "chk", "dar", "dis", "dka",
    "dom", "emn", "gtc", "hou", "ice",
    "inv", "isd", "jou", "ktk", "leg",
    "mbs", "mh1", "mrd", "ogw", "ori",
    "rav", "rix", "roe", "rtr", "sha",
    "soi", "som", "ths", "tsp", "xln",
    "zen", "kld", "khm", "stx"
]

FLAT_FILE_DIR = "../flat_files"

if __name__ == "__main__":
    with open("data/maps.json", "w") as json_file:
        json.dump(data_maps, json_file)

