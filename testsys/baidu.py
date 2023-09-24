import requests
import json
import os
import time
from time import sleep
import urllib

API_KEY = "sZOLcD7gCFOaOUu9sbhT2r2W"
SECRET_KEY = "KbWkOlb9VdhHmsiGqzdgebX4hTiGKs5V"

def readfile(textpath):
    with open(textpath, 'r') as f:
        myList = json.load(f)
    return myList

def writefile(listdata, filepath):
    with open(filepath, 'w') as f:
        json.dump(listdata, f)
    return 0

def gettaskid(text):
    url = "https://aip.baidubce.com/rpc/2.0/ernievilg/v1/txt2img?access_token=" + get_access_token()

    payload = json.dumps({
        "text": text,
        "resolution": "1024*1024",
        "style": "写实风格",
        "num": 1
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.json())
    taskid = response.json()['data']['taskId']
    return taskid

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

def save_img(img_url, file_name, file_path):
    # 保存图片到磁盘文件夹 file_path中，默认为当前脚本运行目录下的 book\img文件夹
    img_path = file_path
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    # 拼接图片名（包含路径）
    filename = os.path.join(img_path, file_name)
    urllib.request.urlretrieve(img_url, filename=filename)

def getimg(taskId):
    url = "https://aip.baidubce.com/rpc/2.0/ernievilg/v1/getImg?access_token=" + get_access_token()
    payload = json.dumps({
        "taskId": taskId
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    # response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.json())
    # filepath1 = os.path.join(file_path, file_name + '_01', 'generated_images')
    # filepath2 = os.path.join(file_path, file_name + '_02', 'generated_images')
    # filepath3 = os.path.join(file_path, file_name + '_03', 'generated_images')
    urls = []
    while True:
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.json())
            urls = response.json()['data']['imgUrls']
            if response.json()['data']['status'] == 1:
                break
            else:
                sleep(20)
                continue
        # except:
        #     print('please waiting')
        #     sleep(20)
        #     continue

    return urls

def getimages(file_path):
    images = []
    for item in os.listdir(file_path):
        images.append(item.split('_')[0]) # imageid
    return images


def saveimage(urls, file_name, filepath, imageid):
    for i, url in enumerate(urls):
        imagename = str(imageid) + '_' + 'Baidu_' + str(time.time()) + '.jpg'
        imageurl = url['image']
        # file = os.path.join(filepath, file_name+'_0'+str(i+1), 'generated_images')
        file = os.path.join(filepath, file_name, 'generated_images')

        # print(file)
        if not os.path.exists(file):
            os.makedirs(file)
        # 拼接图片名（包含路径）
        filename = os.path.join(file, imagename)
        urllib.request.urlretrieve(imageurl, filename=filename)



if __name__ == '__main__':
    data1 = readfile('/home/experiment_t2i/re267num_14relation_re34_test_imageid.json')
    filename1 = 're267num_14relation_re34_test_imageid'
    data2 = readfile('/home/experiment_t2i/267num_14relation_re12_test_imageid.json')
    filename2 = '267num_14relation_re12_test_imageid'

    file_path = '/home/experiment_t2i/Baidu/'
    # file_path = os.path.join(file_path, "Baidu", filename2)
    generatedfile = os.path.join(file_path + filename2 + '/generated_images/')
    # print(generatedfile)
    if not os.path.exists(generatedfile):
        os.makedirs(generatedfile)
    # 如果已经生成了一部分，就不再生成了
    # print(generatedfile)
    existimages = getimages(generatedfile)

    print(len(data2))
    print('the exist image number is', len(existimages))
    data = []
    for item in data2:
        if str(item['image_id']) in existimages:
            continue
        else:
            data.append(item)
            # print(item)
    print('the left data is', len(data))
    # print(file_path)

    i = 0
    for item in data:
        i = i + 1
        print(i)
        caption = item['caption']
        imageid = item['image_id']
        # 单张
        if caption =='an motorcycle with wheels barely off ground tilted slightly upward from the pavement to the blue sky.':
            caption = 'a motorcycle with wheels barely off ground to the blue sky.'
            print(caption)
        taskid = gettaskid(caption)
        urls = getimg(taskid)
        saveimage(urls, filename2, file_path, imageid)

        # 多张
        # global_l1 = []
        # urls = []
        # while len(global_l1) < 3:
        #     taskid = gettaskid(caption)
        #     urls = getimg(taskid, imageid, file_path, filename2)
        #     for j in urls:
        #         if len(global_l1) < 3:
        #             global_l1.append(j)
        #         else:
        #             break
        #
        # print('global_l1', global_l1)
        # print(imageid)
        # saveimage(global_l1, filename2, file_path, imageid)

        # break
    # writefile(data1, os.path.join(file_path, filename1 + '.json'))
    print('baidu done')



