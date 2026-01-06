// ===== Użytkownik / Książki =====

export interface BookRequest {
  userId: string;
}

export interface BookResponse {
  books: Book[];
}

export interface Book {
  id: number;
  title: string;
  author: string;
  year: number;
  genre: string;
  chapters: number;
  completedChapters: number;
}

export interface BookChapterResultsResponse {
  chapterName: string; // np. "Chapter 1 - Początek"
  chapters: number;
  completedChapters: number;
  score: number; // wynik w procentach (0–100), wyświetlany na froncie
  mistakes: number; // liczba błędów popełnionych w rozdziale
  time: string; // łączny czas w formacie mm:ss
}

// ===== Baza gier / Wynik =====

export type GameType = 'fill-gaps' | 'spellcheck' | 'crossout' | 'anagram' | 'switch' | 'choice';

export interface GameRequest {
  bookId: number;
  gameType: GameType;
  chapter: number;
}

export interface ResultRequest {
  gameId: number;
}

export interface ResultResponse {
  score: number; // końcowy wynik (np. w procentach)
  mistakes: number; // liczba błędnych odpowiedzi
  time: string; // czas gry w formacie mm:ss
  accuracy: number; // dokładność, np. 0.87
  pagesCompleted: number; // liczba ukończonych "stron" / ekranów
}

// ===== GRA 1 – Fill (uzupełnianie luk) =====

export interface FillGapsResponse {
  gameId: number;
  riddle: FillGapsRiddle;
}

export interface FillGapsRiddle {
  prompt: {
    parts: FillGapsRiddlePart[];
  };
  options: RiddleOption[];
}

export interface RiddleOption {
  id: string;
  label: string; // tekst opcji, wyświetlany użytkownikowi
}

export interface FillGapsRiddlePart {
  type: 'gap' | 'text';
  value: string;
  // dla "text" – zwykły fragment tekstu (np. "Litwo, ")
  // dla "gap"  – miejsce, w które użytkownik wstawia wybraną opcję
}

// ===== Wspólne struktury tekstu dla Spellcheck / Anagram / Switch =====

/**
 * Tekst gry reprezentowany jako sekwencja słów.
 * Backend:
 *  - dzieli fragment książki na słowa,
 *  - nadaje im unikalne ID,
 *  - ewentualnie modyfikuje słowa (literówki, anagramy, zamiany kolejności).
 * Front:
 *  - renderuje words w podanej kolejności,
 *  - operuje na id słów (kliknięcia, edycje itp.).
 */
export interface GameText {
  words: RiddleWord[];
}

/**
 * Pojedyncze słowo w tekście gry.
 * value może zawierać:
 *  - zwykłe słowo (poprawne),
 *  - słowo z błędem (Spellcheck),
 *  - anagram (Anagram),
 *  - słowo w złym miejscu (Switch),
 *  - ewentualnie interpunkcję przyklejoną do słowa (np. "Litwo,").
 */
export interface RiddleWord {
  id: string; // unikalne ID słowa, używane w odpowiedziach
  value: string; // tekst słowa, np. "Litwo,", "Ojczyzno", "moaj"
}

// ===== GRA 2 – Spellcheck =====
// Litery w wybranych słowach są zamienione miejscami.
// Użytkownik klika słowa, które uważa za zapisane niepoprawnie.

export interface SpellcheckResponse {
  gameId: number;
  riddle: SpellcheckRiddle;
}

export interface SpellcheckRiddle {
  prompt: GameText;
  // Backend przechowuje informację, które słowa są błędne – front jej nie zna.
}

// ===== GRA 3 – Crossout =====
// Do tekstu dodawane są dodatkowe (fałszywe) linie.
// Użytkownik klika linie, które powinny zostać "przekreślone".

export interface CrossoutResponse {
  gameId: number;
  riddle: CrossoutRiddle;
}

export interface CrossoutRiddle {
  lines: CrossoutLine[];
}

export interface CrossoutLine {
  id: string; // ID linii, wykorzystywane przy kliknięciu i w odpowiedziach
  text: string; // pełny tekst linii (może zawierać interpunkcję itp.)
}

// ===== GRA 4 – Anagram =====
// Wybrane słowa są zapisane jako anagramy.
// Użytkownik powinien przywrócić poprawną formę słowa.

export interface AnagramResponse {
  gameId: number;
  riddle: AnagramRiddle;
}

export interface AnagramRiddle {
  prompt: GameText;
  // Backend wie, które słowa są anagramami i jak brzmi ich poprawna forma.
}

// ===== GRA 5 – Switch =====
// Dwie sąsiadujące ze sobą wyrazy są zamienione miejscami.
// Użytkownik musi wskazać słowa należące do błędnych par.

export interface SwitchResponse {
  gameId: number;
  riddle: SwitchRiddle;
  // Backend wie, które słowa są zamienione
}

export interface SwitchRiddle {
  prompt: GameText;
}

// =====================================================================
// ======================  REQUESTY Z ODPOWIEDZIAMI  ====================
// =====================================================================

/**
 * Ogólny typ requestu wysyłanego po zakończeniu gry.
 * Można wystawić pojedynczy endpoint, np.:
 * gdzie backend wykonuje switch po polu `type`.
 */
export type GameAnswerRequest =
  | FillGapsAnswerRequest
  | SpellcheckAnswerRequest
  | CrossoutAnswerRequest
  | AnagramAnswerRequest
  | SwitchAnswerRequest;

// ===== GRA 1 – Fill (uzupełnianie luk) – odpowiedzi =====

export interface FillGapsAnswerRequest {
  type: 'fill-gaps';
  gameId: number;
  answers: FillGapAnswer[];
  elapsedTimeMs?: number; //  czas trwania gry w milisekundach
}

export interface FillGapAnswer {
  gapIndex: number; // indeks w riddle.prompt.parts odpowiadający konkretnej luce
  optionId: string; // id wybranej opcji (RiddleOption.id)
}

// ===== GRA 2 – Spellcheck – odpowiedzi =====
// Użytkownik zaznacza słowa, które uważa za błędne.

export interface SpellcheckAnswerRequest {
  type: 'spellcheck';
  gameId: number;
  selectedWordIds: string[]; // lista id słów (RiddleWord.id), które użytkownik kliknął
  elapsedTimeMs?: number;
}

// ===== GRA 3 – Crossout – odpowiedzi =====
// Użytkownik zaznacza linie, które uznaje za "fałszywe"/dodatkowe.

export interface CrossoutAnswerRequest {
  type: 'crossout';
  gameId: number;
  crossedOutLineIds: string; // id linii (CrossoutLine.id), które użytkownik przekreślił
  elapsedTimeMs?: number;
}

// ===== GRA 4 – Anagram – odpowiedzi =====
// Użytkownik wybiera słowa którę są błędne

export interface AnagramAnswerRequest {
  type: 'anagram';
  gameId: number;
  selectedWordIds: string[];
  elapsedTimeMs?: number;
}

// ===== GRA 5 – Switch – odpowiedzi =====
// Użytkownik zaznacza słowa należące do zamienionych par.

export interface SelectedSwitchPair {
  firstWordId: string;
  secondWordId: string;
}

export interface SwitchAnswerRequest {
  type: 'switch';
  gameId: number;
  selectedPairs: SelectedSwitchPair[]; // lista par wskazanych przez użytkownika
  elapsedTimeMs?: number;
}

export interface ChoiceOption {
  id: string;
  label: string;
}

export interface ChoiceGap {
  id: string;
  correctOptionId: string;
  options: ChoiceOption[];
}

export interface ChoiceRiddle {
  id: string;
  parts: Array<{ type: 'text'; value: string } | { type: 'gap'; gapId: string }>;
  gaps: ChoiceGap[];
}
