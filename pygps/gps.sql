/* 

### Create Postgis template with the following
$ POSTGIS_SQL_PATH=`pg_config --sharedir`/contrib/postgis-2.0
$ createdb -E UTF8 -T template0 template_postgis
$ createlang plpgsql template_postgis
$ psql -d template_postgis -f $POSTGIS_SQL_PATH/postgis.sql
$ psql -d template_postgis -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql 

$ psql -d template_postgis
# grant select, update, insert, delete on table geometry_columns to ajmendez;
# grant select on table spatial_ref_sys to ajmendez;

### Create user, and database
$ createuser -s -P ajmendez # superuser should not do this in production
$ createdb -T template_postgis -E UTF8 -O ajmendez ajmendez

psql -d pygps/gps.sql
*/

DROP TABLE IF EXISTS points;
CREATE TABLE points (
    altitude double precision,
    trackid integer NOT NULL,
    gpx_id bigint NOT NULL,
    "timestamp" timestamp NOT NULL
);
SELECT AddGeometryColumn( 'points', 'geom', 900913, 'POINT', 2 );

DROP TABLE IF EXISTS files;
CREATE TABLE files (
    id bigint NOT NULL,
    filename character varying(255) DEFAULT ''::character varying NOT NULL,
    name character varying(255) NOT NULL,
    "timestamp" timestamp NOT NULL
);
SELECT AddGeometryColumn( 'files', 'geom', 900913, 'POINT', 2 );

CREATE SEQUENCE files_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

ALTER SEQUENCE files_id_seq OWNED BY files.id;
ALTER TABLE files ALTER ID SET DEFAULT NEXTVAL('files_id_seq');

CREATE INDEX points_geom_idx ON points USING GIST ( geom );
