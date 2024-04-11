import math
import numpy as np

roty30 = np.array([
    [np.cos(np.deg2rad(30)), 0, np.sin(np.deg2rad(30)), 0],
    [0, 1, 0, 0],
    [-np.sin(np.deg2rad(30)), 0, np.cos(np.deg2rad(30)), 0],
    [0, 0, 0, 1]
])
rotx180 = np.array([
    [1, 0, 0, 0],
    [0, np.cos(np.pi), -np.sin(np.pi), 0],
    [0, np.sin(np.pi), np.cos(np.pi), 0],
    [0, 0, 0, 1]
])
small_suck = np.array([#######################################################################################3
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
])
fixture_pos_roboDK = np.array([
    [1, 0, 0, 0.090966],
    [0, 1, 0, -0.581292],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
])
fixture_calibration = np.array([
    [1, 0, 0, 0.004],
    [0, 1, 0, 0.003],
    [0, 0, 1, -0.005],
    [0, 0, 0, 1]
])
fixture_pos = fixture_pos_roboDK@fixture_calibration
approach = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, -0.05],
    [0, 0, 0, 1]
])
top_pickup = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0.0117],
    [0, 0, 0, 1]
])
bottom_pickup = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0.0197-0.0012],
    [0, 0, 0, 1]
])
bottom_dropin = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0.007],
    [0, 0, 0, 1]
])
pcb_pickup = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0.0015],
    [0, 0, 0, 1]
])
t = [
    np.array([
    [1, 0, 0, -0.0384 - 0.04916*2],
    [0, 1, 0, 0.06325],
    [0, 0, 1, 0.02332 + 0.05506*2],
    [0, 0, 0, 1]]),

    np.array([
    [1, 0, 0, -0.0384 - 0.04916],
    [0, 1, 0, 0.06325],
    [0, 0, 1, 0.02332 + 0.05506],
    [0, 0, 0, 1]]),

    np.array([
    [1, 0, 0, -0.0384],
    [0, 1, 0, 0.06325],
    [0, 0, 1, 0.02332],
    [0, 0, 0, 1]])
]
b = [
    np.array([
    [1, 0, 0, -0.0384 - 0.04916*2],
    [0, 1, 0, 0.06325 + 0.1205],
    [0, 0, 1, 0.02332 + 0.05506*2],
    [0, 0, 0, 1]]),

    np.array([
    [1, 0, 0, -0.0384 - 0.04916],
    [0, 1, 0, 0.06325 + 0.1205],
    [0, 0, 1, 0.02332 + 0.05506],
    [0, 0, 0, 1]]),

    np.array([
    [1, 0, 0, -0.0384],
    [0, 1, 0, 0.06325 + 0.1205],
    [0, 0, 1, 0.02332],
    [0, 0, 0, 1]])
]
pcb = np.array([
    [1, 0, 0, -0.08513 -0.002],
    [0, 1, 0, 0.30094 -0.002],
    [0, 0, 1, 0.07686],
    [0, 0, 0, 1]])

def matrix_to_angle_axis(T):
    #Cut out rotation matrix from transformation matrix
    R = T[:3, :3]

    # Ensure the matrix is a rotation matrix by checking its determinant
    assert np.isclose(np.linalg.det(R), 1.0), "Input matrix is not a rotation matrix"

    # Compute the angle of rotation using the trace of the rotation matrix
    trace = np.trace(R)
    angle = np.arccos((trace - 1) / 2.0)

    # Compute the axis of rotation by:
    # 1 - Finding eigenvectors of the rotation matrix
    eigvals, eigvecs = np.linalg.eig(R)
    # 2 - Extract the eigenvector corresponding to eigenvalue 1
    axis = eigvecs[:, np.isclose(eigvals, 1.0)].ravel().real

    # If the angle is 0, use a default axis
    if np.isclose(angle, 0):
        axis = np.array([1,0,0])

    # Using UR-standard, the rotation is the angle multiplied by each of the elements in the normalised axis of rotation.
    rotation = angle*axis
    # Put the rotation at the end of a 6-lenth array, containing both pos and rot.
    return np.append(T[0:3,3],rotation).tolist()

# -- Finally, create robot positions in 6-value angle-axis form -- #
top_cover_pos = []
top_cover_approach = []
for matrix in t: #for each of the top cover matrices
    final_matrix = fixture_pos@matrix@roty30@top_pickup@rotx180 #multiply all the matrices to get the final matrix
    top_cover_pos.append(matrix_to_angle_axis(final_matrix)) #convert to angle-axis
    top_cover_approach.append(matrix_to_angle_axis(final_matrix@approach)) #multiply on the approach translation, and convert.

bottom_cover_pos = []
bottom_cover_drop = []
bottom_cover_approach = []
for matrix in b:
    final_matrix = fixture_pos@matrix@roty30@bottom_pickup@rotx180
    drop_pcb_matrix = fixture_pos@matrix@roty30@bottom_dropin@rotx180
    bottom_cover_pos.append(matrix_to_angle_axis(final_matrix))
    bottom_cover_drop.append(matrix_to_angle_axis(drop_pcb_matrix))
    bottom_cover_approach.append(matrix_to_angle_axis(final_matrix@approach))

pcb_matrix = fixture_pos@pcb@roty30@pcb_pickup@rotx180
pcb_pos = matrix_to_angle_axis(pcb_matrix)
pcb_approach = matrix_to_angle_axis(pcb_matrix@approach)

fuse_pos = []
fuse_approach = []

fixture_test_pos = matrix_to_angle_axis(fixture_pos@rotx180)

print("Positions were calculated")