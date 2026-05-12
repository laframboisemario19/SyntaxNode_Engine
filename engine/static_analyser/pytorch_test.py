# import os
# import pandas as pd
# import torch
# from torch import nn
# from torch.utils.data import Dataset, DataLoader
# from torchvision import datasets, transforms
# from torchvision.io import decode_image
# from torchvision.transforms import v2

# import numpy as np
# from typing import Self, Any
# import matplotlib.pyplot as plt
   
# # Dataset : https://github.com/soarsmu/BugsInPy/tree/master
# # Article : https://dl.acm.org/doi/epdf/10.1145/3368089.3417943

# training_data = datasets.FashionMNIST(
#     root="data",
#     train=True,
#     download=True,
#     transform=v2.Compose([v2.ToImage(), v2.ToDtype(torch.float32, scale=True)])
# )

# test_data = datasets.FashionMNIST(
#     root="data",
#     train=False,
#     download=True,
#     transform=v2.Compose([v2.ToImage(), v2.ToDtype(torch.float32, scale=True)])
# )

# def visualize():
#     labels_map = {
#     0: "T-Shirt",
#     1: "Trouser",
#     2: "Pullover",
#     3: "Dress",
#     4: "Coat",
#     5: "Sandal",
#     6: "Shirt",
#     7: "Sneaker",
#     8: "Bag",
#     9: "Ankle Boot",
#     }
#     figure = plt.figure(figsize=(8, 8))
#     cols, rows = 3, 3
#     for i in range(1, cols * rows + 1):
#         sample_idx = torch.randint(len(training_data), size=(1,)).item()
#         img, label = training_data[sample_idx]
#         figure.add_subplot(rows, cols, i)
#         plt.title(labels_map[label])
#         plt.axis("off")
#         plt.imshow(img.squeeze(), cmap="gray")
#     plt.show()

# def iterate_dataloader():
#     train_dataloader = DataLoader(training_data, batch_size=64, shuffle=True)
#     test_dataloader = DataLoader(test_data, batch_size=64, shuffle=True)  

#     for train_features, train_labels in train_dataloader:
#         print(f"Feature batch shape: {train_features.size()}")
#         print(f"Labels batch shape: {train_labels.size()}")
#         img = train_features[0].squeeze()
#         label = train_labels[0]
#         plt.imshow(img, cmap="gray")
#         plt.show()
#         print(f"Label: {label}")

# class CustomImageDataset(Dataset):
#     def __init__(self, annotations_file, img_dir, transform=None, target_transform=None):
#         self.img_labels = pd.read_csv(annotations_file)
#         self.img_dir = img_dir
#         self.transform = transform
#         self.target_transform = target_transform

#     def __len__(self):
#         return len(self.img_labels)

#     def __getitem__(self, idx):
#         img_path = os.path.join(self.img_dir, self.img_labels.iloc[idx, 0])
#         image = decode_image(img_path)
#         label = self.img_labels.iloc[idx, 1]
#         if self.transform:
#             image = self.transform(image)
#         if self.target_transform:
#             label = self.target_transform(label)
#         return image, label

# class NeuralNetwork(nn.Module):
#     def __init__(self:Self) -> None:
#         super().__init__()
#         self.flatten = nn.Flatten()
#         self.linear_relu_stack = nn.Sequential(
#             nn.Linear(28*28, 512),
#             nn.ReLU(),
#             nn.Linear(512, 512),
#             nn.ReLU(),
#             nn.Linear(512, 10)
#         )
    
#     def forward(self:Self, x:Any):
#         x = self.flatten(x)
#         logits = self.linear_relu_stack(x)
#         return logits

# def main():
#     # device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else "cpu"
#     # print(f"Using {device} device")

#     # model = NeuralNetwork().to(device)
#     # print(model)

#     # X = torch.rand(1, 28, 28, device=device)
#     # logits = model(X)
#     # pred_probab = nn.Softmax(dim=1)(logits)
#     # y_pred = pred_probab.argmax(1)
#     # print(f"Predicted class: {y_pred}")

#     # input_image = torch.rand(3, 28, 28)
#     # print(input_image.size())

#     # flatten = nn.Flatten()
#     # flat_image = flatten(input_image)
#     # print(flat_image.size())

#     # layer1 = nn.Linear(in_features=28*28, out_features=20)
#     # hidden1 = layer1(flat_image)
#     # print(hidden1.size())

#     # print(f"Before ReLU: {hidden1}")
#     # hidden1 = nn.ReLU()(hidden1)
#     # print(f"After ReLU: {hidden1}")

#     # seq_modules = nn.Sequential(
#     #     flatten,
#     #     layer1,
#     #     nn.ReLU(),
#     #     nn.Linear(20, 10)
#     # )
#     # input_image = torch.rand(3, 28, 28)
#     # logits = seq_modules(input_image)

#     # softmax = nn.Softmax(dim=1)
#     # pred_probab = softmax(logits)

#     # print(f"Model structure: {model}")

#     # for name, param in model.named_parameters():
#     #     print(f"Layer: {name} | Size: {param.size()} | Values: {param[:2]} \n")
#     rnn = nn.GRU(10, 20, 2)
#     input = torch.randn(5, 3, 10)
#     h0 = torch.randn(2, 3, 20)
#     output, hn = rnn(input, h0)
#     pass

# if __name__ == "__main__":
#     # iterate_dataloader()
#     # visualize()
#     quit(main())   