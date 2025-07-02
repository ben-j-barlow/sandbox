using TikzGraphs
using Graphs

g = DiGraph(4)
add_edge!(g, 1, 2)
add_edge!(g, 2, 3)
TikzGraphs.plot(g)

add_edge!(g, 3, 4)
add_edge!(g, 1, 4)
TikzGraphs.plot(g)

t = TikzGraphs.plot(g)
using TikzPictures # this is required for saving
TikzPictures.save(PDF("graph"), t)
#TikzPictures.save(SVG("graph"), t)
#TikzPictures.save(TEX("graph"), t)

TikzGraphs.plot(g, ["A", "B", "C", "D"])

TikzGraphs.plot(g, ["α", "β", "γ", "δ"]) # unicdoe

using LaTeXStrings
TikzGraphs.plot(g, [L"\int_0^\infty f(x) dx", L"\sqrt{2}", L"x^2", L"\frac{1}{2}"])  # tex strings

TikzGraphs.plot(g, ["α", "β", "γ", "α"])  # repeated labels

TikzGraphs.plot(g, ["α", "β", "γ", "α"], node_style="draw, rounded corners, fill=blue!10") # specify node_style

TikzGraphs.plot(g, ["α", "β", "γ", "α"], node_style="draw, rounded corners, fill=blue!10", node_styles=Dict(1=>"fill=green!10",3=>"fill=yellow!10")) # override node_style

TikzGraphs.plot(g, ["α", "β", "γ", "α"], edge_labels=Dict((1,2)=>"x", (1,4)=>"y")) # edge labels

TikzGraphs.plot(g, ["α", "β", "γ", "α"], edge_labels=Dict((1,2)=>"x", (1,4)=>"y"), edge_style="green") # edge stles

# Layouts

TikzGraphs.plot(g, Layouts.Layered())

TikzGraphs.plot(g, Layouts.Spring())

TikzGraphs.plot(g, Layouts.SimpleNecklace())
