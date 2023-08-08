import time
import random
import numpy as np
import pandas as pd
from tqdm import tqdm
import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset
from torch.utils.data import DataLoader

def data_load(dataset, has_v=True, has_a=True, has_t=True):
    dir_str = '../Data/' + dataset
    train_df = pd.read_csv(os.path.join(dir_str, 'train.csv'), index_col=None, usecols=None)
    max_user_n = train_df['userID'].max()
    train_df['itemID'] = train_df['itemID'] + max_user_n + 1
    train_segment_df = train_df[['userID', 'itemID']]
    train_edge = np.array(train_segment_df)

    user_item_dict = {}
    for (user_id, item_id) in train_edge:
        if user_id not in user_item_dict:
            user_item_dict[user_id] = [item_id]
        else:
            user_item_dict[user_id].append(item_id)


    if dataset == 'movielens':
        num_user = 55485
        num_item = 5986
        v_feat = np.load(dir_str+'/FeatureVideo_normal.npy', allow_pickle=True) if has_v else None
        a_feat = np.load(dir_str+'/FeatureAudio_avg_normal.npy', allow_pickle=True) if has_a else None
        t_feat = np.load(dir_str+'/FeatureText_stl_normal.npy', allow_pickle=True) if has_t else None
        v_feat = torch.tensor(v_feat, dtype=torch.float).cuda() if has_v else None
        a_feat = torch.tensor(a_feat, dtype=torch.float).cuda() if has_a else None
        t_feat = torch.tensor(t_feat, dtype=torch.float).cuda() if has_t else None
    elif dataset == 'Tiktok':
        num_user = 36656
        num_item = 76085
        if has_v:
            v_feat = torch.load(dir_str+'/feat_v.pt')
            v_feat = torch.tensor(v_feat, dtype=torch.float).cuda()
        else:
            v_feat = None

        if has_a:
            a_feat = torch.load(dir_str+'/feat_a.pt')
            a_feat = torch.tensor(a_feat, dtype=torch.float).cuda()
        else:
            a_feat = None

        t_feat = torch.load(dir_str+'/feat_t.pt') if has_t else None
    elif dataset == 'Kwai':
        num_user = 7010
        num_item = 86483
        v_feat = torch.load(dir_str+'/feat_v.pt')
        v_feat = torch.tensor(v_feat, dtype=torch.float).cuda()
        a_feat = t_feat = None
    else:
        if dataset == 'Clothing':
            # Clothing
            num_user = 18209
            num_item = 17318
        elif dataset == 'ToysGames':
            num_user = 18748
            num_item = 11673
        elif dataset == 'Sports':
            # Sports
            num_user = 21400
            num_item = 14825
        elif dataset == 'Office':
            # Office
            num_user = 4874
            num_item = 2406
        elif dataset == 'Baby':
            # Office
            num_user = 12637
            num_item = 6010
        v_feat = np.load(dir_str + '/FeatureImage_normal.npy', allow_pickle=True) if has_v else None
        t_feat = np.load(dir_str + '/FeatureText_normal.npy', allow_pickle=True) if has_t else None
        v_feat = torch.tensor(v_feat, dtype=torch.float).cuda() if has_v else None
        t_feat = torch.tensor(t_feat, dtype=torch.float).cuda() if has_t else None
        a_feat = None

    return num_user, num_item, train_edge, user_item_dict, v_feat, a_feat, t_feat

class TrainingDataset(Dataset):
    def __init__(self, num_user, num_item, user_item_dict, edge_index):
        self.edge_index = edge_index
        self.num_user = num_user
        self.num_item = num_item
        self.user_item_dict = user_item_dict
        self.all_set = set(range(num_user, num_user+num_item))

    def __len__(self):
        return len(self.edge_index)

    def __getitem__(self, index):
        user, pos_item = self.edge_index[index]
        while True:
            neg_item = random.sample(self.all_set, 1)[0]
            if neg_item not in self.user_item_dict[user]:
                break
        return torch.LongTensor([user,user]), torch.LongTensor([pos_item, neg_item])


class VTDataset(Dataset):
    def __init__(self, edge_index):
        self.edge_index = edge_index

    def __len__(self):
        return len(self.edge_index)

    def __getitem__(self, index):
        user = self.edge_index[index][0]
        items = torch.LongTensor(self.edge_index[index][1:])

        return torch.LongTensor([user]), torch.LongTensor(items)




