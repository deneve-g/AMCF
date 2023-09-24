# COCO数据集路径
dataDir = '/home/data/coco'
dataType = 'val2017'
annFile = '{}/annotations/instances_{}.json'.format(dataDir, dataType)
coco = COCO(annFile)

# 获取COCO数据集中的所有分类
cats = coco.loadCats(coco.getCatIds())
cat_names = [cat['name'] for cat in cats]


class SOM(nn.Module):
    def __init__(self, num_nodes, input_dim):
        super(SOM, self).__init__()
        self.num_nodes = num_nodes
        self.input_dim = input_dim
        self.nodes = nn.Parameter(torch.randn(num_nodes, input_dim))

    def forward(self, inputs):
        # 计算输入数据与每个节点之间的距离
        inputs = inputs.unsqueeze(0)
        inputs = inputs.repeat(self.num_nodes, 1, 1)
        nodes = self.nodes.unsqueeze(1)
        nodes = nodes.repeat(1, inputs.shape[1], 1)
        distances = torch.sum(torch.square(inputs - nodes), dim=-1)
        # 找到最近的节点
        winner = torch.argmin(distances, dim=0)
        return winner

    def update(self, inputs, winner, learning_rate, sigma):
        # 更新节点权重
        inputs = inputs.unsqueeze(0)
        inputs = inputs.repeat(self.num_nodes, 1, 1)
        nodes = self.nodes.unsqueeze(1)
        nodes = nodes.repeat(1, inputs.shape[1], 1)
        distances = torch.sum(torch.square(inputs - nodes), dim=-1)
        kernel = torch.exp(-winner.float() / sigma)
        kernel = kernel.unsqueeze(-1)
        delta = learning_rate * kernel * (inputs - nodes)
        self.nodes.data.add_(torch.sum(delta, dim=1))

class COCODataset(Dataset):
    def __init__(self, img_ids, dataDir, dataType, coco):
        self.img_ids = img_ids
        self.dataDir = dataDir
        self.dataType = dataType
        self.coco = coco

    def __len__(self):
        return len(self.img_ids)

    def __getitem__(self, idx):
        img_info = self.coco.loadImgs(self.img_ids[idx])[0]
        img_path = os.path.join(self.dataDir, self.dataType, img_info['file_name'])
        img = Image.open(img_path)
        # 转换图像为RGB格式
        img = img.convert('RGB')
        # 调整图像大小为统一大小
        img = img.resize((256, 256))
        img_data = np.array(img)
        return img_data

def class_diversity():
    # 训练模型
    som_models = {}
    # 为每个分类训练一个SOM模型
    for cat_name in cat_names:
        # 获取该分类下的所有图像ID
        cat_ids = coco.getCatIds(catNms=[cat_name])
        img_ids = coco.getImgIds(catIds=cat_ids)
        print(f'Number of images in {cat_name} category: {len(img_ids)}')
        # 创建数据集实例并使用DataLoader读取数据
        dataset = COCODataset(img_ids, dataDir, dataType, coco)
        dataloader = DataLoader(dataset, batch_size=1024, shuffle=True, num_workers=16)
        # 读取数据并将其添加到numpy数组中
        images = np.empty((0, 256 * 256 * 3))
        for batch in dataloader:
            batch = batch.reshape(batch.shape[0], -1)
            images = np.append(images, batch, axis=0)
        # 数据归一化
        scaler = MinMaxScaler()
        data = scaler.fit_transform(images)
        # 训练SOM模型
        num_nodes = 5 * 5
        input_dim = data.shape[1]
        som = SOM(num_nodes, input_dim).to(device)
        learning_rate = 0.5
        sigma = 0.5
        epochs = 100
        for epoch in range(epochs):
            print(epoch)
            for i in range(data.shape[0]):
                winner = som(torch.tensor(data[i]).float().to(device))
                som.update(torch.tensor(data[i]).float().to(device), winner, learning_rate, sigma)
            learning_rate *= 0.5
            sigma *= 0.5
        # 将SOM模型添加到字典中
        som_models[cat_name] = {'model': som, 'scaler': scaler}
        print(f'Trained SOM model for {cat_name} category')
    return som_models

def caculate_classdiversity():
    som_models = class_diversity()
    # 计算每个图像的SOM向量
    apis = ['Aliyun', 'Baidu', 'Stability', 'Openai', 'DeepAI','coco']
    file = ['267num_14relation_re34_test_imageid', '361num_14relation_re12_test_imageid']
    results = {}
    path = '/home/experiment_t2i'
    for item in apis:
        for i in file:
            for j in range(4):
                if j == 0:
                    filename = i
                else:
                    filename = i + '_0' + str(j)
                results[item + '_' + filename] = []
                image_file = os.path.join(path, item, filename, 'generated_images')
                for k in os.listdir(image_file):
                    image_id = k.split('_')[0]
                    # print(image_id)
                    image_path = os.path.join(image_file, k)
                    # print(image_path)
                    image = Image.open(image_path).convert('RGB').resize((256, 256))
                    img = np.array(image).flatten().reshape(1, -1)
                    # 计算新图像数据与其所属分类下的SOM模型中最近聚类中心之间的距离
                    som_model = som_models[cat_name]['model']
                    scaler = som_models[cat_name]['scaler']
                    new_data = scaler.transform(img)
                    inputs = torch.tensor(new_data).float().to(device)
                    winner = som_model(inputs)
                    nearest_cluster_center = som_model.nodes[winner]
                    nearest_cluster_center = torch.tensor(nearest_cluster_center).float().to(device)
                    distance = torch.norm(inputs - nearest_cluster_center, dim=1)
                    print(f'Distance to nearest cluster center in {cat_name} category: {distance}')
                    results[item + '_' + filename].append(distance.item())

    for k, v in results.items():
        mean_distance = torch.mean(torch.tensor(v))
        print(f'{k} mean distance: {mean_distance}')

if __name__ == '__main__':
    caculate_classdiversity()
