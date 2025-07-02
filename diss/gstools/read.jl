using ReadVTK

vtk = VTRFile("/Users/benbarlow/dev/sandbox/gstools/field.vtr")
cell_data = get_cell_data(vtk)
element_ids = cell_data["element_ids"]
data = get_data(element_ids)



using MeshIO
using FileIO

# Replace "path_to_vtk_file.vtr" with the actual path to your VTK file
mesh = load("/Users/benbarlow/dev/sandbox/gstools/field.vtr")


using Makie

# Assuming the mesh is a structured grid, you can extract the points and create a plot
points = [Point3f0(p) for p in mesh.points]
connectivity = mesh.connectivity

fig = Figure()
ax = Axis3(fig[1, 1])

for cell in connectivity
    # Create a line for each cell
    lines!(ax, [points[i] for i in cell])
end

fig
