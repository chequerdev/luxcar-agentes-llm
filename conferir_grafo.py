"""Imprime o grafo realmente compilado e executado pelo sistema."""
from src.graph import graph

representation = graph.get_graph()
print("NÓS")
for node in sorted(representation.nodes):
    print(f"- {node}")
print("ARESTAS")
for edge in sorted(representation.edges, key=lambda item: (item.source, item.target)):
    marker = " [condicional]" if edge.conditional else ""
    print(f"- {edge.source} -> {edge.target}{marker}")

