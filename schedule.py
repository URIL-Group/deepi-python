#! /usr/bin/env python
'''Schedule actions for the picamera

'''

from crontab import CronTab

USER='pi'

cron = CronTab(user=USER)
