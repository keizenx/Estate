# Module de Gestion Immobilière - Estate_sk
=================================

## Description
Ce module permet la gestion complète d'une agence immobilière, incluant la gestion des propriétés, 
des locations, des locataires, des états des lieux et des factures.

## Compatibilité
- Odoo 18.0
- Python 3.10+

## Fonctionnalités Principales

### 1. Gestion des Propriétés
- Enregistrement des biens immobiliers
- Suivi de l'état (libre, occupé, réservé)
- Gestion des commodités
- Support pour les images

Exemple de modèle (models/propriete.py):
```python
class Propriete(models.Model):
    _name = 'estate.propriete'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nom", required=True, tracking=True)
    type_id = fields.Many2one('estate.type.propriete', string="Type")
    superficie = fields.Float(string="Superficie (m²)")
    loyer_mensuel = fields.Integer(string="Loyer mensuel", required=True)
    commune = fields.Char(string="Commune", required=True)
    etat = fields.Selection([
        ('libre', 'Libre'),
        ('occupee', 'Occupée'),
        ('reservee', 'Réservée')
    ], default="libre")
```

### 2. Gestion des Locations
- Création et suivi des contrats
- Vérification des disponibilités
- Gestion des périodes de location
- Calcul automatique des loyers
- Système de validation en plusieurs étapes

Exemple de modèle (models/location.py):
```python
class Location(models.Model):
    _name = 'estate.location'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Numéro", readonly=True, default="Nouveau")
    locataire_id = fields.Many2one('res.partner', "Locataire", required=True)
    propriete_id = fields.Many2one('estate.propriete', "Propriété", required=True)
    date_de_debut = fields.Date('Date de début', required=True)
    duree_en_annee = fields.Integer("Durée", required=True)
    etat = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('validee', 'Validée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée')
    ], default='brouillon')
```

Vue formulaire (views/location_views.xml):
```xml
<form>
    <header>
        <button name="action_valider" string="Valider" type="object" 
                invisible="etat != 'brouillon'" class="oe_highlight"/>
        <button name="action_demarrer" string="Démarrer" type="object" 
                invisible="etat != 'validee'" class="oe_highlight"/>
        <field name="etat" widget="statusbar"/>
    </header>
    <sheet>
        <group>
            <field name="locataire_id" options="{'no_create': True}"/>
            <field name="propriete_id" options="{'no_create': True, 'no_create_edit': True}"/>
            <field name="date_de_debut"/>
            <field name="duree_en_annee"/>
        </group>
    </sheet>
</form>
```

### 3. États des Lieux
- Création d'états des lieux d'entrée et de sortie
- Support pour les photos
- Gestion des commodités et leur état
- Génération de rapports

Exemple de modèle (models/etat_des_lieux.py):
```python
class EtatDesLieux(models.Model):
    _name = 'estate.etat.des.lieux'
    
    name = fields.Char(string="Référence")
    location_id = fields.Many2one('estate.location', string="Location")
    date = fields.Date(string="Date", required=True)
    type = fields.Selection([
        ('entree', 'Entrée'),
        ('sortie', 'Sortie')
    ], required=True)
    image_ids = fields.One2many('estate.etat.des.lieux.image', 'etat_des_lieux_id')
```

### 4. Adaptations Odoo 18

#### Changements de Syntaxe XML
1. Remplacement de `<tree>` par `<list>`:
```xml
<!-- Ancien -->
<tree>
    <field name="name"/>
</tree>

<!-- Nouveau -->
<list>
    <field name="name"/>
</list>
```

2. Nouvelle syntaxe pour les attributs conditionnels:
```xml
<!-- Ancien -->
<button attrs="{'invisible': [('etat', '!=', 'brouillon')]}"/>

<!-- Nouveau -->
<button invisible="etat != 'brouillon'"/>
```

3. Simplification des états:
```xml
<!-- Ancien -->
<field name="state" widget="statusbar" statusbar_visible="draft,posted,cancel"/>

<!-- Nouveau -->
<field name="state" widget="statusbar"/>
```

### 5. Contraintes et Validations

#### Chevauchement des Locations
```python
@api.constrains('date_de_debut', 'date_de_fin', 'propriete_id')
def _check_date_overlap(self):
    for record in self:
        domain = [
            ('id', '!=', record.id),
            ('propriete_id', '=', record.propriete_id.id),
            ('etat', 'not in', ['terminee', 'annulee']),
            ('date_de_debut', '<=', record.date_de_fin),
            ('date_de_fin', '>=', record.date_de_debut)
        ]
        if self.search_count(domain) > 0:
            raise ValidationError("Cette propriété est déjà réservée pour cette période.")
```

#### Validation des Propriétés
```python
@api.constrains('propriete_id')
def _check_propriete_disponible(self):
    for record in self:
        if record.propriete_id.etat != 'libre':
            raise ValidationError("Cette propriété n'est pas disponible.")
```

### 6. Vues Kanban
```xml
<kanban default_group_by="etat" records_draggable="1">
    <field name="name"/>
    <templates>
        <t t-name="kanban-box">
            <div class="oe_kanban_global_click">
                <div class="oe_kanban_content">
                    <field name="name"/>
                    <span class="badge" invisible="etat != 'en_cours'">
                        En cours
                    </span>
                </div>
            </div>
        </t>
    </templates>
</kanban>
```

## Installation

1. Cloner le module dans le dossier custom_addons:
```bash
git clone [URL_DU_REPO] custom_addons/Estate_sk
```

2. Mettre à jour la liste des applications dans Odoo

3. Installer le module Estate_sk

## Configuration

1. Créer les types de propriétés
2. Configurer les droits d'accès
3. Définir les séquences pour la numérotation automatique

## Sécurité
Le module inclut des groupes de sécurité:
- Estate / Administrateur
- Estate / Utilisateur

## Dépendances
- base
- mail

## Notes de Version
Version 1.0:
- Gestion complète des propriétés
- Système de location
- États des lieux avec photos
- Adaptations Odoo 18 