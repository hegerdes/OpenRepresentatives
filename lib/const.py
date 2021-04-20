import enum
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
    'CDU': Party.CDU.value,
    'CHRISTLICH DEMOKRATISCHE UNION': Party.CDU.value,
    'CHRISTLICH DEMOKRATISCHE UNION DEUTSCHLANDS': Party.CDU.value,
    'SOZIALDEMOKRATISCHE PARTEI DEUTSCHLANDS': Party.SPD.value,
    'SOZIALDEMOKRATISCHE PARTEI': Party.SPD.value,
    'CHRISTLICH-SOZIALE UNION': Party.CSU.value,
    'CHRISTLICH SOZIALE UNION': Party.CSU.value,
    'BÜNDNIS 90/DIE GRÜNEN': Party.GRUENEN.value,
    'BUENDNIS 90/DIE GRUENEN': Party.GRUENEN.value,
    'DIE GRÜNEN': Party.GRUENEN.value,
    'DIE GRUENEN': Party.GRUENEN.value,
    'BUENDNIS 90': Party.GRUENEN.value,
    'BÜNDNIS 90': Party.GRUENEN.value,
    'GRUENEN': Party.GRUENEN.value,
    'GRÜNEN': Party.GRUENEN.value,
    'SPD': Party.SPD.value,
    'CDU/CSU': Party.CDU.value,
    'CSU/CDU': Party.CDU.value,
    'CSU': Party.CSU.value,
    'FDP': Party.FDP.value,
    'AFD': Party.AFD.value,
    'LINKE': Party.LINKE.value,
    'DIE LINKE': Party.LINKE.value,
    'DIE LINKEN': Party.LINKE.value,
    'LINKEN': Party.LINKE.value,
    'FREIE DEMOKRATISCHE PARTEI': Party.FDP.value,
    'DIE FREIE DEMOKRATISCHE PARTEI': Party.FDP.value,
    'ALTERNATIVE FÜR DEUTSCHLAND': Party.AFD.value,
    'ALTERNATIVE FUER DEUTSCHLAND': Party.AFD.value,
    'DIE ALTERNATIVE FÜR DEUTSCHLAND': Party.AFD.value,
    'DIE ALTERNATIVE FUER DEUTSCHLAND': Party.AFD.value,
}