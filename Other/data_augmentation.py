
import os
import random
from skimage import io
import albumentations as A

images_to_generate=800
images_folder = "images/"
masks_folder = "masks/"
aug_images_folder = "aug_images/"
aug_masks_folder = "aug_masks/"

images = sorted([os.path.join(images_folder, file) for file in os.listdir(images_folder)])
masks = sorted([os.path.join(masks_folder, file) for file in os.listdir(masks_folder)])

augmentation = A.Compose([
    A.VerticalFlip(p=0.5),
    A.RandomRotate90(p=0.5),
    A.HorizontalFlip(p=0.5),
    A.Transpose(p=1)
])

def save_image(image, folder, img_name, index):
    path = os.path.join(folder, f"{img_name}_{index}.png")
    io.imsave(path, image)

for i in range(images_to_generate):
    rand_index = random.randint(0, len(images) -1)    
    orig_image = io.imread(images[rand_index])
    orig_mask = io.imread(masks[rand_index])
    
    augmented = augmentation(image=orig_image, mask=orig_mask)
    transformed_image = augmented['image']
    transformed_mask = augmented['mask']
    
    save_image(transformed_image, aug_images_folder, "augmented_image", i)
    save_image(transformed_mask, aug_masks_folder, "augmented_mask", i)
    