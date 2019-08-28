# kakao_arena
code for kakao arena
[https://arena.kakao.com/forum/topics/166]

## 환경 설정
- 용량 문제로 데이터가 업로드되지 못하였습니다. 따라서 아래 2가지의 환경설정을 부탁드립니다.
  1) './res/read/' 폴더 안에 read.tar 파일을 압축 해제 해야합니다.
  2) metadata.json과 users.json를 추가해야 합니다. 위치는 './res/metadata.json', './res/users.json' 입니다.


## 실행 방법

1) python inference.py로 테스트 데이터에 대한 예측 결과가 재현할 수 있다.
2) python train.py 커맨드로 모델을 생성한다.


## 구동 원리

 brunch 사용자들에게 맞춤형 알고리즘을 제시하고자 하였습니다.
 EDA를 거쳐 구독 작가와 최근에 읽었던 글에 영향을 많이 받는다는 것을 알고 
 그 점을 이용하여 새로운 알고리즘을 만들었습니다.

 평가데이터 유저의 구독 작가와 읽었던 글의 작가를 대조하여 일치 하는 경우
 해당 작가의 글을 추천 글로 제시하였다.
 
 만약 구독작가가 없다면, 읽었던 글의 작가 글을 추천
 
 만약 읽었던 글이 없다면, 구독 작가의 글을 추천
 
 
