# 美学统计
# apis = ['Aliyun', 'Baidu', 'Stability', 'Openai', 'DeepAI']
# classify = ['Baidu', 'Aliyun','DeepAI', 'Openai', 'Stability','coco']
import os
import json
def readfile(textpath):
    with open(textpath, 'r') as f:
        myList = json.load(f)
    return myList

def writefile(listdata, filepath):
    with open(filepath, 'w') as f:
        json.dump(listdata, f)
    return 0


apis = ['coco']
file = ['267num_14relation_re34_test_imageid', '361num_14relation_re12_test_imageid']
def calculateA(data):
    # 计算Aesthetics
    A = []
    B = []
    for i in data:
        A.append(i['Aesthetic_mean'])
        B.append(i['Aesthetic_std'])
    A = sum(A)/len(A)
    B = sum(B)/len(B)
    return A,B

path = '/home/experiment_t2i'
for item in apis:
    for i in file:
        for j in range(4):
            if j==0:
                filename = i
            else:
                filename = i + '_0' + str(j)
            json_path = os.path.join(path, item, filename, 'Aesthetic.json')
            if not os.path.exists(json_path):
                continue
            data = readfile(json_path)
            Aesthetic_mean, Aesthetic_std = calculateA(data)
            print(item, filename, Aesthetic_mean, Aesthetic_std)