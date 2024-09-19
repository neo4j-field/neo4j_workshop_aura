# Neo4j workshop Infra setup (Aura)
Aura (or AuraDS) Infra setup for hands-on sessions at Neo4j workshops (Neo4j Introduction, Data modeling, GDS and GenAI)

1. Sign into Neo4j Aura Console (https://console.neo4j.io)
2. Create an Aura instance (eg: 2CPU/8GB) and import/restore the database from the dump file
    - AuraDS instances for GDS and GenAI workshops
    - Aura DB instances for Intro to Neo4j and data modeling workshops
4. Once the instance is up and running, collect the following details
    - Tenant ID (Eg: "6e748720-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    - Client ID and Client Secret (for Aura API access)
    - Instance ID for the new database (Eg: "44683a64")

### Configuration parameters
4. Modify "config.json" and add required parameters under the respective tasks
   - Supported tasks: `create`, `clone`, `pause`, `resume`, `delete`, `status`, `list`, `snapshots`

   **Create**
   
   `dbname_prefix` is used to refer to the instances created for this workshop. It is also used as reference for other tasks - status, pause, delete and resume.
   Update `num_instances` based on the requirements and also update other parameters as needed

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

    **Clone**

   `dbname_prefix` is used to refer to the cloned instances created for this workshop.
   `source_instance_id` and `source_snapshot_date` are required for creating clones from an existing instance.
   Keep the `memory` same as the source instance you created above.  

   ```python
     Example:
    {
         "dbname_prefix": "neo4j_wkshp", # prefix to use for all the newly created machines
         "num_instances": 4, # number of instances 
         "params": {
           "version": "5",
           "region": "europe-west1",
           "memory": "8GB",
           "type": "enterprise-ds",
           "cloud_provider": "gcp",
           "source_instance_id": "44683a64", # source instance for clones
           "source_snapshot_date": "2024-08-13", # update this with today's date or a specific date in the past
           "source_snapshot_id": ""
        }
    }
     ```  
   If you know and plan to use a specific snapshot, update `source_snapshot_id` with that snapshot ID.  Otherwise, leave it blank and the latest snapshot will be used.

   ```python
     Example:
   {
           "source_snapshot_id": "86509b6a-1b56-4a37-a65e-ede480661a67"
   }
   ```

   **Snapshots**

    `instance_id`is required for getting a list of snapshots from an existing instance.
     `snapshot_date` is optional.

     ```python
     Example:
       {
        "instance_id": "44683a64",
        "snapshot_date": "2024-08-13"
        }
     ```

   **Status/Pause/Resume/Delete**

     Parameters are **not** mutually exclusive.

     ```python
     Example:
       {
         "instance_ids": [], # specific instances
         "dbname_prefix":"neo4j_wkshp", # instance ids with names that starts with the prefix
         "exclude": [] # any instance IDs to exclude
       }
     ```

### Task Execution
5. Open the terminal and run the below command for any supported task. Please make sure you have updated the required parameters under the task in `config.json`

   ```shell
   % python /path_to_folder/main.py <tenant_id> <client Id> <client secret> <task> --output /path_to_folder/csvfile.csv
   ```
    - Tenant ID (Eg: "6e748720-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    - Client ID and Client Secret (for Aura API access)
    - Instance ID for the new database (Eg: "44683a64")

    - When new instances are created or cloned, the credentials are written to the output CSV file.  Output is written to "instances.csv" file by default if `/path_to_folder/csvfile.csv` is not specified.
    - **Please save the file and or copy the credentials** The file will be overwritten when you run the code for the second time.

### Collect the credentials for newly created/cloned instances
**If you are running a workshop, you will want readable passwords for printouts.**

6. Open the terminal and run the below command

   ```shell
    % python /path_to_folder/readable_passwords.py /path_to_folder/csvfile.csv
   ```
    - input: output filename/path from step 4
    - output: csv with _readable_pw suffix added

Use `readable_passwords.py` after all of the instances are up and running to create and update login information. If you run this before the instances are running, you will get an `Unable to retrieve routing information error`

### Generate workshop handouts 
**If you are running a workshop, you will want printed credentials to hand out for each participant.**

7. Open the terminal and run the below command

   ```shell
    % python /path_to_folder/generate_handouts.py /path_to_folder/csvfile.csv
   ```
    - input: output filename/path from step 6 (csv with _readable_pw suffix added)
    - output: __pdf__ with _handouts_ prefix added

Print the _handouts_csvfile_readable_pw.pdf_ and pass one page out to each participant at the workshop.
