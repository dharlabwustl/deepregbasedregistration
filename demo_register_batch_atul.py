"""
A DeepReg Demo for classical nonrigid iterative pairwise registration algorithms
"""
import argparse
import os,sys
import shutil

import h5py
import tensorflow as tf

import deepreg.model.layer as layer
import deepreg.util as util
from deepreg.registry import REGISTRY

# parser is used to simplify testing
# please run the script with --full flag to ensure non-testing mode
# for instance:
# python script.py --full
parser = argparse.ArgumentParser()
parser.add_argument("thisfilename",
                    help="The name of the current file to be used for registration")
parser.add_argument("thisdirectoryname",
                    help="The name of the current file to be used for registration")
parser.add_argument(
    "--test",
    help="Execute the script with reduced image size for test purpose.",
    dest="test",
    action="store_true",
)
parser.add_argument(
    "--full",
    help="Execute the script with full configuration.",
    dest="test",
    action="store_false",
)
parser.set_defaults(test=False)
args = parser.parse_args()

print('action:{}'.format(args.thisfilename))
MAIN_PATH = os.getcwd()
PROJECT_DIR ='/software/DeepReg/demos/classical_mr_prostate_nonrigid' # "demos/classical_mr_prostate_nonrigid"
os.chdir(PROJECT_DIR)

DATA_PATH = "dataset"
FILE_PATH = os.path.join(DATA_PATH,args.thisfilename) #sys.argv[1]) ### "demo2.h5")
print(FILE_PATH)
# registration parameters
image_loss_configs = [
    {"name": "lncc"},  # Local normalized cross-correlation
    {"name": "gmi"},   # Normalized mutual information
]
deform_loss_configs = [
    {"name": "bending"},  # Bending energy regularization
    {"name": "elastic"},  # Elastic regularization
]
weights = {"lncc": 1.0, "gmi": 0.5, "bending": 1.0, "elastic": 0.5}

learning_rate = 0.1
number_it=3000  #*4
total_iter = int(10) if args.test else int(number_it) #3000)

# load images
print(DATA_PATH)
if not os.path.exists(DATA_PATH):
    raise ValueError("Download the data using demo_data.py script")
if not os.path.exists(FILE_PATH):
    raise ValueError("Download the data using demo_data.py script")

fid = h5py.File(FILE_PATH, "r")
moving_image = tf.cast(tf.expand_dims(fid["image0"], axis=0), dtype=tf.float32)
fixed_image = tf.cast(tf.expand_dims(fid["image1"], axis=0), dtype=tf.float32)

# optimisation
@tf.function
def train_step(warper, weights, optimizer, mov, fix) -> tuple:
    """
    Train step function for backprop using gradient tape

    :param warper: warping function returned from layer.Warping
    :param weights: trainable ddf [1, f_dim1, f_dim2, f_dim3, 3]
    :param optimizer: tf.optimizers
    :param mov: moving image [1, m_dim1, m_dim2, m_dim3]
    :param fix: fixed image [1, f_dim1, f_dim2, f_dim3]
    :return:
        a tuple:
            - loss: overall loss to optimise
            - individual losses: lncc, gmi, bending, elastic
    """
    with tf.GradientTape() as tape:
        pred = warper(inputs=[weights, mov])

        # Compute individual losses
        loss_lncc = REGISTRY.build_loss(image_loss_configs[0])(y_true=fix, y_pred=pred)
        loss_gmi = REGISTRY.build_loss(image_loss_configs[1])(y_true=fix, y_pred=pred)
        loss_bending = REGISTRY.build_loss(deform_loss_configs[0])(inputs=weights)
        loss_elastic = REGISTRY.build_loss(deform_loss_configs[1])(inputs=weights)

        # Total loss
        total_loss = (
                weights["lncc"] * loss_lncc +
                weights["gmi"] * loss_gmi +
                weights["bending"] * loss_bending +
                weights["elastic"] * loss_elastic
        )

    gradients = tape.gradient(total_loss, [weights])
    optimizer.apply_gradients(zip(gradients, [weights]))

    return total_loss, loss_lncc, loss_gmi, loss_bending, loss_elastic

# ddf as trainable weights
fixed_image_size = fixed_image.shape
initializer = tf.random_normal_initializer(mean=0, stddev=1e-3)
var_ddf = tf.Variable(initializer(fixed_image_size + [3]), name="ddf", trainable=True)

warping = layer.Warping(fixed_image_size=fixed_image_size[1:4])
optimiser = tf.optimizers.Adam(learning_rate)
for step in range(total_iter):
    loss_opt, loss_lncc, loss_gmi, loss_bending, loss_elastic = train_step(
        warping, var_ddf, optimiser, moving_image, fixed_image
    )
    if (step % 50) == 0:  # print info
        tf.print(
            "Step",
            step,
            "Total Loss",
            loss_opt,
            "LNCC",
            loss_lncc,
            "NMI",
            loss_gmi,
            "Bending",
            loss_bending,
            "Elastic",
            loss_elastic,
        )

# warp the moving image using the optimised ddf
warped_moving_image = warping(inputs=[var_ddf, moving_image])

# warp the moving label using the optimised affine transformation
moving_label = tf.cast(tf.expand_dims(fid["label0"], axis=0), dtype=tf.float32)
fixed_label = tf.cast(tf.expand_dims(fid["label1"], axis=0), dtype=tf.float32)
warped_moving_label = warping(inputs=[var_ddf, moving_label])

# save output to files
SAVE_PATH = args.thisdirectoryname

arrays = [
    tf.squeeze(a)
    for a in [
        moving_image,
        fixed_image,
        warped_moving_image,
        moving_label,
        fixed_label,
        warped_moving_label,
        var_ddf,
    ]
]
filename_prefix=os.path.basename(args.thisfilename).split('_resaved_levelset')[0]+"_"
arr_names = [
    "moving_image",
    "fixed_image",
    "warped_moving_image",
    "moving_label",
    "fixed_label",
    "warped_moving_label",
    "ddf",
]
for arr, arr_name in zip(arrays, arr_names):
    util.save_array(
        save_dir=SAVE_PATH, arr=arr, name=arr_name, normalize=True, save_png=False
    )

os.chdir(MAIN_PATH)
