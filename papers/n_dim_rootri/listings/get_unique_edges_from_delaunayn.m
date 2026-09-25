function edges = get_unique_edges_from_delaunayn(T, X)
    if nargin == 2
        filter = true; threshold = 9;
    else
        filter = false;
    end

    P = size(T, 2);
    combs = nchoosek(1:P, 2);
    edges = [];

    for i = 1:size(combs, 1)
        e = T(:, combs(i, :));
        edges = [edges; e];
    end

    edges = sort(edges, 2);
    edges = unique(edges, 'rows');

    if filter
        d = X(edges(:,2),:) - X(edges(:,1),:);
        len2 = sum(d.^2,2);
        avg = mean(len2);
        edges = edges(len2 < threshold * avg, :);
    end
end