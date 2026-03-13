const CURRENCY_LABELS = {
  USD: '🇺🇸  USD  Dolar amerykański ($)',
  EUR: '🇪🇺  EUR  Euro (€)',
  GBP: '🇬🇧  GBP  Funt brytyjski (£)',
  CHF: '🇨🇭  CHF  Frank szwajcarski',
  CZK: '🇨🇿  CZK  Korona czeska',
  DKK: '🇩🇰  DKK  Korona duńska',
  NOK: '🇳🇴  NOK  Korona norweska',
  SEK: '🇸🇪  SEK  Korona szwedzka',
  JPY: '🇯🇵  JPY  Jen japoński (¥)',
  CAD: '🇨🇦  CAD  Dolar kanadyjski ($)',
};

export function getCurrencyLabel(code) {
  return CURRENCY_LABELS[code] || `${code}`;
}
