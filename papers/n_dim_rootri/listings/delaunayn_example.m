clc, clear, close all  
X = rand(100, 5);                
DT = delaunayn(X(:,1:2));
edges = get_unique_edges_from_delaunayn(DT, X);
iso_pts = delaunay_edge_search_N(X, 3, 0.5, edges);