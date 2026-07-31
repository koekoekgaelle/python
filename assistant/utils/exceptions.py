#Fouten rondom spelers
class PlayerError(Exception):
    """Basisklasse voor fouten rond spelers."""

class InvalidPlayerNameError(PlayerError):
    """De opgegeven spelersnaam is ongeldig."""

class PlayerNotFoundError(PlayerError):
    """Deze speler bestaat niet in de huidige spelsessie"""

class PlayerAddError(PlayerError):
    """De speler kon niet worden toegevoegd."""

class ScoreUpdateError(PlayerError):
    """De score kon niet worden bijgewerkt."""

class PlayerLoadError(PlayerError):
    """Spelers konden niet worden opgehaald."""

#Fouten rondom chunks
class DocumentError(Exception):
    """Basisklasse voor fouten rond documenten."""

class LengthChunkError(DocumentError):
    """Aantal chunks komt niet overeen met aantal embeddings."""

class InvalidBatchSizeError(DocumentError):
    """Batch size moet minimaal 1 zijn."""

class InvalidQueryEmbeddingError(DocumentError):
    """Query embedding mag niet leeg zijn"""

class InvalidMatchCountError(DocumentError):
    """Match count moet minimaal 1 zijn."""

class InvalidContentError(DocumentError):
    """Er kon geen tekst uit de PDF worden gehaald."""

class ChunkCreationError(DocumentError):
    """Er konden geen chunkd gemaakt worden van dit PDF bestand."""

#Fouten rondom handleidingen
class RulebookError(Exception):
    """Basisklasse voor fouten rond handleidingen"""

class RulebookCreationError(RulebookError):
    """De handleiding kon niet worden toegevoegd."""

#Fouten rondom spellen.
class GameError(Exception):
    """Basisklasse voor fouten rond spellen."""

class GameCreationError(GameError):
    """Het spel kon niet worden toegevoegd."""

class SessionCreationError(GameError):
    """De spelsessie kon niet worden aangemaakt."""

class GameLoadError(GameError):
    """Spellen konden niet worden opgehaald."""

#Fouten rondom Supabase
class SupabaseError(Exception):
    """Basisklasse voor fouten rondom supabase."""

class SupabaseUrlError(SupabaseError):
    """SUPABASE_URL ontbreekt in het .env-bestand."""

class SupabaseKeyError(SupabaseError):
   """SUPABASE_SECRET_KEY ontbreekt in het .env-bestand."""


#Fouten rondom vragen.
class QuestionError(Exception):
    """Basisklasse voor fouten rond vragen."""


class EmptyQuestionError(QuestionError):
    """De vraag mag niet leeg zijn."""


#Fouten rondom antwoorden
class AnswerError(Exception):
    """Basisklasse voor fouten rond antwoorden."""

class ResultAnswerQuestionError(AnswerError):
    """answer_question gaf geen resultaat terug."""

class NoAnswerError(AnswerError):
    """De assistent gaf geen antwoord terug."""


#Algemene fouten
class GeneralError(Exception):
    """Basis klasse voor algemene fouten."""

class InvalidDataError(GeneralError):
    """Ongeldige gegevens ontvangen."""

class ServerConnectionError(GeneralError):
    """Kan geen verbinding maken met de server. Controleer internet verbinding."""