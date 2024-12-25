import argparse
import os
import shutil
import sys

import h5py
import tensorflow as tf

import deepreg.model.layer as layer
import deepreg.util as util
from deepreg.registry import REGISTRY

# Parser setup for testing
parser = argparse.ArgumentParser()
parser.add_argument("thisfilename", help="The name of the current file to be used for registration")
parser.add_argument("thisdirectoryname", help="The directory for saving results")
parser.add_argument(
    "--test",
    help="Execute the script with reduced image size for test purposes.",
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

print(f"Processing: {args.thisfilename}")
MAIN_PATH = os.getcwd()
PROJECT_DIR = "/software/DeepReg/demos/classical_mr_prostate_nonrigid"
os.chdir(PROJECT_DIR)

DATA_PATH = "dataset"
FILE_PATH = os.path.join(DATA_PATH, args.thisfilename)
print(FILE_PATH)

# Registration parameters
image_loss_config = {"name": "lncc"}  # Default similarity metric (will include NMI)
deform_loss_config = {"name": "bending"}
weight_deform_loss = 1.0
learning_rate = 0.1
total_iter = int(10) if args.test else int(3000)

# Load images
if not os.path.exists(DATA_PATH):
    raise ValueError("Download the data using the demo_data.py script")
if not os.path.exists(FILE_PATH):
    raise ValueError("Download the data using the demo_data.py script")

fid = h5py.File(FILE_PATH, "r")
moving_image = tf.cast(tf.expand_dims(fid["image0"], axis=0), dtype=tf.float32)
fixed_image = tf.cast(tf.expand_dims(fid["image1"], axis=0), dtype=tf.float32)

# Normalized Mutual Information (NMI) Loss Function
def normalized_mutual_information_loss(fixed, warped, num_bins=32):
    """
    Compute the negative normalized mutual information (NMI) between two images.

    Args:
        fixed (tf.Tensor): Fixed image tensor of shape [1, D, H, W].
        warped (tf.Tensor): Warped image tensor of shape [1, D, H, W].
        num_bins (int): Number of histogram bins for intensity values.

    Returns:
        tf.Tensor: Negative normalized mutual information loss.
    """
    # Flatten the tensors
    fixed_flat = tf.reshape(fixed, [-1])
    warped_flat = tf.reshape(warped, [-1])

    # Define histogram bin edges
    bin_edges = tf.linspace(0.0, 1.0, num_bins + 1)

    # Compute histograms
    fixed_hist = tf.histogram_fixed_width(fixed_flat, [0.0, 1.0], nbins=num_bins)
    warped_hist = tf.histogram_fixed_width(warped_flat, [0.0, 1.0], nbins=num_bins)

    # Compute joint histogram manually
    joint_hist = tf.zeros([num_bins, num_bins], dtype=tf.float32)
    for i in range(num_bins):
        for j in range(num_bins):
            joint_hist = tf.tensor_scatter_nd_add(
                joint_hist,
                [[i, j]],
                [tf.reduce_sum(tf.cast((fixed_flat >= bin_edges[i]) & (fixed_flat < bin_edges[i + 1]) &
                                       (warped_flat >= bin_edges[j]) & (warped_flat < bin_edges[j + 1]), tf.float32))]
            )

    # Normalize histograms
    joint_hist /= tf.reduce_sum(joint_hist)
    fixed_hist = tf.cast(fixed_hist, tf.float32) / tf.reduce_sum(fixed_hist)
    warped_hist = tf.cast(warped_hist, tf.float32) / tf.reduce_sum(warped_hist)

    # Compute entropy terms
    H_fixed = -tf.reduce_sum(fixed_hist * tf.math.log(fixed_hist + 1e-8))
    H_warped = -tf.reduce_sum(warped_hist * tf.math.log(warped_hist + 1e-8))
    H_joint = -tf.reduce_sum(joint_hist * tf.math.log(joint_hist + 1e-8))

    # Compute normalized mutual information
    nmi = (H_fixed + H_warped) / (H_joint + 1e-8)

    return -nmi  # Return negative NMI for optimization

# Optimization function
@tf.function
def train_step(warper, weights, optimizer, mov, fix) -> tuple:
    """
    Train step function for backprop using gradient tape.
    """
    with tf.GradientTape() as tape:
        pred = warper(inputs=[weights, mov])

        # Compute similarity loss (e.g., NMI and LNCC)
        nmi_loss = normalized_mutual_information_loss(fix, pred)
        lncc_loss = REGISTRY.build_loss(config=image_loss_config)(y_true=fix, y_pred=pred)
        loss_image = 0.5 * lncc_loss + 0.5 * nmi_loss  # Combine LNCC and NMI with equal weights

        # Compute deformation regularization loss
        loss_deform = REGISTRY.build_loss(config=deform_loss_config)(inputs=weights)

        # Total loss
        loss = loss_image + weight_deform_loss * loss_deform

    # Compute gradients and apply updates
    gradients = tape.gradient(loss, [weights])
    optimizer.apply_gradients(zip(gradients, [weights]))
    return loss, loss_image, loss_deform

# Initialize deformation field
fixed_image_size = fixed_image.shape
initializer = tf.random_normal_initializer(mean=0, stddev=1e-3)
var_ddf = tf.Variable(initializer(fixed_image_size + [3]), name="ddf", trainable=True)

warping = layer.Warping(fixed_image_size=fixed_image_size[1:4])
optimiser = tf.optimizers.Adam(learning_rate)

# Training loop
for step in range(total_iter):
    loss_opt, loss_image_opt, loss_deform_opt = train_step(
        warping, var_ddf, optimiser, moving_image, fixed_image
    )
    if step % 50 == 0:  # Print progress
        tf.print(
            f"Step {step}/{total_iter}",
            "Total Loss:", loss_opt,
            "Image Loss:", loss_image_opt,
            "Deformation Loss:", loss_deform_opt,
        )

# Warp the moving image using the optimized deformation field
warped_moving_image = warping(inputs=[var_ddf, moving_image])

# Warp the moving label
moving_label = tf.cast(tf.expand_dims(fid["label0"], axis=0), dtype=tf.float32)
fixed_label = tf.cast(tf.expand_dims(fid["label1"], axis=0), dtype=tf.float32)
warped_moving_label = warping(inputs=[var_ddf, moving_label])

# Save outputs
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
arr_names = [
    "moving_image",
    "fixed_image",
    "warped_moving_image",
    "moving_label",
    "fixed_label",
    "warped_moving_label",
    "ddf",
]

filename_prefix = os.path.basename(args.thisfilename).split('_resaved_levelset')[0] + "_"
for arr, arr_name in zip(arrays, arr_names):
    util.save_array(
        save_dir=SAVE_PATH, arr=arr, name=arr_name, normalize=True, save_png=False
    )

os.chdir(MAIN_PATH)
