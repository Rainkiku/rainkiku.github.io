import urlfetch
import json
import time
import os

# 抓取数据
url_1 = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5'
url_2 = 'https://view.inews.qq.com/g2/getOnsInfo?name=wuwei_ww_cn_day_counts'

res_1 = urlfetch.fetch(url_1)
res_2 = urlfetch.fetch(url_2)
resstr_1 = res_1.content.decode('utf-8')
resstr_2 = res_2.content.decode('utf-8')

# 解析JSON数据 
jsonRes_1 = json.loads(resstr_1)
jsonRes_2 = json.loads(resstr_2)
data_1 = jsonRes_1['data']
data_2 = jsonRes_2['data']
data_4 = json.loads(data_1)['chinaTotal']
data_1 = json.loads(data_1)['areaTree']
data_1 = data_1[0]['children']
data_2=json.loads(data_2)

# 数据根据日期排序 
data_2.sort(key = lambda x:x['date'])

#构造国内数据
outall_4 = ''
outall_4 = '\t\t{ name: \'' + '确诊病例' + '\', value: '+str(data_4['confirm'])+' },\n'+ '\t\t{ name: \'' + '疑似病例' + '\', value: '+str(data_4['suspect'])+' },\n' + '\t\t{ name: \'' + '死亡病例' + '\', value: '+str(data_4['dead'])+' },\n' + '\t\t{ name: \'' + '治愈病例' + '\', value: '+str(data_4['heal'])+' },\n'


#构造echarts数据
outall_1 = ''
for single in data_1:
    #{ name: '湖北', value:4586 },
    outstr = '\t\t{ name: \'' + single['name'] + '\', value: '+str(single['total']['confirm'])+' },\n'
    outall_1 = outall_1 +outstr

# 构造数据集 （日期，确诊，疑似，死亡，治愈）
outall_2 = ''
for i in range(0,len(data_2)):
    if i != (len(data_2)-1):
        outstr = '\t\t\t\t\t[\''+ str(data_2[i]['date']) + '\', '+str(data_2[i]['confirm'])+', '+str(data_2[i]['suspect'])+', '+str(data_2[i]['dead'])+', '+str(data_2[i]['heal'])+'],\n'
    else:
        outstr = ''
        # 当天的数据通常不准确，暂时不绘制在图中
        #outstr = '\t\t\t\t\t[\''+ str(data_2[i]['date']) + '\', '+str(data_2[i]['confirm'])+', '+str(data_2[i]['suspect'])+', '+str(data_2[i]['dead'])+', '+str(data_2[i]['heal'])+']\n'
    outall_2 = outall_2+outstr

# 获取确诊、疑似数据的最大值
maxOne1 = sorted(data_2, key = lambda x:int(x['confirm']), reverse=True)
maxOne2 = sorted(data_2, key = lambda x:int(x['suspect']), reverse=True)
maxOne = max([int(maxOne1[0]['confirm']),int(maxOne2[0]['suspect'])])
# 获取死亡、治愈数据的最大值
maxTwo1 = sorted(data_2, key = lambda x:int(x['dead']), reverse=True)
maxTwo2 = sorted(data_2, key = lambda x:int(x['heal']), reverse=True)
maxTwo = max([int(maxTwo1[0]['dead']), int(maxTwo2[0]['heal'])])

# 构造各市数据
outall_3 = ''
outall_3_Name = ''
outall_3_Num = ''
for data_3 in data_1:
    strstr = data_3

    outstrName = '\''+strstr['name']+'\','
    outstrNum = str(strstr['total']['confirm'])+','

    out_str = '\t\t<tr class="alt"><td>' + strstr['name'] + '</td><td>'+str(strstr['total']['confirm'])+'</td><td>'+str(strstr['total']['dead'])+'</td><td>'+str(strstr['total']['heal'])+'</td><td>'+str(strstr['today']['confirm'])+'</td><td>'+str(strstr['today']['dead'])+'</td><td>'+str(strstr['today']['heal'])+'</td></tr>\n'
    
    outall_3_Name = outall_3_Name + outstrName
    outall_3_Num = outall_3_Num + outstrNum
    outall_3 = outall_3 +out_str
    
    data_3 = data_3['children']
    for single in data_3:
        outstr = '\t\t<tr><td>' + single['name'] + '</td><td>'+str(single['total']['confirm'])+'</td><td>'+str(single['total']['dead'])+'</td><td>'+str(single['total']['heal'])+'</td><td>'+str(single['today']['confirm'])+'</td><td>'+str(single['today']['dead'])+'</td><td>'+str(single['today']['heal'])+'</td></tr>\n'
        outall_3 = outall_3 +outstr

outall_3 = outall_3.replace("'","").replace(r"\n","")
outall_3_Num = outall_3_Num.replace("'","").replace(r"\n","")
# 获取当前时间，并格式化如21:12 on July 24, 2019
timeNow = time.strftime("%H:%M on %b %d, %Y", time.localtime())

# 读取模板HTML
root = os.getcwd() #获取当前工作目录路径
fid = open(root +'\\txt\\nCovMod.html','rb')
oriStr = fid.read().decode('utf-8')
fid.close() 
# 写入数据集
oriHtml = oriStr.replace('//insertData//',outall_1)
oriHtml = oriHtml.replace('//dataInsert//',outall_2)
oriHtml = oriHtml.replace('//dataCity//',outall_3)
oriHtml = oriHtml.replace('//dataCityName//',outall_3_Name)
oriHtml = oriHtml.replace('//dataCityNum//',outall_3_Num)
oriHtml = oriHtml.replace('//dataCountry//',outall_4)
oriHtml = oriHtml.replace('//TimeNow//',timeNow)
# 写入线图和柱图的Y轴最大值和分隔区间
interval1 = int(int(maxOne)/1000)+1
interval2 = int(float(maxTwo)/(interval1))+1
oriHtml = oriHtml.replace('//maxOne//',str(int(interval1*1000)))
oriHtml = oriHtml.replace('//intervalOne//', '1000')
oriHtml = oriHtml.replace('//maxTwo//',str(int(interval2*interval1)))
oriHtml = oriHtml.replace('//intervalTwo//',str(interval2))
# 输出更新后的HTML
fid = open(root + '\\txt\\nCov.html','wb')
fid.write(oriHtml.encode('utf-8')) 

fid.close()
