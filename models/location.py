# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date
from odoo.exceptions import UserError

class Location(models.Model):
    _name = 'estate.location'
    _description = 'Location'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Champs de base
    name = fields.Char("Numéro")
    locataire_id = fields.Many2one('res.partner', "Locataire")
    propriete_id = fields.Many2one('estate.propriete', "Propriété")
    date_de_reservation = fields.Date('Date de réservation')
    date_de_debut = fields.Date('Date de début')
    duree_en_annee = fields.Integer("Durée", help="Durée de location en année")
    date_de_fin = fields.Date('Date de fin', compute="_compute_date_de_fin", store=True)
    frequence = fields.Selection([
        ('mensuelle', 'Mensuelle'),
        ('bimestrielle', 'Bimestrielle'),
        ('trimestrielle', 'Trimestrielle'),
        ('semestrielle', 'Semestrielle'),
        ('annuelle', 'Annuelle'),
    ], string="Fréquence de paiement", default='mensuelle')
    loyer = fields.Integer(compute="_compute_loyer", store=True)
    etat = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('validee', 'Validée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée')
    ], string="Etat", default='brouillon')
    etats_des_lieux_ids = fields.One2many('estate.etat.des.lieux', 'location_id', string='États des Lieux')

    # Calcul de la date de fin : date_de_debut + duree_en_annee (en années) - 1 jour
    @api.depends('date_de_debut', 'duree_en_annee')
    def _compute_date_de_fin(self):
        for record in self:
            if record.date_de_debut and record.duree_en_annee:
                record.date_de_fin = record.date_de_debut + relativedelta(years=record.duree_en_annee) - relativedelta(days=1)
            else:
                record.date_de_fin = date.today()

    # Calcul du loyer selon la fréquence et le loyer mensuel de la propriété
    @api.depends('propriete_id', 'frequence')
    def _compute_loyer(self):
        for record in self:
            if record.propriete_id:
                if record.frequence == "mensuelle":
                    record.loyer = record.propriete_id.loyer_mensuel
                elif record.frequence == "bimestrielle":
                    record.loyer = record.propriete_id.loyer_mensuel * 2
                elif record.frequence == "trimestrielle":
                    record.loyer = record.propriete_id.loyer_mensuel * 3
                elif record.frequence == "semestrielle":
                    record.loyer = record.propriete_id.loyer_mensuel * 6
                elif record.frequence == "annuelle":
                    record.loyer = record.propriete_id.loyer_mensuel * 12
                else:
                    record.loyer = 0
            else:
                record.loyer = 0

    # Redéfinition de la création pour mettre à jour l'état de la propriété associée
    @api.model
    def create(self, vals):
        record = super(Location, self).create(vals)
        record._update_property_state()
        return record

    # Redéfinition de l'écriture pour mettre à jour l'état de la propriété associée
    def write(self, vals):
        res = super(Location, self).write(vals)
        self._update_property_state()
        return res

    def _update_property_state(self):
        """
        Met à jour l'état de la propriété associée en fonction de l'état de la location :
          - Si la location est validée, la propriété passe à "réservée".
          - Si la location est en cours, la propriété passe à "occupée".
          - Si la location est terminée ou annulée, la propriété repasse à "libre".
        """
        for loc in self:
            if loc.propriete_id:
                if loc.etat == 'validee':
                    loc.propriete_id.write({'etat': 'reservee'})
                elif loc.etat == 'en_cours':
                    loc.propriete_id.write({'etat': 'occupee'})
                elif loc.etat in ('terminee', 'annulee'):
                    loc.propriete_id.write({'etat': 'libre'})

    # Méthodes de transition d'état

    def action_valider(self):
        """
        Passe l'état de la location de 'brouillon' à 'validee' après
        vérification des chevauchements sur la même propriété.
        """
        for loc in self:
            if loc.etat != 'brouillon':
                continue  # On ne peut valider qu'en brouillon
            overlapping = self.search([
                ('id', '!=', loc.id),
                ('propriete_id', '=', loc.propriete_id.id),
                ('etat', 'in', ['validee', 'en_cours']),
                ('date_de_debut', '<=', loc.date_de_fin),
                ('date_de_fin', '>=', loc.date_de_debut),
            ])
            if overlapping:
                raise UserError(_("La propriété est déjà réservée ou en cours pour cette période."))
            loc.write({'etat': 'validee'})
            loc._update_property_state()

    def action_commencer(self):
        """Passe l'état de 'validee' à 'en_cours'."""
        for loc in self:
            if loc.etat != 'validee':
                continue
            loc.write({'etat': 'en_cours'})
            loc._update_property_state()

    def action_terminee(self):
        """Passe l'état de 'en_cours' à 'terminee'."""
        for loc in self:
            if loc.etat != 'en_cours':
                continue
            loc.write({'etat': 'terminee'})
            loc._update_property_state()

    def action_annuler(self):
        """Passe l'état de 'brouillon' ou 'validee' à 'annulee'."""
        for loc in self:
            if loc.etat not in ['brouillon', 'validee']:
                continue
            loc.write({'etat': 'annulee'})
            loc._update_property_state()
