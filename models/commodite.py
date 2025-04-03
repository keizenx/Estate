# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Commodite(models.Model):
    _name = 'estate.commodite'
    _description = 'Commodité'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    piece_id = fields.Many2one('estate.piece', string="Pièce", help="Définir la pièce")
    propriete_id = fields.Many2one('estate.propriete', string="Propriété", help="Définir la propriété", related="piece_id.propriete_id")
    image = fields.Binary('Image')