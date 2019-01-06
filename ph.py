import os,requests,re,json,configparser,time,logging
from bs4 import BeautifulSoup
from PyQt5.QtCore import QSettings,QObject,QThread,pyqtSignal, pyqtSlot
class Variable():
    threads = []    #用于保存所有线程
    login_data=[]
    login_info=''
    authorConfig={}
    objectConfig={}
    authorConfigLen=0
    objectConfigLen=0
    #bugForms结构和searchBugList结构：状态，编号，标题，更新日期
    #新的bugForms：ID、接收者、status、Priority、创建日期、更新日期、标题
    #bugForms -> renewBugForms -> searchBugList
    bugForms = []  #下载下来的bug集合
    renewBugForms=[]  #按状态搜索后的bug集合
    searchBugList=[]  #按关键字搜索后的bug集合

    ##settings = QSettings(QSetting.IniFormat, QSetting.UserScope, 'Phabricator', 'Ph')
    #config_addr = os.path.expandvars('$HOME')
    config_addr = os.path.expanduser('~')
    config_addr = config_addr +'/AppData/Local/phBug/'
    config_file = config_addr + 'config.conf'
    log_file = config_addr + 'LogInfo.log'
    xls_file = config_addr +'exportbug.xlsx'  #导出文件
    if not os.path.exists(config_addr):
        os.makedirs(config_addr)
    # settings = QSettings(config_file, QSettings.IniFormat)  #如果不存在会创建



    ##phinit######
    base_url = 'http://review.mprtimes.net'  ##172.16.6.38     review.mprtimes.net
    login_url = base_url+'/auth/login/password:self/'
    dataSource_url = base_url+'/typeahead/class/PhabricatorSearchDatasource/'   #顶部搜索栏（用于get）
    ownerSource_url = base_url+'/typeahead/class/PhabricatorPeopleOwnerDatasource/'
    projectLogincal_url = base_url+'/typeahead/class/PhabricatorProjectLogicalDatasource/'
    searchBug_url = base_url+'/maniphest/query/advanced/'
    search_url = base_url+'/search/'   #顶部搜索栏(用于post)
    getPeople_url = base_url+'/people/'

    #会话
    rs = requests.Session()

    #cookies
    cookies={}

    #保存人员/标签
    people_List = []        #保存人员名单[[人名,None,'user'],...]
    object_List = []        #保存标签[[标签名,None,tagname],...]
    milestones_List = []    #保存里程碑数据[[里程碑，PHID,'Milestone'],...]

    #登入post数据
    postData = {}
    postData['__csrf__'] = ''
    postData['__form__'] = '1'
    postData['__dialog__'] = '1'
    postData['username'] = ''
    postData['password'] = ''

    #查询post数据
    searchDataPart1={}
    searchDataPart2={}
    searchDataPart2['__csrf__'] = ''
    searchDataPart2['__form__'] = '1'
    searchDataPart2['group'] = 'none'
    searchDataPart2['order'] = 'newest'
    '''
    self.searchDataPart1['assignedPHIDs[0]'] = ''
    self.searchDataPart1['projectPHIDs[0]'] = ''
    self.searchDataPart1['authorPHIDs[0]'] = ''
    self.searchDataPart1['blocked'] = ''
    self.searchDataPart1['blocking'] = ''
    self.searchDataPart1['createdEnd'] = ''
    self.searchDataPart1['createdStart'] = ''
    self.searchDataPart1['fulltext'] = ''
    self.searchDataPart1['limit'] = ''
    self.searchDataPart1['modifiedEnd'] = ''
    self.searchDataPart1['modifiedStart'] = ''
    self.searchDataPart2['priorities[0]'] = ''  #优先级
    self.searchDataPart2['statuses[0]'] = ''   #状态
    '''

    #查询get参数
    dataSourceParams={}
    dataSourceParams['q'] = ''
    dataSourceParams['raw'] = ''
    dataSourceParams['__ajax__'] = 'true'
    dataSourceParams['__metablock__'] = '1'

    #导出excel参数
    exportData={}
    exportData['__csrf__']=''
    exportData['__dialog__']=1
    exportData['__form__']=1
    exportData['excel-format']='ManiphestExcelDefaultFormat'
var=Variable()

class MyThread(QThread): #先用QObject试试，再用QThread试试

    login_status=pyqtSignal(str)    #登入状态信号
    init_data=pyqtSignal(list,str)  #获取用户名和项目标签
    searchBug_result=pyqtSignal(str)
    phid=pyqtSignal(list)


    def __init__(self):
        super().__init__()

        self.pList=[]   #保存人名数据
        self.oList=[]
        self.flag_peoples=False
        self.flag_tags=False
        self.flag_milestones=False
        self.get_phid=[]
        self.hrefs=set()  #保存'Project'类型标签的URL
        self.project_all=[] #保存所有的'项目'的URL
        self.milestones_url=[]#保存里程碑的URL
        self.milestones_text=[]     #保存里程碑
        self.flag_tr=True           #False时结束线程

    #---------登入------------------------
    def userLogin(self):
        #返回状态码和登入状态
        logging.info("start login...")
        var.rs = requests.Session() #先初始化（清空数据）
        try:
            r = var.rs.get(var.base_url, timeout=5)
            self.getCSRF(r.text)
            result='Success'
        except:
            result= 'Out Of Time'
        if result == "Success":
            r = var.rs.post(var.login_url, data=var.postData)
            self.getCSRF(r.text)
            if r.url=='http://review.mprtimes.net/':  #成功跳转(登入成功)
                res = ['login Success', str(r.status_code)]
            else:
                res = ['login Fail', str(r.status_code)]
        else:
            res = ['Network connection failed.', result]   #['Network connection failed.', 'Out Of Time']
        logging.info("login status：%s"%res)
        return res

    def login(self,list):
        '''获取cookies并返回设定参数和状态码，是个数组'''
        self.action='login'
        var.postData['username'] = list[1]
        var.postData['password'] = list[0]
        self.start()

    def getCSRF(self,text):
        text = re.findall(r'"current":"(.+?)"',text)
        csrf = text[0]
        logging.info("csrf=%s"%csrf)
        var.postData['__csrf__'] = csrf
        var.searchDataPart2['__csrf__'] = csrf
        var.exportData['__csrf__']=csrf

    #----------查询people和object---------------------------
    def getData(self,name):
        if name=='peoples':
            self.flag_peoples=True
            self.start()
        elif name=='tags':
            self.flag_tags=True
            self.start()
        elif name=='postdata':
            self.action='postdata'
            self.start()
        elif name=='milestones':
            self.flag_milestones=True
            self.start()

    def getPeople(self,url='http://review.mprtimes.net/people'):
        '''读取人员名单，只有人名，没有PHID'''
        '''[[人名,None,'user'],...]'''
        logging.info("请求user")
        if not self.flag_tr:    #self.flag_tr==False时
            return
        r=var.rs.get(url)
        soup = BeautifulSoup(r.text,'html.parser')
        peopleList = []
        body = soup.body
        #含列表和换页栏
        form = body.contents[0].contents[0].contents[1].contents[0].contents[1]
        form_people = form.contents[1].contents[3]
        people_first = form_people.contents[0]
        while(people_first!=None):          #获取本页人员
            people_name = people_first.contents[0].contents[0].contents[1].contents[0].contents[0].contents[0].contents[0].contents[0].a['title']
            peopleList.append([people_name,None,'user'])
            people_first = people_first.nextSibling
        self.pList +=peopleList       #保存本页人员
        try:                #检查换页栏是否存在
            next_page = form.contents[2].contents[0]
        except:
            pass
        else:
            if len(next_page.find_all('a'))==1:  #检查是否存在下一页，只有一个按钮，则存在下一页
                next_url = next_page.a['href']
                next_url = var.base_url+next_url
                result = self.getPeople(next_url)
                if result==None:
                    return
        return self.pList

    def getObject(self,url='http://review.mprtimes.net/project/query/active/'):
        '''读取所有项目'''
        '''[[项目名称,None,标签],...]'''
        logging.info("请求tag")
        if not self.flag_tr:
            return
        r=var.rs.get(url)
        soup = BeautifulSoup(r.text,'html.parser')
        objectList = [] #保存标签名
        body = soup.body
        #含列表和换页栏
        form = body.contents[0].contents[0].contents[1].contents[0].contents[1]
        form_object = form.contents[1].contents[3]
        object_first = form_object.contents[0]
        while(object_first!=None):          #获取本页项目
            object_name = object_first.contents[0].contents[0].contents[1].contents[0].contents[0].contents[0].contents[0].contents[0].a['title']
            object_tag = object_first.contents[0].contents[0].contents[1].contents[0].contents[0].contents[0].contents[1].contents[0].contents[0].contents[1].string
            objectList.append([object_name,None,object_tag])
            if object_tag.strip()=='Project':
                    href = object_first.contents[0].contents[0].contents[1].contents[0].contents[0].contents[0].contents[0].contents[0].a['href']
                    self.hrefs.add(href)
            object_first = object_first.nextSibling
        self.oList +=objectList       #保存本页项目
        try:                #检查换页栏是否存在
            next_page = form.contents[2].contents[0]
        except:
            pass
        else:
            lenp = len(next_page.find_all('a'))
            if lenp!=2:  #检查是否存在下一页，有1个按钮或3个按钮，则存在下一页
                next_page = next_page.contents[lenp-1]
                next_url = next_page['href']
                next_url = var.base_url+next_url
                result = self.getObject(next_url)
                if result==None:
                    return
        return self.oList
    def getMilestones(self,url_list):
        '''获取里程碑'''
        '''[[里程碑,PHID,'Milestone'],...]'''
        logging.info("请求milestone")
        if not self.flag_tr:
            return
        project_url = list(map(lambda url:var.base_url+'/'+url.split('/')[1]+'/subprojects/'+url.split('/')[3]+'/',url_list))
        result=list(map(self.getMilestoneUrl,project_url)) #获取所有的里程碑URL,[[url1],...]
        milestones_url=[]
        for part in result:
            if part:        #part!=None时
                milestones_url.extend(part)  #将所有的里程碑URL保存起来
        result=list(map(self.getMilestone,milestones_url))
        if None in result:
            return
        return result

    def getMilestone(self,url):
        '''获取单个里程碑'''
        '''[里程碑,PHID,'Milestone']'''
        if not self.flag_tr:
            return
        r=var.rs.get(url)
        soup = BeautifulSoup(r.text,'html.parser')
        body = soup.body
        #获取PHID
        try:
            phid = body.contents[0].contents[0].contents[1].contents[0].contents[0].contents[1].contents[1].\
            contents[0].contents[1].contents[0].contents[0].contents[0].contents[0].contents[0].contents[4].a['href']
            phid = phid.split('/')[3]
        except:
            phid = None
        #获取里程碑名
        try:
            milestone = body.contents[0].contents[0].contents[1].contents[0].contents[0].contents[1].contents[1].\
            contents[0].contents[1].contents[0].contents[1].contents[0].contents[1].span
            milestone=re.findall(r'</span>(.+?)</span>',repr(milestone))
            milestone=milestone[0]
        except:
            milestone = None
        return [milestone,phid,'Milestone']

    def getPHID(self,name,type_):
        '''返回如：['石光雄','xxxxxxxx']'''
        self.action='getPHID'
        self.get_phid=[name,type_]
        self.start()

    def getJsonData(self,data):
        res_input = r'{.*}'
        m_input = re.findall(res_input, data, re.S|re.M)
        jsondata = m_input[0]
        result = json.loads(jsondata)
        payload = result['payload']  #payload是一组数组，每个元素也是一个数组
        return payload

    def getMilestoneUrl(self,url):
        '''通过项目到达Subprojects下的Milestones,读取Milestones子项,获取其URL'''
        '''[url1,url2,...]'''
        if not self.flag_tr:
            return
        r = var.rs.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        body = soup.body
        milestones_ulist = []
        try:
            mile_list = body.contents[0].contents[0].contents[1].contents[0].contents[0].contents[1].contents[1].contents[0].contents[1].contents[0].contents[1].contents[1].contents[1]
            mile_first = mile_list.contents[0]
            while mile_first!=None:
                mile_url = mile_first.contents[0].contents[0].contents[1].a['href']
                mile_url = var.base_url+'/project/manage/'+mile_url.split('/')[3]+'/'
                milestones_ulist.append(mile_url)
                mile_first=mile_first.nextSibling
        except:
            pass
        return milestones_ulist

    def quit_tr(self):
        self.flag_tr=False

    def searchBug(self):
        logging.info('查询POST请求：%s'%var.searchBug_url)
        searchData = dict(var.searchDataPart2, **var.searchDataPart1)
        try:
            r = var.rs.post(var.searchBug_url, data=searchData)
        except:
            # 如果请求失败，超时则再次登入
            pass
			
		#判断是否成功查询到结果
        logging.info('headers: %s'%r.headers)
        logging.info('headers: %s'%r.request.headers)
        soup = BeautifulSoup(r.text,'html.parser')
        title = soup.title.string
        logging.info(title.encode('utf-8'))
        if title.encode('utf-8') == b'Unhandled Exception ("AphrontCSRFException")':
            result='Error'
            logging.info('查询POST请求，结果：%s'%result)
            return result
			# log_rlt = self.userLogin()
			# logging.info('重新查询POST请求：%s'%var.searchBug_url)
			# r = var.rs.post(var.searchBug_url, data=searchData)
			# logging.info('\nheaders:%s \nheaders:%s'%(r.headers,r.request.headers))
        else:
            logging.info("cookies有效")
			
        '''导出bug'''
        soup = BeautifulSoup(r.text, 'html.parser')
        body = soup.body
        ##包含bug列表和换页栏
        form = body.contents[0].contents[0].contents[1].contents[0].contents[1]
        ##顶部框架，包含搜索、bug列表、导出。与scrollBar互为兄弟
        form_up = form.contents[1]
        #查看导出栏是否存在
        try:
            batch_task = form_up.contents[4]
            export = batch_task.contents[0].contents[1].contents[2].contents[0].contents[1]
            export_url = export.a['href']
            # print(export_url)

            #导出到excel中
            if not self.flag_tr:
                return
            r = var.rs.post(var.base_url+export_url, data=var.exportData)
            if 'UNRECOVERABLE FATAL ERROR'.encode() in r.content:
                result = 'No data'
            else:
                with open(var.xls_file, 'wb') as fp:
                    fp.write(r.content)
                result='Success'
        except:
            # print('查询无数据！')
            result = 'No data'
        return result
		
    def run(self):
        if self.flag_peoples:
            self.flag_peoples=False
            list_p = self.getPeople()
            if list_p!=None:
                self.init_data.emit(list_p,'user')
        if self.flag_tags:
            self.flag_tags=False
            list_o = self.getObject()
            if list_o!=None:
                self.init_data.emit(list_o,'tag')
            #获取里程碑,先将URL保存到主线程
            # result = self.getMilestones(self.hrefs)
            # self.init_data.emit(self.hrefs,'milestone_url')
        if self.flag_milestones:
            self.flag_milestones=False
            result = self.getMilestones(self.hrefs)
            # print(result)
            # logging.info("milestone: %s"%result)
            if result:      #result!=None时
                self.init_data.emit(result,'milestone')
        if self.action=='login':
            self.action=''
            self.login_status.emit('Login ...')
            result = self.userLogin()
            self.login_status.emit(result[0])
        elif self.action=='postdata':
            '''查询bug'''
            if not self.flag_tr:
                return
            self.action=''
            rlt = self.searchBug()
            if rlt == "Error":	#需要重新登入
                self.userLogin()
                rlt = self.searchBug()
            #发送信号
            if self.flag_tr:
                logging.info("查询POST请求，结果：%s"%rlt)
                self.searchBug_result.emit(rlt)
        elif self.action=='getPHID':
            '''发送如：['shigx (石光雄)', 'PHID-USER-kx7hox25dk2ymkcuq3yu', 'user(Tag)'] '''
            if not self.flag_tr:
                return
            self.action=''
            name=self.get_phid[0]
            type_=self.get_phid[1]
            if type_=='people':
                r = var.rs.get(var.ownerSource_url, params=var.dataSourceParams)
            elif type_=='object':
                name=self.get_phid[0].strip() #去掉前后空格
                r = var.rs.get(var.projectLogincal_url, params=var.dataSourceParams)
            list_u = self.getJsonData(r.text)  #获取到人员序列
            # print('要查询的内容：{0},查询的结果为：{1}'.format(name,list_u))
            #人员序列数据处理
            user = []   #保存查询到的人员序列,如[['shigx (石光雄)', 'PHID-USER-kx7hox25dk2ymkcuq3yu', 'user']]
            if type_=='people':
                for e in list_u:
                    temp = [e[0].strip(), e[2], e[7]]
                    user.append(temp)
            elif type_=='object':
                for l in list_u:
                    temp = [l[4].strip(), l[2], l[5]]
                    user.append(temp)
            #筛选
            if len(user)>0:
                for people in user:
                    if people[0]==name:
                        if self.flag_tr:
                            logging.info("查询出结果getPHID: %s"%people)
                            self.phid.emit(people)
                        break
                else:
                    logging.info('getPHID查询出%s项数据,但是没有匹配出来'%len(user))

'''
result = var.rs.cookies
result = dict(zip(key, value))
'''
if __name__=="__main__":
	mytr = MyThread().userLogin()
	print(mytr)
	searchData = dict(var.searchDataPart2, **var.searchDataPart1)
	r = var.rs.post(var.searchBug_url, data=searchData)
	print(r.headers)
	print("-----------")
	print(r.request.headers)
	# print(r.text)
	soup = BeautifulSoup(r.content,'html.parser')
	title = soup.title.string
	print(title.encode('utf-8'))
	if title.encode('utf-8') == b'Login to Phabricator':
		print(1)
	else:
		print(2)