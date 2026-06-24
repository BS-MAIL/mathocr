# mathocr

![Uploading image.png…]()


Math OCR 이미지를 LaTeX로 변환하고, 변환된 수식을 MathLive 편집기에서 바로 수정할 수 있는 간단한 FastAPI 웹 앱입니다.


## 기능

- 이미지 업로드 또는 캔버스 손글씨 입력
- OpenAI-compatible MathBong API를 통한 이미지 수식 OCR
- OCR 결과를 MathLive 수식 편집기에서 직접 수정
- 수정된 LaTeX 원문 확인 및 복사

## 요구 사항

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- MathBong API 키

## 환경 변수 설정

`.env.example`을 복사해서 `.env`를 만든 뒤 API 키를 입력합니다.

```bash
cp .env.example .env
```

```env
MATHBONG_BASE_URL=https://llm.mathbong.com/v1
MATHBONG_API_KEY=your_mathbong_api_key_here
MATHBONG_MODEL=codex/gpt-5.5
```

`MATHBONG_API_KEY`에는 실제 키를 넣어야 합니다. `.env`는 `.gitignore`에 포함되어 있으므로 저장소에 커밋하지 않습니다.

## 설치 및 실행

```bash
uv sync
uv run uvicorn app.main:app --reload
```

브라우저에서 http://127.0.0.1:8000 을 엽니다.

## 사용 방법

1. 이미지 파일을 업로드하거나 캔버스에 수식을 직접 그립니다.
2. `인식 후 편집하기` 버튼을 누릅니다.
3. 인식된 LaTeX가 MathLive 편집기에 표시됩니다.
4. MathLive 편집기에서 수식을 직접 고치거나, 아래 `LaTeX 코드` 영역을 수정합니다.
5. `LaTeX 복사` 버튼으로 최종 LaTeX를 복사합니다.

업로드한 이미지가 있으면 업로드 파일을 우선 사용하고, 없으면 캔버스 그림을 변환합니다.

## 프로젝트 구조

```text
app/
  main.py              # FastAPI 서버와 MathBong API 연동
  static/index.html    # 업로드, 캔버스, MathLive 편집 UI
.env.example           # 환경 변수 템플릿
pyproject.toml         # uv 프로젝트 설정
```

## 참고

MathBong API의 조직 예산이나 모델 접근 권한이 제한되어 있으면 OCR 요청이 실패할 수 있습니다. 이 경우 `.env`의 모델명과 API 키 권한, 조직 예산 상태를 확인하세요.
