-- Databricks notebook source
-- MAGIC %run ./Classroom-Setup-Common

-- COMMAND ----------

USE CATALOG IDENTIFIER(DA.catalog_name);
USE SCHEMA default;

-- create order_details to match the one created with UI

CREATE OR REPLACE VIEW order_details
(
 order_ID,
 order_date,
 shipping_mode,
 ship_date,
 total_item_count,
 total_distinct_orders
) WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
source: samples.tpch.lineitem
joins:
   - name: orders
     source: samples.tpch.orders
     on: orders.o_orderkey = source.l_orderkey
     joins:
     - name: customers
       source: samples.tpch.customer
       on: orders.o_custkey = customers.c_custkey
filter: YEAR(orders.o_orderdate) > 1994
measures:
  - name: total_item_count
    expr: COUNT(source.l_orderkey)
    display_name: Total Item Count
  - name: total_distinct_orders
    expr: COUNT(DISTINCT source.l_orderkey)
    display_name: Total Distinct Orders
dimensions:
  - name: order_ID
    expr: orders.o_orderkey
    display_name: Order ID
    synonyms:
      - order identifier
      - receipt number
  - name: shipping_mode
    expr: source.l_shipmode
    display_name: Shipping Mode
  - name: order_date
    expr: orders.o_orderdate
    display_name: Order Date
    format:
      type: date
      date_format: year_month_day
      leading_zeros: false
  - name: shipping_date
    expr: source.l_shipdate
    display_name: Shipping Date
    format:
      type: date
      date_format: year_month_day
      leading_zeros: false
$$ ;
-- create order_details2 to match the one created with SQL Editor

CREATE OR REPLACE VIEW order_details2
(
 order_ID,
 order_date,
 shipping_mode,
 ship_date,
 total_item_count,
 total_distinct_orders
) WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
source: samples.tpch.lineitem
joins:
   - name: orders
     source: samples.tpch.orders
     on: orders.o_orderkey = source.l_orderkey
     joins:
     - name: customers
       source: samples.tpch.customer
       on: orders.o_custkey = customers.c_custkey
filter: YEAR(orders.o_orderdate) > 1994
measures:
  - name: total_item_count
    expr: COUNT(source.l_orderkey)
    display_name: Total Item Count
  - name: total_distinct_orders
    expr: COUNT(DISTINCT source.l_orderkey)
    display_name: Total Distinct Orders
dimensions:
  - name: order_ID
    expr: orders.o_orderkey
    display_name: Order ID
    synonyms:
      - order identifier
      - receipt number
  - name: shipping_mode
    expr: source.l_shipmode
    display_name: Shipping Mode
  - name: order_date
    expr: orders.o_orderdate
    display_name: Order Date
    format:
      type: date
      date_format: year_month_day
      leading_zeros: false
  - name: shipping_date
    expr: source.l_shipdate
    display_name: Shipping Date
    format:
      type: date
      date_format: year_month_day
      leading_zeros: false
$$ ;
