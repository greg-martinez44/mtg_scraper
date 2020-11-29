import re

"""
NEEDS REFORMATTING
"""


def format_decklist(decklist: str) -> str:
    regex_split = re.split(r'^ [0-9] ', decklist)[0]

    return regex_split.split("\n")

def list_colors(card_name: str, set_code: str) -> str:
    for card in set_codes[set_code]:
        if (card_name in card):
            colors = set_codes[set_code][card]["color_id"]
        
    return colors

def split_qty_and_name(formatted_decklist: str) -> (list, list, list):
    qty_column = []
    name_column = []
    code_column = []
    for card in formatted_decklist:
        if (card == "Sideboard") | (card == ""):
            continue
        qty, name = card.split(maxsplit=1)
        code = re.findall("\(.+\)", name)[0][1:-1]
        qty_column.append(qty)
        name_column.append(name)
        code_column.append(code)
    
    return qty_column, name_column, code_column

def export_deck(mtga_decklist):
    color_order = {
        "W": 1,
        "U": 2,
        "B": 3,
        "R": 4,
        "G": 5,
        "A": 6,
        "L": 7
    }
    decklist = format_decklist(mtga_decklist)
    (
        decklist_count, 
        decklist_name, 
        decklist_codes 
    ) = split_qty_and_name(decklist)
    
    color_identity = []
    corrected_names = []
    type_lines = []
    oracle_texts = []
    
    for name in decklist_name:
        raw_set_code = re.findall("\(.+\)", name)
        if len(raw_set_code) > 0:
            set_code = raw_set_code[0][1:-1].lower()
        if set_code not in set_codes:
            set_codes[set_code] = get_set_info(set_code)
        for set_code in set_codes:
            if set_code.upper() in name:
                correct_name = name.split(" (")[0]
                for name in set_codes[set_code]:
                    if correct_name in name:
                        correct_name = name
                corrected_names.append(correct_name)
                colors = list_colors(correct_name, set_code)
                colors.sort(key=lambda x: color_order[x])
                color_identity.append("".join(colors))
                type_line = set_codes[set_code][correct_name]["type_line"]
                type_lines.append(type_line)
                oracle_text = set_codes[set_code][correct_name]["oracle_text"]
                oracle_texts.append(oracle_text)
            
    with open("decklists.txt", "a", encoding="utf-8") as text_file:
        text_file.write("\n---\n")
        for card in list(
            zip(
                decklist_count, 
                corrected_names, 
                color_identity, 
                decklist_codes,
                type_lines,
                oracle_texts
            )
        ):
            text_file.write(
                card[0] + ";"
                + card[1] + ";"
                + "main" + ";"
                + card[2] + ";"
                + card[3] + ";"
                + card[4] + ";"
                + card[5]
                + "\n"
            )
