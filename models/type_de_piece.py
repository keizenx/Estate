# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TypeDePiece(models.Model):
    _name = 'estate.type.piece'
    _description = 'Type de Pièce'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Libellé', tracking=True)
    description = fields.Text()

    pieces_ids = fields.One2many('estate.piece', 'type_id', 'Pièces')
