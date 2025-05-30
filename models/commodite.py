# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Commodite(models.Model):
    _name = 'estate.commodite'
    _description = 'Commodité'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    description = fields.Text(string="Description", tracking=True)
    piece_id = fields.Many2one('estate.piece', string="Pièce", help="Définir la pièce")
    propriete_id = fields.Many2one('estate.propriete', string="Propriété", help="Définir la propriété", related="piece_id.propriete_id")
    
    # Amélioration du champ image pour le support du widget image
    image = fields.Binary('Image', attachment=True)
    
    # Champ pour l'état des lieux
    etat_des_lieux_ids = fields.Many2many('estate.etat.des.lieux', string="États des lieux")


class CommoditeEtatDesLieux(models.Model):
    _name = 'estate.commodite.etat'
    _description = 'État de la commodité'
    _rec_name = 'commodite_id'

    commodite_id = fields.Many2one('estate.commodite', string="Commodité", required=True)
    etat_des_lieux_id = fields.Many2one('estate.etat.des.lieux', string="État des lieux", required=True, ondelete='cascade')
    etat = fields.Selection([
        ('bon', 'Bon état'),
        ('moyen', 'État moyen'),
        ('mauvais', 'Mauvais état'),
        ('neuf', 'Neuf'),
        ('absent', 'Absent/Manquant')
    ], string="État", default='bon', required=True, tracking=True)
    notes = fields.Text(string="Remarques", help="Observations spécifiques sur cette commodité")
    image_ids = fields.One2many('estate.etat.des.lieux.image', 'commodite_etat_id', string="Photos")

    # Champs reliés pour faciliter la recherche et le regroupement
    piece_id = fields.Many2one(related='commodite_id.piece_id', string="Pièce", store=True)
    propriete_id = fields.Many2one(related='commodite_id.propriete_id', string="Propriété", store=True)
    
    _sql_constraints = [
        ('unique_commodite_etat', 'unique(commodite_id, etat_des_lieux_id)', 
         'Une commodité ne peut être évaluée qu\'une seule fois par état des lieux.')
    ]
    
    def action_add_image(self):
        """Ouvre un assistant pour ajouter une photo à cette commodité"""
        self.ensure_one()
        return {
            'name': 'Ajouter une photo',
            'type': 'ir.actions.act_window',
            'res_model': 'estate.etat.des.lieux.image',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_etat_des_lieux_id': self.etat_des_lieux_id.id,
                'default_commodite_id': self.commodite_id.id,
                'default_commodite_etat_id': self.id,
                'default_name': f"Photo de {self.commodite_id.name}"
            }
        }