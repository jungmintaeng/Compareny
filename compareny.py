#compareny.py
#2012726006 신정민
#컴퓨터언어 학기 프로젝트

import requests
from bs4 import BeautifulSoup
from urllib import *
from urllib.request import urlopen
import io
from PIL import Image, ImageTk
from tkinter import *
from tkinter import messagebox
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

### URL 정리 ###
search_jobplanet = 'https://www.jobplanet.co.kr/search/companies/' # + 기업명
search_jobkorea = 'http://www.jobkorea.co.kr/Search/?stext=' # + 기업명
search_saramin = 'http://www.saramin.co.kr/zf_user/salaries/total-salary/list?list_type=total&mcode=&company_type=&rec_status=&order=reg_dt&search_company_nm=' # + 기업명
################

list_ = []

class Company() :
    def __init__(self, name, evaluation, location, salary, comType, logo) :
        self.logo = logo
        self.name = name
        self.evaluation = evaluation
        self.location = location
        self.salary = salary
        self.comType = comType
        
    def toString(self) :
        desc = 'LOGO URL : ' + self.logo + '\n회사명 : ' + self.name + '\n평점 : ' + self.evaluation + '\n회사 위치 : ' + self.location + '\n평균 연봉 : ' + self.salary + '(만원)\n회사 분류 : ' + self.comType
        return desc

class Company_() :
    def __init__(self, name, salary, similarity) :
        self.name = name
        self.salary = salary
        self.similarity = similarity

ERR_CODE = 'ERR'

### requestURL 함수
### parameter : url(string) : 접속할 URL
### GET 방식으로 가져올 웹 페이지 URL을 인자로 받아 해당 URL의 HTML을 텍스트 형태로
### 받아 BeautifulSoup을 이용하여 Parsing 후 BeautifulSoup 객체를 반환
### return value : 성공시 - BeautifulSoup 객체 / 실패시 - ERR_CODE
def requestURL(url) :
    try :
        req = requests.get(url)
    except :
        messagebox.showinfo("인터넷 에러", "인터넷 연결을 확인하세요")
        return ERR_CODE
    if req.status_code == 200 : ## GET방식으로 HTML 문서 가져오기 성공
        html = req.text
        return BeautifulSoup(html, 'html.parser')
    else :
        return ERR_CODE

### getCompanyList 함수
### parameter : keyword(string) : 사용자가 검색한 회사명 -- gui로 바꾸면서 event로 수정
### 사용자가 특정 키워드를 통해 회사를 검색하였을 때 잡플래닛을 기준으로 해당 키워드의 회사 목록을 가져온
def getCompanyList(*arg) :
    global list_
    companyListbox.delete(0, END)
    keyword = searchEntry.get()
    companyList = []
    # TODO : Parsing하여 GUI에 띄우는 행동
    # 가져올 수 있는 요소들 : 회사명, 분류, 회사 위치, 평균 연봉, 평점
    soup = requestURL(search_jobplanet + parse.quote(keyword))
    if soup == ERR_CODE :
        return companyList
    soup = soup.select('.content_wrap')
    value = 0
    for com in soup :
        name = com.select('.us_titb_l3 > a')[0].get_text() #회사명
        comType = com.select('.cominfo dd span.us_stxt_1')[0].get_text()
        try :
            location = com.select('.cominfo dd span.us_stxt_1')[1].get_text()
        except :
            location = "미지원"
        evaluation = com.select('.gfvalue')[0].get_text()
        salary = com.select('.content_col2_4 > dd > a.us_stxt_1 > strong')[0].get_text()
        logo = com.select('.content_col2_2 img')[0]['src']
        
        company = Company(name, evaluation, location, salary, comType, logo)
        companyList.append(company)
        companyListbox.insert(value, name)
        value += 1
    list_ = list(companyList)

def modify(com):
    nameLabel.config(text=com.name)
    evalLabel.config(text="★ " + com.evaluation)
    locationLabel.config(text=com.location)
    typeLabel.config(text=com.comType)
    if com.salary.strip() == 'ERR' :
        jobpLabel.config(text="존재하지 않습니다.")
    else :
        jobpLabel.config(text=com.salary + " (만원)")

### selected 함수
### parameter : event
### 사용자가 회사명으로 검색한 후, 리스트박스의 회사를 선택했을 때 행동
def selected(evt):
    global list_
    w = evt.widget
    if len(w.curselection()) == 0 :
        return
    value = w.get(int(w.curselection()[0]))
    for com in list_ :
        if com.name == value :
            modify(com)
            break
    soup_k = requestURL(search_jobkorea + parse.quote(value))
    soup_s = requestURL(search_saramin + parse.quote(value.replace("(주)",'').replace("(유)",'').replace("(재)",'')))

    koreaList = []
    saramList = []


    ###잡코리아
    if soup_k == ERR_CODE or len(soup_k) == 0 :
        jobkLabel.config(text="존재하지 않습니다.")
    else :
        soup_k = soup_k.select('#smCoList ul.detailList > li')
        for com_k in soup_k :
            name = com_k.select('dt > a')[0].get_text()
            salary = com_k.select('dd.desc')[0].get_text()
            if "평균연봉" in salary :
                salary = salary[salary.find("평균연봉") + 4:salary.rfind("만원"): 1].replace(',','')
            else :
                salary = ERR_CODE
            comp = Company_(name, salary, fuzz.token_sort_ratio(value, name))
            koreaList.append(comp)
        maxi = 0
        maxComIndex = -1
        for index in range(0, len(koreaList)):
            if maxi < koreaList[index].similarity :
                maxi = koreaList[index].similarity
                maxComIndex = index
        if(maxComIndex < 0 or maxComIndex >= len(koreaList)) :
            jobkLabel.config(text="존재하지 않습니다.")
        else :
            if koreaList[maxComIndex].salary != ERR_CODE:
                jobkLabel.config(text=koreaList[maxComIndex].salary + " (만원)")
            else :
                jobkLabel.config(text="존재하지 않습니다.")

    ###사람인
    if soup_s == ERR_CODE or len(soup_s) == 0 :
        saramLabel.config(text="존재하지 않습니다.")
    else :
        soup_s = soup_s.select('ul.list_salary > li')
        for com_s in soup_s :
            name = com_s.select('strong.tit_company > a')[0].get_text()
            salary = com_s.select('.txt_avg')[0].get_text()
            comp = Company_(name, salary, fuzz.token_sort_ratio(value, name))
            saramList.append(comp)
        maxi = 0
        maxComIndex = -1
        for index in range(0, len(koreaList)):
            if maxi < koreaList[index].similarity :
                maxi = koreaList[index].similarity
                maxComIndex = index
        if(maxComIndex < 0 or maxComIndex >= len(saramList)) :
            saramLabel.config(text="존재하지 않습니다.")
        else :
            saramLabel.config(text=saramList[maxComIndex].salary + " (만원)")

###---- main -------
window = Tk()
window.geometry("850x600")
window.title("Compareny , 손 쉬운 회사 연봉 비교")
lframe = Frame(window, width=400, height=768,bd=3, relief=GROOVE)
rframe = Frame(window, width=400, height=768,bd=3, relief=GROOVE)

#Left Frame
Label(lframe, text="회사명으로 검색 : ", width=20, font=('맑은 고딕', 15)).grid(row=0, column=0)
searchEntry = Entry(lframe, width=30)
searchEntry.grid(row=0,column=1, columnspan=3, sticky=W+E, padx=10)
searchButton = Button(lframe, width=10, text="검색", command=getCompanyList)
searchButton.grid(row=0,column=4)
companyListbox = Listbox(lframe)
companyListbox.bind('<<ListboxSelect>>', selected)
companyListbox.grid(row=1, column=0, columnspan=5, rowspan = 10, sticky=W+E+S+N)
searchEntry.bind("<Return>", getCompanyList)
logoImage = PhotoImage(file="data/logo.png")
logo = Label(window, image=logoImage, width=250)
logo.grid(row=0, column=0, sticky=W+E+S+N)

#Right Frame
nameLabel = Label(rframe, text="회사명", font=('맑은 고딕', 20))
nameLabel.pack()
evalLabel = Label(rframe, text="★ 평점", font=('맑은 고딕', 20))
evalLabel.pack()
locationLabel = Label(rframe, text="회사 위치", font=('맑은 고딕', 15))
locationLabel.pack()
typeLabel = Label(rframe, text="회사 분류", font=('맑은 고딕', 15))
typeLabel.pack()
Label(rframe, text='\n\n\n\n').pack()
Label(rframe, text='잡코리아 평균연봉', font=('맑은 고딕', 15)).pack()
jobkLabel = Label(rframe, text='')
jobkLabel.pack()
Label(rframe, text='잡플래닛 평균연봉', font=('맑은 고딕', 15)).pack()
jobpLabel = Label(rframe, text='')
jobpLabel.pack()
Label(rframe, text='사람인 평균연봉', font=('맑은 고딕', 15)).pack()
saramLabel = Label(rframe, text='')
saramLabel.pack()

#root window
lframe.grid(row=1, column = 0)
rframe.grid(row=0, column = 1, rowspan=2, sticky=N+S, ipadx=10)

window.mainloop()
