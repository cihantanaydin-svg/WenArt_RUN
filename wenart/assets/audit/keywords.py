"""Title words: what a model's title says it is, in any of the library's languages (docs/milestone12.md §6.1, D21).

What: ``title_check(title, ftype)`` reads a catalogue title (ABO listings in EN/IT/FR/ES/DE/NL/SV, Sketchfab titles in
any language, our Turkish projects) and says whether it names the catalogue type (``match``), a near type
(``near``: a sideboard filed as a chest of drawers), another type (``conflict``) or nothing (``silent``), plus the
flags that remove a model whatever its type: outdoor, not photoreal (low poly, stylized, test), not the object (an
air bed, a corpse, a terrain), a part of a piece (a sectional component) or a scene (a dining set).

Why: the M8-M10 judges never saw the title and the survey's filter words were English only; the diagnosis (§1.6)
found an air bed ("Luchtbed") as a double bed, "Corpse" as a throw, street lamps as floor lamps, park benches,
ceiling lamps and a sink as trays, wardrobes ("armadio", "Armoire") as tall cabinets.

How: ``fold`` lowercases, strips accents (Turkish dotless i, German sharp s as well) and splits camelCase and
punctuation into tokens. A keyword is a phrase of tokens (a token also matches with a plural ``s`` / ``es``), a
``~stem`` that matches inside one token (German, Dutch and Swedish compounds), or a CJK string matched inside the
folded title. Overlapping matches go to the longest keyword ("coffee table" beats "table", "throw pillow" beats
"throw"). Families map to the types they name (``FAMILY_TYPES``); a family whose types hold the catalogue type
makes the title a ``match`` even when other families are named too ("Side End Table Nightstand"). ``indoor`` in the
title cancels the outdoor words ("Indoor Outdoor Stoneware Vase"). Generated models carry our own titles: their
title says nothing (``generated``). Pure and deterministic.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Optional

# Family -> the catalogue types it names (furniture types and decor names, wenart.furniture.catalog).
FAMILY_TYPES: dict[str, tuple[str, ...]] = {
    "bed": ("bed_single", "bed_double"),
    "bed_single": ("bed_single",),
    "bed_double": ("bed_double",),
    "bunk_bed": ("bunk_bed",),
    "crib": ("crib",),
    "sofa": ("sofa", "sofa_corner"),
    "sofa_corner": ("sofa_corner",),
    "bank": ("bench", "sofa", "sofa_corner"),           # "bank": bench in DE/TR, sofa in NL
    "daybed": ("sofa", "chaise", "bed_single"),
    "chaise": ("chaise",),
    "armchair": ("armchair",),
    "chair": ("chair", "armchair", "office_chair", "bar_stool"),
    "office_chair": ("office_chair",),
    "stool": ("bar_stool", "ottoman"),
    "bar_stool": ("bar_stool",),
    "ottoman": ("ottoman", "bench"),
    "bench": ("bench",),
    "table": ("table_dining", "table_coffee", "desk", "side_table", "console_table", "nightstand"),
    "table_dining": ("table_dining",),
    "table_coffee": ("table_coffee",),
    "side_table": ("side_table", "nightstand"),
    "console_table": ("console_table",),
    "desk": ("desk",),
    "nightstand": ("nightstand",),
    "dressing_table": (),                                # a vanity: no type of ours
    "wardrobe": ("wardrobe",),
    "cabinet": ("wardrobe", "sideboard", "tall_cabinet", "display_cabinet", "shoe_cabinet", "tv_unit", "nightstand",
                "dresser", "bookshelf", "wall_cabinet"),
    "tall_cabinet": ("tall_cabinet",),
    "display_cabinet": ("display_cabinet",),
    "shoe_cabinet": ("shoe_cabinet",),
    "sideboard": ("sideboard",),
    "dresser": ("dresser",),
    "tv_unit": ("tv_unit",),
    "bookshelf": ("bookshelf",),
    "shelf": ("bookshelf",),
    "fridge": ("fridge",),
    "stove": ("stove",),
    "sink_kitchen": ("sink_kitchen",),
    "sink": ("sink_kitchen", "washbasin"),
    "washbasin": ("washbasin",),
    "toilet": ("toilet",),
    "shower": ("shower",),
    "bathtub": ("bathtub",),
    "washing_machine": ("washing_machine",),
    "appliance": ("fridge", "stove", "washing_machine"),
    "floor_lamp": ("floor_lamp",),
    "lamp": ("floor_lamp", "table_lamp", "pendant_light", "ceiling_light"),
    "table_lamp": ("table_lamp",),
    "pendant_light": ("pendant_light",),
    "ceiling_light": ("ceiling_light",),
    "wall_light": (),                                    # a sconce: no type of ours
    "plant": ("potted_plant", "plant", "plant_small", "plant_large"),
    "pot": ("potted_plant", "plant", "plant_small", "plant_large", "vase"),
    "empty_pot": (),                                     # a pot without a plant
    "rug": ("rug",),
    "cushion": ("cushion",),
    "bed_pillow": ("cushion",),
    "curtain": ("curtain",),
    "blind": ("blind",),
    "throw": ("throw",),
    "books": ("books",),
    "candle": ("candle",),
    "basket": ("basket",),
    "tray": ("tray",),
    "clock": ("clock",),
    "floor_clock": (),                                   # a grandfather clock: not a wall clock
    "sculpture": ("sculpture",),
    "mirror": ("mirror",),
    "wall_art": ("wall_art",),
    "vase": ("vase",),
    "bowl": ("bowl", "tray"),
    "window": (),                                        # architecture, not decor
    "towel": (),
    "box": (),
    "animal": (),
    "kitchenware": (),                                   # cutting boards, pans, plates
    "machine": ("fridge", "stove", "washing_machine"),
    "room": (),                                          # a whole room named alone ("Bathroom")
    "furniture": (),                                     # "furniture" alone names no type
}

# Families that name no piece on their own: ignored, but they cancel a room word ("Bedroom Furniture").
IGNORED_FAMILIES = frozenset({"furniture"})

# Types close enough that a title naming one for the other is not a reason to remove (the vision check decides).
NEAR_TYPES: tuple[frozenset, ...] = (
    frozenset({"dresser", "sideboard", "tv_unit", "console_table"}),
    frozenset({"nightstand", "side_table", "dresser"}),
    frozenset({"ottoman", "bench", "bar_stool"}),
    frozenset({"chair", "armchair", "office_chair", "bar_stool"}),
    frozenset({"table_coffee", "side_table"}),
    frozenset({"desk", "console_table", "table_dining"}),
    frozenset({"bookshelf", "display_cabinet", "tall_cabinet", "shoe_cabinet"}),
    frozenset({"sofa", "sofa_corner", "chaise"}),
    frozenset({"bed_single", "bed_double", "bunk_bed", "crib"}),
    frozenset({"pendant_light", "ceiling_light"}),
    frozenset({"potted_plant", "plant", "plant_small", "plant_large", "vase"}),
    frozenset({"sink_kitchen", "washbasin"}),
)

# Keywords per family. "a b" = phrase of tokens; "~stem" = inside one token; CJK = inside the folded title.
KEYWORDS: dict[str, tuple[str, ...]] = {
    "bed": ("bed", "bed frame", "platform bed", "bedframe", "yatak", "bett", "lit", "cama", "letto", "sang", "kravat",
            "кровать", "床", "ベッド"),
    "bed_single": ("single bed", "twin bed", "twin", "tek kisilik yatak", "~einzelbett", "~eenpersoonsbed",
                   "lit simple", "lit 1 place", "cama individual", "letto singolo", "单人床", "單人床"),
    "bed_double": ("double bed", "queen", "king", "queen bed", "king bed", "full bed", "cift kisilik yatak",
                   "~doppelbett", "~tweepersoonsbed", "lit double", "lit 2 places", "cama doble", "cama matrimonial",
                   "letto matrimoniale", "双人床", "雙人床"),
    "bunk_bed": ("bunk bed", "bunk", "bunkbed", "loft bed", "ranza", "~etagenbett", "~hochbett", "~stapelbed",
                 "lits superposes", "lit superpose", "litera", "letto a castello", "双层床", "雙層床"),
    "crib": ("crib", "cot", "cotbed", "baby bed", "cradle", "besik", "~babybett", "~kinderbett", "~gitterbett", "wieg",
             "ledikant", "berceau", "lit bebe", "cuna", "culla"),
    "sofa": ("sofa", "couch", "settee", "loveseat", "love seat", "divan", "kanepe", "koltuk takimi", "canape",
             "divano", "soffa", "диван", "沙发", "沙發", "ソファ", "sofa set"),
    "sofa_corner": ("corner sofa", "sectional", "sectional sofa", "l shaped", "l shape", "u sectional",
                    "l sectional", "kose koltuk", "~ecksofa", "~hoekbank", "canape d angle", "sofa esquinero",
                    "rinconera", "divano angolare"),
    "bank": ("bank", "zitbank"),
    "daybed": ("daybed", "day bed", "futon"),
    "chaise": ("chaise longue", "chaise lounge", "lounger", "sezlong", "chaiselongue", "meridienne"),
    "armchair": ("armchair", "arm chair", "accent chair", "lounge chair", "wingback", "easy chair", "club chair",
                 "berjer", "tekli koltuk", "sessel", "fauteuil", "sillon", "butaca", "poltrona", "fatolj", "fåtölj"),
    "chair": ("chair", "dining chair", "side chair", "sandalye", "stuhl", "stoel", "chaise", "silla", "sedia", "stol",
              "стул", "椅", "椅子"),
    "office_chair": ("office chair", "desk chair", "executive chair", "computer chair", "task chair", "swivel chair",
                     "gaming chair", "ofis koltugu", "calisma sandalyesi", "~burostuhl", "~bureaustoel",
                     "chaise de bureau", "silla de oficina", "sedia da ufficio", "sedia direzionale",
                     "kontorsstol"),
    "stool": ("stool", "tabure", "hocker", "kruk", "tabouret", "taburete", "sgabello", "pall"),
    "bar_stool": ("bar stool", "barstool", "counter stool", "counter height stool", "bar taburesi", "~barhocker",
                  "~barkruk", "tabouret de bar", "taburete de bar", "sgabello da bar"),
    "ottoman": ("ottoman", "pouf", "pouffe", "footstool", "foot stool", "footrest", "puf", "~fusshocker", "poef",
                "repose pied"),
    "bench": ("bench", "banc", "banco", "panca", "panchina", "bankje", "sitzbank"),
    "table": ("table", "masa", "tisch", "tafel", "mesa", "tavolo", "tavolino", "стол", "桌", "テーブル"),
    "table_dining": ("dining table", "kitchen table", "dining kitchen table", "dining room table", "yemek masasi",
                     "~esstisch", "~eettafel", "table a manger", "table de salle a manger", "mesa de comedor",
                     "mesa comedor", "tavolo da pranzo", "matbord", "餐桌"),
    "table_coffee": ("coffee table", "cocktail table", "orta sehpa", "~couchtisch", "~salontafel", "~sofatisch",
                     "table basse", "mesa de centro", "tavolino da salotto", "soffbord", "茶几"),
    "side_table": ("side table", "end table", "accent table", "nesting table", "nesting tables", "lamp table",
                   "yan sehpa", "sehpa", "~beistelltisch", "~bijzettafel", "table d appoint", "bout de canape",
                   "mesa auxiliar", "sidobord", "garden stool"),
    "console_table": ("console table", "console", "sofa table", "hall table", "entryway table", "hallway table",
                      "konsol", "~konsolentisch", "~sidetable", "table console", "consola", "consolle"),
    "desk": ("desk", "writing desk", "computer desk", "study desk", "calisma masasi", "~schreibtisch", "bureau",
             "escritorio", "scrivania", "skrivbord", "书桌", "書桌"),
    "nightstand": ("nightstand", "night stand", "bedside table", "bedside cabinet", "night table", "komodin",
                   "~nachttisch", "~nachtkastje", "table de chevet", "chevet", "mesita de noche", "mesilla",
                   "comodino", "sangbord"),
    "dressing_table": ("dressing table", "vanity table", "makeup table", "makyaj masasi", "~schminktisch",
                       "coiffeuse", "tocador", "toeletta"),
    "wardrobe": ("wardrobe", "armoire", "closet", "gardirop", "elbise dolabi", "~kleiderschrank", "~kledingkast",
                 "penderie", "armario", "ropero", "armadio", "~garderob", "衣柜", "衣櫃"),
    "cabinet": ("cabinet", "cupboard", "dolap", "schrank", "kast", "skap", "skåp",
                "шкаф", "柜", "櫃"),
    "tall_cabinet": ("tall cabinet", "pantry cabinet", "pantry", "storage tower", "column cabinet", "kiler dolabi",
                     "~hochschrank", "colonne", "columna", "colonna", "colonna da bagno"),
    "display_cabinet": ("display cabinet", "china cabinet", "curio", "vitrine", "vitrin", "vitrina", "vetrina",
                        "~vitrinekast", "~vitrinskap", "~vitrinskåp"),
    "shoe_cabinet": ("shoe cabinet", "shoe rack", "shoe bench", "shoe storage", "ayakkabilik", "~schuhschrank",
                     "~schoenenkast", "meuble a chaussures", "zapatero", "scarpiera", "~skoskap", "~skoskåp"),
    "sideboard": ("sideboard", "buffet", "credenza", "bufe", "anrichte", "dressoir", "bahut", "aparador", "credenze",
                  "skank", "skänk"),
    "dresser": ("dresser", "chest of drawers", "chest", "sifonyer", "kommode", "ladekast", "commode", "comoda",
                "cassettiera", "byra", "byrå"),
    "tv_unit": ("tv unit", "tv stand", "tv cabinet", "tv console", "tv board", "media console", "media table",
                "media cabinet", "entertainment center", "tv unitesi", "~tv-schrank", "~lowboard", "meuble tv",
                "mueble tv", "mobile tv", "porta tv", "tv bank", "tv meubel"),
    "bookshelf": ("bookshelf", "bookcase", "book shelf", "shelving unit", "etagere", "kitaplik", "~bucherregal",
                  "~buecherregal", "regal", "~boekenkast", "bibliotheque", "libreria", "estanteria", "~bokhylla",
                  "书架", "書架"),
    "shelf": ("shelf", "shelves", "raf", "scaffale", "hylla", "シェルフ", "棚"),
    "fridge": ("fridge", "refrigerator", "freezer", "buzdolabi", "~kuhlschrank", "~koelkast", "refrigerateur",
               "frigo", "nevera", "frigorifico", "frigorifero", "kylskap", "kylskåp", "冰箱"),
    "stove": ("stove", "cooker", "range", "oven", "hob", "ocak", "firin", "herd", "fornuis", "cuisiniere",
              "horno", "forno", "spis"),
    "sink_kitchen": ("kitchen sink", "evye", "eviye", "~spule", "~spuele", "~gootsteen", "~spoelbak", "evier",
                     "fregadero", "lavello", "diskho"),
    "sink": ("sink",),
    "washbasin": ("washbasin", "wash basin", "basin", "vanity", "lavabo", "~waschbecken", "~wastafel", "lavabo",
                  "lavamanos", "handfat", "洗手盆"),
    "toilet": ("toilet", "wc", "water closet", "klozet", "tuvalet", "toilette", "toilettes", "inodoro", "vater",
               "~toilet", "马桶", "馬桶"),
    "shower": ("shower", "dus", "dusche", "douche", "ducha", "doccia", "dusch", "淋浴"),
    "bathtub": ("bathtub", "bath tub", "tub", "kuvet", "~badewanne", "ligbad", "baignoire", "banera", "vasca",
                "vasca da bagno", "badkar", "浴缸"),
    "washing_machine": ("washing machine", "washer", "washer dryer", "camasir makinesi", "~waschmaschine",
                        "~wasmachine", "lave linge", "lavadora", "lavatrice", "tvattmaskin", "tvättmaskin", "洗衣机",
                        "洗衣機"),
    "appliance": ("appliance",),
    "machine": ("machine",),
    "floor_lamp": ("floor lamp", "standing lamp", "torchiere", "lambader", "~stehlampe", "~stehleuchte",
                   "~vloerlamp", "staande lamp", "lampadaire", "lampara de pie", "lampada da terra", "piantana",
                   "golvlampa", "落地灯", "落地燈"),
    "lamp": ("lamp", "lamba", "lampe", "leuchte", "lampara", "lampada", "lampa", "светильник",
             "灯", "燈", "ランプ"),
    "table_lamp": ("table lamp", "desk lamp", "bedside lamp", "abajur", "~tischlampe", "~tischleuchte",
                   "~tafellamp", "lampe de table", "lampe de chevet", "lampara de mesa", "lampada da tavolo",
                   "bordslampa", "台灯", "檯燈"),
    "pendant_light": ("pendant", "pendant light", "pendant lamp", "chandelier", "hanging light", "hanging lamp",
                      "avize", "~pendelleuchte", "~hangeleuchte", "~kronleuchter", "~hanglamp", "suspension",
                      "lustre", "lampara colgante", "lampadario", "taklampa", "люстра", "吊灯", "吊燈"),
    "ceiling_light": ("ceiling light", "ceiling lamp", "flush mount", "semi flush", "semiflush", "flush mount ceiling",
                      "ceiling fixture", "tavan lambasi", "plafonyer", "~deckenleuchte", "~deckenlampe",
                      "~plafondlamp", "plafonnier", "plafon", "plafoniera", "吸顶灯", "吸頂燈"),
    "wall_light": ("sconce", "wall sconce", "wall light", "wall lamp", "aplik", "~wandleuchte", "~wandlamp", "applique",
                   "aplique", "vagglampa", "väggLampa"),
    "plant": ("plant", "potted plant", "succulent", "cactus", "cacti", "palm", "monstera", "fern", "ficus", "bonsai",
              "olive tree", "houseplant", "bitki", "saksi bitkisi", "~pflanze", "~topfpflanze", "plante", "planta",
              "pianta", "vaxt", "växt", "植物", "盆栽"),
    "pot": ("pot", "planter", "flower pot", "flowerpot", "saksi", "~blumentopf", "bloempot", "cache pot", "maceta",
            "vaso per piante", "kruka"),
    "empty_pot": ("empty pot", "empty flower pot", "empty planter"),
    "rug": ("rug", "area rug", "carpet", "runner rug", "hali", "kilim", "teppich", "~vloerkleed", "tapijt", "tapis",
            "alfombra", "tappeto", "matta", "ковер", "地毯"),
    "cushion": ("cushion", "throw pillow", "decorative pillow", "accent pillow", "pillow cover", "toss pillow",
                "kirlent", "kissen", "~sierkussen", "coussin", "cojin", "cuscino", "kudde", "靠垫", "抱枕"),
    "bed_pillow": ("bed pillow", "pillow", "yastik", "~kopfkissen", "hoofdkussen", "oreiller", "almohada", "guanciale"),
    "curtain": ("curtain", "drape", "drapes", "perde", "vorhang", "gardine", "gordijn", "rideau", "cortina", "tenda",
                "gardin", "窗帘", "窗簾"),
    "blind": ("blind", "roller blind", "roller shade", "venetian blind", "roman shade", "shutter", "stor", "jaluzi",
              "rollo", "jalousie", "~rolgordijn", "store", "persiana", "estor", "tapparella", "rullgardin", "百叶窗"),
    "throw": ("throw", "throw blanket", "blanket", "plaid", "battaniye", "~wolldecke", "deken", "couverture",
              "manta", "coperta", "pled", "filt", "毯"),
    "books": ("book", "books", "book stack", "kitap", "buch", "bucher", "boek", "boeken", "livre", "livres", "libro",
              "libri", "bok", "bocker", "böcker", "书", "書"),
    "candle": ("candle", "candlestick", "candle holder", "candleholder", "candelabra", "lantern", "mum", "samdan",
               "kerze", "~kerzenhalter", "kaars", "bougie", "bougeoir", "vela", "candelabro", "candela", "ljus",
               "蜡烛", "蠟燭"),
    "basket": ("basket", "sepet", "korb", "mand", "panier", "cesta", "cesto", "canasta", "cestino", "korg", "bakul",
               "篮", "籃"),
    "tray": ("tray", "serving tray", "tepsi", "tablett", "dienblad", "plateau", "bandeja", "vassoio", "bricka",
             "托盘"),
    "clock": ("clock", "wall clock", "saat", "duvar saati", "uhr", "~wanduhr", "klok", "horloge", "pendule", "reloj",
              "orologio", "klocka", "钟", "鐘", "時計"),
    "floor_clock": ("grandfather clock", "floor clock", "longcase clock", "~standuhr", "staande klok",
                    "horloge comtoise", "reloj de pie", "orologio a pendolo"),
    "sculpture": ("sculpture", "statue", "statuette", "figurine", "bust", "heykel", "bust", "skulptur", "~statue",
                  "beeld", "beeldje", "escultura", "estatua", "scultura", "statua", "雕塑", "雕像"),
    "mirror": ("mirror", "ayna", "spiegel", "miroir", "espejo", "specchio", "spegel", "镜", "鏡"),
    "wall_art": ("wall art", "art print", "print", "canvas", "poster", "painting", "picture", "framed", "photo",
                 "photograph", "tablo",
                 "~wandbild", "bild", "schilderij", "tableau", "cuadro", "lamina", "quadro", "stampa", "tavla",
                 "画", "畫"),
    "vase": ("vase", "vazo", "vaas", "jarron", "florero", "vaso", "花瓶"),
    "bowl": ("bowl", "kase", "canak", "schale", "~schussel", "kom", "bol", "cuenco", "ciotola", "skal", "skål", "碗"),
    "window": ("window", "pencere", "fenster", "raam", "fenetre", "ventana", "finestra", "fonster", "fönster"),
    "towel": ("towel", "havlu", "handtuch", "handdoek", "serviette", "toalla", "asciugamano", "handduk"),
    "box": ("box", "kutu", "kiste", "doos", "boite", "caja", "scatola", "lada", "låda"),
    "animal": ("cat", "kitty", "dog", "puppy", "bird", "horse", "kedi", "kopek", "katze", "hund", "kat", "chat",
               "chien", "gato", "perro", "gatto", "cane"),
    "kitchenware": ("cutting board", "chopping board", "pan", "frying pan", "plate", "plates", "dish", "cup", "mug",
                    "teapot", "kettle", "bento", "kesme tahtasi", "tabla de cortar", "tagliere"),
    "furniture": ("furniture", "mobilya", "mobel", "moebel", "meubel", "meuble", "mueble", "mobili", "mobile",
                  "mobler", "möbler"),
    "room": ("room", "bathroom", "kitchen", "bedroom", "living room", "interior", "banyo", "mutfak", "oda",
             "badezimmer", "kuche", "badkamer", "keuken", "salle de bain", "cuisine", "bano", "bagno"),
}

# Flags: (category, words). A flag removes the model whatever its type (decide.py), except where noted.
FLAG_WORDS: dict[str, tuple[str, ...]] = {
    "outdoor": ("outdoor", "outdoors", "outside", "exterior", "garden", "gardens", "patio", "park", "park bench",
                "street", "street lamp", "streetlight", "street light", "lamppost", "lamp post", "city", "mainstreet",
                "public", "cemetery", "playground", "picnic", "camping", "bus stop", "bahce", "dis mekan",
                "sokak", "mezarlik", "garten", "aussen", "strasse", "friedhof", "tuin", "buiten", "straat", "jardin",
                "exterieur", "rue", "parc", "cimetiere", "calle", "parque", "cementerio", "giardino", "esterno",
                "strada", "parco", "cimitero", "cemiterio", "tradgard", "trädgård"),
    "crude": ("low poly", "lowpoly", "low polygon", "stylized", "stylised", "cartoon", "toon", "toy", "miniature",
              "test", "wip", "placeholder", "prototype", "voxel", "minecraft", "lego", "dollhouse", "doll house",
              "untextured", "unfinished"),
    "wrong": ("air bed", "airbed", "air mattress", "inflatable", "luchtbed", "~luftbett", "~luftmatratze",
              "matelas gonflable", "materasso gonfiabile", "colchon hinchable", "sisme yatak", "corpse", "cadaver",
              "dead body", "terrain", "hillfort", "linnamagi", "galvanometer"),
    "part": ("component", "sectional component", "spare part", "replacement part", "replacement"),
    "scene": ("scene", "diorama", "dining set", "table and chairs", "table chairs", "with chairs", "room set",
              "furniture set", "furniture pack", "props pack"),
}
# Phrases that cancel a flag word inside them (an indoor ceramic "garden stool"; "indoor outdoor" vases and rugs).
FLAG_EXCEPTIONS: dict[str, tuple[str, ...]] = {
    "outdoor": ("garden stool", "indoor", "king street"),
}

_CJK = re.compile(r"[⺀-鿿぀-ヿ가-힯]")
_CAMEL = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_SPECIAL = str.maketrans({"ı": "i", "ß": "ss", "ø": "o", "æ": "ae", "œ": "oe", "ł": "l", "đ": "d", "ð": "d",
                          "þ": "th"})


def fold(text: str) -> str:
    """Lowercase, accents stripped (Turkish ı, German ß too), camelCase split, every non-word character a space."""
    text = _CAMEL.sub(" ", str(text or ""))
    text = unicodedata.normalize("NFKD", text.lower().translate(_SPECIAL))
    text = "".join(c for c in text if not unicodedata.combining(c)).translate(_SPECIAL)
    text = re.sub(r"[_\W]+", " ", text, flags=re.UNICODE)
    text = re.sub(r"(?<=[a-z])(?=\d)|(?<=\d)(?=[a-z])", " ", text)
    return " ".join(text.split())


def tokens(text: str) -> list[str]:
    return fold(text).split()


def _token_eq(tok: str, word: str) -> bool:
    return tok == word or tok == word + "s" or tok == word + "es"


def _matches(toks: list[str], folded: str, keyword: str) -> list[tuple[int, int, int]]:
    """``(start, end, length)`` spans (token indices; CJK keywords: negative char spans) of one keyword."""
    if _CJK.search(keyword):
        out, start = [], folded.find(keyword)
        while start >= 0:
            out.append((-(start + 1) - 10_000, -(start + 1) - 10_000 + len(keyword), len(keyword) * 3))
            start = folded.find(keyword, start + 1)
        return out
    if keyword.startswith("~"):
        stem = fold(keyword[1:]).replace(" ", "")
        return [(i, i + 1, len(stem)) for i, t in enumerate(toks) if stem and stem in t]
    words = fold(keyword).split()
    n = len(words)
    if not n:
        return []
    return [(i, i + n, len(" ".join(words))) for i in range(len(toks) - n + 1)
            if all(_token_eq(toks[i + k], words[k]) for k in range(n))]


def _resolve(cands: list[tuple[int, int, int, str, str]]) -> list[tuple[int, int, int, str, str]]:
    """Longest keyword first; a match overlapping an accepted one is dropped. Deterministic order."""
    out: list = []
    taken: set = set()
    for c in sorted(cands, key=lambda c: (-c[2], c[0], c[3], c[4])):
        span = set(range(c[0], c[1]))
        if span & taken:
            continue
        taken |= span
        out.append(c)
    return sorted(out, key=lambda c: (c[0], c[3]))


def named_families(title: str) -> list[dict]:
    """The families a title names: ``[{"family", "word"}]`` in title order (overlaps resolved)."""
    toks, folded = tokens(title), fold(title)
    cands = []
    for fam, words in KEYWORDS.items():
        for w in words:
            for s, e, n in _matches(toks, folded, w):
                cands.append((s, e, n, fam, w))
    return [{"family": c[3], "word": c[4]} for c in _resolve(cands)]


def flags(title: str) -> dict[str, list[str]]:
    """``{category: [words]}`` of the flag words in a title (exceptions applied)."""
    toks, folded = tokens(title), fold(title)
    out: dict[str, list[str]] = {}
    for cat, words in FLAG_WORDS.items():
        cands = []
        for w in words:
            cands += [(s, e, n, cat, w) for s, e, n in _matches(toks, folded, w)]
        if not cands:
            continue
        ex = [m for x in FLAG_EXCEPTIONS.get(cat, ()) for m in _matches(toks, folded, x)]
        if cat == "outdoor" and ex:
            continue                     # "indoor" anywhere or an excepted phrase: not an outdoor piece
        found = [c[4] for c in _resolve(cands)]
        if found:
            out[cat] = sorted(set(found), key=found.index)
    return out


def near(a: str, b: str) -> bool:
    return a == b or any(a in g and b in g for g in NEAR_TYPES)


def title_check(title: Optional[str], ftype: str, source: str = "") -> dict:
    """What the title says about a model filed as ``ftype`` (a furniture type or a decor name):
    ``{"verdict": match | near | conflict | silent | generated, "families": [...], "named_types": [...],
    "flags": {category: [words]}, "words": [...]}``. ``room`` alone (a room named, no piece) is a conflict; a room
    word next to a piece word is ignored ("Living Room Chair")."""
    if source == "generated":
        return {"verdict": "generated", "families": [], "named_types": [], "flags": {}, "words": []}
    found = named_families(title or "")
    fams = [f["family"] for f in found]
    if "room" in fams and any(f != "room" for f in fams):
        found = [f for f in found if f["family"] != "room"]
    found = [f for f in found if f["family"] not in IGNORED_FAMILIES]
    fams = [f["family"] for f in found]
    named: list[str] = []
    for fam in fams:
        for t in FAMILY_TYPES.get(fam, ()):
            if t not in named:
                named.append(t)
    fl = flags(title or "")
    if not fams:
        verdict = "silent"
    elif any(ftype in FAMILY_TYPES.get(f, ()) for f in fams):
        verdict = "match"
    elif named and all(any(near(ftype, t) for t in FAMILY_TYPES.get(f, ())) or not FAMILY_TYPES.get(f)
                       for f in fams) and any(near(ftype, t) for t in named):
        verdict = "near"
    else:
        verdict = "conflict"
    return {"verdict": verdict, "families": fams, "named_types": named, "flags": fl,
            "words": [f["word"] for f in found]}


def suggested_type(check: dict, kind: str, known_types) -> Optional[str]:
    """The one type a conflicting title names (of the same kind: "Armoire ... avec miroir" names a wardrobe and a
    mirror, a tall cabinet can only become the wardrobe), or None when it names none or several."""
    if check.get("verdict") not in ("conflict", "near"):
        return None
    from wenart.furniture.catalog import DECOR_TYPES

    def same_kind(t: str) -> bool:
        return t in known_types and (t in DECOR_TYPES) == (kind == "decor")
    cands = [t for t in check.get("named_types") or [] if same_kind(t)]
    specific = [f for f in check.get("families") or [] if len(FAMILY_TYPES.get(f, ())) == 1]
    one = {FAMILY_TYPES[f][0] for f in specific if same_kind(FAMILY_TYPES[f][0])}
    if len(one) == 1:
        return next(iter(one))
    return cands[0] if len(cands) == 1 else None
