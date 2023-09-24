import base64
import requests
import os
import requests
import json
import os
import time
from time import sleep
import urllib


def readfile(textpath):
  with open(textpath, 'r') as f:
    myList = json.load(f)
  return myList


def writefile(listdata, filepath):
  with open(filepath, 'w') as f:
    json.dump(listdata, f)
  return 0

def getimage(text, files, imageid, stabilityfile):
  url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
  body = {
    "steps": 20,
    "width": 1024,
    "height": 1024,
    "seed": 0,
    "cfg_scale": 5,
    "samples": 1,
    "text_prompts": [
      {
        "text": text,
        "weight": 1
      },
      {
        "text": "blurry, bad",
        "weight": -1
      }
    ],
  }

  headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "sk-qzCNvHntGyVK2KI9yVOHzKe78J38AEdeeoKQWWDLnA4t2TSO",
  }

  response = requests.post(
    url,
    headers=headers,
    json=body,
  )

  if response.status_code != 200:
      raise Exception("Non-200 response: " + str(response.text))

  data = response.json()

  for i, image in enumerate(data["artifacts"]):
    filename = str(imageid) + '_' + 'Stability_' + str(time.time()) + '.jpg'
    # file = os.path.join(stabilityfile, files + '_' + str(i), 'generated_images')
    file = os.path.join(stabilityfile, files, 'generated_images')
    if not os.path.exists(file):
      os.makedirs(file)
    file_name = os.path.join(file, filename)
    with open(file_name, "wb") as f:
      f.write(base64.b64decode(image["base64"]))

def getimages(file_path):
  images = []
  for item in os.listdir(file_path):
    images.append(item.split('_')[0])  # imageid
  return images


if __name__ == "__main__":
  file_path = '/home/experiment_t2i/'
  data1 = readfile('/home/experiment_t2i/re267num_14relation_re34_test_imageid.json')
  filename1 = 're267num_14relation_re34_test_imageid'
  data2 = readfile('/home/experiment_t2i/267num_14relation_re12_test_imageid.json')
  filename2 = '267num_14relation_re12_test_imageid'



  generatedfile = os.path.join(file_path + '/Stability/' + filename2 + '/generated_images/')
  stabilityfile = os.path.join(file_path + '/Stability/')

  if not os.path.exists(generatedfile):
    os.makedirs(generatedfile)

  existimages = getimages(generatedfile)
  print('the exist image number is', len(existimages))
  data = []
  for item in data2:
    if str(item['image_id']) in existimages:
      continue
    else:
      data.append(item)

  i=0
  print('the input text number is', len(data))
  for item in data:
    i = i + 1
    caption = item['caption']
    imageid = item['image_id']
    # filename = str(imageid) + '_' + 'Stability_' + str(time.time()) + '.jpg'
    # item['path'] = filename

    # 对输入做处理
    if caption == 'a young boy standing on a field next to a giraffe.':
      caption = 'giraffe is next to a boy'
    if caption == 'a young child squats down in front of a bowl.':
      caption = 'a boy in front of a bowl.'
    if 'child' in caption:
      caption = caption.replace('child', 'boy')
    if 'young' in caption:
      caption = caption.replace('young ', '')
    if 'cock' in caption:
      caption = caption.replace('cock', 'clock')
    
    print(i, caption)
    getimage(caption, filename2, imageid, stabilityfile)
    # break

  print('stability finished')


