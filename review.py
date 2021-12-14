import os,requests
import fnmatch
import time,datetime
import urllib.parse as urlparse
from moviepy.editor import VideoFileClip

for dirpath,dirnames,file in os.walk('../html/livetest/'):
    if os.stat(dirpath).st_size > 0:
        files= file

url = 'http://0.0.0.0:8080/livetest/1111.m3u8?h=1638947451&a=1638948651'
filepath = os.walk('../html/livetest/')
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
tslist = []

for path,dir_list,file_list in filepath:
    for file_name in file_list:
        local_time = os.stat(os.path.join(path,file_name)).st_mtime
        if judge_time_file(path,file_name,local_time):
            tslist.append(file_name)
print(tslist)

s = int(querys['h'])
e = int(querys['a'])
new_m3u8 = "1111.m3u8" + '?' + str(s) + ',' + str(e)
with  open(new_m3u8, 'a',encoding='utf-8')as m:
    #m3u8文件头
    th = ('#EXTM3U' +'\n' +'#EXT-X-VERSION:3' +'\n'+'#EXT-X-MEDIA-SEQUENCE:0'+'\n'+
           '#EXT-X-TARGETDURATION:15'+'\n'+'#EXT-X-DISCONTINUITY'+'\n')
    m.write(th)
    #EXTINF
    # ts_duration = '10.562'#文件时长
    clip = VideoFileClip("../html/livetest/lala-13.ts")
    ts_duration = clip.duration  # seconds

    w = '#EXTINF:' + ts_duration +', no desc'
    #ts片
    for i in tslist:
        m.write(w + "\n")
        m.write(i + "\n")
    m.close()





'''
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-MEDIA-SEQUENCE:0
#EXT-X-TARGETDURATION:15
#EXT-X-DISCONTINUITY
#EXT-X-KEY:METHOD=AES-128,URI="http://10.30.59.36:8080/livetest/1111-0.key",IV=0x70A75B8228C5E273A276425D98714198
#EXTINF:10.562, no desc
1111-0.ts
#EXTINF:14.716, no desc
1111-1.ts
#EXTINF:3.545, no desc
1111-2.ts
'''
