import torch
import torchvision
from torch.utils.data import Dataset
import torchvision.transforms.functional as F
from glob import glob
import os
import numpy as np
from skimage import io, transform
import trimesh
from trimesh import sample
import cv2


class ShapeNetLoader(Dataset):
  def __init__(self, dataroot, partition, npts=2048, imsize=(224, 224)):
    assert(partition in ['test', 'train', 'val'])
    self.dataroot = dataroot
    self.partition = partition
    self.npts = npts
    self.imsize = imsize
    self.dirlist = sorted(glob(os.path.join(dataroot, partition, "*")))
    self.rasterlist = [os.path.join(d, 'raster_32.npy') for d in self.dirlist]
    self.meshlist = [os.path.join(d, 'model.off') for d in self.dirlist]
    self.imlist = [os.path.join(d, 'img_choy2016') for d in self.dirlist]

  def __len__(self):
    return len(self.dirlist)

  def __getitem__(self, idx):
    """Returns tuples of (one random image, raster, surface point samples)
    """
    # load one random image
    s = '{:03d}.jpg'.format(np.random.choice(24))
    img = cv2.imread(os.path.join(self.imlist[idx], s))
    img = transform.resize(img, self.imsize, anti_aliasing=True)
    raster = np.load(self.rasterlist[idx])
    mesh = trimesh.load(self.meshlist[idx])
    pts = sample.sample_surface(mesh, self.npts)[0]

    img = torch.tensor(img).permute(2,0,1).type(torch.float32)
    raster = torch.tensor(raster).float()
    pts = torch.tensor(pts).float()
    return img, raster, pts
