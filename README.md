# Habref-api-module

[![pytest](https://github.com/PnX-SI/Habref-api-module/actions/workflows/pytest.yml/badge.svg)](https://github.com/PnX-SI/Habref-api-module/actions/workflows/pytest.yml)
[![codecov](https://codecov.io/gh/PnX-SI/Habref-api-module/branch/master/graph/badge.svg?token=YM6Q6SO4EI)](https://codecov.io/gh/PnX-SI/Habref-api-module)

API d'interrogation d'Habref : référentiel des typologies d’habitats et de végétation pour la France (https://inpn.mnhn.fr/telechargement/referentiels/habitats).

## Technologies

- Python 3
- Flask
- SQLAlchemy

## Installation

- Créer un virtualenv et l'activer :

```
virtualenv -p /usr/bin/python3 venv
source venv/bin/acticate
```

- Installer le module :

```
pip install https://github.com/PnX-SI/Habref-api-module/archive/<X.Y.Z>.zip
```

- Installer le schéma de base de données :

Le module est fourni avec une commande pour installer la base de données. Cette commande télécharge le référentiel Habref et créé un schéma de base de données nommé ``ref_habitats``.

```
# Depuis le virtualenv
install_habref_schema <database uri>
# Exemple :
# install_habref_schema "postgresql://geonatadmin:monpassachanger@localhost:5432/geonature2db"
```
