"""
#################################################################################################################
Script for extracting below sleep related features using IOS lockstate, brightness, accelerometer and gyroscope data

Feature1(sleepStartTime): Estimated start time of the sleep
Feature2(sleepEndTime): Estimated end time of the sleep
Feature3(sleepDuration): Estimated sleep duration

input/output file names need to be specifed in the code below #config
#################################################################################################################
"""

from imports import *

# Filtered participantIds from another notebook. Only data from these will be analysed
filteredParticipantIds = []
filteredParticipantIds = ['PROSITC1005', 'PROSITC1014', 'PROSITC1018', 'PROSITC1025', 'PROSITC1026', 'PROSITC1027', 'PROSITC1029', 'PROSITC1030', 'PROSITC1031', 'PROSITC1033', 'PROSITC1034', 'PROSITC1036', 'PROSITC1037', 'PROSITC1038', 'PROSITC1039', 'PROSITC1040', 'PROSITC1041', 'PROSITC1043', 'PROSITC1044', 'PROSITC1046', 'PROSITC1057', 'PROSITC1061', 'PROSITC1062', 'PROSITC1066', 'PROSITC1070', 'PROSITC1079', 'PROSITC1080', 'PROSITC1082', 'PROSITC1084', 'PROSITC1086', 'PROSITC1089', 'PROSITC1090', 'PROSITC1097', 'PROSITC1100', 'PROSITC1101', 'PROSITC1104', 'PROSITC1109', 'PROSITC1110', 'PROSITC1111', 'PROSITC1119', 'PROSITC1122', 'PROSITC1126', 'PROSITC1128', 'PROSITC1130', 'PROSITC1132', 'PROSITC1135', 'PROSITC1136', 'PROSITC1137', 'PROSITC1140', 'PROSITC1153', 'PROSITC1158', 'PROSITC1174', 'PROSITC1187', 'PROSITC1192', 'PROSITC1193', 'PROSITC1200', 'PROSITC1221', 'PROSITC1222', 'PROSITC1223', 'PROSITC1224', 'PROSITC1227', 'PROSITC1237', 'PROSITC1240', 'PROSITC1244', 'PROSITC1261', 'PROSITC1272', 'PROSITC1293', 'PROSITC1297', 'PROSITC1299', 'PROSITC1304', 'PROSITC1308', 'PROSITC1317', 'PROSITC1325', 'PROSITC1326', 'PROSITC1343', 'PROSITC1369', 'PROSITC1372', 'PROSITC1379', 'PROSITC1412', 'PROSITC1413', 'PROSITC1422', 'PROSITC1424', 'PROSITC1428', 'PROSITC1438', 'PROSITC1493', 'PROSITC1501', 'PROSITC1502', 'PROSITC1512', 'PROSITC1516', 'PROSITC1526', 'PROSITC1529', 'PROSITC1548', 'PROSITC1550', 'PROSITC1553', 'PROSITC1555', 'PROSITC1562', 'PROSITC1564', 'PROSITC1570', 'PROSITC1602', 'PROSITC1615', 'PROSITC1621', 'PROSITC1623', 'PROSITC1625', 'PROSITC1627', 'PROSITC1629', 'PROSITC1635', 'PROSITC1639', 'PROSITC1642', 'PROSITC1663', 'PROSITC1666', 'PROSITC1671', 'PROSITC1672', 'PROSITC1678', 'PROSITC1684', 'PROSITC1685', 'PROSITC1705', 'PROSITC1705', 'PROSITC1712', 'PROSITC1722', 'PROSITC1748', 'PROSITC1754', 'PROSITC1756', 'PROSITC1761', 'PROSITC1762', 'PROSITC1764', 'PROSITC1785', 'PROSITC1795', 'PROSITC1798', 'PROSITC1803', 'PROSITC1807', 'PROSITC1809', 'PROSITC1810', 'PROSITC1823', 'PROSITC1827', 'PROSITC1831', 'PROSITC1835', 'PROSITC1844', 'PROSITC1861', 'PROSITC1863', 'PROSITC1864', 'PROSITC1865', 'PROSITC1874', 'PROSITC1877', 'PROSITC1881', 'PROSITC1895', 'PROSITC1898', 'PROSITC1911', 'PROSITC1914', 'PROSITC1926', 'PROSITC1942', 'PROSITC1958', 'PROSITC1966', 'PROSITC1979', 'PROSITC1980', 'PROSITC1983', 'PROSITC1985', 'PROSITC1996', 'PROSITC1999', 'PROSITC2017', 'PROSITC2029', 'PROSITC2059', 'PROSITC2060', 'PROSITC2065', 'PROSITC2069', 'PROSITC2076', 'PROSITC2096', 'PROSITC2111', 'PROSITC2117', 'PROSITC2129', 'PROSITC2134', 'PROSITC2156', 'PROSITC2162', 'PROSITC2170', 'PROSITC2195', 'PROSITC2202', 'PROSITC2203', 'PROSITC2135', 'PROSITC2207', 'PROSITC2233', 'PROSITC2259', 'PROSITC2264', 'PROSITC2265', 'PROSITC2267', 'PROSITC2269', 'PROSITC2271', 'PROSITC2278', 'PROSITC2281', 'PROSITC2303', 'PROSITC2306', 'PROSITC2315', 'PROSITC2323', 'PROSITC2327', 'PROSITC2330', 'PROSITC2332', 'PROSITC2333', 'PROSITC2360', 'PROSITC2382', 'PROSITC2384', 'PROSITC2394', 'PROSITC2396', 'PROSITC2411', 'PROSITC2928', 'PROSITC2964', 'PROSITC2975', 'PROSITC2977', 'PROSITC2984', 'PROSITC2986', 'PROSITC3001', 'PROSITC3014', 'PROSITC3025', 'PROSITC3029', 'PROSITC3031', 'PROSITC3035', 'PROSITC3037', 'PROSITC3038', 'PROSITC3044', 'PROSITC3053', 'PROSITC3067', 'PROSITC3070', 'PROSITC3071', 'PROSITC3073', 'PROSITC3076', 'PROSITC3078', 'PROSITC3079', 'PROSITC3102', 'PROSITC3110', 'PROSITC3114', 'PROSITC3117', 'PROSITC3121', 'PROSITC3134', 'PROSITC3150']


def sleep_analysis(df, sleep_break=30):
    """
    method to assign a sleep/awake state to each 10-minute time block
    Estimate the sleeping hours based on consecutive sleep time-blocks
    """
    prev = 0
    sleep = 0
    start = end = 0
    sleep_start = sleep_end = 0
    sleep_duration = 0

    for _, row in df.iterrows():
        curr = row.timeblock
        if (np.round((curr - prev), 2)) <= (sleep_break/10):
            sleep += 1
            end = curr
        else:
            sleep = 0
            start = curr
            end = curr
        
        if sleep>sleep_duration:
            sleep_duration = sleep
            sleep_start = np.round(start, 2)
            sleep_end = np.round(end, 2)

        prev = row.timeblock
    
    sleep_duration = np.round((sleep_duration*10/60), 2)
    # sleep_start_time and sleep_end_time are in minute of the day format
    sleep_start_time = '{:02d}:{:02d}'.format(*divmod(int(sleep_start*10), 60))
    sleep_end_time = '{:02d}:{:02d}'.format(*divmod(int(sleep_end*10), 60))
    # print(f"sleep_duration:{sleep_duration}hrs sleep_start:{sleep_start}, sleep_end:{sleep_end}, no_sleep_interruptions:{no_sleep_interruptions}, duration_of_sleep_interruptions:{duration_of_sleep_interruptions}")
    # return the sleep times detected by the algorithm
    return  sleep_duration, sleep_start_time, sleep_end_time


######################################################################################
# pre processing lockstate data
######################################################################################
def process_lockstate_ios_data(inputDataPath, dataFilename):
    print(f"Processing Lockstate IOS data from '{inputDataPath}'...")
    # read file with a header
    header_list = ["id", "participantId", "attribute", "lck", "timestamp", "uploadtimestamp"]
    lockstate = pd.read_csv(os.path.join(inputDataPath, dataFilename), sep='|', header=None, names=header_list)

    # drop unecessary columns
    lockstate.drop(["id", "attribute", "uploadtimestamp"], axis=1, inplace=True)

    # keep only filtered participantIds
    if len(filteredParticipantIds)!=0:
        lockstate = lockstate[lockstate["participantId"].isin(filteredParticipantIds)]

    #change time to Halifax time
    lockstate["timestamp"] = pd.to_datetime(lockstate["timestamp"], utc=True)
    lockstate["timestamp"] = pd.to_datetime(lockstate["timestamp"]).dt.tz_convert(tz='America/Halifax')
    lockstate["timestamp"] = pd.to_datetime(lockstate["timestamp"], utc=False)

    #add new columns to help extract features
    lockstate["date"] = lockstate["timestamp"].dt.date
    
    # For imputation and concatenation
    lockstateProcessed = pd.DataFrame()
    timeblock = [i for i in range(0,144)]
    allMinutes = pd.DataFrame({"timeblock":timeblock})
    # breaking down processing into multiple iterations
    participantIds = lockstate["participantId"].unique()
    for participantId in tqdm(participantIds):
        lockstate_participantId = lockstate[lockstate["participantId"] == participantId].copy()
        dates = lockstate_participantId["date"].unique()
        for date in dates:
            try:
                lockstate_participantId_date = lockstate_participantId[lockstate_participantId["date"] == date].copy()

                # drop duplicates
                lockstate_participantId_date.drop_duplicates(keep="last", inplace=True)

                #keeping only those rows which indicate locking events
                lockstate_participantId_date = lockstate_participantId_date[(lockstate_participantId_date["lck"] == "UNLOCKED") | (lockstate_participantId_date["lck"] == "LOCKED")].copy()
                
                #sort values
                lockstate_participantId_date.sort_values(["participantId", "timestamp"], inplace=True, ascending=True, ignore_index=True)

                #add necessary columns
                lockstate_participantId_date["timeblock"] = (lockstate_participantId_date["timestamp"].dt.hour * 6) + (lockstate_participantId_date["timestamp"].dt.minute/10).astype(int)

                # drop timestamp column
                lockstate_participantId_date.drop(["timestamp"], axis=1, inplace=True)

                # imputing missing values
                lockstate_participantId_date = pd.merge(lockstate_participantId_date, allMinutes, how="right", on="timeblock")
                lockstate_participantId_date.ffill(inplace=True)
                lockstate_participantId_date.bfill(inplace=True)
                
                # concatenating the data into single dataframe
                lockstateProcessed = pd.concat([lockstateProcessed, lockstate_participantId_date], axis=0)

            except:
                print(f"An exception occurred on Lock_state data for {participantId} {date}")

    print("Preprocessing completed for lockstate data")
    return lockstateProcessed


######################################################################################
# pre processing brightness data
######################################################################################
def process_brightness_ios_data(inputDataPath, dataFilename):
    print(f"Processing Brightness IOS data from '{inputDataPath}'...")
    # read file with a header
    header_list = ["id", "participantId", "attribute", "brt", "timestamp", "uploadtimestamp"]
    brightness = pd.read_csv(os.path.join(inputDataPath, dataFilename), sep='|', header=None, names=header_list)
    
    # drop unecessary columns
    brightness.drop(["id", "attribute", "uploadtimestamp"], axis=1, inplace=True)

    # keep only filtered participantIds
    if len(filteredParticipantIds)!=0:
        brightness = brightness[brightness["participantId"].isin(filteredParticipantIds)].reset_index(drop=True)

    #change time to Halifax time
    brightness["timestamp"] = pd.to_datetime(brightness["timestamp"], utc=True)
    brightness["timestamp"] = pd.to_datetime(brightness["timestamp"]).dt.tz_convert(tz='America/Halifax')
    brightness["timestamp"] = pd.to_datetime(brightness["timestamp"], utc=False)

    #add new columns to help extract features
    brightness["date"] = brightness["timestamp"].dt.date

    # For concatenation
    brightnessProcessed = pd.DataFrame()
    # breaking down processing into multiple iterations
    participantIds = brightness["participantId"].unique()
    for participantId in tqdm(participantIds):
        brightness_participantId = brightness[brightness["participantId"] == participantId].copy()
        dates = brightness_participantId["date"].unique()
        for date in dates:
            try:
                brightness_participantId_date = brightness_participantId[brightness_participantId["date"] == date].copy()

                # drop duplicates
                brightness_participantId_date.drop_duplicates(inplace=True)

                #sort values
                brightness_participantId_date.sort_values(["participantId", "timestamp"], inplace=True, ascending=True, ignore_index=True)

                #add necessary columns
                brightness_participantId_date["timeblock"] = (brightness_participantId_date["timestamp"].dt.hour * 6) + (brightness_participantId_date["timestamp"].dt.minute/10).astype(int)

                # drop timestamp column
                brightness_participantId_date.drop(["timestamp"], axis=1, inplace=True)

                #Aggregate the data over a period of 10minute timeblocks
                brightnessAgg = brightness_participantId_date.groupby(["participantId", "date", "timeblock"])["brt"].aggregate(["mean", "std", "min", "max"]).reset_index()
                header_list = ["participantId", "date", "timeblock", "brightness_mean", "brightness_std", "brightness_min", "brightness_max"]
                brightnessAgg.columns = header_list
                brightnessAgg["brightness_mean"] = round(brightnessAgg["brightness_mean"], 2)

                # concatenating the data into single dataframe
                brightnessProcessed = pd.concat([brightnessProcessed, brightnessAgg], axis=0)

            except:
                print(f"An exception occurred on Brightness data for {participantId} {date}")

    print("Preprocessing completed for brightness data")
    return brightnessProcessed


######################################################################################
# pre processing accelerometer data
######################################################################################
def process_accelerometer_ios_data(inputDataPath, dataFilename):    
    print(f"Processing Accelerometer IOS data from '{inputDataPath}'...")
    # read file with header
    header_list = ["id", "participantId", "attribute", "accX", "accY", "accZ", "timestamp", "uploadtimestamp"]
    accelerometer = pd.read_csv(os.path.join(inputDataPath, dataFilename), sep='|', header=None, names=header_list)
    print("accelerometer before", accelerometer.shape)

    # drop unecessary columns
    accelerometer.drop(["id", "attribute", "uploadtimestamp"], axis=1, inplace=True)

    # keep only filtered participantIds
    if len(filteredParticipantIds)!=0:
        accelerometer = accelerometer[accelerometer["participantId"].isin(filteredParticipantIds)].reset_index(drop=True)

    #change time to Halifax time
    accelerometer["timestamp"] = pd.to_datetime(accelerometer["timestamp"], utc=True)
    accelerometer["timestamp"] = pd.to_datetime(accelerometer["timestamp"]).dt.tz_convert(tz='America/Halifax')
    accelerometer["timestamp"] = pd.to_datetime(accelerometer["timestamp"], utc=False)

    #add a date column
    accelerometer["date"] = accelerometer["timestamp"].dt.date

    # For concatenation
    accelerometerProcessed = pd.DataFrame()
    # breaking down processing into multiple iterations
    participantIds = accelerometer["participantId"].unique()
    for participantId in tqdm(participantIds):
        accelerometer_participantId = accelerometer[accelerometer["participantId"] == participantId].copy()
        dates = accelerometer_participantId["date"].unique()
        for date in dates:
            try:
                accelerometer_participantId_date = accelerometer_participantId[accelerometer_participantId["date"] == date].copy()

                # drop duplicates
                accelerometer_participantId_date.drop_duplicates(keep="last", inplace=True)

                #sort values
                accelerometer_participantId_date.sort_values(["participantId", "timestamp"], inplace=True, ascending=True, ignore_index=True)

                #add necessary columns
                accelerometer_participantId_date["timeblock"] = (accelerometer_participantId_date["timestamp"].dt.hour * 6) + (accelerometer_participantId_date["timestamp"].dt.minute/10).astype(int)

                # ENMO : Euclidean Norm Minus One (ENMO) with negative values rounded to zero in g has been shown to correlate with the magnitude of acceleration and human energy expenditure
                accelerometer_participantId_date["acc"] = np.sqrt(accelerometer_participantId_date["accX"]**2 + accelerometer_participantId_date["accY"]**2 + accelerometer_participantId_date["accZ"]**2)
                # accelerometer_participantId_date["acc"] = np.maximum(0, (np.sqrt((accelerometer_participantId_date["accelerationx"]**2) + (accelerometer_participantId_date["accelerationy"]**2) + (accelerometer_participantId_date["accelerationz"]**2)) - 1))

                # drop timestamp column
                accelerometer_participantId_date.drop(["timestamp"], axis=1, inplace=True)

                #drop axial accelerometer columns
                accelerometer_participantId_date.drop(["accX", "accY", "accZ"], axis=1, inplace=True)

                #Aggregate the data over a period of 10minute timeblocks
                accelerometerAgg = accelerometer_participantId_date.groupby(["participantId", "date", "timeblock"])["acc"].agg("mean").reset_index()
                # accelerometer.columns = ['_'.join(col).strip() if col[1]!="" else col[0] for col in accelerometer.columns.values ]
                accelerometerAgg["acc"] = round(accelerometerAgg["acc"], 2)
                
                # concatenating the data into single dataframe
                accelerometerProcessed = pd.concat([accelerometerProcessed, accelerometerAgg], axis=0)
                
            except:
                print(f"An exception occurred on Accelerometer data for {participantId} {date}")
    print("accelerometer after", accelerometerProcessed.shape)
    print("Preprocessing completed for accelerometer data")
    return accelerometerProcessed


######################################################################################
# pre processing gyroscope data
######################################################################################
def process_gyroscope_ios_data(inputDataPath, dataFilename):    
    print(f"Processing Gyroscope IOS data from '{inputDataPath}'...")
    # read file with header
    header_list = ["id", "participantId", "attribute", "gyroX", "gyroY", "gyroZ", "timestamp", "uploadtimestamp"]
    gyroscope = pd.read_csv(os.path.join(inputDataPath, dataFilename), sep='|', header=None, names=header_list)

    # drop unecessary columns
    gyroscope.drop(["id", "attribute", "uploadtimestamp"], axis=1, inplace=True)

    # keep only filtered participantIds
    if len(filteredParticipantIds)!=0:
        gyroscope = gyroscope[gyroscope["participantId"].isin(filteredParticipantIds)].reset_index(drop=True)

    #change time to Halifax time
    gyroscope["timestamp"] = pd.to_datetime(gyroscope["timestamp"], utc=True)
    gyroscope["timestamp"] = pd.to_datetime(gyroscope["timestamp"]).dt.tz_convert(tz='America/Halifax')
    gyroscope["timestamp"] = pd.to_datetime(gyroscope["timestamp"], utc=False)

    #add new columns to help extract features
    gyroscope["date"] = gyroscope["timestamp"].dt.date

    # For concatenation
    gyroscopeProcessed = pd.DataFrame()
    # breaking down processing into multiple iterations
    participantIds = gyroscope["participantId"].unique()
    for participantId in tqdm(participantIds):
        gyroscope_participantId = gyroscope[gyroscope["participantId"] == participantId].copy()
        dates = gyroscope_participantId["date"].unique()
        for date in dates:
            try:
                gyroscope_participantId_date = gyroscope_participantId[gyroscope_participantId["date"] == date].copy()

                # drop duplicates
                gyroscope_participantId_date.drop_duplicates(keep="last", inplace=True)

                #sort values
                gyroscope_participantId_date.sort_values(["participantId", "timestamp"], inplace=True, ascending=True, ignore_index=True)

                #add necessary columns
                gyroscope_participantId_date["timeblock"] = (gyroscope_participantId_date["timestamp"].dt.hour * 6) + (np.floor(gyroscope_participantId_date["timestamp"].dt.minute / 10)).astype(int)

                # ENMO : Euclidean Norm Minus One (ENMO) with negative values rounded to zero in g has been shown to correlate with the magnitude of acceleration and human energy expenditure
                gyroscope_participantId_date["gyro"] = np.sqrt(gyroscope_participantId_date["gyroX"]**2 + gyroscope_participantId_date["gyroY"]**2 + gyroscope_participantId_date["gyroZ"]**2)
                # gyroscope_participantId_date["acc"] = np.maximum(0, (np.sqrt((gyroscope_participantId_date["accelerationx"]**2) + (gyroscope_participantId_date["accelerationy"]**2) + (gyroscope_participantId_date["accelerationz"]**2)) - 1))=

                # drop timestamp column
                gyroscope_participantId_date.drop(["timestamp"], axis=1, inplace=True)

                #drop axial gyroscope columns
                gyroscope_participantId_date.drop(["gyroX", "gyroY", "gyroZ"], axis=1, inplace=True)

                #Aggregate the data over a period of 10minute timeblocks
                gyroscopeAgg = gyroscope_participantId_date.groupby(["participantId", "date", "timeblock"])["gyro"].agg("mean").reset_index()
                # gyroscopeAgg.columns = ['_'.join(col).strip() if col[1]!="" else col[0] for col in gyroscopeAgg.columns.values ]
                gyroscopeAgg["gyro"] = round(gyroscopeAgg["gyro"], 2)
                
                # concatenating the data into single dataframe
                gyroscopeProcessed = pd.concat([gyroscopeProcessed, gyroscopeAgg], axis=0)

            except:
                print(f"An exception occurred on Gyroscope data for {participantId} {date}")

    print("Preprocessing completed for gyroscope data")
    return gyroscopeProcessed


######################################################################################
# combining all the sensor data to prepare sleep data
######################################################################################
def combine_ios_features(lockstate, brightness, accelerometer, gyroscope):
    dfs = [lockstate, brightness, accelerometer, gyroscope]

    sleep_data = reduce(lambda left,right: pd.merge(left,right,on=["participantId", "date", "timeblock"], how="outer"), dfs)
    sleep_data.fillna(0, inplace=True)

    # datenum: decided not to use this
    # for participantId in sleep_data.participantId.unique():
    #     sleep_data.loc[sleep_data.participantId == participantId,'date_num'] = pd.factorize(sleep_data.loc[sleep_data.participantId == participantId, "date"])[0] + 1

    # defining a dataframe to store the sleep features
    sleepFeatures = pd.DataFrame(columns=["participantId", "date", "date_num", "sleeping_hrs", "sleep_start_time", "sleep_end_time"])

    # participantIds = sleep_data.groupby('participantId').size().reset_index(name="cnt").sort_values("cnt", ascending=False).participantId.unique()
    participantIds = sleep_data["participantId"].unique()
    index = 0
    for participantId in tqdm(participantIds):
        sleep_data_participantId = sleep_data[sleep_data.participantId == participantId].copy()
        sleep_data_participantId['date_num'] = pd.factorize(sleep_data_participantId["date"])[0] + 1
        for date_num in sleep_data_participantId.date_num.unique():
            sleep_data_participantId_date = sleep_data_participantId[sleep_data_participantId.date_num == date_num].copy()

            # set values with less than 0.1 quantile values to 0 to remove noise
            # sleep_data_participantId_date.loc[sleep_data_participantId_date["acc_mean"] <= sleep_data_participantId_date["acc_mean"].quantile(0.1), "acc_mean"] = 0
            # sleep_data_participantId_date.loc[sleep_data_participantId_date["gyro_mean"] <= sleep_data_participantId_date["gyro_mean"].quantile(0.1), "gyro_mean"] = 0

            # filtering out only those timeblocks which show device usage
            sleep_data_participantId_date = sleep_data_participantId_date[(sleep_data_participantId_date["lck"] == "LOCKED") & (sleep_data_participantId_date["brightness_mean" == 0]) & (sleep_data_participantId_date["acc_mean"] == 0) & (sleep_data_participantId_date["gyro_mean"] == 0)]
            
            sleep_duration, sleep_start_time, sleep_end_time = sleep_analysis(sleep_data_participantId_date, sleep_break=30)
            sleepFeatures.loc[index] = [participantId, sleep_data_participantId_date.date.unique()[0], date_num, sleep_duration, sleep_start_time, sleep_end_time]
            index += 1
    
    return sleepFeatures

    
def getIosSleepFeatures(inputDataPath, featurePath):
    '''
    considering below conditions to assign a sleep state to a time block which is chosen as 10mins
    # screen state  - "Locked"
    # brightness    -   0
    # accelerometer -   0
    # gyroscope     -   0
    analysis of continious timeblocks decides the start and end time of sleep duration and no of sleep interruptions.
    '''
    print("Begin extraction - Sleep features")

    # config
    timestamp = datetime.now().strftime("%Y%m%d_%I%M%S%p")
    dbName = inputDataPath.split("/")[-1]

    # screen state data
    dataFilename1 = "Lock_state.csv"
    # dataFilename1 = "Lock_state_temp.csv"
    featureFilename1 = f"ios_Lock_state_processed_for_sleepFeatures_{dbName}_{timestamp}.csv"

    # brightness data
    dataFilename2 = "Brightness.csv"
    # dataFilename2 = "Brightness_temp.csv"
    featureFilename2 = f"ios_Brightness_processed_for_sleepFeatures_{dbName}_{timestamp}.csv"

    # accelerometer data
    dataFilename3 = "Accelerometer.csv"
    # dataFilename3 = "Accelerometer_temp.csv"
    featureFilename3 = f"ios_Accelerometer_processed_for_sleepFeatures_{dbName}_{timestamp}.csv"

    # gyroscope data
    dataFilename4 = "Gyroscope.csv"
    # dataFilename4 = "Gyroscope_temp.csv"
    featureFilename4 = f"ios_Gyroscope_processed_for_sleepFeatures_{dbName}_{timestamp}.csv"

    finalFeatureFilename = f"ios_sleep_features_{dbName}_{timestamp}.csv"

    if not (os.path.exists(os.path.join(inputDataPath, dataFilename1))):
        sys.exit(f"{dataFilename1} file does not exist in {inputDataPath} folder \nscript aborted")
    
    if not (os.path.exists(os.path.join(inputDataPath, dataFilename2))):
        sys.exit(f"{dataFilename2} file does not exist in {inputDataPath} folder \nscript aborted")
    
    if not (os.path.exists(os.path.join(inputDataPath, dataFilename3))):
        sys.exit(f"{dataFilename3} file does not exist in {inputDataPath} folder \nscript aborted")

    if not (os.path.exists(os.path.join(inputDataPath, dataFilename4))):
        sys.exit(f"{dataFilename4} file does not exist in {inputDataPath} folder \nscript aborted")


    # Preprocessing and saving the raw sensor data
    lockstate = process_lockstate_ios_data(inputDataPath, dataFilename1)
    lockstate.to_csv(os.path.join(featurePath, featureFilename1), header=True, index=False)

    brightness = process_brightness_ios_data(inputDataPath, dataFilename2)
    brightness.to_csv(os.path.join(featurePath, featureFilename2), header=True, index=False)

    accelerometer = process_accelerometer_ios_data(inputDataPath, dataFilename3)
    accelerometer.to_csv(os.path.join(featurePath, featureFilename3), header=True, index=False)

    gyroscope = process_gyroscope_ios_data(inputDataPath, dataFilename4)
    gyroscope.to_csv(os.path.join(featurePath, featureFilename4), header=True, index=False)

    sleepFeatures = combine_ios_features(lockstate, brightness, accelerometer, gyroscope)    
    #saving the file
    sleepFeatures.to_csv(os.path.join(featurePath, finalFeatureFilename), header=True, index=False)
    print("Extraction of Sleep features completed")


if __name__ == "__main__":
    # config
    inputDataPath1 = "/csv/backup_frigg1"
    inputDataPath2 = "/csv/backup"
    featurePath = "/csv/features"

    strTime = time.time()
    getIosSleepFeatures(inputDataPath1, featurePath)
    endTime = time.time()

    strTime = time.time()
    getIosSleepFeatures(inputDataPath2, featurePath)
    endTime = time.time()

    print(f"run time: {round((endTime - strTime)/60, 2)}")