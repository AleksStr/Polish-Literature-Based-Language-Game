import type {
  AnagramAnswerRequest,
  AnagramResponse,
  ChoiceRiddle,
  CrossoutAnswerRequest,
  CrossoutResponse,
  FillGapsAnswerRequest,
  FillGapsResponse,
  SpellcheckAnswerRequest,
  SpellcheckResponse,
  SwitchAnswerRequest,
  SwitchResponse,
} from './modelV2.ts';

export const BASE_TEXT = `Litwo, Ojczyzno moja! ty jesteś jak zdrowie;
Ile cię trzeba cenić, ten tylko się dowie,
Kto cię stracił. Dziś piękność twą w całej ozdobie
Widzę i opisuję, bo tęsknię po tobie.`;

// ======================================================
// ===============  GRA 1 – Fill (luki)  =================
// ======================================================

export const fillGapsMockResponse: FillGapsResponse = {
  gameId: 1001,
  riddle: {
    prompt: {
      parts: [
        { type: 'text', value: 'Litwo, ' },
        { type: 'gap', value: '' }, // Ojczyzno
        { type: 'text', value: ' moja! ty jesteś jak ' },
        { type: 'gap', value: '' }, // zdrowie
        { type: 'text', value: ';\n' },
        { type: 'text', value: 'Ile cię trzeba cenić, ten tylko się dowie,\n' },
        { type: 'text', value: 'Kto cię stracił. Dziś ' },
        { type: 'gap', value: '' }, // piękność
        { type: 'text', value: ' twą w całej ozdobie\n' },
        { type: 'text', value: 'Widzę i opisuję, bo tęsknię po tobie.' },
      ],
    },
    options: [
      { id: 'opt1', label: 'Ojczyzno' }, // poprawne do luki przy "Litwo,"
      { id: 'opt2', label: 'zdrowie' }, // poprawne do luki po "jak"
      { id: 'opt3', label: 'piękność' }, // poprawne do luki po "Dziś"
      // parę zmyłek:
      { id: 'opt4', label: 'dziewczyno' },
      { id: 'opt5', label: 'miasto' },
      { id: 'opt6', label: 'słodycz' },
    ],
  },
};
export const fillGapsMockAnswer: FillGapsAnswerRequest = {
  type: 'fill-gaps',
  gameId: 1001,
  answers: [
    { gapIndex: 1, optionId: 'opt1' }, // Ojczyzno
    { gapIndex: 3, optionId: 'opt2' }, // zdrowie
    { gapIndex: 7, optionId: 'opt3' }, // piękność
  ],
  elapsedTimeMs: 45000,
};

// ======================================================
// ===========  GRA 2 – Spellcheck (literówki)  =========
// ======================================================

export const spellcheckMockResponse: SpellcheckResponse = {
  gameId: 1002,
  riddle: {
    prompt: {
      words: [
        { id: 'w1', value: 'Litwo,' },
        { id: 'w2', value: 'Ojczyzno' },
        { id: 'w3', value: 'moja!' },
        { id: 'w4', value: 'ty' },
        { id: 'w5', value: 'jestęs' }, // błąd: powinno być "jesteś"
        { id: 'w6', value: 'jak' },
        { id: 'w7', value: 'zdrowei;' }, // błąd: powinno być "zdrowie;"
        { id: 'w8', value: 'Ile' },
        { id: 'w9', value: 'cię' },
        { id: 'w10', value: 'trzeba' },
        { id: 'w11', value: 'cenić,' },
        { id: 'w12', value: 'ten' },
        { id: 'w13', value: 'tylko' },
        { id: 'w14', value: 'się' },
        { id: 'w15', value: 'dowie,' },
        { id: 'w16', value: 'Kto' },
        { id: 'w17', value: 'cię' },
        { id: 'w18', value: 'stracił.' },
        { id: 'w19', value: 'Dziś' },
        { id: 'w20', value: 'piękność' },
        { id: 'w21', value: 'twą' },
        { id: 'w22', value: 'w' },
        { id: 'w23', value: 'całej' },
        { id: 'w24', value: 'ozdobie' },
        { id: 'w25', value: 'Widzę' },
        { id: 'w26', value: 'i' },
        { id: 'w27', value: 'opisuję,' },
        { id: 'w28', value: 'bo' },
        { id: 'w29', value: 'tęsknię' },
        { id: 'w30', value: 'po' },
        { id: 'w31', value: 'tobie.' },
      ],
    },
  },
};

export const spellcheckMockAnswer: SpellcheckAnswerRequest = {
  type: 'spellcheck',
  gameId: 1002,
  selectedWordIds: ['w5', 'w7'], // user kliknął dwa błędne słowa
  elapsedTimeMs: 3000,
};

// ======================================================
// ========  GRA 3 – Crossout (fałszywe linie)  =========
// ======================================================

export const crossoutMockResponse: CrossoutResponse = {
  gameId: 1003,
  riddle: {
    lines: [
      {
        id: '1',
        text: 'Litwo, Ojczyzno moja! ty jesteś jak zdrowie;',
      },
      {
        id: '2',
        text: 'Ile cię trzeba cenić, ten tylko się dowie,',
      },
      {
        id: '3',
        text: 'Kto cię stracił. Dziś piękność twą w całej ozdobie',
      },
      {
        id: '4',
        text: 'Widzę i opisuję, bo tęsknię po tobie.',
      },
      {
        id: '5',
        text: 'A jutro rano lecę sobie w Bieszczady.', // fałszywa linia
      },
    ],
  },
};

export const crossoutMockAnswer: CrossoutAnswerRequest = {
  type: 'crossout',
  gameId: 1003,
  crossedOutLineIds: '4',
  elapsedTimeMs: 45000,
};

// ======================================================
// =========  GRA 4 – Anagram (poprawianie słów)  =======
// ======================================================

export const anagramMockResponse: AnagramResponse = {
  gameId: 1004,
  riddle: {
    prompt: {
      words: [
        { id: 'w1', value: 'Litwo,' },
        { id: 'w2', value: 'oczjzynO' }, // anagram "Ojczyzno"
        { id: 'w3', value: 'moja!' },
        { id: 'w4', value: 'ty' },
        { id: 'w5', value: 'jesteś' },
        { id: 'w6', value: 'jak' },
        { id: 'w7', value: 'rodzwei;' }, // anagram "zdrowie;"
        { id: 'w8', value: 'Ile' },
        { id: 'w9', value: 'cię' },
        { id: 'w10', value: 'trzeba' },
        { id: 'w11', value: 'cenić,' },
        { id: 'w12', value: 'ten' },
        { id: 'w13', value: 'tylko' },
        { id: 'w14', value: 'się' },
        { id: 'w15', value: 'dowie,' },
        { id: 'w16', value: 'Kto' },
        { id: 'w17', value: 'cię' },
        { id: 'w18', value: 'stracił.' },
        { id: 'w19', value: 'Dziś' },
        { id: 'w20', value: 'piękność' },
        { id: 'w21', value: 'twą' },
        { id: 'w22', value: 'w' },
        { id: 'w23', value: 'całej' },
        { id: 'w24', value: 'ozdobie' },
        { id: 'w25', value: 'Widzę' },
        { id: 'w26', value: 'i' },
        { id: 'w27', value: 'opisuję,' },
        { id: 'w28', value: 'bo' },
        { id: 'w29', value: 'tęsknię' },
        { id: 'w30', value: 'po' },
        { id: 'w31', value: 'tobie.' },
      ],
    },
  },
};

export const anagramMockAnswer: AnagramAnswerRequest = {
  type: 'anagram',
  gameId: 1004,
  selectedWordIds: ['w2', 'w7'],
  elapsedTimeMs: 45000,
};

// ======================================================
// ========  GRA 5 – Switch (zamienione słowa)  =========
// ======================================================

export const switchMockResponse: SwitchResponse = {
  gameId: 1005,
  riddle: {
    prompt: {
      words: [
        { id: 'w1', value: 'Litwo,' },
        { id: 'w2', value: 'moja!' }, // zamienione miejsce
        { id: 'w3', value: 'Ojczyzno' }, // zamienione miejsce
        { id: 'w4', value: 'ty' },
        { id: 'w5', value: 'jesteś' },
        { id: 'w6', value: 'jak' },
        { id: 'w7', value: 'zdrowie;' },
        { id: 'w8', value: 'Ile' },
        { id: 'w9', value: 'cię' },
        { id: 'w10', value: 'trzeba' },
        { id: 'w11', value: 'cenić,' },
        { id: 'w12', value: 'ten' },
        { id: 'w13', value: 'tylko' },
        { id: 'w14', value: 'się' },
        { id: 'w15', value: 'dowie,' },
        { id: 'w16', value: 'Kto' },
        { id: 'w17', value: 'cię' },
        { id: 'w18', value: 'stracił.' },
        { id: 'w19', value: 'Dziś' },
        { id: 'w20', value: 'piękność' },
        { id: 'w21', value: 'twą' },
        { id: 'w22', value: 'w' },
        { id: 'w23', value: 'całej' },
        { id: 'w24', value: 'ozdobie' },
        { id: 'w25', value: 'Widzę' },
        { id: 'w26', value: 'i' },
        { id: 'w27', value: 'opisuję,' },
        { id: 'w28', value: 'bo' },
        { id: 'w29', value: 'tęsknię' },
        { id: 'w30', value: 'po' },
        { id: 'w31', value: 'tobie.' },
      ],
    },
  },
};

export const switchMockAnswer: SwitchAnswerRequest = {
  type: 'switch',
  gameId: 1005,
  selectedPairs: [
    { firstWordId: 'w2', secondWordId: 'w3' },
    { firstWordId: 'w20', secondWordId: 'w21' },
  ],
  elapsedTimeMs: 45000,
};

export const choiceMockRiddle: ChoiceRiddle = {
  id: 'choice-1',
  parts: [
    { type: 'text', value: 'Litwo! Ojczyzno moja! ty jesteś jak ' },
    { type: 'gap', gapId: 'g1' },
    { type: 'text', value: ';\n\nIle cię trzeba ' },
    { type: 'gap', gapId: 'g2' },
    { type: 'text', value: ', ten tylko się dowie,\n\nKto cię ' },
    { type: 'gap', gapId: 'g3' },
    { type: 'text', value: '. Dziś piękność twą w całej ozdobie\n\nW ' },
    { type: 'gap', gapId: 'g4' },
    { type: 'text', value: ' nazwach widzę i opisuję,\n\nBo tęskno mi za tobą i ' },
    { type: 'gap', gapId: 'g5' },
    { type: 'text', value: '.' },
  ],
  gaps: [
    {
      id: 'g1',
      correctOptionId: 'g1-opt1',
      options: [
        { id: 'g1-opt1', label: 'zdrowie' },
        { id: 'g1-opt2', label: 'bogactwo' },
        { id: 'g1-opt3', label: 'siła' },
      ],
    },
    {
      id: 'g2',
      correctOptionId: 'g2-opt1',
      options: [
        { id: 'g2-opt1', label: 'cenić' },
        { id: 'g2-opt2', label: 'szanować' },
        { id: 'g2-opt3', label: 'podziwiać' },
      ],
    },
    {
      id: 'g3',
      correctOptionId: 'g3-opt1',
      options: [
        { id: 'g3-opt1', label: 'stracił' },
        { id: 'g3-opt2', label: 'zapomniał' },
        { id: 'g3-opt3', label: 'opuścił' },
      ],
    },
    {
      id: 'g4',
      correctOptionId: 'g4-opt1',
      options: [
        { id: 'g4-opt1', label: 'polskich' },
        { id: 'g4-opt2', label: 'obcych' },
        { id: 'g4-opt3', label: 'dawnych' },
      ],
    },
    {
      id: 'g5',
      correctOptionId: 'g5-opt1',
      options: [
        { id: 'g5-opt1', label: 'płaczę' },
        { id: 'g5-opt2', label: 'śpiewam' },
        { id: 'g5-opt3', label: 'milczę' },
      ],
    },
  ],
};

export const choiceMockResponse = {
  gameId: 1005,
  riddle: choiceMockRiddle,
};
