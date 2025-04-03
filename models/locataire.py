# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    est_un_locataire = fields.Boolean()
    location_ids = fields.One2many('estate.location', 'locataire_id', 'Locations')

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)

        est_un_locataire = self.env.context.get('est_un_locataire')

        if est_un_locataire:  # In this case, product is reassurance.
            for partner in res:
                partner.write({
                    'est_un_locataire': True
                })

        return res
