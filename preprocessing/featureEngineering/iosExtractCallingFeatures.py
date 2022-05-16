"""
####################################################################################################
Script for extracting below call related features using IOS call data

Feature1: Number of Missed calls in a daily section
Feature2: Number of Dialled but not recieved calls in daily sections
Feature3: Number of Incoming calls in a daily section
Feature4: Number of Outgoing calls in a daily section
Feature5: Total number of calling events in a daily section
Feature6: Min duration of Incoming calls in a daily section
Feature7: Min duration of Outgoing calls in a daily section
Feature8: Max duration of Incoming calls in a daily section
Feature9: Max duration of Outgoing calls in a daily section
Feature10: Total duration of Incoming call in a daily section
Feature11: Total duration of Outgoing calls in a daily section
Feature12: Total duration of any calls in a daily section

*call durations are in minutes
*check for call_hold condition in between calls, not implemented in the code.

input/output file names need to be specifed in the code below #config
####################################################################################################
"""

from imports import *

def getIosCallingFeatures(dataPath, featurePath):
    """
    dataPath: path to folder which has ios call data
    featurePath: path to store the extracted features
    """
    print("Begin extraction - Calling features")

    # config
    dataFilename = "Call.csv"
    date = datetime.now().strftime("%Y%m%d_%I%M%S%p")
    featureFilename = "ios_call_features_" + dataPath.split("/")[-1] + "_" + date + ".csv"

    if not (os.path.exists(os.path.join(dataPath, dataFilename))):
        sys.exit(f"{dataFilename} file does not exist in {dataPath} folder \nscript aborted")

    # Call IOS data
    header_list = ["id", "participantId", "attribute", "callevent", "timestamp", "uploadtimestamp"]
    #read ios file
    call = pd.read_csv(os.path.join(dataPath, dataFilename), sep="|", header=None)
    call.columns = header_list
    call['device'] = "ios"

    #change time to Halifax time
    call["timestamp"] = pd.to_datetime(call["timestamp"], utc=True)
    call["timestamp"] = pd.to_datetime(call["timestamp"]).dt.tz_convert(tz='America/Halifax')
    call["timestamp"] = pd.to_datetime(call["timestamp"], utc=False)

    #add some new columns to help extract features
    call["date"] = call["timestamp"].dt.date
    call["time"] = call["timestamp"].dt.strftime('%H:%M:%S')

    #Drop duplicates and sort as per timestamp
    call = call.sort_values(["participantId", "timestamp"]).reset_index(drop=True)
    call.drop_duplicates(subset=["participantId", "timestamp", "callevent"], keep="last", inplace=True)
    call.drop(["id", "attribute", "uploadtimestamp"], axis=1, inplace=True)

    #keeping only those rows which indicate calling events
    call = call[call.callevent.isin(['CALL_INCOMING', 'CALL_CONNECTED', 'CALL_DISCONNECTED', 'CALL_DIALING', 'CALL_ON_HOLD'])]

    call_processed = pd.DataFrame()

    """
    filter over participantId, date, daily_section:
    check if df is not empty
    remove duplicates
    add first and last rows
    append to processed_df
    ****call duration for features is in minutes****
    """ 
    participantIds = call.participantId.unique()
    # participantIds = ["PROSIT0004","PROSIT001", "PROSIT00A"]
    for participantId in tqdm(participantIds):
        call_participantId = call[call.participantId == participantId].copy()
        dates = call_participantId.date.unique()
        for i, date in enumerate(dates):
            call_participantId_date = call_participantId[call_participantId.date == date].copy()
                
            if call_participantId_date.shape[0] > 1:
                #first_event in a daily section
                first_event = call_participantId_date.iloc[:1, :].copy()
                first_event.lockstate = "CALL_CONNECTED"

                #last_event in a daily section
                last_event = call_participantId_date.iloc[-1:, :].copy()
                last_event.lockstate = "CALL_DISCONNECTED"
                
                call_participantId_date = pd.concat([first_event, call_participantId_date, last_event], ignore_index=True)
                call_participantId_date["duration"] = 0
                call_participantId_date["calltype"] = ""
                
                #logic to call_type and duration_time
                call_participantId_date["callevent_roll1"] = call_participantId_date.callevent.shift(-1)
                call_participantId_date["timestamp_roll1"] = call_participantId_date.timestamp.shift(-1)
                call_participantId_date["callevent_roll2"] = call_participantId_date.callevent.shift(-2)
                call_participantId_date["timestamp_roll2"] = call_participantId_date.timestamp.shift(-2)

                index = (call_participantId_date["callevent"] == "CALL_INCOMING" ) & (call_participantId_date["callevent_roll1"] == "CALL_DISCONNECTED" )
                call_participantId_date.loc[index, "duration"] = (call_participantId_date[index]["timestamp_roll1"] - call_participantId_date[index]["timestamp"]).astype('timedelta64[m]')
                call_participantId_date.loc[index, "calltype"] = "missed"
                call_participantId_date.loc[index, "start_time"] = call_participantId_date.loc[index, "timestamp"].dt.time
                call_participantId_date.loc[index, "end_time"] = call_participantId_date.loc[index, "timestamp_roll1"].dt.time

                index = (call_participantId_date["callevent"] == "CALL_DIALING" ) & (call_participantId_date["callevent_roll1"] == "CALL_DISCONNECTED" )
                call_participantId_date.loc[index, "duration"] = (call_participantId_date[index]["timestamp_roll1"] - call_participantId_date[index]["timestamp"]).astype('timedelta64[m]')
                call_participantId_date.loc[index, "calltype"] = "rejected"
                call_participantId_date.loc[index, "start_time"] = call_participantId_date.loc[index, "timestamp"].dt.time
                call_participantId_date.loc[index, "end_time"] = call_participantId_date.loc[index, "timestamp_roll1"].dt.time

                index = (call_participantId_date["callevent"] == "CALL_INCOMING" ) & (call_participantId_date["callevent_roll1"] == "CALL_CONNECTED" ) & (call_participantId_date["callevent_roll2"] == "CALL_DISCONNECTED")
                call_participantId_date.loc[index, "duration"] = (call_participantId_date[index]["timestamp_roll2"] - call_participantId_date[index]["timestamp_roll1"]).astype('timedelta64[m]')
                call_participantId_date.loc[index, "calltype"] = "incoming"
                call_participantId_date.loc[index, "start_time"] = call_participantId_date.loc[index, "timestamp_roll1"].dt.time
                call_participantId_date.loc[index, "end_time"] = call_participantId_date.loc[index, "timestamp_roll2"].dt.time

                index = (call_participantId_date["callevent"] == "CALL_DIALING" ) & (call_participantId_date["callevent_roll1"] == "CALL_CONNECTED" ) & (call_participantId_date["callevent_roll2"] == "CALL_DISCONNECTED")
                call_participantId_date.loc[index, "duration"] = (call_participantId_date[index]["timestamp_roll2"] - call_participantId_date[index]["timestamp_roll1"]).astype('timedelta64[m]')
                call_participantId_date.loc[index, "calltype"] = "outgoing"
                call_participantId_date.loc[index, "start_time"] = call_participantId_date.loc[index, "timestamp_roll1"].dt.time
                call_participantId_date.loc[index, "end_time"] = call_participantId_date.loc[index, "timestamp_roll2"].dt.time
                
                call_processed = pd.concat([call_processed, call_participantId_date], ignore_index=True)

    #checking if there are any rows with negative call durations
    # call_processed[call_processed.duration < 0]
    # call_processed = call_processed[call_processed["duration"] >= 0]

    # missed rejected incoming outgoing
    df1 = (call_processed[call_processed.calltype=="missed"].groupby(["participantId", "date"]).size().reset_index(name="no_of_missed_calls"))
    df2 = (call_processed[call_processed.calltype=="rejected"].groupby(["participantId", "date"]).size().reset_index(name="no_of_rejected_calls"))
    df3 = (call_processed[call_processed.calltype=="incoming"].groupby(["participantId", "date"]).size().reset_index(name="no_of_incoming_calls"))
    df4 = (call_processed[call_processed.calltype=="outgoing"].groupby(["participantId", "date"]).size().reset_index(name="no_of_outgoing_calls"))
    df5 = (call_processed[call_processed.calltype.isin(["missed", "rejected", "incoming", "outgoing"])].groupby(["participantId", "date"]).size().reset_index(name="total_no_of_calls"))

    df6 = (call_processed[call_processed.calltype=="incoming"].groupby(["participantId", "date"])["duration"].agg("min").reset_index(name="min_duration_of_single_incoming_call"))
    df7 = (call_processed[call_processed.calltype=="outgoing"].groupby(["participantId", "date"])["duration"].agg("min").reset_index(name="min_duration_of_single_outgoing_call"))
    df8 = (call_processed[call_processed.calltype=="incoming"].groupby(["participantId", "date"])["duration"].agg("max").reset_index(name="max_duration_of_single_incoming_call"))
    df9 = (call_processed[call_processed.calltype=="outgoing"].groupby(["participantId", "date"])["duration"].agg("max").reset_index(name="max_duration_of_single_outgoing_call"))

    df10 = (call_processed[call_processed.calltype=="incoming"].groupby(["participantId", "date"])["duration"].agg("sum").reset_index(name="total_duration_of_incoming_calls"))
    df11 = (call_processed[call_processed.calltype=="outgoing"].groupby(["participantId", "date"])["duration"].agg("sum").reset_index(name="total_duration_of_outgoing_calls"))
    df12 = (call_processed[call_processed.calltype.isin(["incoming", "outgoing"])].groupby(["participantId", "date"])["duration"].agg("sum").reset_index(name="total_duration_of_all_calls"))

    df_list = [df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11, df12]

    df1[['key1', 'key2']] = df1[["participantId", "date"]]
    df2[['key1', 'key2']] = df2[["participantId", "date"]]
    df3[['key1', 'key2']] = df3[["participantId", "date"]]
    df4[['key1', 'key2']] = df4[["participantId", "date"]]
    df5[['key1', 'key2']] = df5[["participantId", "date"]]
    df6[['key1', 'key2']] = df6[["participantId", "date"]]
    df7[['key1', 'key2']] = df7[["participantId", "date"]]
    df8[['key1', 'key2']] = df8[["participantId", "date"]]
    df9[['key1', 'key2']] = df9[["participantId", "date"]]
    df10[['key1', 'key2']] = df10[["participantId", "date"]]
    df11[['key1', 'key2']] = df11[["participantId", "date"]]
    df12[['key1', 'key2']] = df12[["participantId", "date"]]

    df = df1.merge(df2, how="outer")
    for next_df in df_list[2:]:
        df = df.merge(next_df, how="outer")

    df= df.fillna(0)
    df = df.sort_values(["participantId", "date"]).reset_index(drop=True)

    # Dropping the key values used for outer joins
    df.drop(['key1', 'key2'], axis=1, inplace=True)
    df = df[(df.total_no_of_calls > 0) & (df.total_duration_of_all_calls > 0)].reset_index(drop=True)

    # save the file
    df = df.round(decimals=2)
    df.to_csv(os.path.join(featurePath, featureFilename), header=True, index=False)
    
    print("Extraction of Call features compelted")


if __name__ == "__main__":
    # config
    dataPath1 = "/csv/backup_frigg1"
    dataPath2 = "/csv/backup"
    featurePath = "/csv/features"

    strTime = time.time()
    getIosCallingFeatures(dataPath1, featurePath)
    endTime = time.time()
    print(f"run time: {round((endTime - strTime)/60, 2)}\n")

    strTime = time.time()
    getIosCallingFeatures(dataPath2, featurePath)
    endTime = time.time()
    print(f"run time: {round((endTime - strTime)/60, 2)}\n")