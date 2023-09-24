import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from diffusers import DiffusionPipeline
import argparse
import json
import os
import time


def readfile(textpath):
    with open(textpath, 'r') as f:
        myList = json.load(f)
    return myList

def writefile(listdata, filepath):
    with open(filepath, 'w') as f:
        json.dump(listdata, f)
    return 0

def generate_images(model_name, json_file):
    # jsonfilename = json_file.split('/')[-1].split('.')[0] + str('_03') # VRD_14relation_re34_test_imageid
    jsonfilename = json_file.split('/')[-1].split('.')[0]

    # vxl-base-1.0
    # pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16,
    #                                          use_safetensors=True, variant="fp16")
    # v2-1
    # pipe = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2-1", torch_dtype=torch.float16)
    # pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    # v1.5
    pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)

    pipe = pipe.to("cuda")
    # pipe = pipe.to("cuda:1")
    data = readfile(json_file)
    i = 0
    dir_path = os.path.join('/home/experiment_t2i', model_name, jsonfilename, 'generated_images')
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    for item in data:
        filename = str(item['image_id']) + '_' + str(model_name.replace('/','_'))+'_'+str(time.time())+'.jpg' # 图片名字为image_id+模型名字+时间戳
        item['path'] = filename
        caption = item['caption']
        image = pipe(caption).images[0]
        save_path = os.path.join(dir_path, filename)
        print(save_path)
        image.save(save_path) #/home/experiment_t2i/VRD_14relation_re34_test_imageid/*.jpg
        i = i+1
        print(i)


    # writefile(data, os.path.join(save_filename, jsonfilename, jsonfilename + '.json'))#/home/experiment_t2i/VRD_14relation_re34_test_imageid.json
    return 0


if __name__ == '__main__':
    # model_id_stablediffusion2_1 = "stabilityai/stable-diffusion-2-1"
    # model_id_openjourney = "prompthero/openjourney"
    # python stablediffusion.py --model_name prompthero/openjourney --file_name /home/MT/coco2017testdata/VRD_14relation_re12_test_imageid.json --save_filename /home/experiment_t2i
    # 图像存储在save_filename/json文件名字/generated_images/*.jpg
    # json文件存储在save_filename/json文件名字/*.json
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, required=True, default="stabilityai/stable-diffusion-2-1")# 路径为图片的上级的上级路径
    parser.add_argument("--json_file", type=str, required=True)# /home/MT/coco2017testdata/VRD_14relation_re34_test_imageid.json
    # parser.add_argument("--save_filename", type=str, required=True)# /home/experiment_t2i
    # parser.add_argument("--c", type=float, default=0.9091363549232483)
    args = parser.parse_args()
    print("Generate images from text...")
    print(generate_images(**vars(args))) # **vars(args) 将args转化为字典
