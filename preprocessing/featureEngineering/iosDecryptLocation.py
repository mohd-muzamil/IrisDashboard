"""
This script is used to decrypt all the location information for ios users
"""

import os
import pandas as pd
import rncryptor as rn
import base64
from time import time
from tqdm import tqdm
tqdm.pandas(desc="my bar!")


def decryptLocation(dataPath):
  """
  This method takes a path where the location file is present, decrypts the GPS information if its encrypted and stores the decrypted data at same location.
  """
  filename = os.path.join(dataPath, "Location.csv")  
  outputFile = os.path.join(dataPath, "Location_decrypted.csv")
  print(f"Begin decrypting {filename}")
  
  header_list = ["id", "participant", "attribute", "latitude", "longitude", "address", "timestamp", "uploadtimestamp"]
  df = pd.read_csv(filename, sep="|", names=header_list, index_col=False, dtype='unicode')
  
  # records with raw location data
  df_raw = df[~df['timestamp'].isna()].copy()

  # records with encrypted location data
  df_encrypted = df[df['timestamp'].isna()].copy()

  df_encrypted['latitude'] = df_encrypted['latitude'].progress_apply(lambda x: rn.decrypt(base64.b64decode(x), "location"))

  df_encrypted["timestamp"] = df_encrypted["longitude"]
  df_encrypted["uploadtimestamp"] = df_encrypted["address"]

  # split column and add new columns to df
  df_encrypted[['latitude', 'longitude', 'address']] = df_encrypted['latitude'].str.split('|', expand=True)

  df_decrypted = pd.concat([df_raw, df_encrypted], axis=0)
  df_decrypted["timestamp"] = pd.to_datetime(df_decrypted["timestamp"], format='%Y-%m-%d %H:%M:%S.%f')
  df_decrypted.sort_values(by=["participant", "timestamp"], ignore_index=True, inplace=True)

  # save the combined to same location with a new name
  if os.path.exists(outputFile):
    os.remove(outputFile)
  df_decrypted.to_csv(outputFile, sep="|", header=True, index=False)
  
  print("End")

if __name__ == "__main__":
  dataPath1 = "/csv/backup_frigg1"
  dataPath2 = "/csv/backup"
  
  strTime = time()
  decryptLocation(dataPath1)
  endTime = time()
  print(f"run time: {round(( endTime - strTime )/60, 2 )}")
	
  strTime = time()
  decryptLocation(dataPath2)
  endTime = time()
  print(f"run time: {round(( endTime - strTime )/60, 2 )}")

  print("done")