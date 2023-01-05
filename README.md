# S3Project

.env 내의 환경변수를 시스템 환경변수 편집에서 추가해줘야 작동합니다.

2023-01-05 기준 문제점

- [해결] metabase compose 이후 에러
-> .env 내의 환경변수 중에서 PG_HOST가 metabase 서비스 내의 MB_DB_HOST에서는 localhost라고 나오는 오류가 발생했음
-> 그냥 postgres를 지정해주면서 해결
- trend_score 가 corpus 내의 단어에 대해서 입력값을 제대로 반영하지 못하는 부분
- docker 빌드 시, insta_Crawl 이 webdriver를 위치를 제대로 잡지 못함
- docker volume을 활용하여 corpus와 api_results를 postgreSQL 이미지끼리 공유할 수 있도록 추가해야함
 
