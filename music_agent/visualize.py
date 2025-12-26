from music_agent.graph import app

def save_graph_image():
    png_data = app.get_graph().draw_mermaid_png()
    output_file = "agent_graph.png"
    with open(output_file, "wb") as f:
        f.write(png_data)

if __name__ == "__main__":
    save_graph_image()