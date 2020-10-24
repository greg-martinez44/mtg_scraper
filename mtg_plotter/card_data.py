import requests

def get_card_info(card_name: str) -> list:
    url = ("https://api.scryfall.com/cards/search?q=name%3A" + card_name)
    api_results = requests.get(url)
    api_json = api_results.json()["data"][0]

    return api_json["color_identity"]

def get_card_name(set_code: str, collectors_number: str) -> str:
    url = ("https://api.scryfall.com/cards/" + set_code + "/" + collectors_number)
    api_results = requests.get(url)
    api_json = api_results.json()

    return api_json["name"]

def connect_to_api(set_code, page):
    url = (
        "https://api.scryfall.com/cards/search?order=set&q=set%3A" 
        + set_code + "&page=" + str(page)
    )
    print(url)
    api_results = requests.get(url)

    return api_results.json()


def get_set_info(set_code) -> (dict, dict):
    set_info = {}
    page = 1
    next_page = True   
    while next_page:
        api_json = connect_to_api(set_code, page)
        next_page = api_json.get("has_more")
        page += 1

        #Could make a Card object to hold all this data...
        for card in api_json["data"]:
            name = card["name"]
            collector_number = card["collector_number"]
            color_id = card["color_identity"]
            type_line = card["type_line"]

            try:
                oracle_text = card["oracle_text"]
            except KeyError:
                oracle_text = " // ".join([
                    card.get("card_faces")[0].get("oracle_text"),
                    card.get("card_faces")[1].get("oracle_text")
                ])
            
            set_info.update({name: {
                "collector_number": collector_number,
                "color_id": [],
                "type_line": type_line,
                "oracle_text": oracle_text.replace("\n", " + ")
            }})

            if len(color_id) > 0:
                set_info.get(name).update({"color_id": color_id})
            elif "Artifact" in type_line:
                set_info.get(name).update({"color_id": ["A"]})
            else:
                set_info.get(name).update({"color_id": ["L"]})

    return set_info

if  __name__ == "__main__":
    the_set = get_set_info("eld")
    with open("did it work.txt", "w", encoding="utf-8") as test:
        test.write(str(the_set))
