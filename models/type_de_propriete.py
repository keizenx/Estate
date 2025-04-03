# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TypeDePropriete(models.Model):
    _name = 'estate.type.propriete'
    _description = 'Type de Propriété'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Libellé', tracking=True)
    description = fields.Text()

    propriete_ids = fields.One2many('estate.propriete', 'type_id', 'Propriétés')
