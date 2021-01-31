CREATE TABLE IF NOT EXISTS event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    link TEXT NOT NULL UNIQUE,
    date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pilot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstName TEXT,
    lastName TEXT DEFAULT "",
	UNIQUE(firstName, lastName)
);
CREATE TABLE IF NOT EXISTS card (
    setNumber TEXT NOT NULL,
    setName TEXT NOT NULL,
    name TEXT,
    cmc INTEGER,
    color TEXT,
    mana_cost TEXT,
    standardLegality TEXT,
    oracle_text TEXT,
    PRIMARY KEY(setNumber, setName)
);
CREATE TABLE IF NOT EXISTS deck (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    eventId INTEGER,
    pilotId INTEGER,
    deckUrl TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    rank TEXT,
    FOREIGN KEY (eventId) REFERENCES event(id),
    FOREIGN KEY (pilotId) REFERENCES pilot(id)
);
CREATE TABLE IF NOT EXISTS deckList (
    cardId TEXT,
    deckId INTEGER,
    count INTEGER,
    slot TEXT,
    cardName TEXT,
    FOREIGN KEY (deckId) REFERENCES deck(id)
);
