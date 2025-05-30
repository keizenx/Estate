# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Propriete(models.Model):
    _name = 'estate.propriete'
    _description = 'Propriété'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nom", required=True, tracking=True)
    type_id = fields.Many2one('estate.type.propriete', string="Type", help="Définir le type de propriété")
    superficie = fields.Float(string="Superficie (m²)")
    piece_ids = fields.One2many('estate.piece', 'propriete_id', 'Pièces')
    commodite_ids = fields.One2many('estate.commodite', 'propriete_id', 'Commodités')
    loyer_mensuel = fields.Integer(string="Loyer mensuel", required=True)
    
    # Nouveaux champs pour la localisation
    commune = fields.Char(string="Commune", required=True, tracking=True)
    quartier = fields.Char(string="Quartier", tracking=True)
    pays = fields.Many2one('res.country', string="Pays", required=True, tracking=True)
    
    # Image de la propriété
    image = fields.Binary(string="Image de la propriété", attachment=True)
    
    etat = fields.Selection([
        ('libre', 'Libre'),
        ('occupee', 'Occupée'),
        ('reservee', 'Réservée'),
        ('bientot_disponible', 'Bientôt disponible'),
    ], string="État", default="libre", tracking=True)

    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.commune:
                name = f"{name} ({record.commune})"
            result.append((record.id, name))
        return result

    @api.model
    def create(self, vals):
        # Vérifier que le loyer mensuel est positif
        if vals.get('loyer_mensuel', 0) <= 0:
            raise models.ValidationError("Le loyer mensuel doit être supérieur à 0.")
        return super(Propriete, self).create(vals)

    def write(self, vals):
        # Vérifier que le loyer mensuel est positif lors de la modification
        if 'loyer_mensuel' in vals and vals['loyer_mensuel'] <= 0:
            raise models.ValidationError("Le loyer mensuel doit être supérieur à 0.")
        return super(Propriete, self).write(vals)

    def action_view_locations(self):
        """Ouvre la vue des locations liées à cette propriété"""
        return {
            'name': 'Locations',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'estate.location',
            'domain': [('propriete_id', '=', self.id)],
            'context': {'default_propriete_id': self.id},
        }
