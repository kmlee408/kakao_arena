# -*- coding: utf-8 -*-
import os
try:
    import cPickle
except ImportError:
    import pickle as cPickle

from collections import Counter
import operator

import tqdm
import pandas as pd

from util import iterate_data_files
import config as conf
import from_to_set as fts


from_dtm = str(fts.train_from_dtm)  # 2018100100
to_dtm = str(fts.train_to_dtm) # 2019022200

def user_reading(from_dtm = from_dtm, to_dtm = to_dtm):

    f_name = 'user_reading_' + from_dtm + '_' + to_dtm
    f_path = conf.format_root + f_name

    if os.path.isfile(f_path):
        return

    files = sorted([path for path, _ in iterate_data_files(from_dtm, to_dtm)])

    user_reading = open(f_path, 'w')
    _groupby = {}

    print('creating... ' + f_name)
    for path in tqdm.tqdm(files, mininterval=1):

        for line in open(path):

            line_ = line.strip().split()
            userid = line_[0]
            seen = line_[1:]
            _groupby.setdefault(userid, []).extend(seen)

    for k, v in _groupby.items():
        user_reading.write('%s %s\n' % (k, ' '.join(v)))

    user_reading.close()


def writing_writer():

    f_name = 'writing_writer_' + from_dtm + '_' + to_dtm
    f_path = conf.format_root + f_name

    if os.path.isfile(f_path):
        return

    print('creating... ' + f_name)
    df_meta = pd.read_json(conf.data_root + 'metadata.json', lines=True)

    with open(f_path, 'w') as ww:

        for i in tqdm.tqdm(range(len(df_meta)), mininterval=1):
            writing_id = df_meta.loc[i]['id']
            writer = df_meta.loc[i]['user_id']
            ww.write('%s %s\n' % (writing_id, writer))


def writing_count(from_dtm = from_dtm, to_dtm = to_dtm):

    f_name = 'writing_count_' + from_dtm + '_' + to_dtm
    f_path = conf.format_root + f_name

    if os.path.isfile(f_path):
        return

    ur_f_name = 'user_reading_' + from_dtm + '_' + to_dtm
    ur_f_path = conf.format_root + ur_f_name

    if os.path.isfile(ur_f_path):
        user_reading = open(ur_f_path)

    else:
        preprocessing.user_reading()
        user_reading = open(ur_f_path)


    writing_list = []
    print('creating... ' + f_name)
    for line in user_reading:
        line_ = line.strip().split()
        seen = line_[1:]
        writing_list += seen

    writing_dict = dict(Counter(writing_list))
    writing_list = sorted(writing_dict.items(), key=operator.itemgetter(1), reverse=True)


    with open(f_path, 'w') as wc:
        for writing_tuple in writing_list:
            wc.write('%s %s\n' % (writing_tuple[0], writing_tuple[1]))