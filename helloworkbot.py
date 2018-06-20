#!/usr/bin/env python3

import argparse
from email.message import EmailMessage
from email.headerregistry import Address
import math
import re
import smtplib
import urllib.parse
import urllib.request

url = 'https://www.hellowork.go.jp/servicef/130050.do'
filename = 'helloworkbot.csv'

mta = 'YOUR_MAIL_SERVER:25'
msg = EmailMessage()
msg['Subject'] = "helloworkbot"
msg['From'] = Address("YOUR NAME", "LOCAL-PART", "DOMAIN")
msg['To'] = (Address("YOUR NAME", "LOCAL-PART", "DOMAIN"),)
A = ["SOME GROUP A KEYWORD", "SOME OTHER GROUP A KEYWORD", "AND SO ON..."]
B = ["SOME GROUP B KEYWORD", "SOME OTHER GROUP B KEYWORD", "AND SO ON..."]
C = ["SOME GROUP C KEYWORD", "SOME OTHER GROUP C KEYWORD", "AND SO ON..."]
A_regex = re.compile("|".join(A), re.IGNORECASE)
B_regex = re.compile("|".join(B), re.IGNORECASE)
C_regex = re.compile("|".join(C))

request_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'www.hellowork.go.jp',
    'Origin': 'https://www.hellowork.go.jp',
    'Referer': 'https://www.hellowork.go.jp/servicef/130020.do',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'helloworkbot',
}
form_data_default = {
    'action': '',
    'actionFlgHidden': '1',
    'codeAssistCode': '',
    'codeAssistDivide': '',
    'codeAssistItemCode': '',
    'codeAssistItemName': '',
    'codeAssistKind': '',
    'codeAssistRankLimit': '',
    'codeAssistType': '',
    #'commonSearch': '検索',
    'freeWord': '',
    'freeWordType': '0',
    'freeWordTypeHidden': '0',
    'fwListLeftPage': '1',
    'fwListNaviCount': '11',
    'fwListNowPage': '1',
    #'gekkyuKagen': '',# gekkyuKagen or jikyuKagen
    'jigyoshomei': '',
    #'jikyuKagen': '',# gekkyuKagen or jikyuKagen
    'kiboSangyo1': '',
    'kiboSangyo2': '',
    'kiboSangyo3': '',
    'kiboShokushu1': '',#
    'kiboShokushu1Hidden': '',#
    'kiboShokushu2': '',#
    'kiboShokushu2Hidden': '',#
    'kiboShokushu3': '',#
    'kiboShokushu3Hidden': '',#
    'kyujinkensu': '0',
    'kyujinShuruiHidden': '',# 1 for full-time, 2 for part-time
    'kyushokuNumber1': '',
    'kyushokuNumber1Hidden': '',
    'kyushokuNumber2': '',
    'kyushokuNumber2Hidden': '',
    'kyushokuUmu': '1',
    'kyushokuUmuHidden': '1',
    'license1': '',
    'license2': '',
    'license3': '',
    #'nenkanKyujitsu': '',# nenkanKyujitsu or (shoteiRodoNissu and shoteiRodoNissuKagen)
    'nenrei': '',
    'nenreiHidden': '',
    'notFreeWord': '',
    'nowPageNumberHidden': '1',
    'rdoJkgi': '9',
    'rdoJkgiHidden': '9',
    'screenId': '130050',
    'shinchakuKyujinHidden': '1',#
    #'shoteiRodoNissu': 1,# nenkanKyujitsu or (shoteiRodoNissu and shoteiRodoNissuKagen)
    #'shoteiRodoNissuKagen': '',# nenkanKyujitsu or (shoteiRodoNissu and shoteiRodoNissuKagen)
    'shugyoJikanKaishiHH': '',
    'shugyoJikanKaishiMM': '',
    'shugyoJikanShuryoHH': '',
    'shugyoJikanShuryoMM': '',
    'shukyuFutsuka': '0',
    'shukyuFutsukaHidden': '0',
    'teate': '1',
    'teateHidden': '1',
    'xab_vrbs': 'commonNextScreen,detailJokenChangeButton,commonDetailInfo,commonSearch,commonDelete',
}
keyword = {
    'job_number': '<th style="width:195px;">求人番号</th>',
    'full_time_or_part_time': '<th style="width:195px;">求人情報の種類</th>',
    'organization_name': '<th style="width:195px;">事業所名</th>',
    'executive_director': '<th style="width:195px;">代表者名</th>',
    'organization_number': '<th style="width:195px;">法人番号</th>',
    'address': '<th style="width:195px;">所在地</th>',
    'phone_number': '<th style="width:195px;">電話番号</th>',
    'fax_number': '<th style="width:195px;">FAX番号</th>',
    'business_description': '<th style="width:195px;">事業内容</th>',
    'type_of_job': '<th style="width:195px;">職種</th>',
    'employment_type': '<th style="width:195px;">雇用形態</th>',
    'industry': '<th style="width:195px;">産業</th>',
    'type_of_work_hours': '<th style="width:195px;">就業形態</th>',
    'period_of_employment': '<th style="width:195px;">雇用期間</th>',
    'age_requirements': '<th style="width:195px;">年齢</th>',
    'reason_for_age_requirements': '<th style="width:195px;">年齢制限の理由<br />',
    'work_hours': '<th style="width:195px;">就業時間</th>',
    'break': '<th style="width:195px;">休憩時間</th>',
    'overtime': '<th style="width:195px;">時間外</th>',
    'work_days_per_week': '<th style="width:195px;">週所定労働日数</th>',
    'wage': '<div>a&#xa0;基本給（月額平均）又は時間額</div>',
    'wage_and_allowance': '<div>a&#xa0;&#x2b;&#xa0;b</div>',
    'bonus': '<th style="width:195px;">賞与</th>',
    'days_of_rest': '<th style="width:195px;">休日</th>',
    'two_day_weekend': '<th style="width:195px;">週休二日</th>',
    'days_of_rest_per_year': '<th style="width:195px;">年間休日数</th>',
    'childcare_leave_record': '<th style="width:195px;">育児休業取得実績</th>',
    'available_day_care_center': '<th style="width:195px;">利用可能な託児所</th>',
    'office_location': '<th style="width:195px;">就業場所</th>',
    'transfer': '<th style="width:195px;">転勤</th>',
    'number_of_employees': '<th style="width:195px;">従業員数</th>',
    'insurance': '<th style="width:195px;">加入保険等</th>',
    'retirement_age': '<th style="width:195px;">定年制</th>',
    'reemployment': '<th style="width:195px;">再雇用</th>',
    'company_housing': '<th style="width:195px;">入居可能住宅</th>',
    'commuting_by_car': '<th style="width:195px;">マイカー通勤</th>',
    'transportation_allowance': '<th style="width:195px;">通勤手当</th>',
    'number_of_positions': '<th style="width:195px;">採用人数</th>',
    'job_description': '<th style="width:195px;">仕事の内容</th>',
    'education': '<th style="width:195px;">学歴</th>',
    'experience': '<th style="width:195px;">必要な経験等</th>',
    'qualifications': '<th style="width:195px;">必要な免許・資格</th>',
    'selection_procedures': '<th style="width:195px;">選考方法</th>',
    'notice_of_result': '<th style="width:195px;">選考結果通知</th>',
    'application_documents': '<th style="width:195px;">応募書類等</th>',
    'selection_schedule': '<th style="width:195px;">選考日時</th>',
    'specific_qualifications': '<th style="width:195px;">求人条件にかかる特記事項</th>',
    'remarks': '<th style="width:195px;">備考</th>',
    'registration_date': '<th style="width:195px;">受理日</th>',
    'expiration_date': '<th style="width:195px;">有効期限日</th>',
    'registration_office': '<th style="width:195px;">受理安定所</th>',
}
output_header = [
                 "job_number",# 求人番号
                 "full_time_or_part_time",# 求人情報の種類
                 "organization_name",# 事業所名
                 "executive_director",# 代表者名
                 "organization_number",# 法人番号
                 "address",# 所在地
                 "phone_number",# 電話番号
                 "fax_number",# FAX番号
                 "business_description",# 事業内容
                 "type_of_job",# 職種
                 "employment_type",# 雇用形態
                 "industry",# 産業
                 "type_of_work_hours",# 就業形態
                 "period_of_employment",# 雇用期間
                 "age_requirements",# 年齢
                 "reason_for_age_requirements",# 年齢制限の理由
                 "work_hours",# 就業時間
                 "break",# 休憩時間
                 "overtime",# 時間外
                 "work_days_per_week",# 週所定労働日数
                 "minimum_wage",# 基本給(下限)
                 "maximum_wage",# 基本給(上限)
                 "minimum_wage_and_allowance",# 基本給と定額(下限)
                 "maximum_wage_and_allowance",# 基本給と定額(上限)
                 "bonus",# 賞与
                 "days_of_rest",# 休日
                 "two_day_weekend",# 週休二日
                 "days_of_rest_per_year",# 年間休日数
                 "childcare_leave_record",# 育児休業取得実績
                 "available_day_care_center",# 利用可能な託児所
                 "office_location",# 就業場所
                 "transfer",# 転勤
                 "number_of_employees_of_organization",# 従業員数(企業全体)
                 "number_of_employees_of_office",# 従業員数(うち就業場所)
                 "number_of_female_employees_of_office",# 従業員数(うち女性)
                 "number_of_part_time_employees_of_office",# 従業員数(うちパート)
                 "insurance",# 加入保険等
                 "retirement_benefit",# 退職金制度
                 "retirement_age",# 定年制
                 "reemployment",# 再雇用
                 "company_housing",# 入居可能住宅
                 "commuting_by_car",# マイカー通勤
                 "transportation_allowance",# 通勤手当
                 "number_of_positions",# 採用人数
                 "job_description",# 仕事の内容
                 "education",# 学歴
                 "experience",# 必要な経験等
                 "qualifications",# 必要な免許・資格
                 "selection_procedures",# 選考方法
                 "notice_of_result",# 選考結果通知
                 "application_documents",# 応募書類等
                 "selection_schedule",# 選考日時
                 "specific_qualifications",# 求人条件にかかる特記事項
                 "remarks",# 備考
                 "registration_date",# 受理日
                 "expiration_date",# 有効期限日
                 "registration_office",# 受理安定所
                ]

table_start_regex = re.compile(r'<table style="width: 810px;" cellspacing="0" class="sole-small">')
table_end_regex = re.compile(r'</table>')
tr_regex = re.compile(r'<tr>(.*?)</tr>')
th_regex = re.compile(r'<th')
td_regex = re.compile(r'<td.*?>\s*<div.*?>\s*(.*?)\s*</div>\s*</td>\s*'
                      r'<td.*?>\s*<div.*?>\s*(.*?)\s*</div>\s*</td>\s*'
                      r'<td.*?>\s*(<a.*?>\s?(\d+)-(\d+)\s?</a>)\s*</td>\s*'
                      r'<td.*?>\s*<div.*?>\s*(.*?)\s*</div>\s*</td>\s*'
                      r'<td.*?>\s*<div.*?>\s*(.*?)\s*</div>\s*</td>\s*'
                      r'<td.*?>\s*<div.*?>\s*(.*?)\s*</div>\s*</td>\s*'
                      r'<td.*?>\s*<div.*?>\s*(.*?)\s*</div>\s*</td>\s*'
                      r'<td.*?>\s*<div.*?>\s*(.*?)\s*</div>\s*</td>\s*'
                      r'<td.*?>\s*<div.*?>\s*(.*?)\s*</div>\s*</td>\s*')
div_regex = re.compile(r'<div.*?>(.*?)</div>')
span_regex = re.compile(r'<span>(.*?)</span>')
a_regex = re.compile(r'<a id="ID_link" name="link" href="http://www.mhlw.go.jp.*?target="_blank">(.*?)</a>')
relative_path_regex = re.compile(r'./130050.do')
excess_spaces_regex = re.compile(r'[ \t][ \t]+')
how_many_records_regex = re.compile(r'<p class="txt90-right">&nbsp;(\d+)&nbsp;件中&nbsp;(\d+)&nbsp;～&nbsp;(\d+)&nbsp;件を表示</p>')
overtime_regex = re.compile(r'(なし|あり)(　月平均)?(\d+)?(時間)?')
pay_rate_regex = re.compile(r'([\d,]+)円～([\d,]+)円')
day_regex = re.compile(r'(\d+)日')
minute_regex = re.compile(r'(\d+)分')
headcount_regex = re.compile(r'(\d+)人')
retirement_benefit_regex = re.compile(r'<div>退職金制度:(.*?)</div>')
date_regex = re.compile(r'平成(\d+)年(\d+)月(\d+)日')
number_of_employees_of_organization_regex = re.compile(r'企業全体:([\d,]+)人')
number_of_employees_of_office_regex = re.compile(r'うち就業場所:([\d,]+)人')
number_of_female_employees_of_office_regex = re.compile(r'うち女性:([\d,]+)人')
number_of_part_time_employees_of_office_regex = re.compile(r'うちパート:([\d,]+)人')

kyujinkensu = 0
local_minimum = 0
local_maximum = 0

def fetch_summary(params):
    data = urllib.parse.urlencode(params)
    data = data.encode('utf-8') # data should be bytes
    req = urllib.request.Request(url)
    for key, value in request_headers.items():
        req.add_header(key, value)
    r = urllib.request.urlopen(req, data)
    return r

def count_number_of_pages(params):
    form_data = form_data_default.copy()
    form_data.update(params)
    fwListNaviBtn = 'commonSearch'
    form_data[fwListNaviBtn] = '検索'
    r = fetch_summary(params=form_data)
    #print(r.read().decode('utf-8'))
    for line in r.read().decode('utf-8').splitlines():
        #print(line)
        if how_many_records_regex.search(line):
            kyujinkensu = int(how_many_records_regex.search(line).group(1))
            local_minimum = int(how_many_records_regex.search(line).group(2))
            local_maximum = int(how_many_records_regex.search(line).group(3))
            #print('###'+str(kyujinkensu))
            #print('###'+str(local_minimum))
            #print('###'+str(local_maximum))
            return int(math.ceil(kyujinkensu/20.0))

def generate_list(**kwargs):
    for i in range(count_number_of_pages(kwargs)):
        #print('### current page ### '+str(i+1))
        form_data = form_data_default.copy()
        for k, v in kwargs.items():
            form_data[k] = v
        remainder = (i+1)%10
        if i+1 <= 10:
            fwListNaviBtn = 'fwListNaviBtn' + str(i+1)
            form_data[fwListNaviBtn] = str(i+1)
        elif i+1 == 11:
            fwListNaviBtn = 'fwListNaviBtn' + '11'
            form_data[fwListNaviBtn] = str(i+1) + '〜'
        elif remainder == 0:
            fwListNaviBtn = 'fwListNaviBtn' + '11'
            form_data[fwListNaviBtn] = str(i+1)
            form_data['fwListNaviCount'] = 12
            form_data['fwListLeftPage'] = i+1-10
        elif remainder == 1:
            fwListNaviBtn = 'fwListNaviBtn' + '12'
            form_data[fwListNaviBtn] = str(i+1) + '〜'
            form_data['fwListNaviCount'] = 12
            form_data['fwListLeftPage'] = i+1-11
        elif 2 <= remainder <= 9:
            fwListNaviBtn = 'fwListNaviBtn' + str(remainder+1)
            form_data[fwListNaviBtn] = str(i+1)
            form_data['fwListNaviCount'] = 12
            form_data['fwListLeftPage'] = i+1-remainder
        form_data['fwListNowPage'] = str(i)
        form_data['nowPageNumberHidden'] = str(i)
        r = fetch_summary(params=form_data)
        ###print(r.read().decode('utf-8'))###
        flag = 0
        html = ''
        for line in r.read().decode('utf-8').splitlines():
            #print(line)
            if flag == 0 and how_many_records_regex.search(line):
                kyujinkensu = int(how_many_records_regex.search(line).group(1))
                local_minimum = int(how_many_records_regex.search(line).group(2))
                local_maximum = int(how_many_records_regex.search(line).group(3))
                #print('###'+str(kyujinkensu))
                #print('###'+str(local_minimum))
                #print('###'+str(local_maximum))
                number_of_pages = int(math.ceil(kyujinkensu/20.0))
                #print(number_of_pages)
            if flag == 0 and table_start_regex.search(line):
                flag = 1
                html += line
                continue
            elif flag == 1:
                line = relative_path_regex.sub(url, line)
                line = excess_spaces_regex.sub(' ', line)
                html += line
                if table_end_regex.search(line):
                    flag = 0
                    break
        for rec in tr_regex.findall(html):
            if th_regex.search(rec):
                continue
            for m in td_regex.finditer(rec):
                yield m.group(4)+'-'+m.group(5)

def fetch_detail(kyujinNumber):
    kn1, kn2 = kyujinNumber.split("-")
    url_get_method = url+'?'+ \
                     "&".join(["screenId=130050",
                               "action=commonDetailInfo",
                               "kyujinNumber1={0}".format(kn1),
                               "kyujinNumber2=%0A{0}".format(kn2),
                               "kyushokuUmuHidden={0}".format(form_data_default['kyushokuUmuHidden']),
                               "kyushokuNumber1Hidden={0}".format(form_data_default['kyushokuNumber1']),
                               "kyushokuNumber2Hidden={0}".format(form_data_default['kyushokuNumber2'])])
    col = {key: None for key in output_header}
    req = urllib.request.Request(url_get_method)
    for key, value in request_headers.items():
        req.add_header(key, value)
    r = urllib.request.urlopen(req)
    flag_key = None
    for line in r.read().decode('utf-8').splitlines():
        #print(line)
        if flag_key == None:
            for key, value in keyword.items():
                if line.find(value) != -1:
                    flag_key = key
                    break
            if retirement_benefit_regex.search(line):
                col["retirement_benefit"] = retirement_benefit_regex.search(line).group(1)
        elif flag_key != None:
            if div_regex.search(line):
                if flag_key == 'overtime':
                    overtime_result = overtime_regex.search(div_regex.search(line).group(1))
                    if overtime_result != None:
                        if overtime_result.group(1) == 'なし':
                            col[flag_key] = '0'
                        elif overtime_result.group(1) == 'あり':
                            col[flag_key] = overtime_result.group(3)
                elif flag_key == 'wage':
                    pay_rate_result = pay_rate_regex.search(div_regex.search(line).group(1))
                    if pay_rate_result != None:
                        col["minimum_wage"] = pay_rate_result.group(1).replace(',', '')
                        col["maximum_wage"] = pay_rate_result.group(2).replace(',', '')
                elif flag_key == 'wage_and_allowance':
                    pay_rate_result = pay_rate_regex.search(div_regex.search(line).group(1))
                    if pay_rate_result != None:
                        col["minimum_wage_and_allowance"] = pay_rate_result.group(1).replace(',', '')
                        col["maximum_wage_and_allowance"] = pay_rate_result.group(2).replace(',', '')
                elif flag_key == 'number_of_employees':
                    number_of_employees_of_organization_result = number_of_employees_of_organization_regex.search(div_regex.search(line).group(1))
                    if number_of_employees_of_organization_result != None:
                        col["number_of_employees_of_organization"] = number_of_employees_of_organization_result.group(1).replace(',', '')
                    number_of_employees_of_office_result = number_of_employees_of_office_regex.search(div_regex.search(line).group(1))
                    if number_of_employees_of_office_result != None:
                        col["number_of_employees_of_office"] = number_of_employees_of_office_result.group(1).replace(',', '')
                    number_of_female_employees_of_office_result = number_of_female_employees_of_office_regex.search(div_regex.search(line).group(1))
                    if number_of_female_employees_of_office_result != None:
                        col["number_of_female_employees_of_office"] = number_of_female_employees_of_office_result.group(1).replace(',', '')
                    number_of_part_time_employees_of_office_result = number_of_part_time_employees_of_office_regex.search(div_regex.search(line).group(1))
                    if number_of_part_time_employees_of_office_result != None:
                        col["number_of_part_time_employees_of_office"] = number_of_part_time_employees_of_office_result.group(1).replace(',', '')
                elif flag_key == 'days_of_rest_per_year':
                    day_result = day_regex.search(div_regex.search(line).group(1))
                    if day_result != None:
                        col[flag_key] = day_result.group(1)
                elif flag_key == 'break':
                    minute_result = minute_regex.search(div_regex.search(line).group(1))
                    if minute_result != None:
                        col[flag_key] = minute_result.group(1)
                elif flag_key == 'number_of_positions':
                    headcount_result = headcount_regex.search(div_regex.search(line).group(1))
                    if headcount_result != None:
                        col[flag_key] = headcount_result.group(1)
                elif flag_key == 'registration_date' or flag_key == 'expiration_date':
                    date_result = date_regex.search(div_regex.search(line).group(1))
                    if date_result != None:
                        col[flag_key] = '{0:4d}-{1:02d}-{2:02d}'.format(int(date_result.group(1))+1988, int(date_result.group(2)), int(date_result.group(3)))
                else:
                    if div_regex.search(line).group(1) == '&nbsp;':
                        col[flag_key] = None
                    else:
                        col[flag_key] = div_regex.search(line).group(1)
                flag_key = None
            elif span_regex.search(line):
                col[flag_key] = span_regex.search(line).group(1)
                flag_key = None
            elif a_regex.search(line):
                col[flag_key] = a_regex.search(line).group(1)
                flag_key = None
    return '^'.join([str(col[k]) for k in col.keys()])

def mail():
    table_A_intersection_B = ''
    table_A_setminus_B_intersection_C = ''
    html = '''<html>
<head></head>
<body>
<p>A = {{x includes one of {0}}}</p>
<p>B = {{x includes one of {1}}}</p>
<p>C = {{x includes one of {2}}}</p>
'''.format(A, B, C)
    file_object = open(filename, 'r')
    for line in file_object:
        v = line.rstrip().split("^")
        #if A_regex.search(line):
        if A_regex.search(v[8]) or A_regex.search(v[9]) or A_regex.search(v[44]) or A_regex.search(v[46]) or A_regex.search(v[47]) or A_regex.search(v[52]) or A_regex.search(v[53]):
            rec = ''
            rec += '<table>\n'
            rec += "<tr><th>job_number</th><td><a href='"+url+'?screenId=130050&action=commonDetailInfo&kyujinNumber1={0}&kyujinNumber2=%0A{1}&kyushokuUmuHidden=1&kyushokuNumber1Hidden={2}&kyushokuNumber2Hidden={3}'.format(v[0].split("-")[0], v[0].split("-")[1], form_data_default['kyushokuNumber1'], form_data_default['kyushokuNumber2'])+"'>"+v[0]+"</a></td></tr>\n"
            for i in range(1, len(output_header)):
                rec += "<tr><th>{0}</th><td>{1}</td></tr>\n".format(output_header[i], v[i])
            rec += "</table>\n"
            rec += "<hr>\n"
            #if B_regex.search(line):
            if B_regex.search(v[8]) or B_regex.search(v[9]) or B_regex.search(v[44]) or B_regex.search(v[46]) or B_regex.search(v[47]) or B_regex.search(v[52]) or B_regex.search(v[53]):
                table_A_intersection_B += rec
            #elif C_regex.search(line):
            elif C_regex.search(v[30]):
                table_A_setminus_B_intersection_C += rec
    html += "<h2>A ∩ B</h2>\n"
    html += table_A_intersection_B
    html += "<h2>(A \ B) ∩ C</h2>\n"
    html += table_A_setminus_B_intersection_C
    html += '''</body>
</html>
'''
    file_object.close()
    msg.set_content(html, subtype='html')
    s = smtplib.SMTP(mta)
    s.send_message(msg)
    s.quit()

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-a', dest='age', action='store',
                        default='18', help='specify your age')
    parser.add_argument('-i', dest='id', action='store',
                        help='specify your job seeker id')
    parser.add_argument('-m', dest='mail', action='store_true',
                        help='mail records including specific words')
    parser.add_argument('-f', dest='full', action='store_true',
                        help='retrieve full-time job offers')
    parser.add_argument('-p', dest='part', action='store_true',
                        help='retrieve part-time job offers')
    parser.add_argument('-c', dest='category', action='store',
                        help='''select job category id from the following:
A 管理的職業
  01 管理的公務員
  02 法人・団体の役員
  03 法人・団体の管理職員
  04 その他の管理的職業
B 専門的・技術的職業
  05 研究者
  06 農林水産技術者
  07 開発技術者
  08 製造技術者
  09 建築・土木・測量技術者
  10 情報処理・通信技術者
  11 その他の技術者
  12 医師、歯科医師、獣医師、薬剤師
  13 保健師、助産師、看護師
  14 医療技術者
  15 その他の保険医療の職業
  16 社会福祉の専門的職業
  17 法務の職業
  18 経営・金融・保険の専門的職業
  19 教育の職業
  20 宗教家
  21 著述家、記者、編集者
  22 美術家、デザイナー、写真家、映像撮影者
  23 音楽家、舞台芸術家
  24 その他の専門的職業
C 事務的職業
  25 一般事務の職業
  26 会計事務の職業
  27 生産関連事務の職業
  28 営業・販売関連事務の職業
  29 外勤事務の職業
  30 運輸・郵便事務の職業
  31 事務用機器操作の職業
D 販売の職業
  32 商品販売の職業
  33 販売類似の職業
  34 営業の職業
E サービスの職業
  35 家庭生活支援サービスの職業
  36 介護サービスの職業
  37 保健医療サービスの職業
  38 生活衛生サービスの職業
  39 飲食物調理の職業
  40 接客・給仕の職業
  41 居住施設・ビル等の管理の職業
  42 その他のサービスの職業
F 保安の職業
  43 自衛官
  44 司法警察職員
  45 その他の保安の職業
G 農林漁業の職業
  46 農業の職業
  47 林業の職業
  48 漁業の職業
H 生産工程の職業
  49 生産設備制御・監視の職業（金属材料製造、金属加工、金属溶接・溶断）
  50 生産設備制御・監視の職業（金属材料製造、金属加工、金属溶接・溶断を除く）
  51 生産設備制御・監視の職業（機械組立）
  52 金属材料製造、金属加工、金属溶接・溶断の職業
  54 製品製造・加工処理の職業（金属材料製造、金属加工、金属溶接・溶断を除く）
  57 機械組立の職業
  60 機械整備・修理の職業
  61 製品検査の職業（金属材料製造、金属加工、金属溶接・溶断）
  62 製品検査の職業（金属材料製造、金属加工、金属溶接・溶断を除く）
  63 機械検査の職業
  64 生産関連・生産類似の職業
I 輸送・機械運転の職業
  65 鉄道運転の職業
  66 自動車運転の職業
  67 船舶・航空機運転の職業
  68 その他の輸送の職業
  69 定置・建設機械運転の職業
J 建設・採掘の職業
  70 建設躯体工事の職業
  71 建設の職業（建設躯体工事の職業を除く）
  72 電気工事の職業
  73 土木の職業
  74 採掘の職業
K 運搬・清掃・包装等の職業
  75 運搬の職業
  76 清掃の職業
  77 包装の職業
  78 その他の運搬・清掃・包装等の職業
''')
    args = parser.parse_args()
    global form_data_default
    if args.age:
        age = {'nenrei': args.age, 'nenreiHidden': args.age}
        form_data_default.update(age)
    if args.category:
        category = {'kiboShokushu1': args.category,
                    'kiboShokushu1Hidden': args.category}
        form_data_default.update(category)
    if args.id:
        kn1, kn2 = args.id.split("-")
        id = {'kyushokuNumber1': kn1,
              'kyushokuNumber2': kn2,
              'kyushokuNumber1Hidden': kn1,
              'kyushokuNumber2Hidden': kn2,
              'kyushokuUmu': '1',
              'kyushokuUmuHidden': '1'}
    else:
        id = {'kyushokuNumber1': '',
              'kyushokuNumber2': '',
              'kyushokuNumber1Hidden': '',
              'kyushokuNumber2Hidden': '',
              'kyushokuUmu': '2',
              'kyushokuUmuHidden': '2'}
    form_data_default.update(id)
    if args.full or args.part:
        file_object = open(filename, 'w')
        file_object.write("^".join(output_header)+"\n")
    #if args.full or (not args.full and not args.part):
    if args.full:
        for n in generate_list(gekkyuKagen='',
                               kyujinShuruiHidden='1',
                               nenkanKyujitsu=''):
            file_object.write(fetch_detail(kyujinNumber=n)+"\n")
    #if args.part or (not args.full and not args.part):
    if args.part:
        for n in generate_list(jikyuKagen='',
                               kyujinShuruiHidden='2',
                               shoteiRodoNissu='1',
                               shoteiRodoNissuKagen=''):
            file_object.write(fetch_detail(kyujinNumber=n)+"\n")
    if args.full or args.part:
        file_object.close()
    if args.mail:
        mail()

if __name__ == '__main__':
    main()
