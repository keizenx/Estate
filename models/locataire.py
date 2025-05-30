# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Locataire(models.Model):
    _inherit = 'res.partner'

    est_un_locataire = fields.Boolean(string="Est un locataire", default=False)
    location_ids = fields.One2many('estate.location', 'locataire_id', string='Locations')
    birthdate_date = fields.Date(string="Date de naissance")
    document_ids = fields.Many2many('ir.attachment', string="Documents", copy=False)
    
    # Champs personnalisés pour les locataires
    prenoms = fields.Char(string="Prénoms")
    contact = fields.Char(string="Contact")
    adresse = fields.Text(string="Adresse")
    ville = fields.Char(string="Ville")
    pays = fields.Char(string="Pays")

    @api.model
    def create(self, vals):
        if self._context.get('default_est_un_locataire'):
            vals['est_un_locataire'] = True
        return super(Locataire, self).create(vals)

    def name_get(self):
        """Personnaliser l'affichage du nom des locataires avec un badge"""
        result = []
        for partner in self:
            name = partner.name
            if partner.est_un_locataire:
                name = f"[Locataire] {name}"
            result.append((partner.id, name))
        return result

    def action_view_locations(self):
        """Ouvre la vue des locations liées à ce locataire"""
        return {
            'name': 'Locations',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'estate.location',
            'domain': [('locataire_id', '=', self.id)],
            'context': {'default_locataire_id': self.id},
        }
