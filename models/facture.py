# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Facture(models.Model):
    _name = 'estate.facture'
    _description = 'Facture de loyer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Référence", readonly=True, copy=False, default="Nouveau")
    date = fields.Date(string="Date de facturation", required=True, default=fields.Date.today, tracking=True)
    montant = fields.Float(string="Montant", compute="_compute_montant", store=True, tracking=True)
    location_id = fields.Many2one('estate.location', string="Location", required=True, tracking=True)
    locataire_id = fields.Many2one(related='location_id.locataire_id', string="Locataire", store=True)
    etat = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('envoyee', 'Envoyée'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée')
    ], string="État", default="brouillon", tracking=True)
    
    # Nouveaux champs pour la facture
    periode_debut = fields.Date(string="Début de période", required=True, tracking=True)
    periode_fin = fields.Date(string="Fin de période", required=True, tracking=True)
    notes = fields.Text(string="Notes")
    
    @api.depends('location_id.loyer')
    def _compute_montant(self):
        for record in self:
            if record.location_id and record.location_id.loyer:
                record.montant = record.location_id.loyer
            else:
                record.montant = 0.0
                
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('estate.facture') or 'Nouveau'
        return super().create(vals_list)
    
    # Méthodes pour changer l'état
    def action_envoyer(self):
        for record in self:
            record.write({'etat': 'envoyee'})
    
    def action_payer(self):
        for record in self:
            record.write({'etat': 'payee'})
    
    def action_annuler(self):
        for record in self:
            record.write({'etat': 'annulee'}) 