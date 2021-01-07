SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = ref_habitats, pg_catalog, public;



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
