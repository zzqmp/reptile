import requests
import json
import os
import time
import re
import shutil

url = "https://www.xiaoqiqiao.com/courselab/CurriculumResourcesInfo/"
url_id = "sectionGroup?courseId=15296&token=74935a221c57f99f3ad53fac2bb9fcb9&resourceType=3&page=1&pageNum=50"
emb_filename = ('./data.json')
jsObj = json.load(open(emb_filename, encoding='UTF-8'))
base_path = "G:/xqy_videos_back"  # 创建存储文件夹


def get_html():
    html = requests.get(url + url_id).json()
    result_list = list(html["result"])
    videos_list = []
    for dict in result_list:
        dict_add = {}
        web_url = dict["web_url"]
        dir_name = dict["sectionTitle"]
        videos = dict["Title"]
        dict_add["web_url"] = web_url
        dict_add["dir_name"] = dir_name
        dict_add["file_name"] = videos
        videos_list.append(dict_add)
    return videos_list  # 返回在get html中有用的信息{url,dir_name,file_name}


def merge_file(path, new_name):  # 合并并移动文件到上一层目录
    cmd = f"copy /b * {new_name}.tmp"
    os.system(cmd)
    print(f"合并{path}/{new_name}.tmp成功")
    path_new = path.rsplit("/", 1)[0]
    # path_new = path.split(dir_new)[0]
    # 获取上一层目录G:\xqy_videos\overlay及SDN\sdn\202010_泰克DC_9-1_华为SDN概述-->
    # -->G:\xqy_videos\overlay及SDN\sdn
    src_dir = f"{path}/{new_name}.tmp"
    dst_dir = f"{path_new}/{new_name}"
    shutil.move(src_dir, dst_dir)
    print(f"移动{path}/{new_name}.tmp to {path_new}/{new_name} 成功！")


def del_dir(videos):  # 删除原本用来下载.ts文件的目录
    for idx in videos:
        dir_name = idx["dirname"].replace(" ", "_")
        file_name = idx["filename"].replace(" ", "_")
        path = base_path + "/" + dir_name
        shutil.rmtree(path, ignore_errors=True)  # 删除目录，忽略报错
        print(f"删除{path}成功!!")


def download_videos(videos):
    for idx in videos:
        id = videos.index(idx) + 1  # 用来计数下载文件
        dir_name = idx["dirname"].replace(" ", "_")
        file_name = idx["filename"].replace(" ", "_")
        web_url = idx["web_url"]
        unknow = True
        if re.match(r"(https:.*)mp4/video.m3u8", web_url):
            all_content = requests.get(web_url).text  # 获取m3u8文件，用于寻找ts文件
            file_line = all_content.split("\n")
            download_path = base_path + "/" + dir_name
            print(f"{id}:" + download_path)
            isExists = os.path.exists(download_path)
            if not isExists:
                os.makedirs(download_path)
                print(f"文件{download_path}创建完成！")
            os.chdir(download_path)
            for index, line in enumerate(file_line):
                if "#EXTINF" in line:  # 找ts地址并下载
                    unknow = False
                    pd_url = web_url.rsplit("/", 1)[0] + "/" + file_line[index + 1]  # 拼出ts片段的URL
                    # print (pd_url)
                    c_fule_name = file_line[index + 1].rsplit("/", 1)[-1]
                    if not (os.path.exists(c_fule_name)):
                        try:
                            res = requests.get(pd_url)
                            with open(os.path.join(download_path, c_fule_name), 'ab') as f:
                                f.write(res.content)
                                f.flush()
                        except:
                            time.sleep(60)
                            print("出错了！···········重新开始download！")
                            download_videos(jsObj)
            merge_file(download_path, file_name)
        else:
            # all_content = requests.get(web_url).text  # 获取m3u8文件，用于寻找ts文件
            # file_line = all_content.split("\n")
            download_path = base_path + "/" + dir_name
            print(f"{id}:" + download_path)
            isExists = os.path.exists(download_path)
            unknow = False
            if not isExists:
                os.makedirs(download_path)
                print(f"文件{download_path}创建完成！")
            os.chdir(download_path)
            if not (os.path.exists(file_name)):
                try:
                    res = requests.get(web_url)
                    print(res)
                    with open(os.path.join(download_path, file_name), 'wb') as f:
                        f.write(res.content)
                        f.flush()
                except:
                    time.sleep(60)
                    print("出错了！···········重新开始download！")
                    download_videos(jsObj)
            merge_file(download_path, file_name)
        if unknow:
            raise BaseException("未找到对应的下载链接")
        else:
            print("下载完成")
            # merge_file(download_path,file_name)


if __name__ == "__main__":
    download_videos(jsObj)
    del_dir(jsObj)
