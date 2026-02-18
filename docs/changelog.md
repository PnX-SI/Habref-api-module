# CHANGELOG

## 0.4.3 (2026-01-14)

**🚀 Nouveautés**

* Ajout du support de Debian 13

## 0.4.2 (2025-05-22)

**🚀 Nouveautés**

* Mise à jour de Utils-Flask-SQLAlchemy en version 0.4.2

## 0.4.1 (2024-01-30)

**🐛 Corrections**

* Mise à jour de Utils-Flask-SQLAlchemy en version 0.4.1

## 0.4.0 (2024-01-29)

**🚀 Nouveautés**

* Mise à jour vers SQLAlchemy 1.4 (#12)
* Abandon du support de Debian 10 (#12)
* Mise à jour du linter Black à la version 24 (#14)

## 0.3.2 (2023-03-20)

**🚀 Nouveautés**

* Mise à jour de Utils-Flask-SQLAlchemy en version 0.3.2
* Ajout de SQLAlchemy version 1.4 dans les tests

**🐛 Corrections**

* Correction d'une régression du filtre des topologies par liste d'habitats (https://github.com/PnX-SI/GeoNature/issues/2405)

## 0.3.1 (2022-09-01)

**🚀 Nouveautés**

* Mise à jour de Utils-Flask-SQLAlchemy en version 0.3.0
* Le code est désormais formaté avec Black et une Github Action y veille.

**🐛 Corrections**

* Correction des modèles
* Correction de l'auto-complétion et ajout d'un test unitaire sur celle ci

## 0.3.0 (2022-01-04)

**🚀 Nouveautés**

* Possibilité de lancer l'API Habref de manière autonome
* Possibilité de créer son schéma de base de données de manière autonome
* Mise en place des tests unitaires
* Mise en place de l'intégration continue
* Intégration de la dépendance Utils-Flask-SQLAlchemy en tant que sous-module Git

**🐛 Corrections**

* Suppression d'anciens fichiers devenus inutiles suite au paquetage
* Suppression du script d'installation de la base de donnée (remplacé par Alembic)

## 0.2.1 (2021-11-30)

**🐛 Corrections**

* Correction de certaines données localisées de Habref
* Correction de l'ordonnancement des résultats de l'API Habref

## 0.2.0 (2021-10-01)

**🚀 Nouveautés**

* Ajout de migrations Alembic pour installer le schéma `ref_habitats`

## 0.1.6 (2021-06-08)

**🚀 Nouveautés**

* Ajout de schémas Marshmallow

**🐛 Corrections**

* Nouvelle méthode pour importer l'instance `DB` d'un module parent

## 0.1.5 (2020-02-04)

**🐛 Corrections**

* Les dépendances du fichier `requirements.txt` ne sont plus fixées à une version

## 0.1.4 (2020-10-21)

**🚀 Nouveautés**

* La route `/habitats/autocomplete` n'a plus de paramètre `id_list` obligatoire
* Ajout de schéma Marshmallow pour la sérialisation
* Mise à jour des dépendances Python (psycopg2 et SQLAlchemy)

## 0.1.3 (2020-06-17)

**🚀 Nouveautés**

* Montée de la version de `utils-flask-sqlalchemy`

## 0.1.2 (2019-12-20)

**Corrections**

* Correction erreur 500 lorsqu'un habitat n'a pas de correspondance

## 0.1.1 (2019-12-18)

**Corrections**

* Ajout des fichiers SQL d'installation du schéma `ref_habitats` dans le paquet
* Montée de version de la librairie utils-Flask-SQLAlchemy

## 0.1.0 (2019-12-17)

Première version stabilisée du sous-module Habref.

* SQL de création d'un schéma `ref_habitats` contenant les données du référentiel HABREF 5.0
* Commande python de création et d'import des données HABREF
* API d'interrogation du référentiel Habref :
  - Recherche dans la table `habref` sur l'ensemble des champs
  - Interrogation de la table `typo_ref`
  - Recherche d'informations sur un habitat et ses correspondances
  - Interrogation auto-complétée et intelligente sur des listes d'habitats créées au préalable