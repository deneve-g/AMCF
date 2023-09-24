# make a generator
import os
import time
import urllib
from time import sleep
import openai
import requests
import argparse
import json
import time

from alibabacloud_imageenhan20190930.client import Client as Client1
from alibabacloud_imageenhan20190930.models import GenerateImageWithTextRequest
from alibabacloud_tea_openapi.models import Config
from alibabacloud_tea_util.models import RuntimeOptions
from alibabacloud_viapi20230117.client import Client as Client2
from alibabacloud_viapi20230117.models import GetAsyncJobResultRequest

parser = argparse.ArgumentParser(description='model choice')
parser.add_argument('--modelname', dest='modelname', type=str, help='Name of the api')
args = parser.parse_args()

def save_img(img_url, file_name, file_path):
    # 保存图片到磁盘文件夹 file_path中，默认为当前脚本运行目录下的 book\img文件夹
    img_path = os.path.join(file_path, 'generated_images')
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    # 拼接图片名（包含路径）
    filename = os.path.join(img_path, file_name)
    urllib.request.urlretrieve(img_url, filename=filename)

def readfile(textpath):
    with open(textpath, 'r') as f:
        myList = json.load(f)
    return myList

def writefile(listdata, filepath):
    with open(filepath, 'w') as f:
        json.dump(listdata, f)
    return 0

class Generator:
    def __init__(self, file_path=None, grid_size=None, resolution=None):
        self.file_path = file_path
        self.grid_size = grid_size
        self.resolution = resolution

    def generate(self):
        print('Not implemented yet')

class DharmaGenerator(Generator):
    def __init__(self, file_path, grid_size, resolution, data, access_key_id, access_key_secret,filename):
        super().__init__(file_path, grid_size, resolution)

        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.data = data

    def generate(self):
        config1 = Config(
            access_key_id='LTAI5tEjUT8d71j282s2PS7e',
            access_key_secret='JshpT39JDhtrkt9itwSnWazbNeM07p',
            endpoint='imageenhan.cn-shanghai.aliyuncs.com',
            region_id='cn-shanghai')

        config2 = Config(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            endpoint='viapi.cn-shanghai.aliyuncs.com',
            region_id='cn-shanghai'
        )
        data = self.data
        resolution = self.resolution
        resolution = resolution.replace("x", "*")
        client1 = Client1(config1)
        client2 = Client2(config2)
        i=1
        for item in data:
            filename = str(time.time()) + '.jpg'
            item['path'] = filename
            caption = item['caption']

            generate_image_with_text_request = GenerateImageWithTextRequest(
                text=caption,
                resolution=resolution,
                number=1
            )
            runtime = RuntimeOptions()
            # 初始化Client
            response = client1.generate_image_with_text_with_options(generate_image_with_text_request, runtime)
            # 获取整体结果
            body = response.body
            rid = body.request_id
            # 使用submit返回的requestID来赋值
            JOB_ID = rid
            get_async_job_result_request = GetAsyncJobResultRequest(
                job_id=JOB_ID
            )
            runtime = RuntimeOptions()

            while True:
                try:
                    response = client2.get_async_job_result_with_options(get_async_job_result_request, runtime)
                    link = response.body.data.result
                    caption = caption.replace(" ", "_")
                    save_img(link[15:-3], filename, self.file_path)
                    print(i, caption)
                    break
                except Exception as error:
                    if "NoneType" in str(error):
                        print("waiting for the result...")
                    sleep(4)
                    continue
            i = i + 1
            break

class DeepAIGenerator(Generator):
    def __init__(self, file_path, api_key, grid_size, resolution, data, filename):
        super().__init__()
        self.file_path = file_path
        self.api_key = api_key
        self.grid_size = grid_size
        self.resolution = resolution
        self.data = data
        self.filename = filename

    def generate(self, ):
        resolution = self.resolution
        resolution = resolution.split("x")
        resolution = resolution[0]
        if int(resolution) not in range(128, 1537):
            print("resolution", resolution, " not supported for deepai!!!")
            exit(9)

        data = self.data
        i=1
        for item in data:
            caption = item['caption']
            imageid = item['image_id']
            filename = str(imageid) + '_' + 'DeepAI_' + str(time.time()) + '.jpg'
            item['path'] = filename
            print(imageid, i, caption)
            r = requests.post(
                "https://api.deepai.org/api/text2img",
                data={
                    'text': caption,
                    'grid_size': self.grid_size,
                },
                headers={'api-key': self.api_key}
            )
            print(r.json())
            # img_id = r.json()['id']
            img_url = r.json()['output_url']
            save_img(img_url, filename, self.file_path)
            i=i+1

        # writefile(data, os.path.join(self.file_path, self.filename+'.json'))


def main(data, file_path, filename):
    openai_key = "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"
    deepai_key = "1a4e01c0-4472-40cc-a45e-ca8496ee78c0"
    access_key_id = 'LTAI5tEjUT8d71j282s2PS7e'
    access_key_secret = 'JshpT39JDhtrkt9itwSnWazbNeM07p'

    grid_size = 1 #不要动
    resolution = "512x512"
    args = parser.parse_args()
    selection = args.modelname

    if selection == "Dharma":
        print('Dharma')
        file_path = os.path.join(file_path, "DharmaImage", filename)
        # 'home/experiment_t2i/DharmaImage/VRD_14relation_re12_test_imageid'
        generator = DharmaGenerator(file_path, grid_size=grid_size, resolution=resolution, data=data,
                                    access_key_id=access_key_id, access_key_secret=access_key_secret, filename=filename)
        generator.generate()
        print('DharmaGenerator Finished')

    elif selection == "deepai":
        print('deepai')
        file_path = os.path.join(file_path, "DeepAI", filename)
        generator = DeepAIGenerator(file_path, api_key=deepai_key, grid_size=grid_size, resolution=resolution,
                                    data=data,filename=filename)
        generator.generate()
        print('DeepAI Finished')
    else:
        print("Please select a model to generate images.")
        exit(1)


def get_textlist(file_path):
    textlist = []
    with open(file_path, 'r') as f:
        data = json.load(f)
        for i in range(len(data)):
            textlist.append(data[i]['caption'])
    return textlist[:50] # 50


def getimages(file_path):
    images = []
    for item in os.listdir(file_path):
        images.append(item.split('_')[0]) # imageid
    return images


if __name__ == '__main__':
    file_path = '/home/experiment_t2i/'
    data1 = readfile('/home/experiment_t2i/re267num_14relation_re34_test_imageid.json')
    filename1 = 're267num_14relation_re34_test_imageid'
    data2 = readfile('/home/experiment_t2i/267num_14relation_re12_test_imageid.json')
    filename2 = '267num_14relation_re12_test_imageid'

    generatedfile = os.path.join(file_path + '/DeepAI/' + filename2 + '/generated_images/')

    if not os.path.exists(generatedfile):
        os.makedirs(generatedfile)

    #
    # # 如果已经生成了一部分，就不再生成了
    existimages = getimages(generatedfile)
    # print(existimages)
    print(len(data2))
    print('已经生成了', len(existimages))
    data = []
    for item in data2:
        if str(item['image_id']) in existimages:
            continue
        else:
            data.append(item)

    print('还有多少没生成', len(data))
    main(data, file_path, filename2)


    # 判断列表中是否有重复项
    # l1 = []
    # for item in data1:
    #     l1.append(item['image_id'])
    # # 判断列表中是否有重复项并输出重复项
    # l2 = set([x for x in l1 if l1.count(x) > 1])
    # print(l2)

