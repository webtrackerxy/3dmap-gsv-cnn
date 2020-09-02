
--
SELECT count(l.street_ena) as cc,street_ena FROM centreline_hongkongisland l, 
road_points_hongkongisland p WHERE l.objectid = p.road_objectid 
group by l.street_ena order by cc ASC

-- Table: pano_data
ALTER SEQUENCE pano_sequence RESTART WITH 1;

DROP TABLE pano_data;

CREATE TABLE pano_data
(
  objectid bigint NOT NULL,
  image_date date,
  pano_yaw_deg numeric,
  tilt_yaw_deg numeric,
  tilt_pitch_deg numeric,
  panoid character varying(255),
  zoomlevels integer,
  lat numeric,
  lng numeric,
  best_view_direction_deg numeric,
  depth_map text,
  geom geometry,
  CONSTRAINT pano_primary_key PRIMARY KEY (objectid)
)
WITH (
  OIDS=FALSE
);

-------------------------------------------
ALTER TABLE pano_data
  OWNER TO postgres;
-----
SELECT *, ST_GeometryType(geom) as type2 from centraline2 where ST_GeometryType(geom) = 'ST_CompoundCurve' 
SELECT  ST_GeometryType(geom) as type2 from centraline2 where ST_GeometryType(geom) = 'ST_LineString' 

-----

ALTER SEQUENCE road_sequence RESTART WITH 1;
DROP TABLE road_points_hongkongisland

CREATE TABLE road_points_hongkongisland AS
WITH line AS 
    (SELECT
        objectid as road_objectid,
        (ST_Dump(geom)).geom AS geom
    FROM centreline_hongkongisland where ST_GeometryType(geom) = 'ST_LineString'),
linemeasure AS
    (SELECT
		line.road_objectid as road_objectid,
        ST_AddMeasure(line.geom, 0, ST_Length(line.geom)) AS linem,
        generate_series(0, ST_Length(line.geom)::int, 5) AS i
    FROM line),
geometries AS (
    SELECT
        i,
        road_objectid,        
        (ST_Dump(ST_GeometryN(ST_LocateAlong(linem, i), 1))).geom AS geom 
    FROM linemeasure)
SELECT
    nextval('road_sequence') as objectid, 
    i as interval,
	road_objectid,
    ST_Transform(geom, 4326) as geom,
    ST_AsText(ST_Transform(geom, 4326)) as points
    
FROM geometries
-----
ALTER SEQUENCE road_sequence RESTART WITH 1;

CREATE TABLE road_points AS
WITH line AS 
    (SELECT
        objectid,
        (ST_Dump(geom)).geom AS geom
    FROM centreline where objectid = 7328),
linemeasure AS
    (SELECT
        ST_AddMeasure(line.geom, 0, ST_Length(line.geom)) AS linem,
        generate_series(0, ST_Length(line.geom)::int, 10) AS i
    FROM line),
geometries AS (
    SELECT
        i,
        (ST_Dump(ST_GeometryN(ST_LocateAlong(linem, i), 1))).geom AS geom 
    FROM linemeasure)
SELECT
    nextval('road_sequence') as objectid, 
    i as interval,
    ST_Transform(geom, 4326) as geom,
    ST_AsText(ST_Transform(geom, 4326)) as points
    
FROM geometries
--------------------------------

https://chartio.com/resources/tutorials/how-to-define-an-auto-increment-primary-key-in-postgresql/
CREATE SEQUENCE road_sequence
  start 1
  increment 1;



https://gis.stackexchange.com/questions/35462/how-can-i-get-the-geometry-length-in-meters



SELECT objectid, ST_AsText(ST_StartPoint(geom)) as start_ponit, ST_AsText(ST_EndPoint(geom)) as end_ponit, ST_Length(geom) as l from centreline order by l desc 




SELECT  ST_AsText(ST_Transform(geom, 4326))
FROM (
  SELECT (ST_DumpPoints(g.geom)).*
  FROM
    (SELECT
       geom from centreline where objectid = 7328
    ) AS g
  ) j;


SELECT  ST_AsText(geom)
FROM (
  SELECT (ST_DumpPoints(g.geom)).*
  FROM
    (SELECT
       geom from centreline where objectid = 7328
    ) AS g
  ) j;


https://gis.stackexchange.com/questions/88196/how-can-i-transform-polylines-into-points-every-n-metres-in-postgis
WITH line AS 
    (SELECT
        objectid,
        (ST_Dump(geom)).geom AS geom
    FROM centreline where objectid = 7328),
linemeasure AS
    (SELECT
        ST_AddMeasure(line.geom, 0, ST_Length(line.geom)) AS linem,
        generate_series(0, ST_Length(line.geom)::int, 10) AS i
    FROM line),
geometries AS (
    SELECT
        i,
        (ST_Dump(ST_GeometryN(ST_LocateAlong(linem, i), 1))).geom AS geom 
    FROM linemeasure)

SELECT
    i,
    ST_SetSRID(ST_MakePoint(ST_X(geom), ST_Y(geom)), 31468) AS geom
FROM geometries