#!/usr/bin/env python3
"""
Remove old MySQL Database Backups more than 15 days
Keep Sunday backup for previous 2 months
Usage:
    python cleandbbackup.py

Author:
    Pranjal Singh 28.09.2021
"""
import sys
import os
import configparser
import logging
from datetime import datetime
from dateutil import relativedelta
import smtplib

CONFIG_FILE = 'dbbackup.config.ini'
CUR_DIR = os.getcwd()
LOG_FORMAT = '%(asctime)s [%(name)s] : %(levelname)s - %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT, level=LOG_LEVEL)


class CleanDbBackup:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config._interpolation = configparser.ExtendedInterpolation()
        config_file_path = CUR_DIR + '/' + CONFIG_FILE
        if not os.path.exists(config_file_path):
            logging.error('Config file {} not found'.format(config_file_path))
            sys.exit()

        logging.info('Reading config file ' + config_file_path)
        self.config.read(config_file_path)

    def process_clean(self):
        today = datetime.today()
        backup_directory_path = self.config.get('setting', 'BackupPath')
        days_to_keep_sunday_db = self.config.getint('setting', 'DaysToKeepSundayDB')
        days_to_keep_db = self.config.getint('setting', 'DaysToKeepDB')
        logging.info('Reading directory [{}] for backup files'.format(backup_directory_path))

        dir_content = os.listdir(backup_directory_path)
        logging.info('{} DB backup files found'.format(len(dir_content)))
        for file_name in dir_content:
            db_file_path = backup_directory_path + '/' + file_name
            timestamp_created_on = os.path.getctime(db_file_path)
            date_obj = datetime.fromtimestamp(timestamp_created_on)
            date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            date_weekday = date_obj.strftime("%w")
            display_date_weekday = date_obj.strftime("%A")
            timestamp_difference = relativedelta.relativedelta(today, date_obj)
            file_age_in_days = timestamp_difference.days

            logging.info("File Name: {:<40} Creation Date: {} Weekday: {} FileAge: {} Days".format(
                file_name, date_str, display_date_weekday, file_age_in_days))

            if file_age_in_days > days_to_keep_sunday_db:
                logging.info("Deleting File [{}] with age: {} Days".format(file_name, file_age_in_days))
                self.delete_file(db_file_path)

            # Check if file Age in between DaysToKeepDB & DaysToKeepSundayDB
            if (days_to_keep_db <= file_age_in_days <= days_to_keep_sunday_db) and date_weekday != 0:
                # Delete the file if its not Sunday
                logging.info("Deleting File [{}] with age: {} Days".format(file_name, file_age_in_days))
                self.delete_file(db_file_path)

    def db_file_count(self):
        dir_content = os.listdir(self.config.get('setting', 'BackupPath'))
        file_list = []
        for file_name in dir_content:
            file_list.append(file_name)

        logging.info('Total DB Version Found: {}'.format(len(file_list)))
        return len(file_list)

    @staticmethod
    def delete_file(db_file_to_remove):
        if os.path.exists(db_file_to_remove):
            os.remove(db_file_to_remove)


def send_notification():
    mail_from = 'DB Cleanup Process'
    mail_to = 'Pranjal SINGH <iampranjalsingh@gmail.com>'
    receivers = ['iampranjalsingh@gmail.com']

    message = """From: {}
    To: {}
    Subject: {}
    
    Hi,\n
    There in not enough Backup version of databases.\n
    Cleaning of old database is not required if Backup Versions are less than 10.
    """.format(mail_from, mail_to, 'Error - Not Enough DB Backup Version')

    server = smtplib.SMTP('your.smtp.host.server')
    server.sendmail('your.smtp.host.server', receivers, message)


def main():
    logging.info('Process Started')
    obj = CleanDbBackup()
    if obj.db_file_count() > 22:
        obj.process_clean()
    else:
        logging.info('There in not enough Backup version of databases. Cleaning of old DB is not required')
        # send_notification() // Enable if mail notification is required
    logging.info('Process Finished')


if __name__ == '__main__':
    sys.exit(main())
