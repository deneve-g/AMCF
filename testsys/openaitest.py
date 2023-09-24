import os
import urllib
import openai
import time
import json
import os
import time
from time import sleep
import urllib

def save_img(img_url, file_name, file_path):
    # 保存图片到磁盘文件夹 file_path中，默认为当前脚本运行目录下的 book\img文件夹
    img_path = file_path
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

def getimages(file_path):
  images = []
  for item in os.listdir(file_path):
    images.append(item.split('_')[0])  # imageid
  return images

def getimage(text, filename, generatedfile, generatedfile1, generatedfile2, generatedfile3):
    openai.api_key = "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"
    success = False
    image_url_0 = ''
    image_url_1 = ''
    image_url_2 = ''
    image_url_3 = ''
    while success==False:
        try:
            response = openai.Image.create(prompt=text, n=1, size="512x512")
            image_url_0 = response['data'][0]['url']
            # image_url_1 = response['data'][1]['url']
            # image_url_2 = response['data'][2]['url']
            # image_url_3 = response['data'][3]['url']

            # imgname = './result/openai/' + str(i) + '.png'
            # save_img(image_url, filename, file_path)
            success = True
        except Exception as e:
            print(e)
            time.sleep(20)
    save_img(image_url_0, filename, generatedfile)
    # save_img(image_url_1, filename, generatedfile1)
    # save_img(image_url_2, filename, generatedfile2)
    # save_img(image_url_3, filename, generatedfile3)




if __name__ == "__main__":
    file_path = '/home/experiment_t2i/'
    data1 = readfile('/home/experiment_t2i/re267num_14relation_re34_test_imageid.json')
    filename1 = 're267num_14relation_re34_test_imageid'
    data2 = readfile('/home/experiment_t2i/267num_14relation_re12_test_imageid.json')
    filename2 = '267num_14relation_re12_test_imageid'

    generatedfile = os.path.join(file_path + '/Openai/' + filename1 + '/generated_images/')
    generatedfile1 = os.path.join(file_path + '/Openai/' + filename1 + '_01' + '/generated_images/')
    generatedfile2 = os.path.join(file_path + '/Openai/' + filename1 + '_02' + '/generated_images/')
    generatedfile3 = os.path.join(file_path + '/Openai/' + filename1 + '_03' + '/generated_images/')

    if not os.path.exists(generatedfile):
        os.makedirs(generatedfile)

    existimages = getimages(generatedfile)
    print('已经生成了', len(existimages))
    data = []
    for item in data1:
        if str(item['image_id']) in existimages:
            continue
        else:
            data.append(item)
    i = 0

    print('还有多少没生成', len(data))

    # for item in data:
    #     i = i + 1
    #     caption = item['caption']
    #     imageid = item['image_id']
    #     filename = str(imageid) + '_' + 'Openai_' + str(time.time()) + '.jpg'
    #     item['path'] = filename
    #     print(i, caption)
    #     getimage(caption, filename, generatedfile, generatedfile1, generatedfile2, generatedfile3)
        # break

    getimage('two people are at a computer desk.', 'test.jpg', '/home/experiment_t2i/', generatedfile1, generatedfile2, generatedfile3)