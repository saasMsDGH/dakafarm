import Swal from 'sweetalert2';
import i18n from '../i18n';

// Exact match translation dictionary for English to natural Swahili
export const swahiliTranslations = {
  // Titles
  'error': 'Hitilafu',
  'error!': 'Hitilafu!',
  'success': 'Imefanikiwa',
  'success!': 'Imefanikiwa!',
  'warning': 'Onyo',
  'warning!': 'Onyo!',
  'are you sure?': 'Una uhakika?',
  'deleted!': 'Imefutwa!',
  'updated!': 'Imesasishwa!',
  'saved!': 'Imehifadhiwa!',
  'info': 'Taarifa',
  'notice': 'Taarifa',

  // Buttons & Confirmations
  "you won't be able to revert this!": "Hutaweza kurudisha nyuma kitendo hiki!",
  "are you sure you want to delete this?": "Una uhakika unataka kufuta hii?",
  'yes, delete it!': 'Ndio, futa!',
  'cancel': 'Ghairi',
  'ok': 'Sawa',
  'yes': 'Ndio',
  'no': 'Hapana',
  'confirm': 'Thibitisha',
  'close': 'Funga',

  // POS & Sales / Purchases
  'cart is empty!': 'Kikapu kiko tupu!',
  'select a customer!': 'Tafadhali chagua mteja!',
  'select a supplier!': 'Tafadhali chagua muuzaji!',
  'out of stock!': 'Bidhaa imekwisha ghalani!',
  'cannot exceed current stock limit.': 'Huwezi kuzidi idadi iliyopo ghalani.',
  'please select a payment account for the amount paid.': 'Tafadhali chagua Akaunti ya Malipo kwa kiasi kilicholipwa.',
  'please select a payment account.': 'Tafadhali chagua Akaunti ya Malipo.',
  'please select a financial account for the upfront payment.': 'Tafadhali chagua Akaunti ya Fedha kwa malipo ya awali.',
  'please select a financial account for this payment.': 'Tafadhali chagua Akaunti ya Fedha kwa malipo haya.',
  'please select a financial account': 'Tafadhali chagua Akaunti ya Fedha.',
  'please select a financial account.': 'Tafadhali chagua Akaunti ya Fedha.',
  'payment amount must be greater than zero.': 'Kiasi cha malipo lazima kiwe zaidi ya sifuri.',
  'sale created successfully!': 'Mauzo yamekamilika kikamilifu!',
  'sale created successfully': 'Mauzo yamekamilika kikamilifu',
  'purchase created successfully!': 'Manunuzi yamekamilika kikamilifu!',
  'purchase created successfully': 'Manunuzi yamekamilika kikamilifu',
  'payment recorded successfully!': 'Malipo yamerekodiwa kikamilifu!',
  'payment recorded successfully': 'Malipo yamerekodiwa kikamilifu',
  'product created successfully': 'Bidhaa imeongezwa kikamilifu',

  // Users & Auth
  'user created successfully': 'Mtumiaji ameongezwa kikamilifu',
  'user updated successfully': 'Mtumiaji amesasishwa kikamilifu',
  'password must be at least 6 characters long.': 'Nenosiri lazima liwe na angalau herufi 6.',
  'password changed successfully': 'Nenosiri limebadilishwa kikamilifu',
  'password updated successfully': 'Nenosiri limesasishwa kikamilifu',
  'profile updated successfully!': 'Wasifu umesasishwa kikamilifu!',
  'failed to login. Please try again.': 'Imeshindwa kuingia. Tafadhali jaribu tena.',
  'failed to login': 'Imeshindwa kuingia',
  'incorrect username or password': 'Jina la mtumiaji au nenosiri si sahihi',
  'user inactive': 'Mtumiaji huyu amesimamishwa',
  'user not found.': 'Mtumiaji hajapatikana.',
  'user not found': 'Mtumiaji hajapatikana',
  'not enough permissions': 'Huna ruhusa ya kutosha kufanya kitendo hiki',
  'could not validate credentials': 'Imeshindwa kuthibitisha kitambulisho',
  'only admins can change active status.': 'Wasimamizi (Admins) pekee ndio wanaoweza kubadilisha hali ya mtumiaji.',
  'password mpya imefanana na yazamani': 'Nenosiri jipya linafanana na la zamani.',
  'email already registered': 'Barua pepe hii imeshajisajiliwa tayari',
  'username already registered': 'Jina hili la mtumiaji limeshajisajiliwa tayari',
  'phone number already registered': 'Namba hii ya simu imeshajisajiliwa tayari',

  // Customers & Suppliers
  'customer updated successfully': 'Mteja amesasishwa kikamilifu',
  'customer added successfully': 'Mteja ameongezwa kikamilifu',
  'customer has been deleted.': 'Mteja amefutwa kikamilifu.',
  'supplier updated successfully': 'Muuzaji amesasishwa kikamilifu',
  'supplier added successfully': 'Muuzaji ameongezwa kikamilifu',
  'supplier has been deleted.': 'Muuzaji amefutwa kikamilifu.',
  'customer not found.': 'Mteja hajapatikana.',
  'customer not found': 'Mteja hajapatikana',
  'supplier not found.': 'Muuzaji hajapatikana.',
  'supplier not found': 'Muuzaji hajapatikana',
  'failed to delete customer. they might be linked to sales.': 'Imeshindwa kufuta mteja. Huenda ameunganishwa na mauzo.',
  'failed to delete supplier. they might be linked to sales.': 'Imeshindwa kufuta muuzaji. Huenda ameunganishwa na manunuzi au gharama.',

  // Expenses & Accounts
  'expense updated successfully': 'Matumizi yamesasishwa kikamilifu',
  'expense added successfully': 'Matumizi yameongezwa kikamilifu',
  'expense has been deleted.': 'Matumizi yamefutwa kikamilifu.',
  'expense not found.': 'Matumizi hayajapatikana.',
  'expense not found': 'Matumizi hayajapatikana',
  'expense is already fully paid.': 'Gharama hii imeshalipwa kikamilifu.',
  'purchase not found.': 'Manunuzi hayajapatikana.',
  'purchase not found': 'Manunuzi hayajapatikana',
  'purchase is already fully paid.': 'Manunuzi haya yameshalipwa kikamilifu.',
  'sale not found.': 'Mauzo hayajapatikana.',
  'sale not found': 'Mauzo hayajapatikana',
  'sale is already fully paid.': 'Mauzo haya yameshalipwa kikamilifu.',
  'financial account not found.': 'Akaunti ya fedha haijapatikana.',
  'financial account not found': 'Akaunti ya fedha haijapatikana',
  'financial account updated successfully': 'Akaunti ya fedha imesasishwa kikamilifu',
  'financial account created successfully': 'Akaunti ya fedha imetengenezwa kikamilifu',
  'amount paid cannot exceed total amount.': 'Kiasi kilicholipwa hakiwezi kuzidi jumla ya fedha.',
  'amount paid cannot exceed total cost.': 'Kiasi kilicholipwa hakiwezi kuzidi jumla ya gharama.',
  'payment method is required if amount is paid.': 'Njia ya malipo inahitajika ikiwa kiasi kitalipwa.',
  'account_id is required if amount is paid.': 'Akaunti ya fedha inahitajika ikiwa kiasi kitalipwa.',
  'failed to delete expense. they might be linked to sales.': 'Imeshindwa kufuta matumizi.',

  // Inventory & Items
  'the category has been updated.': 'Kundi la bidhaa limesasishwa.',
  'the category has been added.': 'Kundi la bidhaa limeongezwa.',
  'the category has been deleted.': 'Kundi la bidhaa limefutwa.',
  'the product has been updated.': 'Bidhaa imesasishwa.',
  'the product has been added.': 'Bidhaa imeongezwa.',
  'the product has been deleted.': 'Bidhaa imefutwa.',
  'the stock movement has been recorded.': 'Mwenendo wa bidhaa umerekodiwa.',

  // Farm Records
  'the flock has been deleted.': 'Kundi la ndege limefutwa.',
  'the house has been deleted.': 'Banda limefutwa.',
  'the record has been updated.': 'Kumbukumbu imesasishwa.',
  'the record has been added.': 'Kumbukumbu imeongezwa.',
  'the record has been deleted.': 'Kumbukumbu imefutwa.',
  'added successfully': 'Imeongezwa kikamilifu',
  'updated successfully': 'Imesasishwa kikamilifu',
  'saved successfully!': 'Imehifadhiwa kikamilifu!',
  'saved successfully': 'Imehifadhiwa kikamilifu',
  'please fill all required fields': 'Tafadhali jaza sehemu zote zinazohitajika',
  'please provide a custom status': 'Tafadhali weka hali maalum',

  // Assets
  'asset updated successfully': 'Mali imesasishwa kikamilifu',
  'asset added successfully and payment recorded in finance': 'Mali imeongezwa kikamilifu na malipo yamerekodiwa kwenye fedha',
  'asset payment successfully recorded and tracked in finance!': 'Malipo ya mali yamerekodiwa na kufuatiliwa kwenye fedha!',
  'asset distributed successfully': 'Mali imegawiwa kikamilifu',
  'asset has been deleted.': 'Mali imefutwa kikamilifu.',

  // HR & Payroll
  'payroll updated successfully': 'Mishahara imesasishwa kikamilifu',
  'payroll added successfully': 'Mishahara imeongezwa kikamilifu',
  'submission failed': 'Imeshindwa kuwasilisha',
  'payment failed': 'Malipo yameshindwa',
  'deletion failed': 'Kufuta kumeshindwa',

  // Common Failures / Load Errors
  'failed to load sales': 'Imeshindwa kupakia taarifa za mauzo',
  'failed to load purchases': 'Imeshindwa kupakia taarifa za manunuzi',
  'failed to load expenses': 'Imeshindwa kupakia taarifa za matumizi',
  'failed to load customers': 'Imeshindwa kupakia orodha ya wateja',
  'failed to load suppliers': 'Imeshindwa kupakia orodha ya wasambazaji',
  'failed to load assets': 'Imeshindwa kupakia orodha ya mali',
  'failed to load financial accounts': 'Imeshindwa kupakia akaunti za fedha',
  'failed to load general ledger transactions.': 'Imeshindwa kupakia miamala ya leja kuu.',
  'failed to fetch users': 'Imeshindwa kupata watumiaji',
  'failed to fetch details.': 'Imeshindwa kupata maelezo.',
  'failed to fetch details': 'Imeshindwa kupata maelezo',
  'failed to fetch sale details': 'Imeshindwa kupata taarifa za mauzo',
  'failed to fetch purchase details': 'Imeshindwa kupata taarifa za manunuzi',
  'failed to fetch expense details': 'Imeshindwa kupata taarifa za matumizi',
  'failed to fetch asset details': 'Imeshindwa kupata taarifa za mali',
  'failed to fetch book data.': 'Imeshindwa kupata taarifa za daftari la hesabu.',
  'failed to save customer': 'Imeshindwa kuhifadhi mteja',
  'failed to save supplier': 'Imeshindwa kuhifadhi muuzaji',
  'failed to save expense': 'Imeshindwa kuhifadhi matumizi',
  'failed to save account': 'Imeshindwa kuhifadhi akaunti ya fedha',
  'failed to save': 'Imeshindwa kuhifadhi',
  'failed to create sale': 'Imeshindwa kutengeneza mauzo',
  'failed to create purchase': 'Imeshindwa kutengeneza manunuzi',
  'failed to create product': 'Imeshindwa kuongeza bidhaa',
  'failed to create user': 'Imeshindwa kuongeza mtumiaji',
  'failed to update user': 'Imeshindwa kusasisha mtumiaji',
  'failed to change password': 'Imeshindwa kubadilisha nenosiri',
  'failed to update user status': 'Imeshindwa kubadilisha hali ya mtumiaji',
  'failed to change account status': 'Imeshindwa kubadilisha hali ya akaunti',
  'failed to generate financial reports.': 'Imeshindwa kutoa ripoti za fedha.',
  'failed to generate report.': 'Imeshindwa kutoa ripoti.',
  'some dashboard data could not be loaded.': 'Baadhi ya taarifa za dashibodi zimeshindwa kupakia.',
  'you do not have permission to view this report.': 'Huna ruhusa ya kutazama ripoti hii.',
  'internal server error': 'Hitilafu ya ndani ya seva. Tafadhali jaribu tena baadaye.',

  // Specific Backend Constraints & Validation Messages
  'a category with this name already exists.': 'Kundi la bidhaa lenye jina hili tayari lipo.',
  'a customer with this code already exists.': 'Mteja mwenye namba hii ya utambulisho tayari yupo.',
  'a flock with this code already exists or there is a database constraint error.': 'Kundi la ndege lenye namba hii tayari lipo au kuna mgongano wa data.',
  'a flock with this flock_code already exists.': 'Kundi la ndege lenye namba hii tayari lipo.',
  'a house with this name already exists.': 'Banda lenye jina hili tayari lipo.',
  'a product with this name already exists or category is invalid.': 'Bidhaa yenye jina hili tayari ipo au kundi si sahihi.',
  'a supplier with this code already exists.': 'Muuzaji mwenye namba hii ya utambulisho tayari yupo.',
  'account_id is required if amount_paid > 0': 'Akaunti ya fedha inahitajika ikiwa kiasi kilicholipwa ni zaidi ya sifuri.',
  'amount paid cannot exceed expense amount.': 'Kiasi kilicholipwa hakiwezi kuzidi gharama.',
  'amount paid cannot exceed net salary.': 'Kiasi kilicholipwa hakiwezi kuzidi mshahara halisi.',
  'an account with this name might already exist.': 'Akaunti yenye jina hili huenda tayari ipo.',
  'an asset with this code might already exist.': 'Mali yenye namba hii huenda tayari ipo.',
  'an employee with this code already exists.': 'Mfanyakazi mwenye namba hii tayari yupo.',
  'an expense with this number already exists.': 'Matumizi yenye namba hii tayari yapo.',
  'asset is already fully paid.': 'Mali hii imeshalipwa kikamilifu.',
  'asset not found.': 'Mali haijapatikana.',
  'cannot delete a house that contains active flocks.': 'Huwezi kufuta banda lenye makundi hai ya ndege.',
  'cannot delete an expense that has payments recorded. this breaks the financial audit trail.': 'Huwezi kufuta matumizi yenye malipo yaliyorekodiwa.',
  'cannot delete asset because it is referenced elsewhere.': 'Huwezi kufuta mali hii kwa sababu inatumika mahali pengine.',
  'cannot delete customer because they are referenced by existing transactions (e.g. sales).': 'Huwezi kufuta mteja huyu kwa sababu anahusika kwenye mauzo au miamala iliyopo.',
  'cannot delete employee because they are referenced by other records.': 'Huwezi kufuta mfanyakazi huyu kwa sababu anahusika kwenye kumbukumbu zilizopo.',
  'cannot delete payroll record.': 'Huwezi kufuta kumbukumbu hii ya mshahara.',
  'cannot delete product because it is referenced by stock transactions.': 'Huwezi kufuta bidhaa hii kwa sababu inatumika kwenye mienendo ya stoo.',
  'cannot delete supplier because they are referenced by existing purchases.': 'Huwezi kufuta muuzaji huyu kwa sababu anahusika kwenye manunuzi yaliyopo.',
  'cannot increase mortality beyond the current flock size.': 'Idadi ya vifo haiwezi kuzidi idadi ya ndege waliopo katika kundi.',
  'conflicts: data already exists': 'Mgongano: taarifa hizi tayari zipo kwenye mfumo.',
  'could not save transaction due to a data integrity error.': 'Imeshindwa kuhifadhi muamala kutokana na hitilafu ya data.',
  'damaged eggs cannot exceed total eggs collected.': 'Mayai yaliyoharibika hayawezi kuzidi jumla ya mayai yaliyokusanywa.',
  'database transaction failed': 'Muamala wa hifadhidata umeshindikana.',
  'inactive user': 'Mtumiaji huyu hajaruhusiwa kutumia mfumo.',
  'incorrect password or username': 'Nenosiri au jina la mtumiaji si sahihi.',
  'integrity error creating payroll record. ensure employee exists.': 'Hitilafu katika kutengeneza rekodi ya mshahara. Hakikisha mfanyakazi yupo.',
  'integrity error updating account.': 'Hitilafu wakati wa kusasisha akaunti.',
  'integrity error updating asset.': 'Hitilafu wakati wa kusasisha mali.',
  'integrity error updating customer.': 'Hitilafu wakati wa kusasisha mteja.',
  'integrity error updating employee.': 'Hitilafu wakati wa kusasisha mfanyakazi.',
  'integrity error updating expense.': 'Hitilafu wakati wa kusasisha matumizi.',
  'integrity error updating payroll.': 'Hitilafu wakati wa kusasisha mshahara.',
  'integrity error updating supplier.': 'Hitilafu wakati wa kusasisha muuzaji.',
  'invalid old password.': 'Nenosiri la zamani si sahihi.',
  'old_password is required to change your password.': 'Nenosiri la zamani linahitajika ili kubadilisha nenosiri.',
  'only admins can change roles.': 'Wasimamizi (Admins) pekee ndio wanaoweza kubadilisha madaraka.',
  'payroll is already fully paid.': 'Mshahara huu umeshalipwa kikamilifu.',
  'payroll not found.': 'Taarifa ya mshahara haijapatikana.',
  'product with that id not found': 'Bidhaa yenye namba hiyo haijapatikana.',
  'product with that name already exist': 'Bidhaa yenye jina hilo tayari ipo.',
  'product_id is strictly required for feed records.': 'Bidhaa inahitajika kwa kumbukumbu za chakula.',
  'product_id is strictly required for medication records.': 'Bidhaa inahitajika kwa kumbukumbu za dawa.',
  'product_id is strictly required for vaccination records.': 'Bidhaa inahitajika kwa kumbukumbu za chanjo.',
  'update failed: data conflict (email might be in use).': 'Kusasisha kumeshindwa: Mgongano wa data (huenda barua pepe inatumika).',
  'user account is inactive. please contact administrator.': 'Akaunti ya mtumiaji imesimamishwa. Tafadhali wasiliana na msimamizi.',
  'you do not have permission to delete this user.': 'Huna ruhusa ya kumfuta mtumiaji huyu.',
  'you do not have permission to perform this action.': 'Huna ruhusa ya kufanya kitendo hiki.',
  'you do not have permission to reset this user': 'Huna ruhusa ya kuweka upya mtumiaji huyu.',
  'you do not have permission to update this user.': 'Huna ruhusa ya kumsasisha mtumiaji huyu.'
};

// Patterns for dynamic strings
const dynamicPatterns = [
  {
    regex: /^not enough stock!\s*only\s+(\d+)\s+available\.?$/i,
    replace: (_, count) => `Hakuna akiba ya kutosha! Zilizopo ni ${count} pekee.`
  },
  {
    regex: /^only\s+(\d+)\s+in stock!?$/i,
    replace: (_, count) => `Zilizopo ghalani ni ${count} pekee!`
  },
  {
    regex: /^payment amount\s*\(([^)]+)\)\s*cannot exceed remaining balance of\s*([^.]+)\.?$/i,
    replace: (_, amt, bal) => `Kiasi cha malipo (${amt}) hakiwezi kuzidi salio lililobaki la ${bal}.`
  },
  {
    regex: /^amount paid\s*\(([^)]+)\)\s*cannot exceed total cost\s*\(([^)]+)\)\.?$/i,
    replace: (_, amt, cost) => `Kiasi kilicholipwa (${amt}) hakiwezi kuzidi jumla ya gharama (${cost}).`
  },
  {
    regex: /^payment amount exceeds remaining balance of\s*([^.]+)\.?$/i,
    replace: (_, bal) => `Kiasi cha malipo kinazidi salio lililobaki la ${bal}.`
  },
  {
    regex: /^product with id\s+(\d+)\s+not found\.?$/i,
    replace: (_, id) => `Bidhaa yenye namba ${id} haijapatikana.`
  },
  {
    regex: /^user\s+(\w+)\s+successfully\.?$/i,
    replace: (_, action) => `Mtumiaji ${action.toLowerCase() === 'activated' ? 'amewashwa' : 'amesimamishwa'} kikamilifu.`
  },
  {
    regex: /^account marked as\s+(active|inactive)$/i,
    replace: (_, status) => `Akaunti imewekwa kuwa ${status.toLowerCase() === 'active' ? 'Inafanya Kazi' : 'Haifanyi Kazi'}.`
  },
  {
    regex: /^transaction failed:\s*(.*)$/i,
    replace: (_, msg) => `Muamala umeshindwa: ${translateToSwahili(msg)}`
  },
  {
    regex: /^commit failed:\s*(.*)$/i,
    replace: (_, msg) => `Utekelezaji umeshindwa: ${translateToSwahili(msg)}`
  }
];

export function isSwahiliActive() {
  const currentLang = i18n.language || localStorage.getItem('i18nextLng') || 'en';
  return currentLang.toLowerCase().startsWith('sw');
}

export function translateToSwahili(text) {
  if (!text || typeof text !== 'string') return text;
  const trimmed = text.trim();
  const lower = trimmed.toLowerCase();

  // 1. Direct dictionary match
  if (swahiliTranslations[lower]) {
    return swahiliTranslations[lower];
  }

  // 2. Dynamic pattern match
  for (const item of dynamicPatterns) {
    const match = trimmed.match(item.regex);
    if (match) {
      return item.replace(...match);
    }
  }

  // Fallback: return as-is
  return text;
}

// Global SweetAlert2 patch
export function initSwalI18n() {
  if (Swal._i18nPatched) return;
  Swal._i18nPatched = true;

  const originalFire = Swal.fire.bind(Swal);

  Swal.fire = function (...args) {
    if (!isSwahiliActive()) {
      return originalFire(...args);
    }

    // Handle object call: Swal.fire({ title: '...', text: '...' })
    if (args.length === 1 && typeof args[0] === 'object' && args[0] !== null) {
      const opts = { ...args[0] };
      if (opts.title) opts.title = translateToSwahili(opts.title);
      if (opts.text) opts.text = translateToSwahili(opts.text);
      if (opts.html && typeof opts.html === 'string') opts.html = translateToSwahili(opts.html);
      if (opts.confirmButtonText) opts.confirmButtonText = translateToSwahili(opts.confirmButtonText);
      if (opts.cancelButtonText) opts.cancelButtonText = translateToSwahili(opts.cancelButtonText);
      if (opts.denyButtonText) opts.denyButtonText = translateToSwahili(opts.denyButtonText);
      return originalFire(opts);
    }

    // Handle argument call: Swal.fire(title, message, icon)
    const translatedArgs = args.map((arg, idx) => {
      // Index 0: Title, Index 1: Message
      if ((idx === 0 || idx === 1) && typeof arg === 'string') {
        return translateToSwahili(arg);
      }
      return arg;
    });

    return originalFire(...translatedArgs);
  };
}
