# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class EtatDesLieux(models.Model):
    _name = 'estate.etat.des.lieux'
    _description = 'Etat des lieux'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Numero", readonly=True, copy=False, default="Nouveau")
    type = fields.Selection([
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
        ('intermediaire', 'Intermédiaire')], string="Type d'état des lieux",
        required=True, tracking=True)
    date = fields.Datetime(default=datetime.now(), tracking=True)
    responsable_id = fields.Many2one('res.users', string='Responsable', required=True, tracking=True)
    propriete_id = fields.Many2one('estate.propriete', string="Propriété", required=True, tracking=True)
    location_id = fields.Many2one('estate.location', "Location", required=True, tracking=True)
    
    # Nouveaux champs pour l'état des lieux
    description = fields.Text(string="Observations générales")
    commodite_ids = fields.Many2many('estate.commodite', string="Commodités vérifiées", tracking=True)
    
    # Relation avec le nouvel objet CommoditeEtatDesLieux
    commodite_etat_ids = fields.One2many('estate.commodite.etat', 'etat_des_lieux_id', string="État des commodités")
    
    # Images d'état des lieux
    image_ids = fields.One2many('estate.etat.des.lieux.image', 'etat_des_lieux_id', string="Images")
    images_count = fields.Integer(string="Nombre d'images", compute="_compute_images_count", store=True)
    
    @api.depends('image_ids')
    def _compute_images_count(self):
        for record in self:
            record.images_count = len(record.image_ids)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('estate.etat.des.lieux') or 'Nouveau'
            
            # S'assurer que propriete_id est toujours défini
            if 'location_id' in vals and not vals.get('propriete_id'):
                location = self.env['estate.location'].browse(vals['location_id'])
                if location and location.propriete_id:
                    vals['propriete_id'] = location.propriete_id.id
                
        return super().create(vals_list)
    
    @api.onchange('propriete_id')
    def _onchange_propriete_id(self):
        """Réinitialise la location si la propriété change"""
        self.location_id = False
        if self.propriete_id:
            # Rechercher toutes les commodités de la propriété
            commodites = self.env['estate.commodite'].search([
                ('propriete_id', '=', self.propriete_id.id)
            ])
            self.commodite_ids = commodites
    
    @api.onchange('location_id')
    def _onchange_location_id(self):
        """Charge automatiquement les commodités de la propriété"""
        if self.location_id and self.location_id.propriete_id:
            # Mettre à jour le champ propriete_id avec la propriété liée à la location
            self.propriete_id = self.location_id.propriete_id.id
            
            # Rechercher toutes les commodités de la propriété
            commodites = self.env['estate.commodite'].search([
                ('propriete_id', '=', self.location_id.propriete_id.id)
            ])
            self.commodite_ids = commodites
        # Assurons-nous que la propriété est bien renseignée même en dehors de l'interface utilisateur
        elif self.location_id and not self.propriete_id:
            location = self.env['estate.location'].browse(self.location_id.id)
            if location and location.propriete_id:
                self.propriete_id = location.propriete_id.id
    
    def write(self, vals):
        # S'assurer que propriete_id est toujours défini
        if 'location_id' in vals and not vals.get('propriete_id'):
            location = self.env['estate.location'].browse(vals['location_id'])
            if location and location.propriete_id:
                vals['propriete_id'] = location.propriete_id.id
        
        return super(EtatDesLieux, self).write(vals)

    def action_print_report(self):
        """Imprime le rapport d'état des lieux"""
        return {
            'name': 'Rapport État des Lieux',
            'type': 'ir.actions.act_window',
            'res_model': 'estate.etat.des.lieux',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
    
    def action_create_commodite(self):
        """Crée une nouvelle commodité"""
        return {
            'name': 'Nouvelle Commodité',
            'type': 'ir.actions.act_window',
            'res_model': 'estate.commodite',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_propriete_id': self.propriete_id.id},
        }


class EtatDesLieuxImage(models.Model):
    _name = 'estate.etat.des.lieux.image'
    _description = 'Image d\'état des lieux'
    
    name = fields.Char(string="Description", required=True)
    image = fields.Binary(string="Image", attachment=True, required=True)
    etat_des_lieux_id = fields.Many2one('estate.etat.des.lieux', string="Etat des lieux", ondelete='cascade')
    commodite_id = fields.Many2one('estate.commodite', string="Commodité associée")
    commodite_etat_id = fields.Many2one('estate.commodite.etat', string="État de la commodité")
    notes = fields.Text(string="Notes")


class CommoditeEtat(models.Model):
    _name = 'estate.commodite.etat'
    _description = 'État des commodités lors des états des lieux'
    
    etat_des_lieux_id = fields.Many2one('estate.etat.des.lieux', string='État des lieux', required=True, ondelete='cascade')
    commodite_id = fields.Many2one('estate.commodite', string='Commodité', required=True)
    piece_id = fields.Many2one('estate.piece', string='Pièce', related='commodite_id.piece_id', store=True)
    etat = fields.Selection([
        ('neuf', 'Neuf'),
        ('bon', 'Bon état'),
        ('moyen', 'État moyen'),
        ('mauvais', 'Mauvais état'),
        ('absent', 'Absent/Manquant')
    ], string='État', default='bon', required=True)
    notes = fields.Text(string='Notes')

