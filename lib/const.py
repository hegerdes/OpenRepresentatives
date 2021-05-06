import enum
import unicodedata
DB_RETRY = 3
COMMENT = '__COMMENT__'
DB_UPDATE_FREQUENCY = 172800
USE_REDIS = False

class Party(enum.Enum):
    CDU = 'CDU/CSU'
    CSU = 'CDU/CSU'
    SPD = 'SPD'
    GRUENEN = 'BÜNDNIS 90/DIE GRÜNEN'
    LINKE = 'DIE LINKE'
    FDP = 'FDP'
    AFD = 'AFD'
    DIEPARTEI=8

PARTY_ALIAS = {
    'CDU': unicodedata.normalize('NFKC',Party.CDU.value),
    'CHRISTLICH DEMOKRATISCHE UNION': unicodedata.normalize('NFKC',Party.CDU.value),
    'CHRISTLICH DEMOKRATISCHE UNION DEUTSCHLANDS': unicodedata.normalize('NFKC',Party.CDU.value),
    'SOZIALDEMOKRATISCHE PARTEI DEUTSCHLANDS': unicodedata.normalize('NFKC',Party.SPD.value),
    'SOZIALDEMOKRATISCHE PARTEI': unicodedata.normalize('NFKC',Party.SPD.value),
    'CHRISTLICH-SOZIALE UNION': unicodedata.normalize('NFKC',Party.CSU.value),
    'CHRISTLICH SOZIALE UNION': unicodedata.normalize('NFKC',Party.CSU.value),
    'BÜNDNIS 90/DIE GRÜNEN': unicodedata.normalize('NFKC',Party.GRUENEN.value),
    'BUENDNIS 90/DIE GRUENEN': unicodedata.normalize('NFKC',Party.GRUENEN.value),
    'DIE GRÜNEN': unicodedata.normalize('NFKC',Party.GRUENEN.value),
    'DIE GRUENEN': unicodedata.normalize('NFKC',Party.GRUENEN.value),
    'BUENDNIS 90': unicodedata.normalize('NFKC',Party.GRUENEN.value),
    'BÜNDNIS 90': unicodedata.normalize('NFKC',Party.GRUENEN.value),
    'GRUENEN': unicodedata.normalize('NFKC',Party.GRUENEN.value),
    'GRÜNEN': unicodedata.normalize('NFKC',Party.GRUENEN.value),
    'SPD': unicodedata.normalize('NFKC',Party.SPD.value),
    'CDU/CSU': unicodedata.normalize('NFKC',Party.CDU.value),
    'CSU/CDU': unicodedata.normalize('NFKC',Party.CDU.value),
    'CSU': unicodedata.normalize('NFKC',Party.CSU.value),
    'FDP': unicodedata.normalize('NFKC',Party.FDP.value),
    'AFD': unicodedata.normalize('NFKC',Party.AFD.value),
    'LINKE': unicodedata.normalize('NFKC',Party.LINKE.value),
    'DIE LINKE': unicodedata.normalize('NFKC',Party.LINKE.value),
    'DIE LINKEN': unicodedata.normalize('NFKC',Party.LINKE.value),
    'LINKEN': unicodedata.normalize('NFKC',Party.LINKE.value),
    'FREIE DEMOKRATISCHE PARTEI': unicodedata.normalize('NFKC',Party.FDP.value),
    'DIE FREIE DEMOKRATISCHE PARTEI': unicodedata.normalize('NFKC',Party.FDP.value),
    'ALTERNATIVE FÜR DEUTSCHLAND': unicodedata.normalize('NFKC',Party.AFD.value),
    'ALTERNATIVE FUER DEUTSCHLAND': unicodedata.normalize('NFKC',Party.AFD.value),
    'DIE ALTERNATIVE FÜR DEUTSCHLAND': unicodedata.normalize('NFKC',Party.AFD.value),
    'DIE ALTERNATIVE FUER DEUTSCHLAND': unicodedata.normalize('NFKC',Party.AFD.value),
}