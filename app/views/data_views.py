import os
import csv
import json
from app.functions import instaCrawl
from app.functions import Models
from flask import Blueprint, request
from app.functions import database
from app.functions.db_models import API_RESULTS

#### 독립적으로 외부 프로젝트에서 config 관리하는 방법
# import sys
# sys.path.append('opt/settings')
# import config

#### 내부에서 환경변수로 관리
from app.config import config

data_bp = Blueprint('data', __name__)

@data_bp.route('/menu', methods=['GET'])
def get_JSONdata():
    """
    get_user 함수는 `menu` 을 키로 한 값을 쿼리 파라미터 값으로 넘겨주면
    instaCrwal의 결과를 json 형태로 반환합니다. 
    
    요구사항:
      - HTTP Method: `GET`
      - Endpoint: `/api/menu`

    상황별 요구사항:
      - `menu` 값이 주어지지 않은 경우:
        - 리턴 값: "No Menu given"
        - HTTP 상태 코드: `400`
      - 주어진 `menu` 값으로 인스타를 정상적으로 조회한 경우:
        - 리턴 값: instacrwal의 반환값을 공공데이터 규격에 맞춰서 딕셔너리화한 값
        - HTTP 상태 코드: `200`
    """
    menu = request.args.get('menu')

    if menu==None:
      return "No menu given", 400
    
    ##### data_dict 요청에 대한 데이터를 DB로 보내는 과정 넣기
    data_dict = Models.Get_all_score_json(menu)
    # try:
    #   data_dict = Models.Get_all_score_json(menu)
    # except:
    #   return "Model Error", 404

    ##### api 사용결과 db에 ADD

    database.add_instance(API_RESULTS, input_value=menu,\
                          pred_category=data_dict['pred_category'],\
                          pred_origin=data_dict['origin_score'],\
                          pred_trend=data_dict['trend_score'],\
                          use_time=data_dict['use_time'])

    json_data = json.dumps(data_dict, ensure_ascii=False, default=str)

    return json_data, 200

@data_bp.route('/set_corpus', methods=['GET'])
def set_corpus():
    """
    요구사항:
      - HTTP Method: `GET`
      - Endpoint: `/api/set_corpus`

    상황별 요구사항:
      - `service_key` 값이 주어지지 않은 경우:
        - 리턴 값: "No service_key given"
        - HTTP 상태 코드: `400`
      - `service_key` 값이 틀린 경우:
        - 리턴 값: "Wrong service_key given"
        - HTTP 상태 코드: `400`
      - 크롤링이 완료된 경우:
        - 리턴 값: "Setting complete"
        - HTTP 상태 코드: `200`
    """
    key = request.args.get('service_key')

    if key==None:
      return "No menu given", 400
    
    if key!="abc123":
      return "Wrong service_key given", 400
    
    instaCrawl.Setting_all_corpus()
    
    # try:
    #   instaCrawl.Setting_all_corpus()
    # except:
    #   return "Crawling Error", 404

    return "Setting complete", 200

