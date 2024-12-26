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
image_loss_config = {"name": "gmi"}
image_loss_config_1 = {"name": "lncc"}
image_loss_config_2 = {"name": "gncc"}

deform_loss_config = {"name": "bending"}
deform_loss_config_1 = {"name": "gradient"}

weight_deform_loss = 1
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
            - loss_image: image dissimilarity
            - loss_deform: deformation regularisation
    """
    with tf.GradientTape() as tape:
        pred = warper(inputs=[weights, mov])
        loss_image = REGISTRY.build_loss(config=image_loss_config)(
            y_true=fix,
            y_pred=pred,
        )
        loss_image_1 = REGISTRY.build_loss(config=image_loss_config_1)(
            y_true=fix,
            y_pred=pred,
        )
        loss_image_2 = REGISTRY.build_loss(config=image_loss_config_2)(
            y_true=fix,
            y_pred=pred,
        )
        loss_deform = REGISTRY.build_loss(config=deform_loss_config)(
            inputs=weights,
        )
        loss_deform_1 = REGISTRY.build_loss(config=deform_loss_config_1)(
            inputs=weights,
        )
        loss = loss_image_2+ loss_image + loss_image_1+ weight_deform_loss * loss_deform + loss_deform_1
    gradients = tape.gradient(loss, [weights])
    optimizer.apply_gradients(zip(gradients, [weights]))
    return loss, loss_image, loss_deform


# ddf as trainable weights
fixed_image_size = fixed_image.shape
initializer = tf.random_normal_initializer(mean=0, stddev=1e-3)
var_ddf = tf.Variable(initializer(fixed_image_size + [3]), name="ddf", trainable=True)

warping = layer.Warping(fixed_image_size=fixed_image_size[1:4])
optimiser = tf.optimizers.Adam(learning_rate)
for step in range(total_iter):
    loss_opt, loss_image_opt, loss_deform_opt = train_step(
        warping, var_ddf, optimiser, moving_image, fixed_image
    )
    if (step % 50) == 0:  # print info
        tf.print(
            "Step",
            step,
            "loss",
            loss_opt,
            image_loss_config["name"],
            loss_image_opt,
            deform_loss_config["name"],
            loss_deform_opt,
        )

# warp the moving image using the optimised ddf
warped_moving_image = warping(inputs=[var_ddf, moving_image])

# warp the moving label using the optimised affine transformation
moving_label = tf.cast(tf.expand_dims(fid["label0"], axis=0), dtype=tf.float32)
fixed_label = tf.cast(tf.expand_dims(fid["label1"], axis=0), dtype=tf.float32)
warped_moving_label = warping(inputs=[var_ddf, moving_label])

# save output to files
SAVE_PATH =args.thisdirectoryname #sys.argv[2] # "logs_reg"
# if os.path.exists(SAVE_PATH):
#     shutil.rmtree(SAVE_PATH)
# os.mkdir(SAVE_PATH)

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
# arr_names = [
#     "moving_image",
#     "fixed_image",
#     "warped_moving_image",
#     "moving_label",
#     "fixed_label",
#     "warped_moving_label",
#     "ddf",
# ]
filename_prefix=os.path.basename(args.thisfilename).split('_resaved_levelset')[0]+"_"
arr_names = [

    "moving_image",
    "fixed_image",
    "warped_moving_image",
    "moving_label",
    "fixed_label",
    "warped_moving_label",
    "ddf",
    # filename_prefix+"moving_image",
    # filename_prefix+"fixed_image",
    # filename_prefix+"warped_moving_image",
    # filename_prefix+"moving_label",
    # filename_prefix+"fixed_label",
    # filename_prefix+"warped_moving_label",
    # filename_prefix+"ddf",
]
for arr, arr_name in zip(arrays, arr_names):
    util.save_array(
        save_dir=SAVE_PATH, arr=arr, name=arr_name, normalize=True, save_png=False
    )

os.chdir(MAIN_PATH)
