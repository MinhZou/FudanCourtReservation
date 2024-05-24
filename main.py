# -*- coding: utf-8 -*-
"""
@author: MinhZou
@date: 2022-04-03
@e-mail: 770445973@qq.com
"""

import os
import yaml
from apscheduler.schedulers.blocking import BlockingScheduler
from scripts.client import Client


if __name__ == '__main__':
    filepath = os.path.join(os.getcwd(), 'configs/user_configs.yaml')
    with open(filepath, 'r', encoding='utf-8') as f:
        configs = yaml.load(f, Loader=yaml.FullLoader)
    user1_configs = configs['user1']
    user1_client = Client(user1_configs)
    user1_client.scheduled_job()

    # sched = BlockingScheduler()
    # for h in [6]:
    #     sched.add_job(Client(user1_configs).scheduled_job, 'cron', day_of_week='0,2', hour=h, minute=57)
    # sched.start()