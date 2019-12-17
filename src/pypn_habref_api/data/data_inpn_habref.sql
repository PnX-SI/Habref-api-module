SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = ref_habitats, pg_catalog;


TRUNCATE TABLE habref CASCADE;
TRUNCATE TABLE typoref CASCADE;
TRUNCATE TABLE bib_habref_typo_rel CASCADE;
TRUNCATE TABLE habref_corresp_taxon CASCADE;
TRUNCATE TABLE habref_corresp_hab CASCADE;


TRUNCATE TABLE bib_habref_statuts CASCADE;
TRUNCATE TABLE cor_habref_terr_statut CASCADE;
TRUNCATE TABLE typoref_fields CASCADE;
TRUNCATE TABLE cor_habref_description CASCADE;
TRUNCATE TABLE habref_sources CASCADE;
TRUNCATE TABLE cor_hab_source CASCADE;

COPY bib_habref_typo_rel 
FROM  '/tmp/habref/HABREF_TYPE_REL_50.csv'
WITH  CSV HEADER 
DELIMITER E';'  encoding 'UTF-8';

COPY bib_habref_statuts 
FROM  '/tmp/habref/HABREF_STATUTS_50.csv'
WITH  CSV HEADER 
DELIMITER E';'  encoding 'UTF-8';

COPY habref_sources 
FROM  '/tmp/habref/HABREF_SOURCES_50.csv'
WITH  CSV HEADER 
DELIMITER E';'  encoding 'UTF-8';

COPY typoref 
FROM '/tmp/habref/TYPOREF_50.csv' 
WITH  CSV HEADER 
DELIMITER E';'  encoding 'UTF-8';

COPY habref 
FROM '/tmp/habref/HABREF_NOHTML_50.csv' 
WITH  CSV HEADER 
DELIMITER E';'  encoding 'UTF-8';

COPY habref_corresp_hab
FROM  '/tmp/habref/HABREF_CORRESP_HAB_50.csv'
WITH  CSV HEADER 
DELIMITER E';'  encoding 'UTF-8';

COPY habref_corresp_taxon 
FROM  '/tmp/habref/HABREF_CORRESP_TAXON_50.csv'
WITH  CSV HEADER 
DELIMITER E';'  encoding 'UTF-8';

COPY cor_habref_terr_statut 
FROM  '/tmp/habref/HABREF_TERR_50.csv'
WITH  CSV HEADER 
DELIMITER E';'  encoding 'UTF-8';

COPY typoref_fields 
FROM  '/tmp/habref/TYPOREF_FIELDS_50.csv'
WITH  CSV HEADER 
DELIMITER E';'  encoding 'UTF-8';

COPY cor_habref_description 
FROM  '/tmp/habref/HABREF_DESCRIPTION_NOHTML_50.csv'
WITH  CSV HEADER 
DELIMITER E';'  encoding 'UTF-8';

COPY cor_hab_source 
FROM  '/tmp/habref/HABREF_LIEN_SOURCES_50.csv'
WITH  CSV HEADER 
DELIMITER E';'  encoding 'UTF-8';


-- suppression des colonnes inutiles (mise pour lisibilité dans HABREF)
ALTER TABLE cor_habref_description DROP COLUMN cd_typo;
ALTER TABLE cor_habref_description DROP COLUMN lb_code;
ALTER TABLE cor_habref_description DROP COLUMN lb_hab_field;

-- TODO ? conversion en timestamp ?
--     to_timestamp(date_crea, 'YYYYMMDDHH24MISS') ,
--     to_timestamp(date_modif, 'YYYYMMDDHH24MISS')


-- CREATE TABLE AUTOCOMPLETE

INSERT INTO ref_habitats.autocomplete_habitat
SELECT 
cd_hab,
h.cd_typo,
lb_code,
lb_nom_typo,
concat(lb_code, ' - ', lb_hab_fr, ' ', lb_hab_fr_complet)
FROM ref_habitats.habref h
JOIN ref_habitats.typoref t ON t.cd_typo = h.cd_typo;