import requests
from bs4 import BeautifulSoup as bs
from matplotlib import pyplot as plt
import skimage.io
import time
import os
from PIL import Image
import io
import sys
import time
import string
import random
from urllib.parse import quote, unquote
from breaker_single import break_captcha
#except Exception: #    sys.stderr.write('Unable to import break_captcha\n')
#    def break_captcha(captcha_image):
#        plt.imshow(captcha_image)
#        plt.show()
#        checkcode = input('CheckCode: ')
#        return checkcode
    
class ZhengfangCrawler:
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._is_logined = False
        self._base_url = 'http://110.65.10.182'
        self._sess = requests.session()
        
    def _get_captcha(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36', \
                    'Host': '110.65.10.182', 'Connection': 'keep-alive', \
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'}
        data_response = self._sess.get(self._base_url+'/default2.aspx', headers=headers)
        try:
            data_response.raise_for_status()
        except Exception:
            raise Exception('Unable to connect!')
        self._random_code = data_response.url.split('/')[-2]
        checkcode_url = '/'.join([self._base_url, self._random_code,  'CheckCode.aspx?'])
        index_soup = bs(data_response.content, 'html5lib')
        viewstate = index_soup.find(id='form1').input['value']
        checkcode_response = self._sess.get(checkcode_url, stream=True, headers=headers)
        checkcode_image = plt.imread((io.BytesIO(checkcode_response.content)), format='gif')
        return checkcode_image, viewstate
    
    def _login(self):
        if not self._is_logined:
            captcha_image, viewstate = self._get_captcha()
            checkcode_str = break_captcha(captcha_image[:,:,:3]/255.)
            data = {'__VIEWSTATE': viewstate, 'txtUserName': self._username, 'TextBox2': self._password, 'txtSecretCode': checkcode_str, \
                    'RadioButtonList1': quote('学生', encoding='gb2312'), 'Button1': '', 'lbLanguage': '', 'hidPdrs': '', 'hidsc': ''}
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36', \
                       'Host': '110.65.10.182', 'Connection': 'keep-alive', \
                       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'}
            login_url = '/'.join([self._base_url, self._random_code, 'default2.aspx'])
            login_response = self._sess.post(login_url, data=data, headers=headers)
            soup = bs(login_response.content, 'html5lib')
            if '个人信息' in soup.get_text():
                res = '登陆成功'
                self._is_logined = True
                self._student_name = soup.find(id='xhxm').text[:-2]
            elif '验证码不正确' in soup.get_text():
                res = '验证码错误'
            elif '密码错误' in soup.get_text():
                res = '密码错误'
            else:
                res = '未知错误, 可能是用户名不合法'
        else:
            res = '已登录'
        return self._is_logined, res
    
    def get_main_page(self):
        while not self._is_logined:
            self._login()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36', \
                   'Host': '110.65.10.182', 'Connection': 'keep-alive', \
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'}
        main_page_url = '/'.join([self._base_url, self._random_code, 'xs_main.aspx?xh={}'.format(self._username)])
        self._sess.get(main_page_url, headers=headers)
        content_url = '/'.join([self._base_url, self._random_code, 'content.aspx'])
        self._sess.get(content_url)
        
    def get_scores(self):
        """get all scores"""
        self.get_main_page()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36', \
                   'Host': '110.65.10.182', 'Connection': 'keep-alive', \
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', \
                   'Upgrade-Insecure-Requests': '1', \
                   'Referer': '/'.join([self._base_url, self._random_code, 'xs_main.aspx?xh={}'.format(self._username)])}
        query_scores_url = '/'.join([self._base_url, self._random_code]) + \
            '/xscjcx.aspx' + '?xh=' + self._username + '&xm=' + quote(self._student_name, encoding='gb2312') + '&gnmkdm=N121605'
        query_scores_response = self._sess.get(query_scores_url, headers=headers)
        qs_soup = bs(query_scores_response.content, 'html5lib')
        headers['Referer'] = query_scores_response.url
        headers['Cookie'] = 'tabId=ext-comp-1002'
        headers['Origin'] = 'http://110.65.10.182'
        viewstate = qs_soup.find('form', id='Form1').find_all('input')[2]['value']
        data = {
            '__EVENTTARGET': '', '__EVENTARGUMENT': '', '__VIEWSTATE': viewstate, \
            'hidLanguage': '', 'ddlXN': '', 'ddlXQ': '', 'ddl_kcxz': '', 'btn_zcj': '%C0%FA%C4%EA%B3%C9%BC%A8'
        }
        query_scores_response = self._sess.post(query_scores_url, headers=headers, data=data)
        qs_soup = bs(query_scores_response.content, 'html5lib')
        scores = qs_soup.find('table', id='Datagrid1')
        res_all = []
        for item in scores.find_all("tr")[1:] :
            item_split = item.find_all('td')
            res_item = {
                'lesson': item_split[3].text,
                'score': item_split[8].text,
                'credit': item_split[7].text, 
                'lesson_type': item_split[4].text
            }
            res_all.append(res_item)
        return res_all
    
    def get_lessons_table(self, year=None, semester=None):
        self.get_main_page()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36', \
                   'Host': '110.65.10.182', 'Connection': 'keep-alive', \
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', \
                   'Upgrade-Insecure-Requests': '1', \
                   'Referer': '/'.join([self._base_url, self._random_code, 'xs_main.aspx?xh={}'.format(self._username)])}
        query_lessons_url = '/'.join([self._base_url, self._random_code]) + \
            '/xskbcx.aspx' + '?xh=' + self._username + '&xm=' + quote(self._student_name, encoding='gb2312') + '&gnmkdm=N121603'
        query_lessons_response = self._sess.get(query_lessons_url, headers=headers)
        ql_soup = bs(query_lessons_response.content, 'html5lib')
        import pdb
        pdb.set_trace()
        if year and semester:
            headers['Referer'] = query_lessons_response.url
            headers['Cookie'] = 'tabId=ext-comp-1002'
            headers['Origin'] = 'http://110.65.10.182'
            viewstate = ql_soup.find('form', id='xskb_form').find_all('input')[2]['value']
            data = [
                ('__EVENTTARGET', 'xnd'), ('__EVENTARGUMENT', ''), ('__VIEWSTATE', viewstate), \
                ('xnd', year), ('xqd', str(semester))
            ]
            query_lessons_response = self._sess.post(query_lessons_url, headers=headers, data=data)
            ql_soup = bs(query_lessons_response.content, 'html5lib')
        res = ql_soup.find('table', id='Table1')
        return res
    
    def get_empty_classroom(self, week, day_of_the_week, period, year, semester, campus):
        """get empty classroom of a specific period on one day
        Arguments:
            week -- int, from 1 to 20
            day_of_the_week -- int, from 1 to 7
            period -- int, from 1 to 10
                1 -- 一二节
                2 -- 三四节
                3 -- 五六节
                4 -- 七八节
                5 -- 九十十一节
                6 -- 上午
                7 -- 下午
                8 -- 晚上
                9 -- 白天
                10 -- 整天
            year -- str, such like '2017-2018'
            semester -- int, either 1 or 2
            campus -- int in [1, 2, 3] or None
        Returns:
            tbody -- instance of BeautifulSoup, which contains the required 
                tbody tag, if no empty classroom was found, None will be returned
        """
        self.get_main_page()
        periods = [
            "'1'|'1','0','0','0','0','0','0','0','0'",\
            "'2'|'0','3','0','0','0','0','0','0','0'",\
            "'3'|'0','0','5','0','0','0','0','0','0'",\
            "'4'|'0','0','0','7','0','0','0','0','0'",\
            "'5'|'0','0','0','0','9','0','0','0','0'",\
            "'6'|'1','3','0','0','0','0','0','0','0'",\
            "'7'|'0','0','5','7','0','0','0','0','0'",\
            "'8'|'0','0','0','0','9','0','0','0','0'",\
            "'9'|'1','3','5','7','0','0','0','0','0'",\
            "'10'|'1','3','5','7','9','0','0','0','0'"
        ]
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36', \
                   'Host': '110.65.10.182', 'Connection': 'keep-alive', \
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', \
                   'Upgrade-Insecure-Requests': '1', \
                   'Referer': '/'.join([self._base_url, self._random_code, 'xs_main.aspx?xh={}'.format(self._username)])}
        query_emtpy_url = '/'.join([self._base_url, self._random_code]) + \
            '/xxjsjy.aspx' + '?xh=' + self._username + '&xm=' + quote(self._student_name, encoding='gb2312') + '&gnmkdm=N121611'
        query_empty_response = self._sess.get(query_emtpy_url, headers=headers)
        qe_soup = bs(query_empty_response.content, 'html5lib')
        headers['Referer'] = query_empty_response.url
        headers['Cookie'] = 'tabId=ext-comp-1002'
        headers['Origin'] = 'http://110.65.10.182'
        viewstate = qe_soup.find('form', id='Form1').find_all('input')[2]['value']
        
        xiaoq = str(campus) if campus else '' # 校区
        kssj = jssj = '{}{:0>2d}'.format(day_of_the_week, week) # 开始时间
        xqj = str(day_of_the_week) # 星期几
        ddlDsz = '单' if week%2 else '双'
        sjd = periods[period-1] # 时间段
        xn = year
        xq = str(semester)
        ddlSyXn = xn
        ddlSyxq = xq
        data = [
            ('__EVENTTARGET', ''), ('__EVENTARGUMENT', ''), ('__VIEWSTATE', viewstate), \
            ('xiaoq', xiaoq), ('jslb', ''), ('min_zws', '0'), ('max_zws', ''), ('kssj', kssj), \
            ('jssj', jssj), ('xqj', xqj), ('ddlDsz', quote(ddlDsz, encoding='gb2312')), \
            ('sjd', quote(sjd, encoding='gb2312')), \
            ('Button2', quote('空教室查询', encoding='gb2312')), \
            ('dpDataGrid1%3AtxtChoosePage', '1'), ('dpDataGrid1%3AtxtPageSize', '40'), \
            ('xn', xn), ('xq', xq), ('ddlSyXn', ddlSyXn), ('ddlSyxq', ddlSyxq)
        ]
        query_empty_response = self._sess.post(query_emtpy_url, headers=headers, data=data)
        qe_soup = bs(query_empty_response.content, 'html5lib')
        import pdb
        pdb.set_trace()
        viewstate = qe_soup.find('form', id='Form1').find_all('input')[2]['value']
        data = [
            ('__EVENTTARGET', ''), ('__EVENTARGUMENT', ''), ('__VIEWSTATE', viewstate), \
            ('xiaoq', xiaoq), ('jslb', ''), ('min_zws', '0'), ('max_zws', ''), ('kssj', kssj), \
            ('jssj', jssj), ('xqj', xqj), ('ddlDsz', quote(ddlDsz, encoding='gb2312')), \
            ('sjd', quote(sjd, encoding='gb2312')), \
            ('dpDataGrid1%3AtxtChoosePage', '1'), ('dpDataGrid1%3AtxtPageSize', '40'), \
            ('dpDataGrid1%3AbtnNextPage', quote('下一页', encoding='gb2312')), \
            ('xn', xn), ('xq', xq), ('ddlSyXn', ddlSyXn), ('ddlSyxq', ddlSyxq)
        ]
        query_empty_response = self._sess.post(query_emtpy_url, headers=headers, data=data)
        qe_soup = bs(query_empty_response.content, 'html5lib')
        tbody = qe_soup.find('tbody')
        return tbody
