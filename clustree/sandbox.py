import cv2
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import networkx as nx

import igraph as ig
import matplotlib.pyplot as plt

import igraph as ig
import matplotlib.pyplot as plt

from matplotlib.path import get_path_collection_extents
import PIL

def getbb(sc, ax):
    """ Function to return a list of bounding boxes in data coordinates
        for a scatter plot """
    ax.figure.canvas.draw() # need to draw before the transforms are set.
    transform = sc.get_transform()
    transOffset = sc.get_offset_transform()
    offsets = sc._offsets
    paths = sc.get_paths()
    transforms = sc.get_transforms()

    if not transform.is_affine:
        paths = [transform.transform_path_non_affine(p) for p in paths]
        transform = transform.get_affine()
    if not transOffset.is_affine:
        offsets = transOffset.transform_non_affine(offsets)
        transOffset = transOffset.get_affine()

    if isinstance(offsets, np.ma.MaskedArray):
        offsets = offsets.filled(np.nan)

    bboxes = []

    if len(paths) and len(offsets):
        if len(paths) < len(offsets):
            # for usual scatters you have one path, but several offsets
            paths = [paths[0]]*len(offsets)
        if len(transforms) < len(offsets):
            # often you may have a single scatter size, but several offsets
            transforms = [transforms[0]]*len(offsets)

        for p, o, t in zip(paths, offsets, transforms):
            result = get_path_collection_extents(
                transform.frozen(), [p], [t],
                [o], transOffset.frozen())
            print(type(result))
            bboxes.append(result.transformed(ax.transData.inverted()))

    return bboxes

def bb_to_extent(bb):
    bb = bb._points
    l, b = bb[0][0], bb[0][1]
    r, t = bb[1][0], bb[1][1]
    print(r-l, t-b)
    return (l, r, b, t)


def generate_graph():
    dg = nx.random_tree(n=10, create_using=nx.DiGraph, seed=10)

    g = ig.Graph()
    nodes = list(dg.nodes)
    g.add_vertices(n=nodes)
    edges = list(dg.edges)
    g.add_edges(edges)
    layout = g.layout_reingold_tilford(root=[0])
    pos = {k: v for k, v in zip(nodes, layout.coords)}

    x_vals, y_vals = [v[0] for k, v in pos.items()], [v[1] for k, v in pos.items()]
    min_y, max_y = min(y_vals), max(y_vals)
    min_x, max_x = min(x_vals), max(x_vals)

    norm_x = [(x - min_x) / (max_x - min_x) for x in x_vals]
    norm_y = [(y - min_y) / (max_y - min_y) for y in y_vals]
    pos = {k: (x, 1 - y) for k, x, y in zip(list(pos.keys()), norm_x, norm_y)}
    return dg, pos

ind = {f'{k_upper}_{k_lower}' for k_upper in range(1, 4) for k_lower in range(1, 4) if k_lower <= k_upper}
imgs = {
    key: PIL.Image.open(f'/Users/benbarlow/dev/clustree/tests/data/input/{key}.png')
    for key in ind
}
img = imgs["1_1"]

dg, pos = generate_graph()

fig, ax = plt.subplots(figsize=(4, 4), dpi=200)
#ax.axis("off")

nx.draw_networkx_edges(G=dg, pos=pos, node_shape="s", node_size=200, arrows=False, ax=ax)

axis_to_data = ax.transAxes + ax.transData.inverted()

nodes = nx.draw_networkx_nodes(G=dg, pos=pos, node_shape="s", node_size=100)

plt.savefig("my_fig1.png", dpi=1000, bbox_inches="tight")
plt.close()

nodelist=list(dg)
xy = np.asarray([pos[v] for v in nodelist])
node_size=300
node_color="#1f78b4"
node_shape="s"
alpha=None
cmap=None
vmin=None
vmax=None
ax=ax
linewidths=None
edgecolors=None
label=None
margins=None

node_collection = ax.scatter(
    xy[:, 0],
    xy[:, 1],
    s=node_size,
    c=node_color,
    marker='s',
    cmap=cmap,
    vmin=vmin,
    vmax=vmax,
    alpha=alpha,
    linewidths=linewidths,
    edgecolors=edgecolors,
    label=label,
)

bb = getbb(sc=node_collection, ax=ax)
bb = [bb_to_extent(ele) for ele in bb]

fig, ax = plt.subplots(figsize=(10, 10), dpi=200)

nx.draw_networkx_edges(G=dg, pos=pos, node_shape="s", node_size=200, arrows=False, ax=ax)

for b in bb:
    ax.imshow(np.asarray(img), extent=b, aspect=1, origin="upper", zorder=2)
ax.autoscale()
#ax.set_ylim((-0.5,5))

plt.savefig("my_fig2.png", dpi=1000, bbox_inches="tight")