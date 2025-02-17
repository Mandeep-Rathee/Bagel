########### train gnn for movie_reviews dataset

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import sys

from torch_geometric.loader import DataLoader

from torch_geometric.nn import global_mean_pool


sys.path.append('/home/rathee/Bagel-benchmark/bagel_benchmark')


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

import torch_geometric

from dataset.create_movie_reviews import *
from graph_classification import models



import torch_geometric.utils as pyg_utils
from torch.utils.data.dataloader import default_collate
from torch_geometric.datasets import TUDataset
import os.path as osp
import sys
import tqdm
import json



dataset_type = 'linear'


assert dataset_type in ['linear', 'complex'], "dataset type needs to be 'linear' or 'complex'"





dataset_dim = [300,2]



criterion = torch.nn.CrossEntropyLoss()

#path_base = osp.join('..', '..')

path_base = '../bagel_benchmark/dataset'



if dataset_type == 'linear':
    dataset_class = AnnotatedMoviesLinear
else:
    dataset_class = AnnotatedMoviesComplex

def load_dataset():
    train_dataset = dataset_class(path_base, preload_to=device)
    test_dataset = dataset_class(path_base, dataset_type='test', preload_to=device)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False)
    return train_loader, test_loader, test_dataset



def train(model,train_loader):
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    model.train()
    for data in train_loader:  
         out = model(data.x, data.edge_index, data.batch)  
         loss = criterion(out, data.y)  
         loss.backward()  
         optimizer.step()  
         optimizer.zero_grad() 

def test(model, loader):
     model.eval()
     correct = 0
     for data in loader:  
         out = model(data.x, data.edge_index, data.batch)
         pred = out.argmax(dim=1)
         correct += int((pred == data.y).sum())  
     return correct / len(loader.dataset)  

def load_model(path, model):
     if not torch.cuda.is_available():
         model.load_state_dict(torch.load(path, map_location="cpu"))
     else:
         model.load_state_dict(torch.load(path))
     model.eval()

    
def train_gnn(model, train_loader, test_loader):
    for epoch in range(1, 100):
        train(model,train_loader)
        train_acc = test(model,train_loader)
        test_acc = test(model, test_loader)
        print(f'Epoch: {epoch:03d}, Train Acc: {train_acc:.4f}, Test Acc: {test_acc:.4f}')



# model = models.GCN(dataset_dim)

# train_loader, test_loader, _ = load_dataset()


# train_gnn(model, train_loader=train_loader, test_loader=test_loader)




