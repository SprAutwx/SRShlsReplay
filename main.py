import os,requests
import fnmatch,re
import time,datetime
import urllib.parse as urlparse
from moviepy.editor import VideoFileClip
from flask import Flask,request,redirect,url_for
import simplejson as json

app = Flask(__name__)
@app.route("/hlsreplay",methods = ['GET'])
def  hlsreplay():
    get_data = request.args.to_dict()
    app = get_data.get('app')
    stream = get_data.get('stream')
    st_time = get_data.get('st')
    en_time = get_data.get('en')
    stream_name = stream[:stream.find('.')]
    res_json = json.dumps(get_data)

    #从uri中获取app、stream，拼接出切片所在路径
    app_path = '../html/' + app
    filepath = os.walk(app_path)#取切片文件的路径
    # #从字典取h和a对应的value，即开始时间，结束时间，并转换为pythondatetime时间格式
    start_time = datetime.datetime.fromtimestamp(int(st_time))
    # #print("starttime",start_time)#starttime 2021-12-08 15:10:51
    end_time = datetime.datetime.fromtimestamp(int(en_time))
    time1 = time.mktime(time.strptime(str(start_time),"%Y-%m-%d %H:%M:%S"))
    time2 = time.mktime(time.strptime(str(end_time),"%Y-%m-%d %H:%M:%S"))
    #查找文件写入列表
    tslist = []
    for path,dir_list,file_list in filepath:
        for file_name in file_list:
            local_time = os.stat(os.path.join(path,file_name)).st_mtime
            if judge_time_file(path,file_name,local_time,time1,time2):
                tslist.append(file_name)
    #对列表进行排序
    sort = []
    for ts in tslist:
        ts = re.sub("\D","",ts)
        sort.append(ts)
    tslist_1 = sorted(list(map(int,sort)))
    ts_list = [(stream_name + '-' +str(i)+'.ts') for i in tslist_1]

    #编写新的m3u8文件
    s = str(st_time)
    e = str(en_time) 
    new_m3u8 = stream_name  + '-' + s + ',' + e + '.m3u8'
    new_m3u8_path = '../html' + '/' + app + '/' + new_m3u8
    with  open(new_m3u8_path, 'a',encoding='utf-8')as m:
        #m3u8文件头
        th = ('#EXTM3U' +'\n' +'#EXT-X-VERSION:3' +'\n'+'#EXT-X-MEDIA-SEQUENCE:0'+'\n'+
               '#EXT-X-TARGETDURATION:15'+'\n'+'#EXT-X-DISCONTINUITY'+'\n')
        m.write(th)
        #EXTINF
        for i in ts_list:
            ts_path = app_path + '/' + i
            clip = VideoFileClip(ts_path)
            ts_duration = clip.duration  # seconds 一片视频的长度
            w = '#EXTINF:' + str(ts_duration) +', no desc'
            m.write(w + "\n")#写EXTINF 
            m.write(i + "\n")#写入ts文件名
        m.write('#EXT-X-ENDLIST')#添加结尾
        m.close()
    red_url =  host + '/' + app + '/' + new_m3u8
    return redirect(red_url,code=303)
    # return res_json
def judge_time_file(path,file,update_time,time1,time2):
    if not file.endswith('.ts'):
        return False
    if time1 < update_time < time2:
        return True
    return False

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=6000)
