function iso_points = delaunay_edge_search_N(X, search_dim, iso_val, DT_Edges)
    target = X(:, search_dim);
    edge_vals = target(DT_Edges);
    lambda = (iso_val - edge_vals(:,1)) ./ (edge_vals(:,2) - edge_vals(:,1));
    valid = (lambda >= 0) & (lambda <= 1);

    D = size(X,2);
    iso_points = NaN(sum(valid), D);
    iso_points(:, search_dim) = iso_val;

    dim = 1:D; dim(dim == search_dim) = [];
    for k = dim
        vals = X(:, k);
        pts = vals(DT_Edges);
        delta = pts(:,2) - pts(:,1);
        interp = pts(:,1) + lambda .* delta;
        iso_points(:, k) = interp(valid);
    end
end