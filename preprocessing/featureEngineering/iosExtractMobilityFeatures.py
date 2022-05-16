"""
####################################################################################################
Script for extracting below mobility related features using IOS GPS data

Feature1(noOfStayPoints): Number of stay points
Feature2(locationVariance): Location variance
Feature3(entropy): Entropy
Feature4(normalizedEntropy): Normalized entropy
Feature5(homeStay): Homestay - percentage of time spent at home
Feature6(radiusOfGyration): Radius of Gyration

input/output file names need to be specifed in the code below #config
####################################################################################################
"""

from imports import *


def get_stayPoints(df, roaming_distance=50, minimum_stay=10, number_jobs=1):
    """
    method returns the total number of stay points for the given location points
    uses the logic used in Microsoft paper
    """
    # Parameters
    roaming_distance = meters2degrees(roaming_distance) # 50 meters converted to degrees
#     minimum_stay  # minimum of time that the participantId has to spend at a location to consider that as a stay point
#     number_jobs   # number of parallel jobs

    # Set index 
    df = df.reset_index().set_index(["participantId", "timestamp"])

    # Call helper-function to process entire df in one go
    df_stops = process_data(df=df, 
                            roam_dist=roaming_distance, 
                            min_stay=minimum_stay, 
                            n_jobs=number_jobs,
                            print_output="notebook")
    df_stops = pd.concat(df_stops)

    # Only keep users with more than one stop
    df_stops = (df_stops
        .groupby("participantId").filter(lambda x: len(x) > 1)
        .set_index(["participantId"]))

    return df_stops


def get_clusters(df_stops, linkage_method = 'complete', distance=100):
    """
    method returns the total number of clusters for the given stay points for the given location points
    uses the logic used in Microsoft paper
    need to see if i can merge this with above method
    """
    # Clustering parameters
    # linkage_method = 'centroid'/'complete'
    distance = meters2degrees(distance)

    # Cluster stoplocations on a per user basis
    df_clusters = (df_stops.groupby('participantId')
                  .apply(lambda x: 
                         cluster_stoplocations(x, linkage_method, distance))
                  .reset_index())

    return df_clusters


def getIosMobilityFeatures(dataPath, featurePath):
    print("Begin extraction - Mobility features")

    # config
    # dataFilename = "Location_decrypted.csv"
    dataFilename = "Location_decrypted_temp.csv"
    date = datetime.now().strftime("%Y%m%d_%I%M%S%p")
    featureFilename = "ios_mobility_features_" + dataPath.split("/")[-1] + "_" + date + ".csv"

    if not (os.path.exists(os.path.join(dataPath, dataFilename))):
        sys.exit(f"{dataFilename} file does not exist in {dataPath} folder \nscript aborted")

    # read file with a header
    location = pd.read_csv(os.path.join(dataPath, dataFilename), sep="|")

    #change time to Halifax time
    location["timestamp"] = pd.to_datetime(location["timestamp"], utc=True)
    location["timestamp"] = pd.to_datetime(location["timestamp"]).dt.tz_convert(tz='America/Halifax')
    location["timestamp"] = pd.to_datetime(location["timestamp"], utc=False)

    #add new columns to help extract features
    # location["date"] = pd.to_datetime(location["timestamp"]).dt.date
    # location["weekday"] = pd.to_datetime(location["timestamp"]).dt.weekday    # Monday=0, Sunday=6
    # location["time"] = pd.to_datetime(location["timestamp"]).dt.strftime('%H:%M:%S')

    # sort data, remove duplicates and drop unecessary columns
    location = location.sort_values(["participantId", "timestamp"]).reset_index(drop=True)
    location.drop_duplicates(subset=["participantId", "timestamp", "latitude", "longitude", "address"], keep="last", inplace=True)
    location.drop(["id", "attribute", "address", "uploadtimestamp"], axis=1, inplace=True)

    df_stops = get_stayPoints(location)
    df_clusters = get_clusters(df_stops)

    df_clusters = df_clusters.sort_values(["participantId", "timestamp"]).reset_index(drop=True)

    df_clusters["duration"] = (df_clusters["t_end"] - df_clusters["t_start"]).astype('timedelta64[m]')
    df_clusters["date"] = pd.to_datetime(df_clusters["timestamp"]).dt.date
    df_clusters["weekday"] = pd.to_datetime(df_clusters["timestamp"]).dt.weekday    # Monday=0, Sunday=6

    # columns=["participantId", "date", "weekday", "noOfStayPoints", "locationVariance", "entropy", "normalizedEntropy", "homeStay", "radiusOfGyration"]
    mobilityFeatures = pd.DataFrame()

    # get no of Stay points in a day
    mobilityFeatures[["participantId", "date", "weekday", "noOfStayPoints"]] = df_clusters.groupby(["participantId", "date", "weekday"]).size().reset_index(name="noOfStayPoints")
    
    # get Location Variance
    df_locationVariance = df_clusters.groupby(["participantId", "date"]).apply(lambda x: np.log10(x["latitude"].var()**2 + x["longitude"].var()**2)).reset_index(name="locationVariance")
    mobilityFeatures = pd.merge(mobilityFeatures, df_locationVariance, on=["participantId", "date"], how="left")
    
    # get cluster where max time is spent i.e. Home
    df_home = df_clusters.groupby(["participantId", "cluster_assignment"])["duration"].sum().reset_index()
    df_home_temp = df_home.groupby(["participantId"])["duration"].max().reset_index()
    df_home = pd.merge(df_home, df_home_temp[["participantId", "duration"]], on=["participantId", "duration"], how="inner")
    df_home["home"] = 1
    df_home.drop("duration", axis=1, inplace=True)

    #  get homestay
    df_clusters = pd.merge(df_clusters, df_home, on=["participantId", "cluster_assignment"], how="left")
    df_clusters.fillna(0, inplace=True)

    df_home_stay = df_clusters.loc[df_clusters["home"]==1, :].groupby(["participantId", "date"])["duration"].sum().reset_index(name="homeStay")
    df_home_stay["homeStay"] = round(df_home_stay["homeStay"] * 100 / (24*60), 2)

    mobilityFeatures = pd.merge(mobilityFeatures, df_home_stay, on=["participantId", "date"], how="left")
    
    # Entropy
    df_entropy = df_clusters.groupby(["participantId", "date"])["duration"].apply(lambda x : sum(x*np.log10(x))).reset_index(name="entropy")
    mobilityFeatures = pd.merge(mobilityFeatures, df_entropy, on=["participantId", "date"], how="left")
    
    # Normalized Entropy
    df_N = df_clusters.groupby(["participantId", "date"])["cluster_assignment"].size().reset_index(name="N")
    mobilityFeatures = pd.merge(mobilityFeatures, df_N, on=["participantId", "date"], how="left")
    
    mobilityFeatures["normalizedEntropy"] = mobilityFeatures["entropy"] / mobilityFeatures["N"]
    mobilityFeatures.drop("N", axis=1, inplace=True)


    # Get medoid of each destination (cluster)
    df_clustermedoids = (df_clusters.groupby('participantId')
        .apply(lambda x: get_clustermedoids(x))
        .reset_index(drop=True))

    # Compute stop counts at each destination
    df_clustersizes = (df_clusters
                    .groupby(['participantId', 'date', 'cluster_assignment'])
                    .apply(lambda x: len(x))
                    .reset_index(name='count'))

    # Merge medoids and counts
    df_destinations = pd.merge(df_clustermedoids.loc[:,['participantId', 'date', 'timestamp',
                                                    'latitude', 'longitude',
                                                    'cluster_assignment']], 
                                df_clustersizes, 
                                on=['participantId', 'date', 'cluster_assignment'], 
                                how='left')

    # Export and preview data
    # df_destinations

    # Cluster stoplocations on a per user basis
    df_rgyration = (df_destinations
                    .loc[:,['participantId', 'date', 'longitude', 'latitude', 'count']]
                    .groupby(['participantId', 'date'])
                    .apply(lambda x: rgiration_at_k(x, k=None))
                    .reset_index())

    df_rgyration.columns = ['participantId', 'date', 'radius_gyration']

    mobilityFeatures = pd.merge(mobilityFeatures, df_rgyration, on=["participantId", "date"], how="left")

    # saving the file
    mobilityFeatures.to_csv(os.path.join(featurePath, featureFilename), header=True, index=False)

    print("Extraction of Mobility features compelted")


if __name__ == "__main__":
    # config
    dataPath1 = "/csv/backup_frigg1"
    dataPath2 = "/csv/backup"
    featurePath = "/csv/features"
    
    # processing data from DB1
    strTime = time.time()
    getIosMobilityFeatures(dataPath1, featurePath)
    endTime = time.time()
    print(f"run time: {round((endTime - strTime)/60, 2)}")

    # processing data from DB2
    strTime = time.time()
    getIosMobilityFeatures(dataPath2, featurePath)
    endTime = time.time()
    print(f"run time: {round((endTime - strTime)/60, 2)}")