# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img
# MAGIC     src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png"
# MAGIC     alt="Databricks Learning"
# MAGIC   >
# MAGIC </div>
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Building Semantic Models in Databricks with UC metric views
# MAGIC
# MAGIC In this course, you’ll learn how to empower your data consumers to get validated business insights with less burden on you and the rest of your enterprise's data and AI team. Through building a semantic layer on top of your gold layer, you'll offer decision makers and business analysts the opportunity to explore key business performance indicators in novel ways, while still maintaining efficient data operations and enterprise-vetted metrics.
# MAGIC
# MAGIC ------
# MAGIC
# MAGIC ### Prerequisites
# MAGIC You should meet the following prerequisites before starting this course:
# MAGIC
# MAGIC - Ability to compose queries using Databricks SQL
# MAGIC - Understanding of Databricks data modeling concepts
# MAGIC
# MAGIC ---
# MAGIC ### Course Agenda
# MAGIC The following modules are part of the **Data Warehousing Learning** Path by Databricks Academy.
# MAGIC | # | Notebook Name |
# MAGIC | --- | --- |
# MAGIC | 1 | [Create a Simple Metric View]($./1 Demo - Create a Simple Metric View) |
# MAGIC | 2 | [Consume a Simple Metric View]($./2 Demo - Consume a Simple Metric View) |
# MAGIC | 3L | [Create and Consume a Simple Metric View]($./3 Lab - Create and Consume a Simple Metric View) |
# MAGIC | 4 | [Define and Use Computed and Composed Measures]($./4 Demo - Define and Use Computed and Composed Measures) |
# MAGIC | 5 | [Define and Use Window Measures]($./5 Demo - Define and Use Window Measures) |
# MAGIC | 6L | [Define Composed and Windowed Measures]($./6 Lab - Define Composed and Windowed Measures) |
# MAGIC | 7L | [Summative Experience]($./7 Lab - Summative Experience) |
# MAGIC
# MAGIC --- 
# MAGIC
# MAGIC ### Requirements
# MAGIC
# MAGIC Please review the following requirements before starting the lesson:
# MAGIC
# MAGIC * To run demo and lab notebooks, you need to use the following Databricks runtime: **`16.4.x-scala2.12`**
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC &copy; 2026 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="_blank">Apache Software Foundation</a>.<br/><br/><a href="https://databricks.com/privacy-policy" target="_blank">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use" target="_blank">Terms of Use</a> | <a href="https://help.databricks.com/" target="_blank">Support</a>
