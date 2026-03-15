-- Databricks notebook source
-- THIS CREATE DA VARIABLE USING SQL WAREHOUSE FOR USER INFORMATION FROM THE META TABLE

-- Create a temp view storing information from the obs table.
CREATE OR REPLACE TEMP VIEW user_info AS
SELECT map_from_arrays(collect_list(replace(key,'.','_')), collect_list(value))
FROM dbacademy.ops.meta;

-- Create SQL dictionary var (map)
DECLARE OR REPLACE DA MAP<STRING,STRING>;

-- Set the temp view in the DA variable
SET VAR DA = (SELECT * FROM user_info);

DROP VIEW IF EXISTS user_info;
