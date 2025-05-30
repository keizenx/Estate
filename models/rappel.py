# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Rappel(models.Model):
    _name = 'estate.rappel'
    _description = 'Rappel de paiement'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Référence", required=True, copy=False, default="Nouveau", tracking=True)
    montant_loyer = fields.Float(string="Montant du loyer", tracking=True)
    montant = fields.Float(string="Montant du rappel", tracking=True)
    date = fields.Date(string="Date du rappel", default=fields.Date.today, tracking=True)
    location_id = fields.Many2one('estate.location', string="Location", required=True, tracking=True)
    locataire_id = fields.Many2one(related='location_id.locataire_id', string="Locataire", store=True)
    etat = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('envoye', 'Envoyé'),
        ('paye', 'Payé'),
        ('annule', 'Annulé')
    ], string="État", default="brouillon", tracking=True)
    
    # Nouveaux champs
    motif = fields.Selection([
        ('retard', 'Retard de paiement'),
        ('partiel', 'Paiement partiel'),
        ('charges', 'Rappel de charges'),
        ('autre', 'Autre')
    ], string="Motif du rappel", tracking=True)
    description = fields.Text(string="Description détaillée", tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('estate.rappel') or 'Nouveau'
        return super().create(vals_list)
    
    # Méthodes d'actions pour les boutons
    def action_envoyer(self):
        for record in self:
            record.write({'etat': 'envoye'})
    
    def action_payer(self):
        for record in self:
            record.write({'etat': 'paye'})
    
    def action_annuler(self):
        for record in self:
            record.write({'etat': 'annule'})
            
    @api.onchange('location_id')
    def _onchange_location_id(self):
        if self.location_id:
            self.montant_loyer = self.location_id.montant_loyer 