-- Databricks notebook source
-- MAGIC %run ./Classroom-Setup-Common

-- COMMAND ----------

USE CATALOG IDENTIFIER(DA.catalog_name);
USE SCHEMA default;

CREATE OR REPLACE VIEW order_details
(
 order_ID,
 order_date,
 shipping_mode,
 ship_date,
 total_item_count,
 total_distinct_orders,
 average_discount_pct,
 item_return_rate_pct,
 order_year_quarter,
 order_status,
 order_delay,
 order_delay_status
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
  - name: average_discount_pct
    expr: AVG(source.l_discount)
    display_name: Average Discount (%)
    format:
      type: percentage
      decimal_places: 
        type: exact
        places: 2
  - name: item_return_rate_pct
    expr: |
          SUM(CASE WHEN source.l_returnflag = 'R' 
                 THEN 1
                 ELSE 0
            END) 
          / COUNT(*)
    display_name: Item Return Rate (%)
    format:
      type: percentage
      decimal_places: 
        type: exact
        places: 2
dimensions:
  - name: order_ID
    expr: orders.o_orderkey
    display_name: Order ID
  - name: order_date
    expr: orders.o_orderdate
    display_name: Order Date
    format:
      type: date
      date_format: year_month_day
      leading_zeros: false
  - name: shipping_mode
    expr: source.l_shipmode
    display_name: Shipping Mode
  - name: shipping_date
    expr: source.l_shipdate
    display_name: Shipping Date
    format:
      type: date
      date_format: year_month_day
      leading_zeros: false
  - name: order_year_quarter
    expr: CONCAT(YEAR(orders.o_orderdate), '-Q', QUARTER(orders.o_orderdate))
    display_name: Order Year Quarter
  - name: order_status
    expr: |
           CASE
           WHEN orders.o_orderstatus = "O" THEN "Open"
           WHEN orders.o_orderstatus = "P" THEN "Processing"
           WHEN orders.o_orderstatus = "F" THEN "Final"
           ELSE "Error"
           END
    display_name: Order Status
  - name: order_delay
    expr: DATEDIFF(source.l_shipdate,orders.o_orderdate)
    display_name: Order Delay in Days
  - name: order_delay_status
    expr: |
          CASE
             WHEN order_delay < 0 THEN "Item Shipped Before Order!"
             WHEN order_delay BETWEEN 0 AND 2 THEN "0-2 days"
             WHEN order_delay BETWEEN 2 AND 4 THEN "2-4 days"
             ELSE "5+ days"
          END
    display_name: Order Delay Status
$$ ;
