import os
import argparse
from glob import glob
from typing import List
import csv
import numpy as np

NO_PROFILING_TIMESTAMPS = 14

def getNodeIndexFromDumpedCsvFileName(filename: str) -> int:
    nodeIdx = int(filename.split('-')[0])
    return nodeIdx

def getNoNodesFromDumpedCsvFileName(filename: str) -> int:
    noNodes = int(filename.split('-')[1][0])
    return noNodes

def sortCsvFiles(csvFiles: List[str]):
    filesBasenames = [os.path.basename(f) for f in csvFiles]
    unsortedFiles = {}
    for basePath, completePath in zip(filesBasenames, csvFiles):
        unsortedFiles[getNodeIndexFromDumpedCsvFileName(basePath)] = completePath

    sortedFiles = {k: unsortedFiles[k] for k in sorted(unsortedFiles)}
    return sortedFiles

def readCsvs(sortedCsvs):
    minNoSamples = float("inf")
    maxNoSamples = -1

    timestampHeaders = ["header_timestamp"] + [f"prof_{i}" for i in range(NO_PROFILING_TIMESTAMPS)] + ["callback_timestamp"]
    timestamps = {}
    for nodeIdx, filePath in sortedCsvs.items():
        noSamples = 0
        timestampsCurrFile = {k: [] for k in timestampHeaders}
        with open(filePath) as f:
            reader = csv.DictReader(f)
            for row in reader:
                for header in timestampHeaders:
                    timestampsCurrFile[header].append(float(row[header]))
                noSamples += 1

            timestamps[nodeIdx] = timestampsCurrFile
        minNoSamples = min(noSamples, minNoSamples)
        maxNoSamples = max(noSamples, maxNoSamples)

    return minNoSamples, maxNoSamples, timestamps

def calcLatenciesEndToEnd(parentDir: str):
    if not os.path.exists(parentDir):
        raise FileNotFoundError(f"Directory {parentDir} does not exist.")

    dumpedCsvsPerRun = glob(f"{parentDir}/*.csv")
    sortedCsvs = sortCsvFiles(dumpedCsvsPerRun)
    noNodes = getNoNodesFromDumpedCsvFileName(os.path.basename(dumpedCsvsPerRun[0]))

    minNoSamples, maxNoSamples, timestamps = readCsvs(sortedCsvs)
    latencies = {"e2e": None}

    tFirstNode = timestamps[2]['header_timestamp']
    tEndNode = timestamps[noNodes]['callback_timestamp']

    latencies["e2e"] = np.array(tEndNode) - np.array(tFirstNode)
    for i in range(NO_PROFILING_TIMESTAMPS):
        latencies[f"prof_{i}"] = np.zeros(minNoSamples)

    for nodeIdx in timestamps.keys():
        for profilingIdx in range(NO_PROFILING_TIMESTAMPS-2):
            currProfilingTimestamps = timestamps[nodeIdx][f"prof_{profilingIdx}"]
            nextProfilingTimestamps = timestamps[nodeIdx][f"prof_{profilingIdx+1}"]
            latencies[f"prof_{profilingIdx+1}"] += np.array(nextProfilingTimestamps) - np.array(currProfilingTimestamps)

        latencies["prof_0"] += np.array(timestamps[nodeIdx]["prof_0"]) - np.array(timestamps[nodeIdx]["header_timestamp"])
        latencies["prof_13"] += np.array(timestamps[nodeIdx]["prof_13"]) - np.array(timestamps[nodeIdx]["prof_12"])
    return latencies

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, help='relative path to directory containing dumped csvs.')
    args = parser.parse_args()

    latencies = calcLatenciesEndToEnd(args.directory)