#!/usr/bin/env python3
"""
MySQL Database Backup
Using mysqldump utility
Check dbbackup.config.ini to update DB Backup Settings
Usage:
    python dbbackup.py -p [DEV|TEST|REG|PROD]

Author:
    Pranjal Singh 28.09.2021
"""
import time
import sys
import configparser
import logging
import os
import gzip
import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--phase', dest='env',
                    help='Type Environment for which this would execute.',
                    required=True, choices=['DEV', 'TEST', 'REG', 'PROD'])
args = parser.parse_args()
SET_ENV = args.env

DATE_TIME = time.strftime('%Y_%m_%d_%H_%M_%S')
CONFIG_FILE = 'dbbackup.config.ini'
CUR_DIR = os.getcwd()
LOG_FORMAT = '%(asctime)s [%(name)s] : %(levelname)s - %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT, level=LOG_LEVEL)


class DbBackup:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config._interpolation = configparser.ExtendedInterpolation()
        config_file_path = CUR_DIR + '/' + CONFIG_FILE
        if not os.path.exists(config_file_path):
            logging.error('Config file {} not found'.format(config_file_path))
            sys.exit()

        logging.info('Reading config file ' + config_file_path)
        self.config.read(config_file_path)
        self.check_config()
        self.check_backup_directory()

    def process_backup(self):
        backup_dbs = [x.strip() for x in self.get_config_value(SET_ENV, 'db').split(',') if x != '']
        if len(backup_dbs) == 0:
            logging.error('DB not set for the backup in setting')
            logging.info('In setting section of config, please use BackupDB: db1,db2,...')
            sys.exit()

        logging.info('{} DB found for backup [{}]'.format(len(backup_dbs), ', '.join(backup_dbs)))
        for db_set in backup_dbs:
            if SET_ENV in self.config.sections()[1:]:
                logging.info('Using [{}] config to generate the backup for [{}] database'.format(SET_ENV, db_set))
                self.db_dump(db_set)
            else:
                logging.warning('DB Config [{}] not found. Skipping backup process'.format(SET_ENV))

    def db_dump(self, db_name):
        db_host = self.get_config_value(SET_ENV, 'host')
        db_port = self.get_config_value(SET_ENV, 'port')
        db_user = self.get_config_value(SET_ENV, 'user')
        db_pass = self.get_config_value(SET_ENV, 'pass')

        logging.info('Generating backup for database [{}] using [{}] from server [{}]'.format(
            db_name, db_user, db_host))
        db_file_abs_path = '{}/{}_{}.sql'.format(self.get_config_value('setting', 'BackupPath'), db_name, DATE_TIME)
        db_dump_cmd = "mysqldump -h {} -P {} -u {} -p{} {} > {}".format(
            db_host, db_port, db_user, db_pass, db_name, db_file_abs_path)
        cmd_status = os.system(db_dump_cmd)
        if cmd_status == 0:
            logging.info('Successfully generated backup file at {}'.format(db_file_abs_path))
            if self.config.getboolean('setting', 'compression'):
                self.gzip_db_file(db_file_abs_path)
        else:
            logging.info('Failed to generate database backup for [{}]'.format(db_name))

    @staticmethod
    def gzip_db_file(db_file_path):
        with open(db_file_path, 'rb') as f_in:
            with gzip.open(db_file_path + '.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        if os.path.exists(db_file_path + '.gz'):
            os.remove(db_file_path)

    def check_backup_directory(self):
        backup_directory_path = self.get_config_value('setting', 'BackupPath') + '/'
        if not os.path.exists(backup_directory_path):
            logging.info('Creating backup directory at {}'.format(backup_directory_path))
            os.makedirs(backup_directory_path)

    def get_config_value(self, section_name, section_option):
        if self.config.has_option(section_name, section_option):
            option_value = self.config.get(section_name, section_option)
        else:
            option_value = ''
        return option_value

    def check_config(self):
        if len(self.config.sections()) == 0:
            logging.error('No section found in config file')
            sys.exit()

        if len(self.config.sections()[1:]) == 0:
            logging.error('No Database specific section found in config file')
            sys.exit()

        if 'setting' not in self.config.sections():
            logging.error('No setting section found in config file')
            sys.exit()


def main():
    logging.info('Process Started')
    obj = DbBackup()
    obj.process_backup()
    logging.info('Process Finished')


if __name__ == '__main__':
    sys.exit(main())
