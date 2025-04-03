# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class EtatDesLieux(models.Model):
    _name = 'estate.etat.des.lieux'
    _description = 'Etat des lieux'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Numero")
    type = fields.Selection([
        ('entree', 'Entrée'),
        ('sortie', 'Sortie')], string="Type d'état des lieux",
        required=True)
    date = fields.Datetime(default=datetime.now())
    responsable_id = fields.Many2one('res.users', string='Responsable', required=True)
    location_id = fields.Many2one('estate.location', "Location")
    photo_entree = fields.Binary("Photo d'Entrée")
    photo_sortie = fields.Binary("Photo de Sortie")

