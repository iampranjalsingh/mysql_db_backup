# MySQL DB Backup
Python scripts to take MySQL database backup periodically and clean the older database as well.
* mysqldbbackup.py
* dbbackup.py
* cleandbbackup.py

## mysqldbbackup.py
This script will generate and save the backups in different timestamp directory.
### mysqldbbackup.config.ini
```
[setting]
# Name of the Databases for backups.
# For each DB the db parameter needs to be set at the bottom section
BackupDB: employees,sampledb
# Path where backup sould be stored
BackupPath: C:\Tmp\dbbackup
# Backup file in compressed format True/False
Compression: True

# Should match exactly the key provided in the Setting Section of BackupDB
[employees]
host: localhost
port: 3306
user: dbuser
pass: password
db: employees
# table: Optional, if require to take backup of some specific tables from this database
table: employee,salary
```
To run the script
```
python mysqldbbackup.py
```

## dbbackup.py
This script will generate and save the backups based on Database Environments DEV, TEST, REG, PROD.
### dbbackup.config.ini
```
[setting]
# Name of the Databases for backups from each environments.
BackupDB: employees,sampledb
# Path where backup sould be stored
BackupPath: C:\Tmp\dbbackup
# Backup file in compressed format True/False
Compression: True
# For how many days old databse should kept
DaysToKeepDB: 15
# 2 months of Sunday backup would be saved
DaysToKeepSundayDB: 60

# For each enviorments the DB configuration need to be added
[DEV]
host: localhost
port: 3306
user: dbuser
pass: password
# db: default parameter would be all the BackupDB but can be updated here to save some specific databases 
db: ${setting:BackupDB}
```
To run the script
```
python dbbackup.py -p [DEV|TEST|REG|PROD]
```

## cleandbbackup.py
Remove old MySQL Database Backups more than 15 days & keep Sunday backup for previous 2 months
To run the script
```
python cleandbbackup.py
```