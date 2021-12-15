import os,requests
import fnmatch,re
import time,datetime
import urllib.parse as urlparse
from moviepy.editor import VideoFileClip

# for dirpath,dirnames,file in os.walk('../html/livetest/'):
#     if os.stat(dirpath).st_size > 0:
#         files= file

#testurl
url = 'http://0.0.0.0:8080/livetest/lala.m3u8?h=1639473720&a=1639473960'

#从url中获取app、stream，拼接出切片所在路径
pat_app = re.compile('8080/' + '(.*?)' + '/',re.S)#('.com/' + '(.*?)' + '/')
app_result = pat_app.findall(url)
for p in app_result:
    app_path = '../html/' + p 
    pat_stream = re.compile(p + '/' + '(.*?)' + '.m3u8',re.S)
    stream_result = pat_stream.findall(url)
for s in stream_result:
    stream_name = s #stream名
filepath = os.walk(app_path)#取切片文件的路径

#将url中的请求参数写入字典
parsed = urlparse.urlparse(url)
querys = urlparse.parse_qs(parsed.query)
querys = {k: v[0] for k, v in querys.items()}
#从字典取h和a对应的value，即开始时间，结束时间，并转换为pythondatetime时间格式
start_time = datetime.datetime.fromtimestamp(int(querys['h']))
#print("starttime",start_time)#starttime 2021-12-08 15:10:51
end_time = datetime.datetime.fromtimestamp(int(querys['a']))
time1 = time.mktime(time.strptime(str(start_time),"%Y-%m-%d %H:%M:%S"))
time2 = time.mktime(time.strptime(str(end_time),"%Y-%m-%d %H:%M:%S"))
def judge_time_file(path,file,update_time):
    if not file.endswith('.ts'):
        return False
    if time1 < update_time < time2:
        return True
    return False
#查找文件写入列表
tslist = []
for path,dir_list,file_list in filepath:
    for file_name in file_list:
        local_time = os.stat(os.path.join(path,file_name)).st_mtime
        if judge_time_file(path,file_name,local_time):
            tslist.append(file_name)
#对列表进行排序
sort = []
for ts in tslist:
    ts = re.sub("\D","",ts)
    sort.append(ts)
tslist_1 = sorted(list(map(int,sort)))
ts_list = [(stream_name + '-' +str(i)+'.ts') for i in tslist_1]

#编写新的m3u8文件
s = int(querys['h'])
e = int(querys['a'])
new_m3u8 = stream_name + '.m3u8' + '/' + str(s) + ',' + str(e)
with  open(new_m3u8, 'a',encoding='utf-8')as m:
    #m3u8文件头
    th = ('#EXTM3U' +'\n' +'#EXT-X-VERSION:3' +'\n'+'#EXT-X-MEDIA-SEQUENCE:0'+'\n'+
           '#EXT-X-TARGETDURATION:15'+'\n'+'#EXT-X-DISCONTINUITY'+'\n')
    m.write(th)
    #EXTINF
    # ts_duration = '10.562'#文件时长
    # clip = VideoFileClip("../html/livetest/lala-60.ts")
    # ts_duration = clip.duration  # seconds
    # w = '#EXTINF:' + str(ts_duration) +', no desc'
    #ts片
    for i in ts_list:
        ts_path = app_path + '/' + i
        clip = VideoFileClip(ts_path)
        ts_duration = clip.duration  # seconds 一片视频的长度
        w = '#EXTINF:' + str(ts_duration) +', no desc'
        m.write(w + "\n")#写EXTINF 
        m.write(i + "\n")#写入ts文件名
    m.close()
