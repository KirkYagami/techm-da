from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("GUI Test").getOrCreate()

data = [("Spark", 1), ("Dataproc", 2), ("Iceberg", 3)]
df = spark.createDataFrame(data, ["Tech", "Id"])

df.show()
print(f"Row Count: {df.count()}")

spark.stop()