SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

CREATE SCHEMA IF NOT EXISTS ref_habitats;

SET search_path = ref_habitats, pg_catalog, public;

SET default_with_oids = false;


-------------
--FUNCTIONS--
-------------

CREATE OR REPLACE FUNCTION ref_habitats.is_communitarian(my_cd_hab integer)
  RETURNS boolean AS
$BODY$
--fonction permettant de savoir si un habitat est communautaire
  DECLARE is_com integer;
  BEGIN
    SELECT INTO is_com count(*)
    FROM ref_habitats.habref hab
    JOIN ref_habitats.typoref typ ON hab.cd_typo = typ.cd_typo
    WHERE typ.cd_table = 'TYPO_HIC' 
    AND hab.cd_hab = my_cd_hab;
    RETURN is_com = 1;
 END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;


----------
--TABLES--
----------
-- init référentiel HABREF 4.0, table TYPOREF
CREATE TABLE typoref (
    cd_typo serial NOT NULL,
    cd_table character varying(255),
    lb_nom_typo character varying(100),
    nom_jeu_donnees character varying(255),
    date_creation character varying(255),
    date_mise_jour_table character varying(255),
    date_mise_jour_metadonnees character varying(255),
    auteur_typo character varying(4000),
    auteur_table character varying(4000),
    territoire character varying(4000),
    organisme character varying(255),
    langue character varying(255),
    presentation character varying(4000),
    description character varying(4000),
    origine character varying(4000),
    ref_biblio character varying(4000),
    mots_cles character varying(255),
    referencement character varying(4000),
    diffusion character varying(4000), -- pas de doc
    derniere_modif character varying(4000),
    type_table character varying(6),
    cd_typo_entre integer,
    cd_typo_sortie integer,
    niveau_inpn character varying(255) -- pas de doc
);
COMMENT ON TABLE ref_habitats.typoref IS 'typoref, table TYPOREF du référentiel HABREF 4.0';

-- init référentiel HABREF 4.0, table HABREF
CREATE TABLE habref (
    cd_hab integer NOT NULL,
    fg_validite character varying(20) NOT NULL,
    cd_typo integer NOT NULL,
    lb_code character varying(50),
    lb_hab_fr character varying(500),
    lb_hab_fr_complet character varying(500),
    lb_hab_en character varying(500),
    lb_auteur character varying(500),
    niveau integer,
    lb_niveau character varying(100),
    cd_hab_sup integer,
    path_cd_hab character varying(2000),
    france character varying(5),
    lb_description character varying(4000)
);
COMMENT ON TABLE ref_habitats.habref IS 'habref, table HABREF référentiel HABREF 4.0 INPN';



CREATE TABLE habref_corresp_hab(
    cd_corresp_hab integer NOT NULL,
    cd_hab_entre integer NOT NULL,
    cd_hab_sortie integer,
    cd_type_relation integer,
    lb_condition character varying(1000),
    lb_remarques character varying(4000),
    validite boolean,
    cd_typo_entre integer,
    cd_typo_sortie integer,
    date_crea text,
    date_modif text,
    diffusion boolean
);
COMMENT ON TABLE ref_habitats.habref_corresp_hab IS 'Table de corespondances entres les habitats de differentes typologie';


CREATE TABLE habref_corresp_taxon(
    cd_corresp_tax integer NOT NULL,
    cd_hab_entre integer NOT NULL,
    cd_nom integer,
    cd_type_relation integer,
    lb_condition character varying(1000),
    lb_remarques character varying(4000),
    nom_cite character varying(500),
    validite boolean,
    date_crea text,
    date_modif text
);
COMMENT ON TABLE ref_habitats.habref_corresp_taxon IS 'Table de corespondances entres les habitats les taxon (table taxref)';


CREATE TABLE bib_habref_typo_rel(
    cd_type_rel integer,
    lb_type_rel character varying(200),
    lb_rel character varying(1000),
    corresp_hab boolean,
    corresp_esp boolean,
    corresp_syn boolean,
    date_crea text,
    date_modif text
);
COMMENT ON TABLE ref_habitats.bib_habref_typo_rel IS 'Bibliothèque des types de relations entre habitats - Table habref_typo_rel de HABREF';


CREATE TABLE bib_habref_statuts(
    statut character varying(1) NOT NULL,
    description character varying(50) NOT NULL,
    definition character varying(500) NOT NULL,
    ordre integer
);
COMMENT ON TABLE ref_habitats.bib_habref_statuts IS 'Bibliothèque des types statut d''habitat - Présence, absence ... - Table habref_status de HABREF';

CREATE TABLE cor_habref_terr_statut(
    cd_hab_ter integer NOT NULL,
    cd_hab integer NOT NULL,
    cd_sig_terr character varying(20) NOT NULL,
    cd_statut_presence character varying(1),
    date_crea text,
    date_modif text
);
COMMENT ON TABLE ref_habitats.cor_habref_terr_statut IS 'Table de correspondance entre un habitat, un territoire et son statut - Table habref_terr de HABREF' ;

CREATE TABLE typoref_fields(
    cd_hab_field integer NOT NULL,
    cd_typo integer NOT NULL,
    lb_hab_field character varying(30) NOT NULL,
    format_hab_field character varying(200),
    descript_hab_field character varying(3000),
    ordre_hab_field integer,
    length_hab_field integer,
    lb_label character varying(200),
    date_crea text,
    date_modif text
);
COMMENT ON TABLE ref_habitats.cor_habref_terr_statut IS 'Table de descritpion des champs additionnels de chaque typologie.' ;

CREATE TABLE cor_habref_description(
    cd_hab_description integer NOT NULL,
    cd_hab integer NOT NULL,
    cd_hab_field integer NOT NULL,
    cd_typo integer,
    lb_code character varying(50),
    lb_hab_field character varying(200),
    valeurs text
);
COMMENT ON TABLE ref_habitats.cor_habref_description IS 'Table de correspondance entre un habitat et les champs additionnels décrit dans la table typoref_fields - Table habref_description de HABREF' ;


CREATE TABLE habref_sources(
    cd_source integer NOT NULL,
    cd_doc integer,
    type_source character varying(1),
    auteur_source character varying(255),
    date_source integer,
    lb_source character varying(1000),
    lb_source_complet character varying(2000),
    titre character varying(1000),
    link character varying(1000),
    date_crea text,
    date_modif text
);
COMMENT ON TABLE ref_habitats.habref_sources IS 'Table des sources décrivant les habitats' ;


CREATE TABLE cor_hab_source(
    cd_hab_lien_source integer NOT NULL,
    cd integer NOT NULL,
    type_lien character varying(7) NOT NULL,
    cd_source integer NOT NULL,
    origine character varying(5),
    date_crea text,
    date_modif text
);
COMMENT ON TABLE ref_habitats.cor_hab_source IS 'Table de corespondance entre une unité (cd_hab, cd_coresp_hab, cd_coresp_taxon) et une source - Table habref_lien_source de HABREF';


CREATE TABLE bib_list_habitat (
    id_list serial NOT NULL,
    list_name character varying(255) NOT NULL
);
COMMENT ON TABLE ref_habitats.bib_list_habitat IS 'Table des listes des habitats';

CREATE TABLE cor_list_habitat (
    id_cor_list serial NOT NULL,
    id_list integer NOT NULL,
    cd_hab integer NOT NULL
);
COMMENT ON TABLE ref_habitats.cor_list_habitat IS 'Habitat de chaque liste';


CREATE TABLE autocomplete_habitat(
    cd_hab integer NOT NULL,
    cd_typo integer NOT NULL,
    lb_code character varying(50),
    lb_nom_typo character varying(100) NOT NULL,
    search_name character varying(1000) NOT NULL
);

---------------
--PRIMARY KEY--
---------------

ALTER TABLE ONLY typoref
    ADD CONSTRAINT pk_typoref PRIMARY KEY (cd_typo);

ALTER TABLE ONLY habref 
    ADD CONSTRAINT pk_habref PRIMARY KEY (cd_hab);

ALTER TABLE ONLY habref_corresp_taxon 
    ADD CONSTRAINT pk_habref_corresp_taxon PRIMARY KEY (cd_corresp_tax);

ALTER TABLE ONLY bib_habref_typo_rel 
    ADD CONSTRAINT pk_bib_habref_typo_rel PRIMARY KEY (cd_type_rel);

ALTER TABLE ONLY habref_corresp_hab 
    ADD CONSTRAINT pk_habref_corresp_hab PRIMARY KEY (cd_corresp_hab);

ALTER TABLE ONLY bib_list_habitat 
    ADD CONSTRAINT pk_bib_list_habitat PRIMARY KEY (id_list);

ALTER TABLE ONLY cor_list_habitat 
    ADD CONSTRAINT pk_cor_list_habitat PRIMARY KEY (id_cor_list);

ALTER TABLE ONLY bib_habref_statuts
    ADD CONSTRAINT pk_bib_habref_statuts PRIMARY KEY (statut);

ALTER TABLE ONLY typoref_fields
    ADD CONSTRAINT pk_typoref_fields PRIMARY KEY (cd_hab_field);

ALTER TABLE ONLY cor_habref_description
    ADD CONSTRAINT pk_cor_habref_description PRIMARY KEY (cd_hab_description);

ALTER TABLE ONLY cor_hab_source
    ADD CONSTRAINT pk_cor_hab_source PRIMARY KEY (cd_hab_lien_source);


ALTER TABLE ONLY cor_habref_terr_statut
    ADD CONSTRAINT pk_cor_habref_terr_statut PRIMARY KEY (cd_hab_ter);

ALTER TABLE ONLY habref_sources
    ADD CONSTRAINT pk_habref_sources PRIMARY KEY (cd_source); 

ALTER TABLE ONLY autocomplete_habitat
    ADD CONSTRAINT pk_autocomplete_habitat PRIMARY KEY (cd_hab); 

---------------
--FOREIGN KEY--
---------------

ALTER TABLE ONLY habref 
    ADD CONSTRAINT fk_typoref FOREIGN KEY (cd_typo) REFERENCES ref_habitats.typoref (cd_typo) ON UPDATE CASCADE;

ALTER TABLE ONLY cor_list_habitat
    ADD CONSTRAINT fk_cor_list_habitat_cd_hab FOREIGN KEY (cd_hab) REFERENCES ref_habitats.habref (cd_hab) ON UPDATE CASCADE;
    
ALTER TABLE ONLY cor_list_habitat
    ADD CONSTRAINT fk_cor_list_habitat_id_list FOREIGN KEY (id_list) REFERENCES ref_habitats.bib_list_habitat (id_list) ON UPDATE CASCADE;


ALTER TABLE ONLY habref_corresp_hab
    ADD CONSTRAINT fk_habref_corresp_hab_cd_type_rel FOREIGN KEY (cd_type_relation) REFERENCES ref_habitats.bib_habref_typo_rel (cd_type_rel) ON UPDATE CASCADE;

ALTER TABLE ONLY habref_corresp_hab
    ADD CONSTRAINT fk_habref_corresp_hab_cd_hab_entre FOREIGN KEY (cd_hab_entre) REFERENCES ref_habitats.habref (cd_hab) ON UPDATE CASCADE;

ALTER TABLE ONLY habref_corresp_hab
    ADD CONSTRAINT fk_habref_corresp_hab_cd_hab_sortie FOREIGN KEY (cd_hab_sortie) REFERENCES ref_habitats.habref (cd_hab) ON UPDATE CASCADE;

ALTER TABLE ONLY habref_corresp_taxon
    ADD CONSTRAINT fk_habref_corresp_tax_cd_typ_rel FOREIGN KEY (cd_type_relation) REFERENCES ref_habitats.bib_habref_typo_rel (cd_type_rel) ON UPDATE CASCADE;

ALTER TABLE ONLY habref_corresp_taxon
    ADD CONSTRAINT fk_habref_corresp_tax_cd_hab_entre FOREIGN KEY (cd_hab_entre) REFERENCES ref_habitats.habref (cd_hab) ON UPDATE CASCADE;

-- ALTER TABLE ONLY habref_corresp_taxon
--     ADD CONSTRAINT fk_habref_corresp_tax_cd_nom FOREIGN KEY (cd_nom) REFERENCES taxonomie.taxref (cd_nom) ON UPDATE CASCADE;

ALTER TABLE ONLY cor_habref_terr_statut
    ADD CONSTRAINT fk_cor_habref_terr_statut_cd_hab FOREIGN KEY (cd_hab) REFERENCES ref_habitats.habref (cd_hab) ON UPDATE CASCADE;

ALTER TABLE ONLY cor_habref_terr_statut
    ADD CONSTRAINT fk_cor_habref_terr_statut_cd_statut_presence FOREIGN KEY (cd_statut_presence) REFERENCES ref_habitats.bib_habref_statuts (statut) ON UPDATE CASCADE;

ALTER TABLE ONLY cor_habref_description
    ADD CONSTRAINT fk_cor_habref_description_cd_hab FOREIGN KEY (cd_hab) REFERENCES ref_habitats.habref (cd_hab) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY cor_habref_description
    ADD CONSTRAINT fk_cor_habref_description_cd_hab_field FOREIGN KEY (cd_hab_field) REFERENCES ref_habitats.typoref_fields (cd_hab_field) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY cor_hab_source
    ADD CONSTRAINT fk_cor_cor_hab_source_cd_source FOREIGN KEY (cd_source) REFERENCES ref_habitats.habref_sources (cd_source) ON UPDATE CASCADE ON DELETE CASCADE;


----------
--UNIQUE--
----------

ALTER TABLE ONLY cor_list_habitat
    ADD CONSTRAINT unique_cor_list_habitat UNIQUE ( id_list, cd_hab );
