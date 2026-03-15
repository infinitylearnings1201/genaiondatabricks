# Databricks notebook source
# MAGIC %sql
# MAGIC USE CATALOG IDENTIFIER(DA.catalog_name);
# MAGIC USE SCHEMA IDENTIFIER(DA.schema_name);
# MAGIC CREATE OR REPLACE TABLE lineitem CLONE `samples`.`tpch`.`lineitem`;
