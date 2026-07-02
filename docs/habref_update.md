# Mise à jour du référentiel HABREF

Scripts permettant de mettre à jour le référentiel des habitats (HABREF) vers une nouvelle version.

## Avant de commencer

La mise à jour du référentiel HABREF remplace l'intégralité des données de référence.

Il est fortement recommandé de **faire une sauvegarde de la base de données** avant de commencer.

## Commandes disponibles

Les commandes sont accessibles depuis le virtualenv de GeoNature :

```bash
cd ~/geonature
source backend/venv/bin/activate
```

---

## Étape 1 — Importer la nouvelle version et détecter les orphelins

```bash
geonature habref import-v07
```

Cette commande :

1. Télécharge l'archive `HABREF_70.zip`
2. Importe les données dans des tables temporaires `ref_habitats.tmp_*` (sans toucher aux données en production)
3. Parcourt toutes les tables de la base (tous modules confondus) qui référencent les tables HABREF et identifie les valeurs qui deviendront orphelines
4. Exporte le résultat dans le fichier `tmp/habref/orphans_habref.csv`

Le CSV généré contient les colonnes suivantes :

| Colonne               | Description                                              |
| --------------------- | -------------------------------------------------------- |
| `ref_table`           | Table du référentiel concernée (ex: `habref`, `typoref`) |
| `table_name`          | Table applicative contenant la référence orpheline       |
| `schema`              | Schéma de cette table                                    |
| `fk_column`           | Colonne portant la clé étrangère                         |
| `fk_value`            | Valeur orpheline                                         |
| `nb_lignes_affectees` | Nombre de lignes concernées                              |

Si la commande est relancée, les tables temporaires existantes sont automatiquement supprimées et recréées.

---

## Étape 2 — Analyser et corriger les données orphelines

Consultez le fichier `tmp/habref/orphans_habref.csv`. Pour chaque ligne, la valeur `fk_value` est un code habitat qui sera supprimé lors de la mise à jour.

Vous devez décider, pour chaque cas :

- **Mettre à jour** les observations concernées avec le `cd_hab` de remplacement dans la nouvelle version
- **Supprimer** les observations si elles ne peuvent plus être rattachées
- **Ignorer** si les données ne sont plus actives

Ces corrections peuvent être regroupées dans un fichier SQL et exécutées manuellement avant de passer à l'étape suivante.

---

## Étape 3 — Appliquer la mise à jour

Une fois les données orphelines corrigées :

```bash
geonature habref apply-v07
```

Cette commande :

1. Désactive temporairement les contraintes de clés étrangères
2. Vide toutes les tables du schéma `ref_habitats` (dans l'ordre inverse des dépendances)
3. Recopie le contenu des tables temporaires `tmp_*` dans les tables de production
4. Reconstruit la table `ref_habitats.autocomplete_habitat`
5. Réactive les contraintes de clés étrangères
6. Supprime les tables temporaires `tmp_*`

> ⚠️ Si des données orphelines subsistent au moment du `apply-v07`, des erreurs de contraintes FK pourraient apparaître et la migration ne se feras pas. Assurez-vous que toutes les corrections ont bien été appliquées avant de lancer cette commande.
