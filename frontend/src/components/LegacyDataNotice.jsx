import React from 'react';
import { Link } from 'react-router-dom';
import { Routes } from '../routes';
export default function LegacyDataNotice() {
  return <div className="alert alert-warning mt-3" role="note">
    <strong>Rapport historique à contrôler.</strong> Les devises, coûts et règles comptables de ces anciens indicateurs n’ont pas été validés pour DAKREX. Pour vérifier les pièces et calculer un résultat de gestion par campagne, utilisez <Link to={Routes.CampaignData.path}>Campagnes et données</Link>.
  </div>;
}
