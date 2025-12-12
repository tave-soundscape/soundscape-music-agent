import os
import sys

# 프로젝트 루트 경로 추가 (모듈 import를 위해)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from music_agent.graph import app


def save_graph_image():
    print("🎨 그래프 시각화 파일 생성 중...")

    try:
        # 1. 그래프를 Mermaid PNG 바이너리 데이터로 변환
        png_data = app.get_graph().draw_mermaid_png()

        # 2. 파일로 저장 (wb 모드: Binary 쓰기)
        output_file = "agent_graph.png"
        with open(output_file, "wb") as f:
            f.write(png_data)

        print(f"✅ 저장 완료! 프로젝트 폴더의 '{output_file}' 파일을 확인하세요.")

    except Exception as e:
        print(f"❌ 이미지 저장 실패: {e}")
        print("대신 아래 Mermaid 코드를 복사해서 https://mermaid.live 에 붙여넣으세요:\n")
        print(app.get_graph().draw_mermaid())


if __name__ == "__main__":
    save_graph_image()