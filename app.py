# Back-End server using Flask to create routes used to serve the dashboard.

from flask import Flask, render_template, jsonify, request, redirect, url_for, send_file, make_response
import pandas as pd
import numpy as np

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
    icon_width = 1.15*(1/(width/(2*radius)))
    icon_height = 1.1*(1/(height/(2*radius)))

    dimReduxProjectionsOverlapRemoved = DGrid(icon_width, icon_height, delta=1).fit_transform(cords)
    resultX = np.round(dimReduxProjectionsOverlapRemoved[:, 0], 3)
    resultY = np.round(dimReduxProjectionsOverlapRemoved[:, 1], 3)
    return resultX, resultY


def getTSNE(df, columns, width, height, radius):
    #TSNE projection
    tsne = TSNE(n_components=2, verbose=1,
                perplexity=40, n_iter=300, init='random', learning_rate="auto")
    tsneResult = tsne.fit_transform(df.loc[:, columns])
    tsneResult = np.round(MinMaxScaler().fit_transform(tsneResult), 3)
    tsneX, tsneY = tsneResult[:, 0], tsneResult[:, 1]
    tsneX_overlapRemoved, tsneY_overlapRemoved = DGridRemoveOverlap(tsneResult, width, height, radius)
    return tsneX, tsneY, tsneX_overlapRemoved, tsneY_overlapRemoved


def getPCA(df, columns, width, height, radius):
    #PCA projection
    pca = PCA(n_components=2)
    pcaResult = pca.fit_transform(df.loc[:, columns])
    pcaResult = np.round(MinMaxScaler().fit_transform(pcaResult), 3)
    pcaX, pcaY = pcaResult[:, 0], pcaResult[:, 1]
    pcaX_overlapRemoved, pcaY_overlapRemoved = DGridRemoveOverlap(pcaResult, width, height, radius)
    return pcaX, pcaY, pcaX_overlapRemoved, pcaY_overlapRemoved


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
    # Feature imporance score is measured by training an XGboost model.
    label = "variety"
    le = LabelEncoder().fit(df[label].values)
    df["label"] = le.transform(df[label].values)
    X, y = df.loc[:, columns], df.loc[:, "label"]
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05, random_state=42)
    X_train, y_train = X, y     #no test set, since all of the instances are needed to calculate the feature importance
    
    xgb_clf = xgb.XGBClassifier()
    xgb_clf.fit(X_train, y_train)
    #feature importance using XGboost model alone
    importanceScore = xgb_clf.feature_importances_

    #Permutation importance for feature evaluation using XGboost classifier. Works better in cases with test data, which is different that train data used for model fitting.
    # importanceScore = permutation_importance(xgb_clf, X_train, y_train).importances_mean

    importanceScore = np.round(importanceScore, 3)
    return dict(sorted(zip(columns, [str(x) for x in importanceScore])))


app = Flask(__name__, static_url_path='', static_folder='')


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html', title="Home", header="Home")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404


# Get a list of distinct Ids
@app.route('/getIds', methods=['GET'])
def getIds():
    featureData = pd.read_csv(os.path.join("data/rawData", featureFile))
    ids = featureData["id"].unique().tolist()
    return jsonify(ids)


@app.route('/dimReduceIds', methods=['POST'])
def dimReduceids():
    featureData = pd.read_csv(os.path.join("data/rawData", featureFile))

    if request.method == 'POST':
        content = request.get_json()
        columns = content["featureColumns"]
        width = content['width']
        height = content['height']
        radius = int(content["radius"])
        k = int(content["k"])
        toggleDimRedux = content["toggleDimRedux"]

        # dim reduction
        if toggleDimRedux == "tsne":
            x, y, x_overlapRemoved, y_overlapRemoved = getTSNE(featureData, columns, width, height, radius)
        elif toggleDimRedux == "pca":
            x, y, x_overlapRemoved, y_overlapRemoved = getPCA(featureData, columns, width, height, radius)
        
        cluster = getClusters(featureData, columns, k)    #KNN clustering
        for column in [ feature for feature in featureData.columns if feature not in ["id", "variety"]]:
            featureData["scaled_"+column] = np.round(featureData[column] / featureData[column].abs().max(), 3)

        featureData["x"], featureData["y"] = x, y
        featureData["x_overlapRemoved"], featureData["y_overlapRemoved"] = x_overlapRemoved, y_overlapRemoved
        featureData["cluster"] = cluster
        
        featureData.dropna(axis=1, how='all', inplace=True)
        featureData.to_csv(os.path.join(
            "data/processedData", featureFile), index=False, header=True)
        message = "status1:fileUpdated"
    return jsonify(message)


@app.route('/knnClustering', methods=["POST"])
def knnClustering():
    """
    This function is used to just calculate the k-nearest neighbours of the feature instances
    """
    featureData = pd.read_csv(os.path.join("data/processedData", featureFile))
    if request.method == 'POST':
        content = request.get_json()
        columns = content["featureColumns"]
        k = int(content["k"])

        cluster = getClusters(featureData, columns, k)    #KNN clustering
        featureData["cluster"] = cluster
        featureData.dropna(axis=1, how='all', inplace=True)
        featureData.to_csv(os.path.join(
            "data/processedData", featureFile), index=False, header=True)
        message = "status1:fileUpdated"

    return jsonify(message)


@app.route('/getProjections', methods=['GET'])
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


@app.route('/getAggFeatures', methods=['POST'])
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


# Sort features based on their feature importance: 
# Permutation Based Feature Importance using XGBoost is used to calculate feature importance
# https://mljar.com/blog/feature-importance-xgboost/
# https://explained.ai/rf-importance/
@app.route('/getFeatureImportance', methods=['POST'])
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
    app.run(port=5012, debug=True)