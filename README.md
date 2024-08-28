# Neo4j workshop Training Setup (Aura)
Aura (or AuraDS) Infra setup for hands-on sessions at Neo4j workshops (Neo4j Introduction, Data modeling, GDS and GenAI)

1. Sign into Neo4j Aura Console (https://console.neo4j.io)
2. Create an AuraDS instance (eg: 2CPU/8GB) and import/restore the database from the dump file
3. Once the instance is up and running, collect the following details
    - Tenant ID (Eg: "6e748720-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    - Client ID and Client Secret (for Aura API access)
    - Instance ID for the new database (Eg: "44683a64")

### Configuration parameters
4. Modify "config.json" and add required parameters under the respective tasks

   - Create

     -- `dbname_prefix` is used to refer to the instances created for this workshop. It is used as reference for pause/delete and resume functions.

     -- `memory` should be the same as the instance you created above.
      Update other parameters as needed

     ```python
     Example:
        {
             "dbname_prefix": "neo4j_wkshp", # prefix to use for all the newly created machines
             "num_instances": 4,
             "params": {
               "version": "5",
               "region": "europe-west1",
               "memory": "8GB",
               "type": "enterprise-ds",
               "cloud_provider": "gcp"
            }
        }
     ```

   - Clone

   `source_instance_id` and `source_snapshot_date` are required for creating clones from an existing instance. 

   ```python
     Example:
    {
           "source_instance_id": "44683a64", # source instance for clones
           "source_snapshot_date": "2024-08-13" # update this with today's date or a specific date in the past
    }
     ```
   
   If you know and plan to use a specific snapshot, update `source_snapshot_id` with that snapshot ID.  Otherwise, leave it blank and the latest snapshot will be used.

   ```python
     Example:
       {
           "source_instance_id": "44683a64", # source instance for clones
           "source_snapshot_id": "86509b6a-1b56-4a37-a65e-ede480661a67"
      }
     ```

    - Snapshots

    `instance_id`is required for getting a list of snapshots from an existing instance.
     `snapshot_date` is optional.

     ```python
     Example:
       {
        "instance_id": "44683a64",
        "snapshot_date": "2024-08-13"
        }
     ```

   - Status/Pause/Resume/Delete

     Parameters are **not** mutually exclusive.

     ```python
     Example:
       {
         "instance_ids": [], # specific instances
         "dbname_prefix":"neo4j_wkshp", # instance ids with names that starts with the prefix
         "exclude": [] # any instance IDs to exclude
       }
     ```

### Creating/Cloning new instances
5. Open the terminal and run the below command

   ```shell
   % python /path_to_folder/main.py <tenant_id> <client Id> <client secret> <task> --output /path_to_folder/csvfile.csv
   ```
    - Tenant ID (Eg: "6e748720-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    - Client ID and Client Secret (for Aura API access)
    - Instance ID for the new database (Eg: "44683a64")
    - Supported tasks: `create`, `pause`, `resume`, `delete`, `status`, `list`, `get_snapshot_id`
    - Output is written to a csv file when new instances are created. Please save the file and or copy the credentials. The file will be overwritten when you run the code for the second time.

### Collect the credentials for newly created instances
**If you are running a workshop, you will want readable passwords for printouts.**

6. Open the terminal and run the below command

   ```shell
    % python /path_to_folder/readable_passwords.py /path_to_folder/csvfile.csv
   ```
    - input: output filename/path from step 4
    - output: csv with _readable_pw suffix added

Use `readable_passwords.py` after all of the instances are up and running to create and update login information. If you run this before the instances are running, you will get an `Unable to retrieve routing information error`
