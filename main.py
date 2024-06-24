import os
import shutil
import datetime
import time
import argparse
import logging

def setup_logging(log_file):
    #initializing logging
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

def path_validation(source, replica):
    # checking the paths and if they are not inside itself
    
    source = os.path.abspath(source)
    replica = os.path.abspath(replica)

    if source == replica:
        raise ValueError("Source and replica folders can't be the same.")
    
    if os.path.commonpath([source]) == os.path.commonpath([source, replica]):
        if replica.startswith(source):
            raise ValueError("Replica folder can't be inside the source folder.")

def sync_folders(source, replica):
    

    if not os.path.exists(source):
        raise FileNotFoundError(f"Source folder '{source}' does not exist")

    if not os.path.exists(replica):
        os.makedirs(replica)

    # Sync folders
    for root, dirs, files in os.walk(source):
        relative_path = os.path.relpath(root, source)
        replica_path = os.path.join(replica, relative_path)

        # Check to see if replica folder structure matches source
        if not os.path.exists(replica_path):
            os.makedirs(replica_path)
            logging.info(f"Created: {replica_path}")
            print(f"{datetime.datetime.now()} - Created: {replica_path}")
            
        # COpy files
        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_path, file)

            if not os.path.exists(replica_file) or os.path.getmtime(source_file) > os.path.getmtime(replica_file):
                shutil.copy2(source_file, replica_file)
                logging.info(f"Copied: '{source_file}' to '{replica_file}'")
                print(f"{datetime.datetime.now()} - Copied: '{source_file}' to '{replica_file}'")
                
    # Remove files and directories not in source
    for root, dirs, files in os.walk(replica):
        relative_path = os.path.relpath(root, replica)
        source_path = os.path.join(source, relative_path)

        for file in files:
            replica_file = os.path.join(root, file)
            source_file = os.path.join(source_path, file)

            if not os.path.exists(source_file):
                os.remove(replica_file)
                logging.info(f"Removed: '{replica_file}'")
                print(f"{datetime.datetime.now()} - Removed: '{replica_file}'")

        for dir in dirs:
            replica_dir = os.path.join(root, dir)
            source_dir = os.path.join(source_path, dir)

            if not os.path.exists(source_dir):
                shutil.rmtree(replica_dir)
                logging.info(f"Removed: {replica_dir}")
                print(f"{datetime.datetime.now()} - Removed: {replica_dir}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', help='Path to source.')
    parser.add_argument('replica', help='Path to replica.')
    parser.add_argument('sync_interval', type=int, help='Synchronization interval in seconds.')
    parser.add_argument('log', help='Path to log.')

    args = parser.parse_args()

    try:
        setup_logging(args.log)
        path_validation(args.source, args.replica)

        while True:
            sync_folders(args.source, args.replica)
            time.sleep(args.sync_interval)

    except Exception as error:
        logging.error(f"Error: {error}")
        print(f"Error: {error}")

if __name__ == "__main__":
    main()
