import os.path
# import random
# import numpy as np
from PIL import Image
import torchvision.transforms.functional as tf
# import torchvision.transforms as transforms
from data.base_dataset import BaseDataset, get_transform


class Iharmony4Dataset(BaseDataset):
    """A template dataset class for you to implement custom datasets."""
    def __init__(self, opt, is_for_train):
        """Initialize this dataset class.
        Parameters:
            opt (Option class) -- stores all the experiment flags; needs to be a subclass of BaseOptions
        A few things can be done here.
        - save the options (have been done in BaseDataset)
        - get image paths and meta information of the dataset.
        - define the image transformation.
        """
        # save the option and dataset root
        BaseDataset.__init__(self, opt)
        self.image_paths, self.mask_paths, self.gt_paths = [], [], []
        self.isTrain = is_for_train
        self._load_images_paths()
        self.transform = get_transform(opt)

    def _load_images_paths(self,):
        if self.isTrain:
            print('loading training file...')
            self.trainfile = os.path.join(self.opt.dataset_root, 'IHD_train.txt')
            with open(self.trainfile, 'r') as f:
                for line in f.readlines():
                    line = line.rstrip()
                    name_parts = line.split('_')
                    # data_parts = line.split('/')
                    # if data_parts[0] != 'HAdobe5k':
                    #    continue
                    mask_path = line.replace('composite_images', 'masks')
                    mask_path = mask_path.replace(('_' + name_parts[-1]), '.png')
                    gt_path = line.replace('composite_images', 'real_images')
                    gt_path = gt_path.replace('_' + name_parts[-2] + '_' + name_parts[-1], '.jpg')

                    self.image_paths.append(os.path.join(self.opt.dataset_root, line))
                    self.mask_paths.append(os.path.join(self.opt.dataset_root, mask_path))
                    self.gt_paths.append(os.path.join(self.opt.dataset_root, gt_path))

        elif not self.isTrain:
            print('loading test file...')
            self.trainfile = os.path.join(self.opt.dataset_root, 'IHD_test.txt')
            with open(self.trainfile, 'r') as f:
                for line in f.readlines():
                    line = line.rstrip()
                    name_parts = line.split('_')
                    # data_parts = line.split('/')
                    # if data_parts[0] != 'HAdobe5k':
                    mask_path = line.replace('composite_images', 'masks')
                    mask_path = mask_path.replace(('_' + name_parts[-1]), '.png')
                    gt_path = line.replace('composite_images', 'real_images')
                    gt_path = gt_path.replace('_' + name_parts[-2] + '_' + name_parts[-1], '.jpg')

                    self.image_paths.append(os.path.join(self.opt.dataset_root, line))
                    self.mask_paths.append(os.path.join(self.opt.dataset_root, mask_path))
                    self.gt_paths.append(os.path.join(self.opt.dataset_root, gt_path))

    def __getitem__(self, index):
        comp = Image.open(self.image_paths[index]).convert('RGB')
        real = Image.open(self.gt_paths[index]).convert('RGB')
        mask = Image.open(self.mask_paths[index]).convert('1')
        comp = tf.resize(comp, [256, 256])
        mask = tf.resize(mask, [256, 256])
        real = tf.resize(real, [256, 256])

        # apply the same transform to composite and real images
        comp = self.transform(comp)
        mask = tf.to_tensor(mask)
        real = self.transform(real)
        comp = self._compose(comp, mask, real)

        return {'comp': comp, 'mask': mask, 'real': real, 'img_path': self.image_paths[index]}

    def __len__(self):
        """Return the total number of images."""
        return len(self.image_paths)

    def _compose(self, foreground_img, foreground_mask, background_img):
        return foreground_img * foreground_mask + background_img * (1 - foreground_mask)
