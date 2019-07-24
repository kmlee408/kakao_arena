# -*- coding: utf-8 -*-
import os
try:
    import cPickle
except ImportError:
    import pickle as cPickle

import random
import tqdm

from collections import Counter
import operator

import from_to_set as fts
import config as conf
import preprocessing as pp
import train


class inference():

    def __init__(self):

        self.from_dtm = str(fts.train_from_dtm)  # 2018100100
        self.to_dtm = str(fts.train_to_dtm) # 2019022200

        self.from_dtm_dev = str(fts.dev_from_dtm) # 2019022200
        self.to_dtm_dev = str(fts.dev_to_dtm) # 2019031400

        #평가 데이터 유저 목록
        self.user_list = []

        # 추천 글 수
        self.recommend_size = 100

        # 주요 작가 당 추천 받을 글 수
        self.import_following_size = 20

        # 작가 당 추천 받을 글 수(optimize)
        self.following_writing_size = 5

        #format data user_reading
        self.ur = {}
        #format data writing_writer
        self.ww = {}
        #format data writing_count
        self.wc = []

    def set_user_reading(self):
        f_name = 'user_reading_' + self.from_dtm + '_' + self.to_dtm
        f_path = conf.format_root + f_name

        if os.path.isfile(f_path):
            user_reading = open(f_path)
        else:
            pp.user_reading()
            user_reading = open(f_path)

        for line in user_reading:
            line_ = line.strip().split()
            user = line_[0]
            seen = line_[1:]
            self.ur[user] = seen

        user_reading.close()

    def set_writing_writer(self):
        f_name = 'writing_writer_' + self.from_dtm + '_' + self.to_dtm
        f_path = conf.format_root + f_name

        if os.path.isfile(f_path):
            writing_writer = open(f_path)
        else:
            pp.writing_writer()
            writing_writer = open(f_path)

        for line in writing_writer:
            line_ = line.strip().split()
            user = line_[0]
            seen = line_[1:]
            self.ww[user] = seen

        writing_writer.close()

    def set_writing_count(self):
        f_name = 'writing_count_' + self.from_dtm + '_' + self.to_dtm
        f_path = conf.format_root + f_name

        if os.path.isfile(f_path):
            writing_count = open(f_path)
        else:
            pp.writing_count()
            writing_count = open(f_path)

        for line in writing_count:
            writing = line.strip().split()[0]

            self.wc.append(writing)

        writing_count.close()

    def get_flw_model(self):

        model_name = 'flw.model_'+ self.from_dtm_dev + '_' + self.to_dtm_dev
        model_path = conf.model_root + model_name

        if os.path.isfile(model_path):
            flw_model = cPickle.load(open(model_path, 'rb'))
            return flw_model

        else:
            train.train().build_flw_model()
            flw_model = cPickle.load(open(model_path, 'rb'))
            return flw_model

    def get_user_flw_model(self):

        model_name = 'user_flw.model_' + self.from_dtm_dev + '_' + self.to_dtm_dev
        model_path = conf.model_root + model_name

        if os.path.isfile(model_path):
            u_flw_model = cPickle.load(open(model_path, 'rb'))
            return u_flw_model

        else:
            train.train().build_user_flw_model()
            u_flw_model = cPickle.load(open(model_path, 'rb'))
            return u_flw_model

    def set_user_list(self, Test = False):

        if Test:
            user = open(conf.data_root + 'predict/test.users')
        else:
            user = open(conf.data_root + 'predict/dev.users')
        for line in user:
            self.user_list.append(line[:-1])

    def recommend(self):

        self.set_user_reading()
        self.set_writing_writer()
        self.set_writing_count()

        flw_model = self.get_flw_model()
        user_flw_model = self.get_user_flw_model()

        self.set_user_list(Test = True)

        count_list = []
        recommend_size = self.recommend_size

        print('recommending...')
        reco_txt = open('./recommend.txt', 'w')
        with open('./recommend', 'w') as recommend:

            for user in tqdm.tqdm(self.user_list, mininterval=1):

                recommend_list = []

                writer_bool = False
                reading_bool = False

                try:
                    # user.tar 기반
                    # 구독 작가 리스트
                    user_flw = user_flw_model[user]
                    writer_bool = True

                except:
                    writer_bool = False

                try:
                    # reading 기반
                    # 본 글 리스트
                    seen = self.ur[user]
                    reading_bool = True

                except:
                    reading_bool = False

                # 1단계 구독+ 봤던 글 중에 겹치는 작가 확인.
                if writer_bool and reading_bool:
                    # 구독작가, 글 기록 있다면.

                    seen_length = len(seen)
                    seen_writer_list = []
                    import_flw = []

                    # 봤던 글의 작가 목록 작성
                    for writing in self.ur[user]:
                        try:
                            if self.ww[writing][0] in seen_writer_list:
                                continue
                            seen_writer_list.append(self.ww[writing][0])
                        except:
                            continue


                    # 주요 작가 선정
                    for sw in seen_writer_list:
                        if sw in user_flw:
                            import_flw.append(sw)

                    # 주요 작가
                    ifs = self.import_following_size  # 글 몇개를 할거냐 defalut는 위에서 설정

                    # 주요 작가가 너무 많으면.. 추천글수를 줄여줌
                    if len(import_flw) * self.import_following_size > recommend_size+ seen_length:
                        ifs = max(1, int(recommend_size+seen_length / len(import_flw)))

                    # 주요 작가의 글 추천
                    for im_flw in import_flw:

                        if not im_flw in flw_model.keys():
                            continue

                        range_ = ifs
                        # 글의 수가 범위보다 작으면 수정
                        if len(flw_model[im_flw]) < range_:
                            range_ = len(flw_model[im_flw])

                        # 저장할 글이 중복인지 확인.
                        for ifw in flw_model[im_flw][:range_]:

                            if ifw in seen:
                                continue

                            if ifw in recommend_list:
                                continue

                            recommend_list.append(ifw)

                    # 추천 수가 모자라면 다른 구독 작가 글 중 추천
                    if len(recommend_list) < recommend_size:

                        for writer in user_flw:
                            # 주요작가는 스킵
                            if writer in import_flw:
                                continue
                            if not writer in flw_model.keys():
                                continue

                            # 다른 구독 작가 글 중 추천
                            wt = flw_model[writer][:self.following_writing_size]
                            for wt_ in wt:
                                if wt_ in seen:
                                    continue
                                else:
                                    recommend_list.append(wt_)

                            if len(recommend_list) >= recommend_size:
                                break

                    # 그래도 추천 수가 모자라면 봤던 글의 작가 중 글 추천
                    if len(recommend_list) < recommend_size:

                        for writer in seen_writer_list:

                            if writer in import_flw:
                                continue

                            if not writer in flw_model.keys():
                                continue

                            #봤던 글의 작가 중 글 추천
                            wt = flw_model[writer][:self.following_writing_size]

                            for wt_ in wt:
                                if wt_ in seen:
                                    continue
                                else:
                                    recommend_list.append(wt_)

                            if len(recommend_list) >= recommend_size:
                                break

                # 2단계 구독 작가는 있는데 기록은 없는 경우
                if writer_bool and not reading_bool:

                    for writer in user_flw:

                        if not writer in flw_model.keys():
                            continue

                        # 구독 작가의 글 저장
                        writing_list = flw_model[writer]

                        for writing in writing_list:
                            recommend_list.append(writing)

                # 3단계 구독 작가는 없는데 기록은 있는 경우
                if not writer_bool and reading_bool:

                    seen_writer_list = []

                    for writing in seen:
                        try:
                            if self.ww[writing][0] in seen_writer_list:
                                continue
                            seen_writer_list.append(self.ww[writing][0])
                        except:
                            continue

                    # 최근에 봤던 글이 상위에 포진되게 수정


                    for writer in seen_writer_list:

                        if not writer in flw_model.keys():
                            continue

                        writing_list = flw_model[writer]

                        for writing in writing_list:
                            recommend_list.append(writing)



                # 둘다 없는 경우 가장 많이 본 글 추천
                if len(recommend_list) < recommend_size:

                    try:
                        seen = self.ur[user]
                    except:
                        seen = []

                    # 그 이후로 뭘 볼지 가늠이 안되므로 랜덤 추첨
                    while len(recommend_list) < recommend_size:

                        ran_num = random.randrange(0, len(self.wc))

                        writing = self.wc[ran_num]

                        # 중복 제거
                        if not writing in recommend_list:
                            if not writing in seen:
                                recommend_list.append(writing)

                # print('after', len(recommend_list))
                # print('\n')
                recommend_list = recommend_list[:recommend_size]
                # print('after', len(recommend_list) ,user)
                recommend.write('%s %s\n' % (user, ' '.join(recommend_list)))
                reco_txt.write('%s %s\n' % (user, ' '.join(recommend_list)))

        reco_txt.close()



if __name__ == '__main__':
    inference_ = inference()
    inference_.recommend()