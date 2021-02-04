=========
CHANGELOG
=========

0.1.5 (2020-02-04)
------------------

**🐛 Corrections**

* Les dépendances du fichier `requirements.txt` ne sont plus fixées à une version


0.1.4 (2020-10-21)
------------------

**🚀 Nouveautés**

* La route `/habitats/autocomplete` n'a plus de paramètre `id_list` obligatoire
* Ajout de schéma Marshmallow pour la sérialisation 
* Mise à jour des dépendances Python (psycopg2 et SQLAlchemy)

0.1.3 (2020-06-17)
------------------

**🚀 Nouveautés**

* Montée de la version de ``utils-flask-sqlalchemy``

0.1.2 (2019-12-20)
------------------

**Corrections**

* Correction erreur 500 lorsqu'un habitat n'a pas de correspondance

0.1.1 (2019-12-18)
------------------

**Corrections**

* Ajout des fichiers SQL d'installation du schéma ``ref_habitats`` dans le paquet
* Montée de version de la librairie utils-Flask-SQLAlchemy

0.1.0 (2019-12-17)
------------------

Première version stabilisée du sous-module Habref.

* SQL de création d'un schéma ``ref_habitats`` contenant les données du référentiel HABREF 5.0
* Commande python de création et d'import des données HABREF 
* API d'interrogation du référentiel Habref :

  - Recherche dans la table ``habref`` sur l'ensemble des champs
  - Interrogation de la table ``typo_ref``
  - Recherche d'informations sur un habitat et ses correspondances
  - Interrogation auto-complétée et intelligente sur des listes d'habitats créées au préalable
