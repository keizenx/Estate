# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Piece(models.Model):
    _name = 'estate.piece'
    _description = 'Pièce'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    type_id = fields.Many2one('estate.type.propriete', string="Type", help="Définir le type de propriété")
    propriete_id = fields.Many2one('estate.propriete', string="Propriété", help="Définir la propriété")
    superficie = fields.Float()
    commodite_ids = fields.One2many('estate.commodite', 'piece_id', 'Pièces')
