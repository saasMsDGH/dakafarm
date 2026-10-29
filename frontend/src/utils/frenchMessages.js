import english from '../../public/locales/en/translation.json';
import french from '../../public/locales/fr/translation.json';

const messages = Object.fromEntries(Object.entries(english).map(([key, value]) => [value.toLowerCase(), french[key] || value]));
Object.assign(messages, {
  'error': 'Erreur', 'error!': 'Erreur', 'success': 'Opération réussie',
  'success!': 'Opération réussie', 'warning': 'Attention', 'warning!': 'Attention',
  'deleted!': 'Suppression effectuée', 'saved!': 'Enregistrement effectué',
  'updated!': 'Mise à jour effectuée', 'yes': 'Oui', 'no': 'Non', 'ok': 'OK',
  'incorrect password or username': 'Adresse courriel ou mot de passe incorrect.',
  'incorrect username or password': 'Adresse courriel ou mot de passe incorrect.',
  'user account is inactive. please contact administrator.': 'Compte désactivé. Contactez l’administrateur.',
  'inactive user': 'Compte désactivé.', 'not authenticated': 'Authentification requise.',
  'could not validate credentials': 'Session invalide. Reconnectez-vous.',
  'you do not have permission to perform this action.': 'Vous n’avez pas la permission d’effectuer cette action.',
  'database transaction failed': 'Échec de l’enregistrement en base.',
  'user not found.': 'Utilisateur introuvable.',
  'password mpya imefanana na yazamani': 'Le nouveau mot de passe est identique à l’ancien.',
  'sale created successfully!': 'Vente enregistrée.',
  'purchase created successfully!': 'Achat enregistré.',
  'payment recorded successfully!': 'Paiement enregistré.',
  'product created successfully': 'Produit créé.',
});

export function translateToFrench(text) {
  if (typeof text !== 'string' || !text) return text;
  return messages[text.trim().toLowerCase()] || text;
}
