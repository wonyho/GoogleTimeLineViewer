# Google TimeLine Map Viewer

Google Takeout에서 받은 **Location History (Timeline)** JSON을 [Leaflet](https://leafletjs.com/) 지도 위에서 날짜별로 보고, 장소 이름을 정리·내보내기 할 수 있는 단일 HTML 뷰어입니다.

## 필요한 것

- 최신 브라우저 (Chrome, Safari, Edge 등)
- 지도 타일·Leaflet CDN을 쓰므로 **인터넷 연결**
- 타임라인 데이터 파일 (아래 참고)

## 데이터 파일 준비

1. `TimeLineViewer.html` 안의 `FILE` 상수를 본인의 JSON 파일 이름에 맞게 수정합니다.

   ```javascript
   const FILE = "TimeLine20260321.json";
   ```

2. 해당 JSON은 **Google Takeout**의 Location History 형식(예: `semanticSegments` 포함)이어야 합니다.

3. JSON에는 **이동·체류 등 민감한 위치 정보**가 들어갑니다. GitHub 등에 올릴 때는 **공개 저장소에 원본 JSON을 포함하지 않는 것**을 권장합니다.

## 실행 방법

`fetch()`로 같은 폴더의 JSON을 읽기 때문에, **그냥 파일을 더블클릭(`file://`)으로 열면** 브라우저 보안 때문에 로드가 실패할 수 있습니다. **로컬 HTTP 서버**에서 여는 것을 권장합니다.

터미널에서 이 폴더로 이동한 뒤:

```bash
cd "/Volumes/Samsung_T5/GooglePhoto/GoogleTimeLine"
python3 -m http.server 8080
```

브라우저에서 다음 주소로 엽니다.

```text
http://localhost:8080/TimeLineViewer.html
```

## 주요 기능

| 기능 | 설명 |
|------|------|
| 날짜 | Load / Prev / Next / 슬라이더로 하루 단위 이동 |
| 재생 | 그날 동선을 따라 마커가 움직이는 애니메이션 (Play / Pause / Stop) |
| 장소 편집 | 이름 직접 입력, URL 링크, (선택) Google Places로 주변 검색 |
| 백업 | `places.json` — 브라우저 `localStorage`에 저장된 장소 메타데이터 다운로드 |
| 블로그용 HTML | 선택한 날짜 기준으로 단독 HTML 파일로 내보내기 |

장소 이름·좌표 보정 등은 브라우저 **localStorage**에 `places` 키로 저장됩니다. 다른 PC나 시크릿 창에서는 비어 있습니다.

## Google Maps API (선택)

**구글 지명 자동 변환** 등 Places 관련 기능을 쓰려면 `TimeLineViewer.html` 상단의 `GOOGLE_API_KEY`에 [Google Maps Platform](https://developers.google.com/maps/documentation/javascript/get-api-key) 키를 넣습니다. 비우거나 placeholder만 두면 **수동 입력 모드**로 동작합니다.

**보안:** API 키를 **공개 GitHub 저장소에 그대로 커밋하지 마세요.** 키가 노출되었다면 [Google Cloud Console](https://console.cloud.google.com/)에서 키를 비활성화·재발급하고, 앱 제한(HTTP 리퍼러 등)을 설정하는 것이 좋습니다.

## GitHub에 올릴 때

- HTML만 올리고 JSON은 제외하려면 `.gitignore`에 `*.json` 등을 추가할 수 있습니다.
- 정적 사이트로 배포(GitHub Pages 등)할 때도 **API 키·개인 위치 JSON**은 다시 한 번 확인하세요.

## 기타 파일

- `archive_browser.html` — 같은 프로젝트 내 보조용 HTML이 있을 수 있습니다.
- `Location History (Timeline)/` — Takeout 원본 세그먼트 JSON이 들어 있는 경우가 많습니다.

## 문제 해결

- **「파일 로드 실패. 웹 서버에서 실행하세요」** — 위처럼 `python3 -m http.server` 등으로 `http://localhost`에서 열었는지 확인합니다.
- **지도가 안 보임** — 광고 차단·스크립트 차단 확장 프로그램이 CDN을 막는지 확인합니다.

## 라이선스

이 저장소의 스크립트는 개인 로컬/배포 용도로 사용하세요. Leaflet·OSM·Google Maps API는 각각의 이용 약관을 따릅니다.
