# Habref-api-module

API d'interrogation d'Habref: référentiel des Habitat de l'INPN : https://inpn.mnhn.fr/telechargement/referentiels/habitats

## Technologies

- Python 3
- Flask
- SqlAlchemy

## Installation

- Créer un virtualenv et l'activer


    virtualenv -p /usr/bin/python3 venv
    source venv/bin/acticate

- Installer le module


    pip install https://github.com/PnX-SI/Habref-api-module/archive/<X.Y.Z>.zip

- Installer le schéma de base de données

Le module est fourni avec une commande pour installer la base de données. Cette commande télécharge le référentiel habref et crée un schéma de base de données nommé `ref_habitat`

::

    # depuis le virtualenv
    install_habref_schema <database uri>
    # ex:
    # install_habref_schema "postgresql://geonatadmin:monpassachanger@localhost:5432/geonature2db"
