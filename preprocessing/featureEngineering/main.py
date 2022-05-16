"""

"""
from imports import *
from iosExtractScreenFeatures import *
from iosExtractCallingFeatures import *
# from iosExtractMobilityFeatures import *
from iosExtractSleepFeatures import *

def getFeatures(config):
    if (list(config.keys()) != ["path", "features", "values"] or len(config["path"]) != 2  or len(config["features"]) != 4 or len(config["values"]) != 4):
        print('Please enter config in below format/n {"features":["screen", "calling", "mobility", "sleep"], "values":"1111"}')
    else:
        dataPath = config["path"][0]
        featurePath = config["path"][1]

        if (config["features"][0] == "screen" and config["values"][0] == "1"):
            getIosScreenFeatures(dataPath, featurePath)
        if (config["features"][1] == "calling" and config["values"][1] == "1"):
            getIosCallingFeatures(dataPath, featurePath)
        if (config["features"][2] == "sleep" and config["values"][2] == "1"):
            getIosSleepFeatures(dataPath, featurePath)
        if (config["features"][3] == "mobility" and config["values"][3] == "1"):
            print("GPS data will not be processed at this point in time")
            # getIosMobilityFeatures(dataPath, featurePath)


def combineFeatures(featurePath, featureFiles, finalFeatureFilename):
    """
    method to combine all the features based on data and patricipant
    """
    # Filtered participants from another notebook : participants with more that 14days of data
    filteredParticipants = ['PROSITC1005', 'PROSITC1014', 'PROSITC1018', 'PROSITC1025', 'PROSITC1026', 'PROSITC1027', 'PROSITC1029', 'PROSITC1030', 'PROSITC1031', 'PROSITC1033', 'PROSITC1034', 'PROSITC1036', 'PROSITC1037', 'PROSITC1038', 'PROSITC1039', 'PROSITC1040', 'PROSITC1041', 'PROSITC1043', 'PROSITC1044', 'PROSITC1046', 'PROSITC1057', 'PROSITC1061', 'PROSITC1062', 'PROSITC1066', 'PROSITC1070', 'PROSITC1079', 'PROSITC1080', 'PROSITC1082', 'PROSITC1084', 'PROSITC1086', 'PROSITC1089', 'PROSITC1090', 'PROSITC1097', 'PROSITC1100', 'PROSITC1101', 'PROSITC1104', 'PROSITC1109', 'PROSITC1110', 'PROSITC1111', 'PROSITC1119', 'PROSITC1122', 'PROSITC1126', 'PROSITC1128', 'PROSITC1130', 'PROSITC1132', 'PROSITC1135', 'PROSITC1136', 'PROSITC1137', 'PROSITC1140', 'PROSITC1153', 'PROSITC1158', 'PROSITC1174', 'PROSITC1187', 'PROSITC1192', 'PROSITC1193', 'PROSITC1200', 'PROSITC1221', 'PROSITC1222', 'PROSITC1223', 'PROSITC1224', 'PROSITC1227', 'PROSITC1237', 'PROSITC1240', 'PROSITC1244', 'PROSITC1261', 'PROSITC1272', 'PROSITC1293', 'PROSITC1297', 'PROSITC1299', 'PROSITC1304', 'PROSITC1308', 'PROSITC1317', 'PROSITC1325', 'PROSITC1326', 'PROSITC1343', 'PROSITC1369', 'PROSITC1372', 'PROSITC1379', 'PROSITC1412', 'PROSITC1413', 'PROSITC1422', 'PROSITC1424', 'PROSITC1428', 'PROSITC1438', 'PROSITC1493', 'PROSITC1501', 'PROSITC1502', 'PROSITC1512', 'PROSITC1516', 'PROSITC1526', 'PROSITC1529', 'PROSITC1548', 'PROSITC1550', 'PROSITC1553', 'PROSITC1555', 'PROSITC1562', 'PROSITC1564', 'PROSITC1570', 'PROSITC1602', 'PROSITC1615', 'PROSITC1621', 'PROSITC1623', 'PROSITC1625', 'PROSITC1627', 'PROSITC1629', 'PROSITC1635', 'PROSITC1639', 'PROSITC1642', 'PROSITC1663', 'PROSITC1666', 'PROSITC1671', 'PROSITC1672', 'PROSITC1678', 'PROSITC1684', 'PROSITC1685', 'PROSITC1705', 'PROSITC1705', 'PROSITC1712', 'PROSITC1722', 'PROSITC1748', 'PROSITC1754', 'PROSITC1756', 'PROSITC1761', 'PROSITC1762', 'PROSITC1764', 'PROSITC1785', 'PROSITC1795', 'PROSITC1798', 'PROSITC1803', 'PROSITC1807', 'PROSITC1809', 'PROSITC1810', 'PROSITC1823', 'PROSITC1827', 'PROSITC1831', 'PROSITC1835', 'PROSITC1844', 'PROSITC1861', 'PROSITC1863', 'PROSITC1864', 'PROSITC1865', 'PROSITC1874', 'PROSITC1877', 'PROSITC1881', 'PROSITC1895', 'PROSITC1898', 'PROSITC1911', 'PROSITC1914', 'PROSITC1926', 'PROSITC1942', 'PROSITC1958', 'PROSITC1966', 'PROSITC1979', 'PROSITC1980', 'PROSITC1983', 'PROSITC1985', 'PROSITC1996', 'PROSITC1999', 'PROSITC2017', 'PROSITC2029', 'PROSITC2059', 'PROSITC2060', 'PROSITC2065', 'PROSITC2069', 'PROSITC2076', 'PROSITC2096', 'PROSITC2111', 'PROSITC2117', 'PROSITC2129', 'PROSITC2134', 'PROSITC2156', 'PROSITC2162', 'PROSITC2170', 'PROSITC2195', 'PROSITC2202', 'PROSITC2203', 'PROSITC2135', 'PROSITC2207', 'PROSITC2233', 'PROSITC2259', 'PROSITC2264', 'PROSITC2265', 'PROSITC2267', 'PROSITC2269', 'PROSITC2271', 'PROSITC2278', 'PROSITC2281', 'PROSITC2303', 'PROSITC2306', 'PROSITC2315', 'PROSITC2323', 'PROSITC2327', 'PROSITC2330', 'PROSITC2332', 'PROSITC2333', 'PROSITC2360', 'PROSITC2382', 'PROSITC2384', 'PROSITC2394', 'PROSITC2396', 'PROSITC2411', 'PROSITC2928', 'PROSITC2964', 'PROSITC2975', 'PROSITC2977', 'PROSITC2984', 'PROSITC2986', 'PROSITC3001', 'PROSITC3014', 'PROSITC3025', 'PROSITC3029', 'PROSITC3031', 'PROSITC3035', 'PROSITC3037', 'PROSITC3038', 'PROSITC3044', 'PROSITC3053', 'PROSITC3067', 'PROSITC3070', 'PROSITC3071', 'PROSITC3073', 'PROSITC3076', 'PROSITC3078', 'PROSITC3079', 'PROSITC3102', 'PROSITC3110', 'PROSITC3114', 'PROSITC3117', 'PROSITC3121', 'PROSITC3134', 'PROSITC3150']

    # concatinating files with same sensor group
    df_list = []
    for sensorGroup in featureFiles:
        if len(sensorGroup) == 0:
            continue
        df1 = pd.read_csv(os.path.join(featurePath, sensorGroup[0]))
        df2 = pd.read_csv(os.path.join(featurePath, sensorGroup[1]))
        df = pd.concat([df1, df2], ignore_index=True)
        for file in sensorGroup[2:]:
            next_df = pd.read_csv(os.path.join(featurePath, file))
            df = pd.concat([df, next_df], ignore_index=True)
        df_list.append(df)
    
    # merging all the feature files into a single file
    if len(df_list) == 0:
        sys.exit("no feature files to merge")
    df1 = df_list[0]
    df2 = df_list[1]
    featureData = pd.merge(df1, df2, on=["participant", "date"], how="inner")
    
    for next_featureFile in df_list[2:]:
        featureData = pd.merge(featureData, next_featureFile, on=["participant", "date"], how="inner")

    # keep only filtered participants
    featureData = featureData[featureData["participant"].isin(filteredParticipants)].reset_index(drop=True)
    featureData.to_csv(os.path.join(featurePath, "..", finalFeatureFilename), header=True, index=False)


if __name__ == "__main__":
    """
    config["values"] will be used to control the features that will be extracted from the raw data, '1' means True and anything else will be Flase.
    """
    # config
    dataPath1 = "/csv/backup_frigg1"
    dataPath2 = "/csv/backup"
    featurePath = "/csv/features"
    finalFeatureFilename = "final_featureData.csv"

    # create output directory if not exits
    isExist = os.path.exists(featurePath)
    if not isExist:
        os.makedirs(featurePath)

    config1 = {"path":[dataPath1, featurePath], "features":["screen", "calling", "sleep", "mobility"], "values":"1110"}
    config2 = {"path":[dataPath2, featurePath], "features":["screen", "calling", "sleep", "mobility"], "values":"1110"}

    strTime = time.time()
    getFeatures(config1)
    endTime = time.time()
    print(f"run time: {round((endTime - strTime)/60, 2)}\n")

    strTime = time.time()
    getFeatures(config2)
    endTime = time.time()
    print(f"run time: {round((endTime - strTime)/60, 2)}\n")

    # idividual feature files that needs to be combined to get a final output feature file that's needed by the Dashboard
    allFiles = os.listdir(featurePath)
    screenFeatureFiles = [file for file in allFiles if "ios_screen_features_" in file]
    callFeatureFiles = [file for file in allFiles if "ios_call_features_" in file]
    sleepFeatureFiles = [file for file in allFiles if "ios_sleep_features_" in file]
    # mobilityFeatureFiles = [file for file in allFiles if "ios_mobility_features_" in file]
    mobilityFeatureFiles = []   #empty since I wont be analysisng GPS data, use above line if GPS data is neeeded
    
    featureFiles = [screenFeatureFiles, callFeatureFiles, sleepFeatureFiles, mobilityFeatureFiles]
    combineFeatures(featurePath, featureFiles, finalFeatureFilename)
