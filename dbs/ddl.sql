

CREATE TABLE IF NOT EXISTS pilot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstName TEXT,
    lastName TEXT DEFAULT "",
	UNIQUE(firstName, lastName)
);
CREATE TABLE IF NOT EXISTS card (
    cardId INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    cmc INTEGER,
    color TEXT
);
CREATE TABLE IF NOT EXISTS deck (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    eventId INTEGER,
    pilotId INTEGER,
    deckUrl TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    rank INTEGER,
    FOREIGN KEY (eventId) REFERENCES event(id),
    FOREIGN KEY (pilotId) REFERENCES pilot(id)
);
CREATE TABLE IF NOT EXISTS deckList (
    cardId INTEGER,
    deckId INTEGER
    count INTEGER,
    slot TEXT,
    FOREIGN KEY (cardId) REFERENCES card(id),
    FOREIGN KEY (deckId) REFERENCES deck(id)
);
