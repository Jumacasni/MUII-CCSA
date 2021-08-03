import pyspark.sql.functions as func
from pyspark import SparkContext, SparkConf, SQLContext
from pyspark.sql.types import IntegerType
from pyspark.mllib.evaluation import MulticlassMetrics
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.classification import RandomForestClassifier, DecisionTreeClassifier, GBTClassifier
from pyspark.ml.tuning import TrainValidationSplit, ParamGridBuilder
from pyspark.ml.feature import VectorAssembler

title = "Práctica 4 - Juan Manuel Castillo Nievas" # Título para la configuración de Spark
name_file="/vol_exchange/filteredC.small.training" # Fichero del conjunto de datos
columns= ['PredSA_central', 'PSSM_r2_0_K', 'PSSM_r2_1_G', 'PSSM_r1_1_H', 'PSSM_r2_0_E', 'PredRCH_r1_-4'] # Mis columnas
train_sample = 0.7 # Partición del conjunto de entrenamiento
test_sample = 0.3 # Partición del conjunto de test

def predictions(estimator, paramGrid, train, test):
    ''' Evaluación del modelo creado: accuracy y AUC '''

    train_validator = TrainValidationSplit(estimator=estimator,
                                            estimatorParamMaps=paramGrid,
                                            evaluator=BinaryClassificationEvaluator(),
                                            trainRatio=train_sample,
                                            seed=5000)
    model = train_validator.fit(train)
    predictions = model.transform(test)

    # Convierto `prediction` y `label` a float, de lo contrario no funciona
    pred_and_label = predictions.select("prediction","label")
    pred_and_label = pred_and_label.withColumn("prediction", func.round(pred_and_label['prediction']).cast('float'))
    pred_and_label = pred_and_label.withColumn("label", func.round(pred_and_label['label']).cast('float'))

    metrics=MulticlassMetrics(pred_and_label.rdd.map(tuple))

    evaluator = BinaryClassificationEvaluator()

    auc = evaluator.evaluate(predictions)
    accuracy = round(metrics.accuracy*100, 3)

    print("Accuracy %s" % accuracy)
    print("AUC %s" % auc)

def random_forest_1(train, test):
    ''' Modelo de clasificación Random Forest versión 1 '''

    rf = RandomForestClassifier(labelCol="label", featuresCol="features")

    paramGridRF = (ParamGridBuilder()
                    .addGrid(rf.maxDepth, [2, 5, 10])
                    .addGrid(rf.maxBins, [5, 10, 20])
                    .addGrid(rf.numTrees, [5, 20, 50])
                    .build())

    predictions(rf,paramGridRF,train,test)

def random_forest_2(train, test):
    ''' Modelo de clasificación Random Forest versión 2 '''

    rf = RandomForestClassifier(labelCol="label", featuresCol="features")

    paramGridRF = (ParamGridBuilder()
                    .addGrid(rf.maxDepth, [2, 4, 6])
                    .addGrid(rf.maxBins, [10, 20, 30])
                    .addGrid(rf.numTrees, [10, 30, 50])
                    .build())

    predictions(rf,paramGridRF,train,test)
    
def decision_tree_1(train, test):
    ''' Modelo de clasificación Decision Tree versión 1 '''

    dt = DecisionTreeClassifier(labelCol="label", featuresCol="features")

    dtparamGrid = (ParamGridBuilder()
                    .addGrid(dt.maxDepth, [2, 5, 10, 20, 30])
                    .addGrid(dt.maxBins, [10, 20, 40, 80, 100])
                    .build())

    predictions(dt,dtparamGrid,train,test)

def decision_tree_2(train, test):
    ''' Modelo de clasificación Decision Tree versión 2 '''

    dt = DecisionTreeClassifier(labelCol="label", featuresCol="features")

    dtparamGrid = (ParamGridBuilder()
                    .addGrid(dt.maxDepth, [2, 5, 10, 15, 20])
                    .addGrid(dt.maxBins, [10, 20, 30, 40, 50])
                    .build())

    predictions(dt,dtparamGrid,train,test)

def gradient_boosted_1(train, test):
    ''' Modelo de clasificación Gradient-Boosted Tree versión 1 '''

    gb = GBTClassifier(labelCol="label", featuresCol="features")

    gbparamGrid = (ParamGridBuilder()
                     .addGrid(gb.maxDepth, [2, 5, 10])
                     .addGrid(gb.maxBins, [10, 20, 40])
                     .addGrid(gb.maxIter, [5, 10, 20])
                     .build())
    
    predictions(gb,gbparamGrid,train,test)

def gradient_boosted_2(train, test):
    ''' Modelo de clasificación Gradient-Boosted Tree versión 2 '''

    gb = GBTClassifier(labelCol="label", featuresCol="features")
    
    gbparamGrid = (ParamGridBuilder()
                     .addGrid(gb.maxDepth, [2, 3, 5])
                     .addGrid(gb.maxBins, [10, 20, 30])
                     .addGrid(gb.maxIter, [2, 5, 10])
                     .build())
    
    predictions(gb,gbparamGrid,train,test)

def configurate_spark(title):
    ''' Configuración de Spark. Inicializa SQLContext para las funcionalidades SQL (leer csv) '''

    conf = SparkConf().setAppName(title)
    context = SparkContext.getOrCreate(conf=conf)
    sql_context = SQLContext(context)

    return sql_context

def delete_null_rows(df):
    ''' Eliminación de valores perdidos '''

    return df.dropna()

def undersampling(df):
    ''' Aplicación de la técnica de undersampling '''

    pos = df.filter(df['class']==0)
    neg = df.filter(df['class']==1)

    total_pos = pos.count()
    total_neg = neg.count()

    if total_pos > total_neg:
        fr = float(total_neg)/float(total_pos)
        sampled = pos.sample(withReplacement=False, fraction=fr)
        return sampled.union(neg)
    else:
        fr = float(total_pos)/float(total_neg)
        sampled = neg.sample(withReplacement=False, fraction=fr)
        return sampled.union(pos)

def preprocessing(df):
    ''' Preprocesamiento del conjunto de datos '''

    df = delete_null_rows(df)

    df = undersampling(df)

    return df

if __name__ == "__main__":
    sql_context = configurate_spark(title)

    # Leer datos del csv
    df = sql_context.read.csv(name_file, sep=",", header=True, inferSchema=True)

    # Todas las variables de tipo Integer
    print(df.dtypes)
    df = df.withColumn("PredRCH_r1_-4", df["PredRCH_r1_-4"].cast(IntegerType())) 
    print(df.dtypes)

    # Clases positivas y negativas antes del preprocesamiento
    pos = df.filter(df['class']==0)
    neg = df.filter(df['class']==1)
    total_pos = pos.count()
    total_neg = neg.count()
    print("\n\nClases positivas/Clases negativas antes del preprocesamiento: %s / %s \n\n" % (total_pos, total_neg))

    # Preprocesamiento de datos
    df = preprocessing(df)

    # Clases positivas y negativas después del preprocesamiento
    pos = df.filter(df['class']==0)
    neg = df.filter(df['class']==1)
    total_pos = pos.count()
    total_neg = neg.count()
    print("\n\nClases positivas/Clases negativas despues del preprocesamiento: %s / %s \n\n" % (total_pos, total_neg))

    # Partición del conjunto de entrenamiento y test
    df_train, df_test = df.randomSplit([train_sample, test_sample])

    assembler = VectorAssembler(inputCols=columns, outputCol='features')
    training_data = assembler.transform(df_train).select("features","class").withColumnRenamed("class","label")
    test_data = assembler.transform(df_test).select("features","class").withColumnRenamed("class","label")

    # Técnicas de clasificación usadas

    # random_forest_1(training_data, test_data)
    # random_forest_2(training_data, test_data)
    
    # decision_tree_1(training_data, test_data)
    # decision_tree_2(training_data, test_data)

    gradient_boosted_1(training_data, test_data)
    # gradient_boosted_2(training_data, test_data)