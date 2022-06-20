import networkx as nx
import matplotlib.pyplot as plt
from time import sleep

class GraphVisualization:

	def __init__(self, graph):
		self.graph = graph
		self.nodes_list = []
		self.edges_list = []
		self.transform_graph(graph)

	def transform_graph(self, graph):
		self.nodes_list = list(graph.keys())
		self.edges_list = self.dict_product(graph)

	def dict_product(self,d):
		keys = d.keys()
		list = []
		for key in keys:
			values_from_key = d[key]
			for value in values_from_key:
				list.append([key, value])
		return list

	# In visualize function G is an object of
	# class Graph given by networkx G.add_edges_from(visual)
	# creates a graph with a given list
	# nx.draw_networkx(G) - plots the graph
	# plt.show() - displays the graph
	def visualize(self):
		G = nx.Graph()
		G.add_nodes_from(self.nodes_list)
		G.add_edges_from(self.edges_list)
		nx.draw_networkx(G)
		plt.show()