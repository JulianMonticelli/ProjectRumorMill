import networkx as nx

# Done:
# density, betweenness, closeness_centrality, connectivity, centrality, clustering

# Extra:
# num_nodes, num_edges, degree_histogram_frequency,

# To Do:
# add opportunity for other parameters for the graph measures that can
# add secruity to these methods
##################################################################################

# dictionary to hold all results
dictionary_to_write_out = {}
# the graph to run program on
graph_to_read = "simpletest.graphml"

#
# def main():
#    # read in a graph
#    graph = read_in_graph()
#
#    # run through all graph metrics
#    full_run_through(graph)
#
#    # run through chosen graph metrics
#
#    # write the results of all these tests to a file
#    # write_results_out()
#
#    print_results()


def read_in_graph(graph):
   # Read in a graph
   try:
      simulation_graph = nx.read_graphml(graph_to_read)
      return simulation_graph
   except IOError:
      print("Error reading in the Graph - Exiting Now")
      exit(-1)


def full_run_through(graph):

   # set the variable simulation_graph as the passed in graph object
   simulation_graph = graph
   num_nodes = find_number_nodes(simulation_graph)
   num_edges = find_number_edges(simulation_graph)
   dict_nodes_and_betweenness = find_graph_betweenness(simulation_graph)
   density = find_graph_density(simulation_graph)
   degree_freq = find_graph_degree_frequency(simulation_graph)
   connectivity = find_graph_connected(simulation_graph)
   centrality = find_graph_centrality(simulation_graph)
   closeness = find_graph_closeness_centrality(simulation_graph)
   avg_clustering = find_avg_clustering_of_graph(simulation_graph)
   sub_graph_count = find_subgraph_count(simulation_graph)
   disjoint = find_if_graph_is_disjoint(simulation_graph)

   return dictionary_to_write_out

def write_results_out():
   graph_res = graph_to_read.split(".", 1)
   graph_res = str(graph_res[0]) + "_results"
   f = open(graph_res, 'w')
   dk = dictionary_to_write_out.keys()
   for key in dk:
       f.write("\n" + key + "\n")
       s = str(dictionary_to_write_out.get(key))
       s = s + "\n"
       f.write(s)

   f.close

def print_results():
   dk = dictionary_to_write_out.keys()
   for key in dk:
    #   if key == ""
    #   print('Graph has ' + str(graph.number_of_nodes()) + ' node(s) and ' + str(graph.number_of_edges()) + ' edge(s).')
      print(key)
      s = str(dictionary_to_write_out.get(key))
      s = s + "\n"
      print(s)


def find_graph_betweenness(graph):
   d = nx.betweenness_centrality(graph)
   dictionary_to_write_out["Betweenness: "] = d
   return d

def find_graph_density(graph):
   d = nx.betweenness_centrality(graph)
   dictionary_to_write_out["Density: "] = d
   return d

def find_graph_degree_frequency(graph):
    d = nx.degree_histogram(graph)
    dictionary_to_write_out["Degree Frequency: "] = d
    return d

def find_graph_connected(graph):
    d = nx.is_connected(graph)
    dictionary_to_write_out["Node Connectivity: "] = d
    return d

def find_graph_centrality(graph):
    d = nx.degree_centrality(graph)
    dictionary_to_write_out["Graph Centrality:"] = d
    return d

def find_graph_closeness_centrality(graph):
    d = nx.closeness_centrality(graph)
    dictionary_to_write_out["Closeness Centrality:"] = d
    return d

def find_number_nodes(graph):
    d = nx.number_of_nodes(graph)
    dictionary_to_write_out["Number of Nodes:"] = d
    return d

def find_number_edges(graph):
    d = nx.number_of_edges(graph)
    dictionary_to_write_out["Number of edges:"] = d
    return d

def find_avg_clustering_of_graph(graph):
    d = nx.average_clustering(graph)
    dictionary_to_write_out["Clustering of Graph:"] = d
    return d

def find_subgraph_count(graph):
    graphs = list(nx.connected_component_subgraphs(graph, copy=True))
    d = len(graphs)
    dictionary_to_write_out["Number of graphs:"] = d
    return d


def find_if_graph_is_disjoint(graph):
   graphs = list(nx.connected_component_subgraphs(graph, copy=True))
   d = len(graphs)
   if d > 1:
       d = True
   else:
       d = False
   dictionary_to_write_out["Disjoint: "] = d
   return d


#
# # Run the main method
# if __name__ == "__main__":
#    main()
