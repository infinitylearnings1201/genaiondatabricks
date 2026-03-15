# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
# MAGIC </div>
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC # Pipeline Deployment
# MAGIC
# MAGIC In this demo, we will show how to use a model as part of a data pipeline for inference. In the first section of the demo, we will prepare data and perform some basic feature engineering. Then, we will fit and register the model to model registry. Please note that these two steps are already covered in other courses and they are not the main focus of this demo. In the last section, which is the main focus of this demo, we will create a Lakeflow Declarative (FKA Delta Live Tables or DLT) pipeline and use the registered model as part of the pipeline. 
# MAGIC
# MAGIC **Learning Objectives:**
# MAGIC
# MAGIC *By the end of this demo, you will be able to;*
# MAGIC
# MAGIC * Describe steps for deploying a model within a pipeline.
# MAGIC
# MAGIC * Develop a simple pipeline that performs batch inference in its final step.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## REQUIRED - SELECT CLASSIC COMPUTE
# MAGIC Before executing cells in this notebook, please select your classic compute cluster in the lab. Be aware that **Serverless** is enabled by default.
# MAGIC
# MAGIC Follow these steps to select the classic compute cluster:
# MAGIC 1. Navigate to the top-right of this notebook and click the drop-down menu to select your cluster. By default, the notebook will use **Serverless**.
# MAGIC
# MAGIC 2. If your cluster is available, select it and continue to the next cell. If the cluster is not shown:
# MAGIC
# MAGIC    - Click **More** in the drop-down.
# MAGIC    
# MAGIC    - In the **Attach to an existing compute resource** window, use the first drop-down to select your unique cluster.
# MAGIC
# MAGIC **NOTE:** If your cluster has terminated, you might need to restart it in order to select it. To do this:
# MAGIC
# MAGIC 1. Right-click on **Compute** in the left navigation pane and select *Open in new tab*.
# MAGIC
# MAGIC 2. Find the triangle icon to the right of your compute cluster name and click it.
# MAGIC
# MAGIC 3. Wait a few minutes for the cluster to start.
# MAGIC
# MAGIC 4. Once the cluster is running, complete the steps above to select your cluster.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Requirements
# MAGIC
# MAGIC Please review the following requirements before starting the lesson:
# MAGIC
# MAGIC * To run this notebook, you need to use one of the following Databricks runtime(s): **16.4.x-cpu-ml-scala2.12**

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Classroom Setup
# MAGIC
# MAGIC Before starting the demo, run the provided classroom setup script. This script will define configuration variables necessary for the demo. Execute the following cell:

# COMMAND ----------

# MAGIC %run ../Includes/Classroom-Setup-3.1a

# COMMAND ----------

# MAGIC %md
# MAGIC **Other Conventions:**
# MAGIC
# MAGIC Throughout this demo, we'll refer to the object `DA`. This object, provided by Databricks Academy, contains variables such as your username, catalog name, schema name, working directory, and dataset locations. Run the code block below to view these details:

# COMMAND ----------

print(f"Username:          {DA.username}")
print(f"Catalog Name:      {DA.catalog_name}")
print(f"Schema Name:       {DA.schema_name}")
print(f"Working Directory: {DA.paths.working_dir}")
print(f"User DB Location:  {DA.paths.datasets}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Preparation
# MAGIC
# MAGIC For this demonstration, we will utilize a fictional dataset from a Telecom Company, which includes customer information. This dataset encompasses **customer demographics**, including gender, as well as internet subscription details such as subscription plans and payment methods.
# MAGIC
# MAGIC After loading the dataset, we will perform simple **data cleaning and feature selection**. 
# MAGIC
# MAGIC In the final step, we will split the dataset into **features** and **response** sets.

# COMMAND ----------

from pyspark.sql.functions import col

# Load dataset with spark
shared_volume_name = 'telco' # From Marketplace
csv_name = 'telco-customer-churn-missing' # CSV file name
dataset_p_telco = f"{DA.paths.datasets.telco}/{shared_volume_name}/{csv_name}.csv" # Full path

# Dataset specs
primary_key = "customerID"
response = "Churn"
features = ["SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"] # Keeping numerical only for simplicity and demo purposes

# Read dataset (and drop nan)
telco_df = spark.read.csv(dataset_p_telco, inferSchema=True, header=True, multiLine=True, escape='"')\
            .withColumn("TotalCharges", col("TotalCharges").cast('double'))\
            .na.drop(how='any')

# Separate features and ground-truth
features_df = telco_df.select(primary_key, *features)
response_df = telco_df.select(primary_key, response)

# Train a sklearn Decision Tree Classification model
# Convert data to pandas dataframes
X_train_pdf = features_df.drop(primary_key).toPandas()
Y_train_pdf = response_df.drop(primary_key).toPandas()

for col in X_train_pdf.select_dtypes("int32"):
    X_train_pdf[col] = X_train_pdf[col].astype("double")

# COMMAND ----------

print(X_train_pdf.info())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Model Preparation
# MAGIC
# MAGIC **Note:** This section is not the main focus of this course. We are just repeating the model development and registration process here.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ### Setup Model Registry with UC
# MAGIC
# MAGIC Before we start model deployment, we need to fit and register a model. In this demo, **we will log models to Unity Catalog**, which means first we need to setup the **MLflow Model Registry URI**.

# COMMAND ----------

import mlflow

# Point to UC model registry
mlflow.set_registry_uri("databricks-uc")
client = mlflow.MlflowClient()


def get_latest_model_version(model_name):
    """Helper function to get latest model version"""
    model_version_infos = client.search_model_versions("name = '%s'" % model_name)
    return max([model_version_info.version for model_version_info in model_version_infos])

# COMMAND ----------

# MAGIC %md
# MAGIC ### Fit and Register a Model with UC

# COMMAND ----------

from sklearn.tree import DecisionTreeClassifier
from mlflow.models import infer_signature

# Use 3-level namespace for model name
model_name = f"{DA.catalog_name}.{DA.schema_name}.ml_model" 

alias_name = "pipeline"

# model to use for classification
clf = DecisionTreeClassifier(max_depth=4, random_state=10)

with mlflow.start_run(run_name="Model-Deployment demo") as mlflow_run:

    # Enable automatic logging of input samples, metrics, parameters, and models
    mlflow.sklearn.autolog(
        log_input_examples=True,
        log_models=False,
        log_post_training_metrics=True,
        silent=True)
    
    clf.fit(X_train_pdf, Y_train_pdf)

    # Log model and push to registry
    signature = infer_signature(X_train_pdf, Y_train_pdf)
    mlflow.sklearn.log_model(
        clf,
        artifact_path="decision_tree",
        signature=signature,
        registered_model_name=model_name
    )

    # Set model alias
    client.set_registered_model_alias(model_name, alias_name, get_latest_model_version(model_name))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configure Pipeline to Run Batch Inference
# MAGIC
# MAGIC Now that our model is registered and ready, we can move on the most important part; using the model for inference inside a pipeline. 
# MAGIC
# MAGIC **Note: The pipeline is already defined in `3.1b` notebook.**
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Config Variables
# MAGIC
# MAGIC While defining the pipeline, you will need to use the following variables. Run the code block below first. Then, use the output in the next section while creating the pipeline.
# MAGIC

# COMMAND ----------

print(f"mlpipeline.bronze_dataset_path: {dataset_p_telco}")
print(f"mlpipeline.model_name: {model_name}")
print(f"mlpipeline.model_alias: {alias_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create the ETL Pipeline
# MAGIC This Vocareum environment has be configured so that **Lakeflow Declarative Pipelines** has been enabled (this feature is currently in Beta). 
# MAGIC > ****Note:**** To enable the Lakeflow Pipelines Editor: Open your user settings, go to Developer, and enable ****Lakeflow Pipelines Editor****.
# MAGIC ### Instructions
# MAGIC 1. Navigate to **Jobs & Pipelines** on the left side menu and click on **ETL pipeline** card at the top of the screen. 
# MAGIC 2. Give the Pipeline the name `<labuserXXXXXXXX_XXXXXXXXXX>-pipeline`, where you need to replace `<labuserXXXXXXXX_XXXXXXXXXX>` with your labuser name.
# MAGIC     - Click on the profile icon at the top right to copy your labuser name or see the output to cell 8 above.
# MAGIC 3. Make sure the catalog `dbacademy` is selected. 
# MAGIC 4. Select your labuser schema, which is of the form `<labuserXXXXXXXX_XXXXXXXXXX>`. 
# MAGIC 5. Select **Add existing assets** near the bottom under **Advanced options** 
# MAGIC </br>
# MAGIC <img src="../Includes/Images/etl-pipeline-1.png" width="500"/>
# MAGIC </br>
# MAGIC 6. In **Pipeline root folder**, and search for and select the folder **M03 - Pipeline Deployment/Pipeline**. 
# MAGIC 7. In **Source code paths**, click on the folder icon and select **3.1b Demo - Inference Pipeline** and click **Select**. 
# MAGIC 8. Back in the **Add existing assets** select **Add** at the bottom right. 
# MAGIC 9. Click on the **Pipeline** menu item at the top left and select the notebook **3.1b Demo - Inference Pipeline**. 
# MAGIC 10. This new editor will display the notebook in the center of the screen and the **Pipeline graph** on the right of the screen. We will need to configure the variables shown in the notebook **3.1b Demo - Inference Pipeline** in the **Pipeline settings**. To do this, click on the **settings** icon next to **Pipeline configuration** to open the pipeline settings. Then, scroll down to the **Configuration** section and click **Add configuration** to set up the necessary variables for the pipeline.
# MAGIC </br>
# MAGIC <img src="../Includes/Images/add-config.png" width="500"/>
# MAGIC </br>
# MAGIC 11. The config variable values are defined in the section **Config Variables** in this notebook (**3.1a Demo - Pipeline Deployment**). Copy and paste the key-value pair into the configuration and click **Save**. 
# MAGIC </br>
# MAGIC <img src="../Includes/Images/kv-pair.png" width="500"/>
# MAGIC </br>
# MAGIC 12. Back in **Pipeline settings**, navigate to and click **Dry run** at the top right. 
# MAGIC     - Dry-run mode allows you to test your policy configuration and monitor outbound connections without disrupting access to resources. This will not create or update any tables. 
# MAGIC 13. Once the dry run is is completed, click **Run pipeline**. This will now create or update any tables in our pipeline. 
# MAGIC
# MAGIC > Note we did not use classic compute for this pipeline run. We left **Serverless** as our compute by default.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Additional Resources and Trainings
# MAGIC This demo is not a comprehensive introduction to **Lakeflow Declarative Pipelines**. For a deeper dive into this Databricks feature, check out our course **[Build Data Pipeline with Lakeflow Declarative Pipelines](https://www.databricks.com/training/catalog?search=lakeflow+declarative+pipelines)**.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusion
# MAGIC
# MAGIC In this demonstration, we walked through the sequential process of training, registering, and deploying a model within a pipeline. Following the standard procedure of fitting and registering the model, we then established a Delta Live Tables pipeline. This pipeline not only ingests data from a source file but also implements necessary data transformations, culminating in the utilization of the registered model as the final step in the pipeline. While your specific project requirements may vary, this example illustrates how to set up and integrate a model for inference within the Delta Live Tables pipeline.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>
