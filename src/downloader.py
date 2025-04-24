#!/usr/bin/python3

import sys
import re
import datetime
import yaml
import argparse
from amcrest import AmcrestCamera

class Config:
    def __init__(self, raw):
        self.address = raw['address']
        self.port = raw['port']
        self.username = raw['username']
        self.password = raw['password']
        self.destination = raw['destination']

def isValidFileObject(f):
    attrs = ["FilePath", "StartTime", "EndTime"]
    for attr in attrs:
        if attr not in f:
            return False
    return True

def isCompleteFile(f):
    if f["FilePath"].endswith("_"):
        return False
    return True

def findFiles(start_time, end_time):
    res = []

    for text in camera.find_files(start_time, end_time, channel=1):
        #print(f"MARAT {text}")
        tokens = text.split('\r\n')
        if len(tokens) == 0:
            continue
        k, v = tokens[0].split('=')[:2]
        if k != 'found':
            raise Exception('unexpected format, first line should be')
    
        current_index = 0
        current_object = {}
        for line in tokens[1:]:
            if line == '':
                continue
            indexes = re.findall(r'items\[(\d+)\]', line)
            if len(indexes) != 1:
                raise Exception(f'cannot parse index of an items {line}')
            index = indexes[0]
            if index != current_index:
                if isValidFileObject(current_object) and isCompleteFile(current_object):
                    res.append(current_object)
                current_index = index
                current_object = {}
            key, value = list(line.split("=", 1) + [None])[:2]
            if key.endswith(".FilePath"):
                current_object["FilePath"] = value
            if key.endswith(".StartTime"):
                current_object["StartTime"] = value
            if key.endswith(".EndTime"):
                current_object["EndTime"] = value
            #TODO: Parse flags
            #items[3].Flags[0]=Event
        if isValidFileObject(current_object) and isCompleteFile(current_object):
            res.append(current_object)

    return res

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="Path to Config file")
parser.add_argument("-t", "--test", help="Test mode that there is a connection to camera", action='store_true')
parser.add_argument("-l", "--list", help="List latest objects from camera", action='store_true')
parser.add_argument("-d", "--daemon", help="Start in daemon mode to download files from camera", action='store_true')

args = parser.parse_args()
if not args.config:
    print("must set config option with -c or --config")
    sys.exit(1)

with open(args.config, 'r') as f:
    config = Config(yaml.safe_load(f))

if not config.destination:
    print("Destination for downloads is not set")
    sys.exit(1)

camera = AmcrestCamera(config.address, config.port, config.username, config.password).camera

if args.test:
    print("Testing connection")
    print(f"Successful connection to camera at address {config.address}:{config.port}: {camera.software_information}")
    sys.exit(0)

if args.list:
    print("Listing last files")
    print(f"Successful connection to camera at address {config.address}:{config.port}: {camera.software_information}")

    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(hours=2)
    
    for text in camera.find_files(start_time, end_time, channel=1):
        for line in text.split("\r\n"):
            key, value = list(line.split("=", 1) + [None])[:2]
            if key.endswith(".FilePath"):
                print("Found file {}".format(value))

if args.daemon:
    print("Starting in daemon mode")
    print("NOT IMPLEMENTED YET")
    sys.exit(1)


end_time = datetime.datetime.now()
start_time = end_time - datetime.timedelta(hours=2)
files = findFiles(start_time, end_time)
print(f"len={len(files)}; files={files}")

#if file_name:
#    print("Downloading {}...".format(file_name))
#    with open("snapshot.mp4", "wb") as file:
#        file.write(camera.download_file(file_name))
#    print("Saved as {}!".format("snapshot.jpg"))
