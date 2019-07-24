# kakao_arena
code for kakao arena

# 환경 설정
- 용량 문제로 업로드가 안되었다.
  1) './res/read/' 폴더 안에 read.tar 파일을 압축 해제 해야함
  2) metadata.json과 users.json를 추가해야 한다. 위치는 './res/metadata.json', './res/users.json' 이다.
 
# 실행 방법

1) python inference.py로 테스트 데이터에 대한 예측 결과가 재현할 수 있다.
2) python train.py 커맨드로 모델을 생성한다.

# 구동 원리

 평가데이터 유저의 구독 작가와 읽었던 글의 작가를 대조하여 일치 하는 경우
 해당 작가의 글을 추천 글로 제시하였다.
 
 만약 구독작가가 없다면, 읽었던 글의 작가 글을 추천
 만약 읽었던 글이 없다면, 구독 작가의 글을 추천
 
 
