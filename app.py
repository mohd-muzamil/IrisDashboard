from cProfile import label
from flask import Flask, render_template, jsonify, request, redirect, url_for, send_file, make_response
import pandas as pd
import os
import numpy as np
import json

# sklearn
from sklearn.neighbors import KNeighborsClassifier
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.inspection import permutation_importance
from sklearn.preprocessing import LabelEncoder

from removeOverlap.dgrid import *

# Data files
featureFile = "iris_data.csv"

def DGridRemoveOverlap(dimReduxProjections, width, height, radius):
    # Overlap removal of projections
    x = np.expand_dims(dimReduxProjections[:, 0], axis=1)
    y = np.expand_dims(dimReduxProjections[:, 1], axis=1)
    cords = np.concatenate((x, y), axis=1)
    icon_width = 1/(width/(2*radius))
    icon_height = 1/(height/(2*radius))

    dimReduxProjectionsOverlapRemoved = DGrid(icon_width, icon_height, delta=1).fit_transform(cords)
    resultX = np.round(dimReduxProjectionsOverlapRemoved[:, 0], 3)
    resultY = np.round(dimReduxProjectionsOverlapRemoved[:, 1], 3)
    return resultX, resultY


def getTSNE(df, columns, DGrid, width, height, radius):
    #TSNE projection
    tsne = TSNE(n_components=2, verbose=1,
                perplexity=40, n_iter=300, init='random', learning_rate="auto")
    tsneResult = tsne.fit_transform(df.loc[:, columns])
    tsneResult = np.round(MinMaxScaler().fit_transform(tsneResult), 3)
    if DGrid:
        tsneX, tsneY = DGridRemoveOverlap(tsneResult, width, height, radius)
    else:
        tsneX, tsneY = tsneResult[:, 0], tsneResult[:, 1]
    return tsneX, tsneY


def getPCA(df, columns, DGrid, width, height, radius):
    #PCA projection
    pca = PCA(n_components=2)
    pcaResult = pca.fit_transform(df.loc[:, columns])
    pcaResult = np.round(MinMaxScaler().fit_transform(pcaResult), 3)
    if DGrid:
        pcaX, pcaY = DGridRemoveOverlap(pcaResult, width, height, radius)
    else:
        pcaX, pcaY = pcaResult[:, 0], pcaResult[:, 1]
    return pcaX, pcaY


def getClusters(df, columns, k):
    # KNN clustering
    X = df.loc[:, columns]
    Y = df.loc[:, "variety"]
    clusters = []
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X, Y)
    clusters = knn.predict(X)
    return clusters


def getFeatureImportance(df, columns):
    label = "variety"
    le = LabelEncoder().fit(df[label].values)
    df["label"] = le.transform(df[label].values)
    X, y = df.loc[:, columns], df.loc[:, "label"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05, random_state=42)
    xgb_clf = xgb.XGBClassifier()
    # es = xgb.callback.EarlyStopping(
    #     rounds=2,
    #     abs_tol=1e-3,
    #     save_best=True,
    #     maximize=False,
    #     data_name="validation_0",
    #     metric_name="mlogloss",
    # )
    xgb_clf.fit(X_train, y_train)
    # perm_importance = permutation_importance(xgb_clf, X_test, y_test)
    # sorted_idx = perm_importance.importances_mean.argsort()
    importanceScore = np.round(xgb_clf.feature_importances_, 3)
    return dict(sorted(zip(columns, [str(x) for x in importanceScore])))


app = Flask(__name__, static_url_path='', static_folder='')
@app.route("/ping")
def hello_world():
    return jsonify("pong")


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html', title="Home", header="Home")


@app.route('/dimReduceIds', methods=['POST'])
def dimReduceids():
    global featureData

    featureData = pd.read_csv(os.path.join("data/rawData", featureFile))

    if request.method == 'POST':
        content = request.get_json()
        columns = content["featureColumns"]
        width = content['width']
        height = content['height']
        radius = int(content["radius"])
        k = int(content["k"])
        toggleDimRedux = content["toggleDimRedux"]
        toggleDGrid = content["toggleDGrid"]
        if len(columns)<2:  #in case of feature columns are selected in dropdown, consider only those
            columns = [col for col in list(featureData.columns) if col not in ["id", "variety"]]
            message = "status2:singleColumn"
        else:
            message = "status1:fileUpdated"

        # dim reduction
        if toggleDimRedux == "TSNE":
            x, y = getTSNE(featureData, columns, toggleDGrid, width, height, radius)
        elif toggleDimRedux == "PCA":
            x, y = getPCA(featureData, columns, toggleDGrid, width, height, radius)
        
        cluster = getClusters(featureData, columns, k)    #KNN clustering
        for column in [ feature for feature in featureData.columns if feature not in ["id", "variety"]]:
            featureData["scaled_"+column] = np.round(featureData[column] / featureData[column].abs().max(), 3)

        featureData["x"], featureData["y"] = x, y
        featureData["cluster"] = cluster
        
        featureData.to_csv(os.path.join(
            "data/processedData", featureFile), index=False, header=True)
    return jsonify(message)


@app.route('/fetchProjections', methods=['GET'])
def fetchProjections():
    """
    Return Data for Chart1: Personality scores that are used to make glyphs
    """
    if request.method == 'GET':
        featureData = pd.read_csv(os.path.join("data/processedData", featureFile))

        resp = make_response(featureData.to_csv(index=False))
        resp.headers["Content-Disposition"] = "attachment; filename=personalityScores.csv"
        resp.headers["Content-Type"] = "text/csv"
        return resp


@app.route('/fetchAggFeatures', methods=['POST'])
def fetchAggFeatures():
    """
    Returns Data for Parallel cordinate chart to visualize extracted features
    """
    if request.method == 'POST':
        content = request.get_json()
        id = content['id']

        featureData = pd.read_csv(os.path.join("data/rawData", featureFile))

        # rearraging the data such that selectedId is last in the index, this is useful to put selected data on the top using d3
        idx = featureData.index.tolist()
        index_to_shift = featureData.index[featureData["id"] == int(id)].tolist()[0]
        idx.pop(index_to_shift)
        featureData_new = featureData.reindex(idx + [index_to_shift])

        resp = make_response(featureData_new.to_csv(index=False))
        resp.headers["Content-Disposition"] = "attachment; filename=personalityScores.csv"
        resp.headers["Content-Type"] = "text/csv"
        return resp


# Get a list of distinct Ids
@app.route('/getIds', methods=['GET'])
def getIds():
    featureData = pd.read_csv(os.path.join("data/rawData", featureFile))
    ids = featureData["id"].unique().tolist()
    return jsonify(ids)

# Sort features based on their feature importance: 
# Permutation Based Feature Importance using XGBoost is used to calculate feature importance
# https://mljar.com/blog/feature-importance-xgboost/
# https://explained.ai/rf-importance/
@app.route('/featureImportance', methods=['POST'])
def featureImportance():
    """
    Returns a list of features sorted based on their importance to classify the dataset. 
    This will be used to sort features in parallel cord chart
    """
    if request.method == 'POST':
        content = request.get_json()
        columns = content["featureColumns"]

        featureData = pd.read_csv(os.path.join("data/rawData", featureFile))
        if len(columns)<=1:
            columns = [col for col in list(featureData.columns) if col not in ["id", "variety"]]
        featuresWithImportance = getFeatureImportance(featureData, columns)
        return jsonify(featuresWithImportance)


if __name__ == "__main__":
    app.run(port=5050, debug=True)