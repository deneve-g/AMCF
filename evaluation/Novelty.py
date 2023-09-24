import numpy as np
from PIL import Image
import os
import json
from sklearn.preprocessing import MinMaxScaler
from skimage.metrics import structural_similarity as compare_ssim

def readfile(textpath):
    with open(textpath, 'r') as f:
        return json.load(f)

def calculate_similarity_o(images):
    image_arrays = [np.array(image).flatten() for image in images]
    scaler = MinMaxScaler()
    scaled_arrays = scaler.fit_transform(image_arrays)
    distances = np.linalg.norm(scaled_arrays[:, np.newaxis, :] - scaled_arrays[np.newaxis, :, :], axis=-1)
    similarities = 1 / (1 + distances)
    return np.mean(similarities)

def calculate_similarity(images):
    """
    计算图像之间的相似度矩阵

    Args:
        images: 包含 n 张图像的列表，每张图像应该是一个 PIL.Image 对象

    Returns:
        平均相似度，一个浮点数
    """
    similarities = []

    # 由于SSIM是两两比较的，我们需要比较图像列表中的每对图像
    for i in range(len(images)):
        for j in range(i + 1, len(images)):
            image1 = np.array(images[i].convert("L"))  # 转为灰度图像
            image2 = np.array(images[j].convert("L"))  # 转为灰度图像

            # 计算SSIM
            ssim_value, _ = compare_ssim(image1, image2, full=True)
            similarities.append(ssim_value)

    # 返回平均SSIM
    return np.mean(similarities)


def compute_results(apis, files, base_path):
    results = {}
    for api in apis:
        for filename in files:
            image_paths = [os.path.join(base_path, api, filename if j == 0 else f"{filename}_0{j}", 'generated_images') for j in range(4)]
            total_similarity = 0
            sample_size = len(os.listdir(image_paths[0]))
            for t in os.listdir(image_paths[0]):
                image_id = t.split('_')[0]
                images = [Image.open(os.path.join(item, file)).resize((256, 256)) for item in image_paths for file in os.listdir(item) if file.split('_')[0] == image_id]
                total_similarity += calculate_similarity(images)
            results[f"{api}_{filename}"] = total_similarity
    return results

def main():
    base_path = '/home/experiment_t2i/'
    apis = ['Openai', 'DeepAI', 'Aliyun', 'Baidu', 'Stability']
    files = ['267num_14relation_re34_test_imageid', '361num_14relation_re12_test_imageid']
    results = compute_results(apis, files, base_path)
    print(results)

if __name__ == '__main__':
    main()
