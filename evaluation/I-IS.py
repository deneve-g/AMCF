import torch
from torch import nn
from torch.autograd import Variable
from torch.nn import functional as F
import torch.utils.data
import os

from torchvision.models.inception import inception_v3
import argparse
import numpy as np
from scipy.stats import entropy
import torch
import torchvision.transforms as transforms
from torchvision.datasets import ImageFolder


def inception_score(images_folder, cuda=True, batch_size=32, resize=False, splits=1, c=0.9091363549232483):
    """Computes the inception score of the generated images imgs

    images_folder -- Torch dataset of (3xHxW) numpy images normalized in the range [-1, 1]
    cuda -- whether or not to run on GPU
    batch_size -- batch size for feeding into Inception v3
    splits -- number of splits
    c -- constant for scaling the logits 0.9091363549232483 on imagenet
    """
    if cuda:
        dtype = torch.cuda.FloatTensor
    else:
        if torch.cuda.is_available():
            print("WARNING: You have a CUDA device, so you should probably set cuda=True")
        dtype = torch.FloatTensor

    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    # GET
    parent_dir = os.path.dirname(images_folder)

    dataset = ImageFolder(images_folder, transform=transform)

    N = len(dataset)
    print('sum of images:', N)
    assert batch_size > 0
    assert N > batch_size

    # Set up dataloader
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size)

    # Load inception model
    inception_model = inception_v3(pretrained=True, transform_input=False).type(dtype)
    inception_model.eval()
    up = nn.Upsample(size=(299, 299), mode='bilinear').type(dtype)

    def get_pred(x):
        if resize:
            x = up(x)
        x = inception_model(x)
        return F.softmax(x / c, dim=1).data.cpu().numpy()

    # Get predictions
    preds = np.zeros((N, 1000))

    for i, batch in enumerate(dataloader, 0):
        batch = batch[0].type(dtype)
        batchv = Variable(batch)
        batch_size_i = batch.size()[0]

        preds[i * batch_size:i * batch_size + batch_size_i] = get_pred(batchv)

    # Now compute the mean kl-div
    split_scores = []

    for k in range(splits):
        part = preds[k * (N // splits): (k + 1) * (N // splits), :]
        py = np.mean(part, axis=0)
        scores = []
        for i in range(part.shape[0]):
            pyx = part[i, :]
            scores.append(entropy(pyx, py))
        split_scores.append(np.exp(np.mean(scores)))

    return np.mean(split_scores), np.std(split_scores)


if __name__ == '__main__':
    # python inception_score.py --images_folder /home/experiment_t2i/VRD_14relation_re12_test_imageid/
    # 注意不写到generated_images
    parser = argparse.ArgumentParser()
    parser.add_argument("--images_folder", type=str, required=True)  # 路径为图片的上级的上级路径
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--resize", action="store_true")
    parser.add_argument("--splits", type=int, default=1)
    parser.add_argument("--c", type=float, default=0.9091363549232483)
    args = parser.parse_args()
    print("Calculating Inception Score...")
    print(inception_score(**vars(args)))  # 越高，型生成的图像的多样性和质量越高
