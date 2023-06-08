from simplify import *
from matplotlib import pyplot as plt
from skimage.metrics import structural_similarity as ssim
from svg import SVGDocument
from svgpath import lower_precision

vector_image = SVGDocument("examples/a.svg")
path_data = vector_image.get_path()
path = path_data.rearrange()
path = lower_precision(path, 5)

optimized = path_data.simplify_rdp()
optimized2 = path_data.simplify_vw()

vb = vector_image.dimensions
magnify = 5
vb = [vb[2] - vb[0], vb[3] - vb[1]]
ratio = vb[0] / vb[1]
fSize = (magnify * ratio, magnify) if ratio < 1 else (magnify, magnify * ratio)
s_id = 0

images = []

for shape in [path, optimized, optimized2]:
    fig = plt.figure(dpi=100, figsize=fSize)
    ax = fig.add_subplot(1, 1, 1)

    plt.box(False)
    ax.set_aspect('equal', 'box')
    ax.axis('off')
    ax.invert_yaxis()  # axis('off')
    plt.autoscale()
    plt.tight_layout(pad=0.0)

    for i_, s in enumerate(shape):
        plt.plot(s[:, 0], s[:, 1], linestyle='-', linewidth=2, color="black")
        clr = "white" if i_ in path_data.holes else "black"
        ax.fill(s[:, 0], s[:, 1], color=clr)

    fig.canvas.draw()
    buf = fig.canvas.buffer_rgba()
    X = np.asarray(buf)
    images.append(X[:, :, 0])  # img to grayscale
    # fig.show() # plt.savefig(f'shape{s_id}.png')
    s_id += 1

original = images.pop(0)


def mse(img_a, img_b):
    # the 'Mean Squared Error' between the two images is the sum of the squared difference between the two images
    mse_error = np.sum((img_a.astype("float") - img_b.astype("float")) ** 2)
    mse_error /= float(img_a.shape[0] * img_a.shape[1])

    return mse_error


def compare(img_a, img_b):
    return ssim(img_a, img_b)


for i in range(2):

    mse_value = mse(original, images[i])
    ssim_value = compare(original, images[i])
    print(f'MSE: {mse_value} | SSIM : {ssim_value}')

