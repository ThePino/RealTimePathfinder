% Telling prolog that the third property could be changed
:- dynamic prop/3.

% tells if a variable it's a node
is_node(X):-
    prop(X, type, node).

% tells the coord of a node
get_node_coord(X, Lat, Lot):-
    is_node(X),
    prop(X, lat, Lat),
    prop(X, lon, Lot).

% tells if a variable it's a way
is_way(X):-
    prop(X, type, way).

% Rule to check if a way is available
is_available(Way) :-
    is_way(Way),
    prop(Way, available, true).

% change the fact on way
set_available_attribute(Way, Available) :-
    is_way(Way),
    retract(prop(Way, available, _)), % Remove the old available attribute
    assertz(prop(Way, available, Available)). % Assert the updated available attribute


% get all the ids presents for the way
get_all_way_ids(Way):-
    is_way(Way).

% get all the ids presents for the node
get_all_node(Node, Lat, Lon):-
    is_node(Node),
    prop(Node, lat, Lat),
    prop(Node, lon, Lon).

% gets all the ways from a given node From_node and/or To_node
get_ways(Way, From_node, To_node):-
    is_way(Way),
    prop(Way, from_node, From_node),
    prop(Way, to_node, To_node).

% get all the ways available
get_available_ways(Way, From_node, To_node):-
    get_ways(Way, From_node, To_node),
    is_available(Way).

% get the max speed of the way
get_max_speed_way(Way, X):-
    is_way(Way),
    prop(Way, max_speed, X).

% get the max speed between two nodes
get_max_speed_from_nodes(From_node, To_node, Max_speed):-
    get_available_ways(Way, From_node, To_node),
    get_max_speed_way(Way, Max_speed).


% get all the info of the edge
get_way_all_info_available(From_node, To_node, To_node_lat, To_node_lon, Max_speed):-
    get_available_ways(Way, From_node, To_node),
    get_max_speed_way(Way, Max_speed),
    get_node_coord(To_node, To_node_lat, To_node_lon).


