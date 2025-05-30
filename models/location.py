# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import date


class Location(models.Model):
    _name = 'estate.location'
    _description = 'Location'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Numéro", readonly=True, copy=False, default="Nouveau")
    locataire_id = fields.Many2one(
        'res.partner', 
        string="Locataire", 
        required=True, 
        tracking=True,
        domain="[('est_un_locataire', '=', True)]",
        context={'default_est_un_locataire': True}
    )
    propriete_id = fields.Many2one(
        'estate.propriete', 
        string="Propriété", 
        required=True, 
        tracking=True,
        domain="[('etat', 'in', ['libre', 'reservee', 'bientot_disponible'])]"
    )
    date_de_reservation = fields.Date('Date de réservation', tracking=True)
    date_de_debut = fields.Date('Date de début', required=True, tracking=True)
    duree_en_annee = fields.Integer("Durée", help="Durée de location en année", required=True, tracking=True)
    date_de_fin = fields.Date('Date de fin', compute="_compute_date_de_fin", store=True, tracking=True)
    frequence = fields.Selection([
        ('mensuelle', 'Mensuelle'),
        ('bimestrielle', 'Bimestrielle'),
        ('trimestrielle', 'Trimestrielle'),
        ('semestrielle', 'Semestrielle'),
        ('annuelle', 'Annuelle'),
        ],
        string="Fréquence de paiement",
        default='mensuelle',
        tracking=True)
    loyer = fields.Integer(compute="_compute_loyer", store=True)
    montant_loyer = fields.Integer(compute="_compute_loyer", store=True, 
                                  help="Montant du loyer - Champ ajouté pour compatibilité")
    etat = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('validee', 'Validée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée')], string="Etat",
        default='brouillon', tracking=True)
    etats_des_lieux_ids = fields.One2many('estate.etat.des.lieux', 'location_id', string='Etats des Lieux')
    facture_ids = fields.One2many('estate.facture', 'location_id', string='Factures')
    
    # Champs pour les notes et documents
    notes = fields.Text(string="Notes")
    documents = fields.Binary(string="Documents", attachment=True)

    _sql_constraints = [
        ('check_dates', 'CHECK(date_de_debut <= date_de_fin)',
         'La date de début doit être antérieure à la date de fin.')
    ]

    @api.depends('date_de_debut', 'duree_en_annee')
    def _compute_date_de_fin(self):
        for record in self:
            if record.date_de_debut and record.duree_en_annee:
                record.date_de_fin = record.date_de_debut + relativedelta(years=record.duree_en_annee) - relativedelta(days=1)
            else:
                record.date_de_fin = date.today()

    @api.depends('propriete_id', 'frequence')
    def _compute_loyer(self):
        for record in self:
            if record.propriete_id:
                if record.frequence == "mensuelle":
                    record.loyer = record.propriete_id.loyer_mensuel
                    record.montant_loyer = record.propriete_id.loyer_mensuel
                elif record.frequence == "bimestrielle":
                    record.loyer = record.propriete_id.loyer_mensuel * 2
                    record.montant_loyer = record.propriete_id.loyer_mensuel * 2
                elif record.frequence == "trimestrielle":
                    record.loyer = record.propriete_id.loyer_mensuel * 3
                    record.montant_loyer = record.propriete_id.loyer_mensuel * 3
                elif record.frequence == "semestrielle":
                    record.loyer = record.propriete_id.loyer_mensuel * 6
                    record.montant_loyer = record.propriete_id.loyer_mensuel * 6
                elif record.frequence == "annuelle":
                    record.loyer = record.propriete_id.loyer_mensuel * 12
                    record.montant_loyer = record.propriete_id.loyer_mensuel * 12
                else:
                    record.loyer = 0
                    record.montant_loyer = 0
            else:
                record.loyer = 0
                record.montant_loyer = 0
    
    @api.constrains('propriete_id')
    def _check_propriete_etat(self):
        for record in self:
            if record.propriete_id and record.propriete_id.etat == 'occupee':
                raise models.ValidationError(
                    "Cette propriété est déjà occupée et n'est pas disponible pour la location. "
                    "Veuillez choisir une autre propriété."
                )
                
    @api.constrains('date_de_debut', 'date_de_fin', 'propriete_id', 'etat')
    def _check_date_overlap(self):
        for record in self:
            if record.date_de_debut and record.date_de_fin and record.propriete_id and record.etat not in ['terminee', 'annulee']:
                # Rechercher les locations qui se chevauchent pour la même propriété
                domain = [
                    ('id', '!=', record.id),
                    ('propriete_id', '=', record.propriete_id.id),
                    ('etat', 'not in', ['terminee', 'annulee']),
                    ('date_de_debut', '<=', record.date_de_fin),
                    ('date_de_fin', '>=', record.date_de_debut)
                ]
                
                overlapping = self.search_count(domain)
                if overlapping > 0:
                    raise models.ValidationError(
                        "Cette propriété est déjà réservée pour cette période. "
                        "Veuillez choisir une autre période ou une autre propriété."
                    )

    @api.onchange('propriete_id')
    def _onchange_propriete_id(self):
        if self.propriete_id and self.propriete_id.etat == 'occupee':
            return {
                'warning': {
                    'title': 'Propriété non disponible',
                    'message': "Cette propriété est déjà occupée et n'est pas disponible pour la location. "
                             "Veuillez choisir une autre propriété."
                }
            }

    @api.onchange('date_de_debut', 'duree_en_annee', 'propriete_id')
    def _onchange_dates(self):
        if self.date_de_debut and self.duree_en_annee and self.propriete_id:
            date_fin = self.date_de_debut + relativedelta(years=self.duree_en_annee) - relativedelta(days=1)
            
            # Rechercher les locations qui se chevauchent
            domain = [
                ('id', '!=', self._origin.id),
                ('propriete_id', '=', self.propriete_id.id),
                ('etat', 'not in', ['terminee', 'annulee']),
                ('date_de_debut', '<=', date_fin),
                ('date_de_fin', '>=', self.date_de_debut)
            ]
            
            overlapping = self.env['estate.location'].search(domain)
            if overlapping:
                return {
                    'warning': {
                        'title': 'Attention !',
                        'message': "Cette propriété est déjà réservée pour cette période.\n"
                                 "Locations existantes :\n" + "\n".join(
                                     f"- {loc.name} : du {loc.date_de_debut.strftime('%d/%m/%Y')} "
                                     f"au {loc.date_de_fin.strftime('%d/%m/%Y')}"
                                     for loc in overlapping
                                 )
                    }
                }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('estate.location') or 'Nouveau'
            
            # Vérifier les chevauchements avant la création
            if 'date_de_debut' in vals and 'date_de_fin' in vals and 'propriete_id' in vals:
                domain = [
                    ('propriete_id', '=', vals['propriete_id']),
                    ('etat', 'not in', ['terminee', 'annulee']),
                    ('date_de_debut', '<=', vals['date_de_fin']),
                    ('date_de_fin', '>=', vals['date_de_debut'])
                ]
                if self.search_count(domain) > 0:
                    raise models.ValidationError(
                        "Cette propriété est déjà réservée pour cette période. "
                        "Veuillez choisir une autre période ou une autre propriété."
                    )
                
        return super().create(vals_list)

    def write(self, vals):
        # Vérifier les chevauchements avant la modification
        if any(field in vals for field in ['date_de_debut', 'date_de_fin', 'propriete_id']):
            for record in self:
                date_debut = vals.get('date_de_debut', record.date_de_debut)
                date_fin = vals.get('date_de_fin', record.date_de_fin)
                propriete_id = vals.get('propriete_id', record.propriete_id.id)
                
                if date_debut and date_fin and propriete_id:
                    domain = [
                        ('id', '!=', record.id),
                        ('propriete_id', '=', propriete_id),
                        ('etat', 'not in', ['terminee', 'annulee']),
                        ('date_de_debut', '<=', date_fin),
                        ('date_de_fin', '>=', date_debut)
                    ]
                    if self.search_count(domain) > 0:
                        raise models.ValidationError(
                            "Cette propriété est déjà réservée pour cette période. "
                            "Veuillez choisir une autre période ou une autre propriété."
                        )
        
        return super().write(vals)

    # Méthodes pour changer l'état
    def action_valider(self):
        for record in self:
            # Vérifier les chevauchements avant de valider
            domain = [
                ('id', '!=', record.id),
                ('propriete_id', '=', record.propriete_id.id),
                ('etat', 'in', ['validee', 'en_cours']),  # Vérifier uniquement les locations validées ou en cours
                ('date_de_debut', '<=', record.date_de_fin),
                ('date_de_fin', '>=', record.date_de_debut)
            ]
            
            overlapping = self.search(domain)
            if overlapping:
                raise models.ValidationError(
                    "Impossible de valider cette location car il existe déjà une location active pour cette période.\n"
                    "Locations en conflit :\n" + "\n".join(
                        f"- {loc.name} ({loc.etat}) : du {loc.date_de_debut.strftime('%d/%m/%Y')} "
                        f"au {loc.date_de_fin.strftime('%d/%m/%Y')}"
                        for loc in overlapping
                    )
                )
                
            # Vérifier que la propriété est encore libre, réservée ou bientôt disponible
            if record.propriete_id.etat not in ['libre', 'reservee', 'bientot_disponible']:
                raise models.ValidationError(
                    "Cette propriété n'est plus disponible pour la location (état actuel: %s). "
                    "Veuillez choisir une autre propriété." % record.propriete_id.etat
                )

            record.write({'etat': 'validee'})
            # Mettre à jour l'état de la propriété
            if record.propriete_id:
                record.propriete_id.write({'etat': 'reservee'})
    
    def action_demarrer(self):
        for record in self:
            # Vérifier que la propriété est disponible pour être occupée
            if record.propriete_id.etat not in ['libre', 'reservee', 'bientot_disponible']:
                if record.propriete_id.etat == 'occupee':
                    # Vérifier si c'est cette location qui l'occupe déjà
                    autres_locations = self.search([
                        ('id', '!=', record.id),
                        ('propriete_id', '=', record.propriete_id.id),
                        ('etat', '=', 'en_cours')
                    ])
                    if autres_locations:
                        raise models.ValidationError(
                            "Cette propriété est déjà occupée par une autre location. "
                            "Impossible de démarrer cette location."
                        )
                else:
                    raise models.ValidationError(
                        "Cette propriété n'est pas disponible pour la location (état actuel: %s)." % record.propriete_id.etat
                    )
                
            record.write({'etat': 'en_cours'})
            # Mettre à jour l'état de la propriété
            if record.propriete_id:
                record.propriete_id.write({'etat': 'occupee'})
    
    def action_terminer(self):
        for record in self:
            record.write({'etat': 'terminee'})
            # Vérifier si d'autres locations actives existent pour cette propriété
            autres_locations = self.search([
                ('id', '!=', record.id),
                ('propriete_id', '=', record.propriete_id.id),
                ('etat', 'in', ['validee', 'en_cours'])
            ])
            
            if not autres_locations and record.propriete_id:
                # S'il n'y a pas d'autres locations actives, changer l'état à libre
                record.propriete_id.write({'etat': 'libre'})
    
    def action_annuler(self):
        for record in self:
            old_state = record.etat
            record.write({'etat': 'annulee'})
            
            # Vérifier si d'autres locations actives existent pour cette propriété
            autres_locations = self.search([
                ('id', '!=', record.id),
                ('propriete_id', '=', record.propriete_id.id),
                ('etat', 'in', ['validee', 'en_cours'])
            ])
            
            # Si la location était en cours et qu'il n'y a pas d'autres locations actives
            if old_state in ['en_cours', 'validee'] and not autres_locations and record.propriete_id:
                record.propriete_id.write({'etat': 'libre'})

    def action_create_property(self):
        """Ouvre le formulaire de création de propriété."""
        action = {
            'name': 'Créer une propriété',
            'type': 'ir.actions.act_window',
            'res_model': 'estate.propriete',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_etat': 'libre',
            },
        }
        return action

    @api.onchange('propriete_id')
    def _onchange_propriete_id(self):
        if self.propriete_id and self.propriete_id.etat != 'libre':
            # Réinitialiser le champ
            self.propriete_id = False
            return {
                'warning': {
                    'title': 'Propriété non disponible',
                    'message': 'Cette propriété est déjà occupée ou réservée. Veuillez en choisir une autre.'
                }
            }

    @api.constrains('propriete_id')
    def _check_propriete_disponible(self):
        for record in self:
            if record.propriete_id and record.propriete_id.etat != 'libre':
                raise models.ValidationError(
                    "Cette propriété n'est pas disponible car elle est déjà occupée ou réservée. "
                    "Veuillez en choisir une autre."
                )

    def action_print_report(self):
        """Imprime le rapport d'état des lieux"""
        return {
            'name': 'Imprimer Rapport',
            'type': 'ir.actions.act_window',
            'res_model': 'estate.etat.des.lieux',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_location_id': self.id,
                'default_propriete_id': self.propriete_id.id,
            }
        }
        
    def action_create_etat_lieux(self):
        """Crée un nouvel état des lieux"""
        return {
            'name': 'Nouvel État des Lieux',
            'type': 'ir.actions.act_window',
            'res_model': 'estate.etat.des.lieux',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_propriete_id': self.propriete_id.id,
                'default_location_id': self.id,
            }
        }
        
    def action_create_facture(self):
        """Crée une nouvelle facture pour cette location"""
        # Calculer les dates pour la période suivante en fonction de la fréquence
        today = fields.Date.today()
        
        # Par défaut, commencer la période à aujourd'hui
        periode_debut = today
        periode_fin = None
        
        # Si des factures existent déjà, utiliser la dernière période comme référence
        last_facture = self.env['estate.facture'].search([
            ('location_id', '=', self.id),
            ('etat', '!=', 'annulee')
        ], order='periode_fin desc', limit=1)
        
        if last_facture:
            # Commencer le jour après la fin de la dernière période
            periode_debut = last_facture.periode_fin + relativedelta(days=1)
            
        # Calculer la date de fin en fonction de la fréquence
        if self.frequence == 'mensuelle':
            periode_fin = periode_debut + relativedelta(months=1) - relativedelta(days=1)
        elif self.frequence == 'bimestrielle':
            periode_fin = periode_debut + relativedelta(months=2) - relativedelta(days=1)
        elif self.frequence == 'trimestrielle':
            periode_fin = periode_debut + relativedelta(months=3) - relativedelta(days=1)
        elif self.frequence == 'semestrielle':
            periode_fin = periode_debut + relativedelta(months=6) - relativedelta(days=1)
        elif self.frequence == 'annuelle':
            periode_fin = periode_debut + relativedelta(years=1) - relativedelta(days=1)
        else:
            # Par défaut : mensuel
            periode_fin = periode_debut + relativedelta(months=1) - relativedelta(days=1)
            
        return {
            'name': 'Nouvelle Facture',
            'type': 'ir.actions.act_window',
            'res_model': 'estate.facture',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_location_id': self.id,
                'default_locataire_id': self.locataire_id.id,
                'default_periode_debut': periode_debut,
                'default_periode_fin': periode_fin,
                'default_montant': self.loyer,
            }
        }