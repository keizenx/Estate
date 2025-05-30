# -*- coding: utf-8 -*-
{
    'name': "Estate_sk",

    'summary': "Module de gestion immobilière pour les agences et professionnels",

    'description': """
Module de Gestion Immobilière - Estate_sk
=========================================

Ce module permet de gérer des propriétés immobilières, leurs locations,
les locataires, les factures et les rappels de paiement.

Fonctionnalités principales:
---------------------------
* Gestion des propriétés (appartements, maisons, etc.)
* Gestion des locations et des contrats
* Suivi des locataires
* Facturation des loyers
* États des lieux avec support d'images
* Gestion des commodités avec support d'images
* Rappels automatiques pour les paiements
    """,

    'author': "SK Development",
    'website': "https://www.sk-development.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Real Estate',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        # Security
        'security/estate_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/ir_sequence_data.xml',
        
        # Reports (chargés avant les vues qui les référencent)
        'reports/etat_des_lieux_report.xml',
        
        # Views - chargeons les définitions d'actions avant les menus
        'views/type_de_propriete_views.xml',
        'views/type_de_piece_views.xml',
        'views/piece_views.xml',
        'views/propriete_views.xml',
        'views/location_views.xml',
        'views/locataire_views.xml',
        'views/etats_des_lieux_views.xml',
        'views/facture_views.xml',
        'views/rappel_views.xml',
        'views/commodite_views.xml',
        
        # Vues additionnelles pour kanban, pivot, graph
        'views/vues_additionnelles.xml',
        'views/action_updates.xml',
        
        # Menu principal - chargé en dernier
        'views/estate_menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

