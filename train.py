# -*- coding: utf-8 -*-
import os
try:
    import cPickle
except ImportError:
    import pickle as cPickle

import pandas as pd
import tqdm

import from_to_set as fts
import config as conf
from util import datetime2unixtime

import operator

class train():

    def __init__(self):

        # 평가 기간 설정
        self.from_dtm = str(fts.dev_from_dtm)
        self.to_dtm = str(fts.dev_to_dtm)

        # 작가가 쓴 글 중 오래된 글의 기준 설정(optimize)
        self.day = 5


    def build_flw_model(self):

        limit_from_ut = datetime2unixtime(self.from_dtm)
        limit_to_ut = datetime2unixtime(self.to_dtm)
        limit_day = 86400 * self.day

        model_name = 'flw.model_'+ self.from_dtm + '_' + self.to_dtm
        model_path = conf.model_root + model_name

        if os.path.isfile(model_path):
            print('The model has already been created.', model_path )
            return

        print('creating flw_model... [1/2]')
        df_meta = pd.read_json(conf.data_root + 'metadata.json', lines =True)

        with open(model_path, 'wb') as flw_model:

            flw_dict = {}
            for index in tqdm.tqdm(range(len(df_meta)), mininterval=1):

                reg_ts = str(df_meta.loc[index]['reg_ts'])[:-3]

                # 평가 날짜 이후의 글은 제거..
                if len(reg_ts) == 0 or int(reg_ts) > limit_to_ut:
                    continue

                # 평가 시작 날로 부터 5일 전 글만 사용
                # 5일 전 글부터 순서대로 저장, 순서대로 첫 페이지부터 노출하기 위함
                if len(reg_ts) == 0 or int(reg_ts) + limit_day < limit_from_ut:
                    continue

                writer = df_meta.loc[index]['user_id']
                wr_id = df_meta.loc[index]['id']

                flw_dict.setdefault(writer, []).append((wr_id, reg_ts))

            print('creating flw_model... [2/2]')
            for key in tqdm.tqdm(flw_dict.keys(), mininterval=1):
                wt = sorted(flw_dict[key], key=operator.itemgetter(1))
                wt = list(map(lambda x: x[0], wt))
                # 글 등록 시간이 빠른 순서대로 정렬 후 리스트형태로 저장
                flw_dict[key] = wt

            cPickle.dump(flw_dict, flw_model)
            print('complete flw_model')

    def build_user_flw_model(self):

        model_name = 'user_flw.model_'+ self.from_dtm + '_' + self.to_dtm
        model_path = conf.model_root + model_name

        if os.path.isfile(model_path):
            print('The model has already been created.', model_path )
            return

        df_user = pd.read_json(conf.data_root + 'users.json', lines=True)

        print('creating user_flw_model...')
        with open(model_path, 'wb') as user_flw_model:
            user_following_dict = {}

            for i in tqdm.tqdm(range(len(df_user)), mininterval =1 ):
                user_following_dict[df_user.loc[i]['id']] = df_user.loc[i]['following_list']

            cPickle.dump(user_following_dict, user_flw_model)

        print('complete user_flw_model')

if __name__ == '__main__':
    train_ = train()
    train_.build_flw_model()
    train_.build_user_flw_model()