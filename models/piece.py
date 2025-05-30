# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Piece(models.Model):
    _name = 'estate.piece'
    _description = 'Pièce'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nom", tracking=True)
    type_id = fields.Many2one('estate.type.piece', string="Type", help="Définir le type de pièce", tracking=True)
    propriete_id = fields.Many2one('estate.propriete', string="Propriété", help="Définir la propriété", tracking=True)
    superficie = fields.Float(string="Superficie (m²)", tracking=True)
    commodite_ids = fields.One2many('estate.commodite', 'piece_id', string='Commodités')
    
    # Méthodes pour la gestion des boutons du formulaire simplifié
    def action_save(self):
        """Sauvegarder la pièce et fermer le formulaire"""
        return {'type': 'ir.actions.act_window_close'}
    
    def action_save_and_new(self):
        """Sauvegarder la pièce et ouvrir un nouveau formulaire"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'estate.piece',
            'view_mode': 'form',
            'view_id': self.env.ref('Estate_sk.estate_piece_form_simple').id,
            'target': 'new',
            'context': {
                'default_propriete_id': self.propriete_id.id,
                'hide_propriete_id': bool(self.propriete_id),
            }
        }
    
    @api.onchange('type_id')
    def _onchange_type_id(self):
        """Suggérer un nom en fonction du type de pièce"""
        if self.type_id and not self.name:
            self.name = self.type_id.name
