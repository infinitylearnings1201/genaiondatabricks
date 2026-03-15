-- Databricks notebook source
-- MAGIC %run ./Classroom-Setup-Common

-- COMMAND ----------

USE CATALOG IDENTIFIER(DA.catalog_name);
USE SCHEMA default;
DROP VIEW IF EXISTS order_details;
DROP VIEW IF EXISTS order_details2;
