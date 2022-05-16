"""
####################################################################################################
Script for extracting below screen usage related features using IOS lockstate data

Feature1: No of screen unlocks in a daily section
Feature2: First screen unlock event in a day
Feature3: Last screen lock event in a day
Feature4: Maximum screen unlock time in a daily section
Feature5: Maximum screen lock time in a daily section
Feature6: Total screen unlock time in a daily section
Feature7: Total screen lock time in a daily section

*screen usage durations are in minutes

input/output file names need to be specifed in the code below #config
####################################################################################################
"""

from imports import *

def getIosScreenFeatures(dataPath, featurePath):
    """
    Feature Engineering - "Screenstate (LOCKED/UNLOCKED)"
    This script will read files from predefined location and write feature data into predefined location

    dataPath: path to folder which has ios screen data
    featurePath: path to store the extracted features
    """
    print("Begin extraction - Screen features")
    
    # config
    dataFilename = "Lock_state.csv"
    date = datetime.now().strftime("%Y%m%d_%I%M%S%p")
    featureFilename = "ios_screen_features_" + dataPath.split("/")[-1] + "_" + date + ".csv"

    if not (os.path.exists(os.path.join(dataPath, dataFilename))):
        sys.exit(f"{dataFilename} file does not exist in {dataPath} folder \nscript aborted")

    #read ios file
    screenstate = pd.read_csv(os.path.join(dataPath, dataFilename), sep="|", header=None)
    screenstate.columns = ["id", "participantId", "attribute", "lockstate", "timestamp", "uploadtimestamp"]

    #change time to Halifax time
    screenstate["timestamp"] = pd.to_datetime(screenstate["timestamp"], utc=True)
    screenstate["timestamp"] = pd.to_datetime(screenstate["timestamp"]).dt.tz_convert(tz='America/Halifax')
    screenstate["timestamp"] = pd.to_datetime(screenstate["timestamp"], utc=False)

    #add new columns to help extract features
    screenstate["date"] = screenstate["timestamp"].dt.date
    screenstate["time"] = screenstate["timestamp"].dt.strftime('%H:%M:%S')

    # decided not to filter out participantIds at this stage
    # codeblock to get participantIds who have data greater that some range
    # filtering_df = screenstate.groupby(["participantId", "date"]).size().reset_index().groupby("participantId").size().reset_index(name="noOfDays")
    # filtering_df = filtering_df[(filtering_df.noOfDays >= 7) & (filtering_df.noOfDays <= 35)]
    # filtering_df = filtering_df[(filtering_df.noOfDays >= 7)]
    # filtered_participantIds = filtering_df.participantId.unique().tolist()

    #filter the df to take only the required participantIds
    # screenstate = screenstate[screenstate.participantId.isin(filtered_participantIds)].copy()

    # sort data, remove duplicates and drop unecessary columns
    screenstate = screenstate.sort_values(["participantId", "timestamp"]).reset_index(drop=True)
    screenstate.drop_duplicates(subset=["participantId", "timestamp", "lockstate"], keep="last", inplace=True)
    screenstate.drop(["id", "attribute", "uploadtimestamp"], axis=1, inplace=True)

    #keeping only those rows which indicate screen usage
    screenstate = screenstate[(screenstate.lockstate == "LOCKED") | (screenstate.lockstate == "UNLOCKED")]

    df_screen_state_processed = pd.DataFrame()

    """
    1: filter over participantId, date:
    2: check if df is not empty
    3: remove duplicates
    4: add first and last rows
    5: append to processed_df
    """ 
    participantIds = screenstate["participantId"].unique()
    # participantIds = ["PROSIT0004","PROSIT001", "PROSIT00A"]
    for participantId in tqdm(participantIds):
        screenstate_participantId = screenstate[screenstate.participantId == participantId].copy()
        dates = screenstate_participantId.date.unique()

        for i, date in enumerate(dates):
            screenstate_participantId_date = screenstate_participantId[screenstate_participantId.date == date].copy()

            if screenstate_participantId_date.shape[0] > 1:
                #add logic to remove duplicates using roll columns
                screenstate_participantId_date = screenstate_participantId_date[screenstate_participantId_date.lockstate != screenstate_participantId_date.lockstate.shift(1)]
                
                # adding first and last events to help detect screen usage from time 0 to time 1440 minutes of the day
                #first_event in a daily section
                first_event = screenstate_participantId_date.iloc[:1, :].copy()
                if first_event.lockstate.item() == "LOCKED":
                    first_event.lockstate = "UNLOCKED"
                elif first_event.lockstate.item() == "UNLOCKED":
                    first_event.lockstate = "LOCKED"
                
                #last_event in a daily section
                last_event = screenstate_participantId_date.iloc[-1:, :].copy()
                if last_event.lockstate.item() == "LOCKED":
                    last_event.lockstate = "UNLOCKED"
                elif last_event.lockstate.item() == "UNLOCKED":
                    last_event.lockstate = "LOCKED"
                
                screenstate_participantId_date = pd.concat([first_event, screenstate_participantId_date, last_event], ignore_index=True)
                screenstate_participantId_date["screen_on_time"] = 0
                screenstate_participantId_date["screen_off_time"] = 0
                
                #logic to calculate screen_time
                index = (screenstate_participantId_date.lockstate == "UNLOCKED" ) & (screenstate_participantId_date.lockstate.shift(-1) == "LOCKED" )
                screenstate_participantId_date.loc[index, "screen_on_time"] = (screenstate_participantId_date.timestamp.shift(-1)[index] - screenstate_participantId_date.timestamp[index]).astype('timedelta64[s]')
                
                index = (screenstate_participantId_date.lockstate == "LOCKED" ) & (screenstate_participantId_date.lockstate.shift(-1) == "UNLOCKED" )
                screenstate_participantId_date.loc[index, "screen_off_time"] = (screenstate_participantId_date.timestamp.shift(-1)[index] - screenstate_participantId_date.timestamp[index]).astype('timedelta64[s]')
                
                screenstate_participantId_date.screen_on_time = np.round(screenstate_participantId_date.screen_on_time / 60)    #use /60 here to convert time to minutes
                screenstate_participantId_date.screen_off_time = np.round(screenstate_participantId_date.screen_off_time / 60)  #use /60 here to convert time to minutes
                
                df_screen_state_processed = pd.concat([df_screen_state_processed, screenstate_participantId_date], ignore_index=True)

    df_screen_state_processed[df_screen_state_processed.screen_on_time < 0]
    df_screen_state_processed = df_screen_state_processed[df_screen_state_processed.screen_on_time >= 0]

    df1 = (df_screen_state_processed[df_screen_state_processed.lockstate=="UNLOCKED"].groupby(["participantId", "date"]).size().reset_index(name="no_of_unlocks"))
    df2 = (df_screen_state_processed[df_screen_state_processed.lockstate=="UNLOCKED"].groupby(["participantId", "date"])["screen_on_time"].agg("max").reset_index(name="max_screen_on_time"))
    df3 = (df_screen_state_processed[df_screen_state_processed.lockstate=="UNLOCKED"].groupby(["participantId", "date"])["screen_on_time"].agg("sum").reset_index(name="total_screen_on_time"))
    df4 = (df_screen_state_processed[df_screen_state_processed.lockstate=="UNLOCKED"].groupby(["participantId", "date"])["time"].agg("min").reset_index(name="first_screen_unlock_time"))
    df5 = (df_screen_state_processed[df_screen_state_processed.lockstate=="LOCKED"].groupby(["participantId", "date"])["time"].agg("max").reset_index(name="last_screen_lock_time"))

    df_list = [df1, df2, df3, df4, df5]

    df = df1.merge(df2, how="right")
    for next_df in df_list[2:]:
        df = df.merge(next_df, on=["participantId", "date"], how="inner")
    
    df= df.fillna(0)
    df = df.sort_values(["participantId", "date"]).reset_index(drop=True)

    df["first_screen_unlock_time"] = pd.to_datetime(df["first_screen_unlock_time"], format='%H:%M:%S')
    # df["first_screen_unlock_time"] = round((df["first_screen_unlock_time"].dt.hour * 60 + df["first_screen_unlock_time"].dt.minute)/60, 2)
    # decided to use hour for first screen on time
    df["first_screen_unlock_time"] = df["first_screen_unlock_time"].dt.hour

    df["last_screen_lock_time"] = pd.to_datetime(df["last_screen_lock_time"], format='%H:%M:%S')
    # df["last_screen_lock_time"] = round((df["last_screen_lock_time"].dt.hour * 60 + df["last_screen_lock_time"].dt.minute)/60, 2)
    # decided to use hour for last screen on time
    df["last_screen_lock_time"] = df["last_screen_lock_time"].dt.hour
    
    #saving the file
    df.to_csv(os.path.join(featurePath, featureFilename), header=True, index=False)
    
    print("Extraction of Screen features compelted")


if __name__ == "__main__":
    # config
    dataPath1 = "/csv/backup_frigg1"
    dataPath2 = "/csv/backup"
    featurePath = "/csv/features"

    strTime = time.time()
    getIosScreenFeatures(dataPath1, featurePath)
    endTime = time.time()
    print(f"run time: {round((endTime - strTime)/60, 2)}")

    strTime = time.time()
    getIosScreenFeatures(dataPath2, featurePath)
    endTime = time.time()
    print(f"run time: {round((endTime - strTime)/60, 2)}")