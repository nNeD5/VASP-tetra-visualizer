import numpy as np


KPOINTS_NUMBER_LINE = 1
KPOINTS_LIST_BEGIN_LINE = 3


with open("IBZKPT") as f:
    lines = f.readlines()
lines = list(map(str.strip, lines))

# KPOINTS
n_k = int(lines[KPOINTS_NUMBER_LINE])
k = np.empty([n_k, KPOINTS_LIST_BEGIN_LINE], dtype=np.float64)
for i, line in enumerate(lines[KPOINTS_LIST_BEGIN_LINE:]):
    if i >= n_k:
        break
    line = line.split()[:3]
    k[i] = list(map(float, line))

# TETRA
TETTRA_NUMBER_LINE = KPOINTS_LIST_BEGIN_LINE + n_k + 1
TETTRA_NUMBER_LIST_BEGIN_LINE = TETTRA_NUMBER_LINE + 1

n_tetra = int(lines[TETTRA_NUMBER_LINE].split()[0])
tetra = np.empty([n_tetra, 4], dtype=np.int32)
for i, line in enumerate(lines[TETTRA_NUMBER_LIST_BEGIN_LINE:]):
    line = line.split()[1:]
    tetra[i] = list(map(int, line))
    tetra[i] -= 1 # match with k indexes in array


# LATTICE
CELL_A_VECTOR_LINE = 2
CELL_B_VECTOR_LINE = 3
CELL_C_VECTOR_LINE = 4
with open("CONTCAR") as f:
    lines = f.readlines()
lines = list(map(str.strip, lines))
reciprocal_lattice = np.empty([3, 3], dtype=np.float64)
reciprocal_lattice[0] = list(map(float, lines[CELL_A_VECTOR_LINE].split()))
reciprocal_lattice[1] = list(map(float, lines[CELL_B_VECTOR_LINE].split()))
reciprocal_lattice[2] = list(map(float, lines[CELL_C_VECTOR_LINE].split()))

reciprocal_lattice[0] = np.divide(
        1, reciprocal_lattice[0],
        where=reciprocal_lattice[0] != 0, out=np.zeros(3)
)
reciprocal_lattice[1] = np.divide(
        1, reciprocal_lattice[1],
        where=reciprocal_lattice[1] != 0, out=np.zeros(3)
)
reciprocal_lattice[2] = np.divide(
        1, reciprocal_lattice[2],
        where=reciprocal_lattice[2] != 0, out=np.zeros(3)
)


# KPOINTS to cartesian
k = np.dot(k, reciprocal_lattice)

# VISUALISE
import plotly.graph_objects as go

fig = go.Figure()
for tet in tetra:
    x, y, z = np.array([
            k[tet[0]], k[tet[1]],
            k[tet[2]], k[tet[3]]
    ]).T
    faces = [[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]]

    fig.add_trace(
            go.Mesh3d(
                x=x, y=y, z=z,
                i=[face[0] for face in faces],
                j=[face[1] for face in faces],
                k=[face[2] for face in faces],
                opacity=0.5, visible=False
            )
    )

k_trans = k.transpose()
fig.add_trace(
    go.Scatter3d(
        x=k_trans[0], y=k_trans[1], z=k_trans[2],
        mode="markers", marker=dict(color="red")
    )
)

steps = []
for i in range(n_tetra):
    step = dict(
        method="restyle",
        args=[dict(visible=[False] * len(fig.data))],
        label=i,
    )
    step["args"][0]["visible"] = [False] * len(fig.data)
    step["args"][0]["visible"][i] = True
    # step["args"][0]["visible"][:i] = [True] * i

    step["args"][0]["visible"][-1] = True
    steps.append(step)
sliders = [dict(
    active=0,
    currentvalue=dict(prefix="Tetra: "),
    pad=dict(t=50, b=20),
    steps=steps
)]

fig.update_layout(
        sliders=sliders,
        margin=dict(r=0, l=0, b=0, t=0),
        showlegend=False,
)
fig.update_scenes(
        xaxis=dict(nticks=6),
        yaxis=dict(nticks=6),
        zaxis=dict(nticks=6),
        aspectmode="manual",
        aspectratio=dict(x=1, y=1, z=1),
)
fig.data[0].visible = True

# fig.show()
fig.write_html("visual_tetra.html")
