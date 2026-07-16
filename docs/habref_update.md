# Mise à jour du référentiel HABREF

Scripts permettant de mettre à jour le référentiel des habitats (HABREF) vers une nouvelle version.

## Avant de commencer

> [!WARNING]
> La mise à jour du référentiel HABREF efface les données de la version du référentiel précédemment installée.

> [!WARNING]
> Il est fortement recommandé de **faire une sauvegarde de la base de données** avant de commencer.

## 1. Importer la nouvelle version et détecter les orphelins

Dans la première étape, il faut télécharger les données du référentiels, stocker ces dernières dans une table temporaire (ref*habitats.tmp*<num_version>). Pour cela, on lance la commande :

```bash
geonature habref import-v07
```

> [!DANGER]
> Il se peut que certaines entrées du référentiels soient supprimées lors d'une mise à jours. Dans ce cas, le fichier `tmp/habref/orphans_habref.csv` liste l'ensemble des données dans votre base utilisant ces entrées Habref.

Si la commande est relancée, les tables temporaires existantes sont automatiquement supprimées et recréées.

---

## 2 — Analyser et corriger les données orphelines

Dans le cas où plusieurs données orphelines ont été détecté dans l'étape précédente, consultez le fichier `tmp/habref/orphans_habref.csv`. Pour chaque ligne de ce fichier, la valeur `fk_value` est un code habitat qui sera supprimé lors de la mise à jour.

Le CSV généré contient les colonnes suivantes :

| Colonne               | Description                                              |
| --------------------- | -------------------------------------------------------- |
| `ref_table`           | Table du référentiel concernée (ex: `habref`, `typoref`) |
| `table_name`          | Table applicative contenant la référence orpheline       |
| `schema`              | Schéma de cette table                                    |
| `fk_column`           | Colonne portant la clé étrangère                         |
| `fk_value`            | Valeur orpheline                                         |
| `nb_lignes_affectees` | Nombre de lignes concernées                              |

Vous devez décider, pour chaque cas :

- **Mettre à jour** les données concernées avec le `cd_hab` de remplacement dans la nouvelle version
- **Supprimer** les observations si elles ne peuvent plus être rattachées

---

## 3 — Appliquer la mise à jour

Une fois les données orphelines corrigées, lancez la mise à jour effective du référentiel à l'aide de la commande suivante :

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

> [!WARNING]
> ⚠️ Si des données orphelines subsistent au moment du `apply-v07`, des erreurs de contraintes FK pourraient apparaître et la migration ne se feras pas. Assurez-vous que toutes les corrections ont bien été appliquées avant de lancer cette commande.
