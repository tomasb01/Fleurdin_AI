from IPython.display import Image, display

def visualize(graph, output_path="graph.png"):
    """
    Visualizes a LangGraph graph and saves it to a PNG file.

    Args:
        graph: The compiled LangGraph graph
        output_path: Path where to save the PNG file (default: "graph.png")
    """
    try:
        # Generate the graph visualization
        png_data = graph.get_graph().draw_mermaid_png()

        # Save to file
        with open(output_path, "wb") as f:
            f.write(png_data)

        print(f"✅ Graf uložen do {output_path}")

    except Exception as e:
        print(f"⚠️ Nepodařilo se vytvořit vizualizaci: {e}")
        print("Graf bude fungovat i bez vizualizace.")
