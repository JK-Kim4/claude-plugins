# 점검 목록 (catalog 1.0.0)

이 파일은 `catalog.py render`가 checks.json·incidents.json에서 만든다. 직접 고치지 않는다.

- 릴리스: 2026-11-07 · 조사 기준일: 2026-11-07 · 사건 85건 · 점검 57건

## 인터넷 노출 자산·미패치 (`unpatched-exposed`)

인터넷에 노출된 서버·VPN·방화벽·미들웨어·업무 앱의 알려진 취약점(CVE)이 패치되지 않아 첫 침입 지점이 된 경우. AI 정찰이 가장 먼저 찾는 곳.

사건: Oracle Cloud(레거시 로그인 서버)(2025-03), Citrix NetScaler 사용 기관(2025-06), 온프레미스 SharePoint 운영 기관 400곳+(2025-07), 의료·응급서비스·정부 등 최소 17개 조직(2025-08), Oracle E-Business Suite 고객 수십~100곳+(2025-08), Asahi Group(일본)(2025-09), Cisco ASA/Firepower 사용 기관(2025-09), KT(2025-09), 롯데카드(2025-09), 기술·금융·화학·정부 약 30곳(2025-11), Ivanti EPMM 사용 기관(EU 집행위, 네덜란드 정부 등)(2026-01), OpenClaw(자체 호스팅 에이전트 게이트웨이)(2026-01), Cisco Catalyst SD-WAN 사용 기관(2026-02), 55개국 FortiGate 장비 600대+(2026-02), 동아시아 기술·보안 기업 등(2026-05), PTC Windchill·FlexPLM 사용 제조사(2026-06), 노출된 Langflow 서버 경유 운영 DB(2026-07), 행정안전부 정부24(어린이포털)(2026-08), 기술·SaaS 기업과 고객 테넌트, 항공사, 에너지 기업(2026-09), 유럽 정당·언론·싱크탱크(2026-02), 신한·KB국민·하나은행 등 금융사 37곳(2026-09)

| 심각도 | 점검 | 방식 | 근거 사건 | 추가 |
|---|---|---|---|---|
| critical | `unpatched-exposed/ai-workflow-server-exposure` AI 워크플로·에이전트 서버 노출 | config | 노출된 Langflow 서버 경유 운영 DB, OpenClaw(자체 호스팅 에이전트 게이트웨이), 기술·SaaS 기업과 고객 테넌트, 항공사, 에너지 기업, LiteLLM(AI 게이트웨이) 사용자 | 1.0.0 |
| critical | `unpatched-exposed/edge-and-enterprise-patch-sla` 노출된 엣지 장비·엔터프라이즈 앱의 패치 기한 | infra | 롯데카드, Oracle Cloud(레거시 로그인 서버), 온프레미스 SharePoint 운영 기관 400곳+, Oracle E-Business Suite 고객 수십~100곳+, Cisco ASA/Firepower 사용 기관, Ivanti EPMM 사용 기관(EU 집행위, 네덜란드 정부 등), Cisco Catalyst SD-WAN 사용 기관, PTC Windchill·FlexPLM 사용 제조사, Asahi Group(일본), Citrix NetScaler 사용 기관 | 1.0.0 |
| critical | `unpatched-exposed/test-debug-endpoints` 운영에 남은 테스트·디버그·관리 엔드포인트 | code | 신한·KB국민·하나은행 등 금융사 37곳, 행정안전부 정부24(어린이포털), 유럽 정당·언론·싱크탱크 | 1.0.0 |
| high | `unpatched-exposed/internet-exposure-inventory` 인터넷 노출 자산과 관리 인터페이스 목록 | infra | 롯데카드, 신한·KB국민·하나은행 등 금융사 37곳, 55개국 FortiGate 장비 600대+, 동아시아 기술·보안 기업 등, 기술·금융·화학·정부 약 30곳, 의료·응급서비스·정부 등 최소 17개 조직, KT | 1.0.0 |
| high | `unpatched-exposed/post-patch-session-and-key-reset` 패치 후 세션 무효화와 키 교체 | process | Citrix NetScaler 사용 기관, 온프레미스 SharePoint 운영 기관 400곳+ | 1.0.0 |

## 자격증명·키·토큰 관리 (`credential-key`)

평문 저장·하드코딩된 비밀, 폐기되지 않은 서명키·접근 토큰, 장기 유효 자격증명, 재사용 비밀번호가 침해 경로나 확산 경로가 된 경우.

사건: Bybit / Safe{Wallet}(2025-02), SK텔레콤(2025-04), McDonald's 채용 AI 챗봇(Paradox.ai)(2025-07), 의료·응급서비스·정부 등 최소 17개 조직(2025-08), LG유플러스(2025-08), Nx npm 패키지 사용자(2025-08), Salesloft Drift 경유 Salesforce 고객 700곳+(2025-08), KT(2025-09), npm 생태계(1차 500+, 2차 약 800 패키지)(2025-09), 행정안전부(온나라·GVPN)(2025-10), 불특정(일부 국가 배후)(2025-11), 기술·금융·화학·정부 약 30곳(2025-11), 쿠팡(2025-11), Gainsight 앱 사용 Salesforce 고객 200+ 인스턴스(2025-11), 업비트(두나무)(2025-11), ServiceNow Virtual Agent / Now Assist(2026-01), 55개국 FortiGate 장비 600대+(2026-02), Moltbook(바이브 코딩 AI 에이전트 SNS)(2026-02), European Commission(2026-03), Aqua Trivy(하류: LiteLLM, EU 집행위 등)(2026-03), Drift Protocol(Solana DeFi)(2026-04), Lovable 공개 프로젝트(2026-04), Vercel(Context.ai 경유)(2026-04), Klue → 고객사 약 200곳(2026-06), 티빙(2026-06), 노출된 Langflow 서버 경유 운영 DB(2026-07), 기술·SaaS 기업과 고객 테넌트, 항공사, 에너지 기업(2026-09), AI 기업 약 30곳의 평가 샌드박스(2026-09), 유럽 정당·언론·싱크탱크(2026-02), Binance(2026-10)

| 심각도 | 점검 | 방식 | 근거 사건 | 추가 |
|---|---|---|---|---|
| critical | `credential-key/default-and-weak-credentials` 기본·약한·테스트 자격증명 | config | 노출된 Langflow 서버 경유 운영 DB, McDonald's 채용 AI 챗봇(Paradox.ai), 55개국 FortiGate 장비 600대+ | 1.0.0 |
| critical | `credential-key/hardcoded-secrets` 소스·클라이언트·이미지에 하드코딩된 비밀 | code | 티빙, 쿠팡, 기술·SaaS 기업과 고객 테넌트, 항공사, 에너지 기업, 유럽 정당·언론·싱크탱크, Lovable 공개 프로젝트, Moltbook(바이브 코딩 AI 에이전트 SNS) | 1.0.0 |
| critical | `credential-key/high-value-signing-controls` 고액 서명·출금 시스템의 통제 | infra | Bybit / Safe{Wallet}, Drift Protocol(Solana DeFi), 업비트(두나무), Binance | 1.0.0 |
| critical | `credential-key/plaintext-credential-storage` 평문으로 저장된 계정·비밀번호·키 | code | SK텔레콤, Moltbook(바이브 코딩 AI 에이전트 SNS), LG유플러스 | 1.0.0 |
| critical | `credential-key/signing-key-lifecycle` 토큰 서명키 보관·교체·폐기 | code | 쿠팡 | 1.0.0 |
| high | `credential-key/incident-secret-rotation` 침해 후 비밀 일괄 교체 | process | Aqua Trivy(하류: LiteLLM, EU 집행위 등), Gainsight 앱 사용 Salesforce 고객 200+ 인스턴스, LiteLLM(AI 게이트웨이) 사용자 | 1.0.0 |
| high | `credential-key/long-lived-cloud-keys` 장기 유효·과다 권한 클라우드 키 | config | European Commission, Bybit / Safe{Wallet}, 티빙 | 1.0.0 |
| high | `credential-key/orphaned-credentials` 퇴사자·협력사·파일럿용으로 발급된 뒤 남은 자격증명 | process | Klue → 고객사 약 200곳, 쿠팡 | 1.0.0 |
| high | `credential-key/shared-device-and-instance-secrets` 여러 장비·인스턴스가 공유하는 같은 키·인증서 | code | KT, ServiceNow Virtual Agent / Now Assist | 1.0.0 |
| medium | `credential-key/secret-classification-in-platforms` 배포 플랫폼 환경변수의 민감 분류 | config | Vercel(Context.ai 경유) | 1.0.0 |

## 인증·인가 결함 (`authn-authz`)

인증 우회, 객체 단위 인가 누락(IDOR/BOLA), 크리덴셜 스터핑 방어 부재, 약한 MFA처럼 애플리케이션이 '누가 무엇을 할 수 있는가'를 잘못 판정한 경우.

사건: GS리테일(GS25·GS SHOP)(2025-01), Base44(바이브 코딩 플랫폼)(2025-07), McDonald's 채용 AI 챗봇(Paradox.ai)(2025-07), 행정안전부(온나라·GVPN)(2025-10), 쿠팡(2025-11), ServiceNow Virtual Agent / Now Assist(2026-01), 55개국 FortiGate 장비 600대+(2026-02), Odido(네덜란드 통신사)(2026-02), Stryker(2026-03), Lovable 공개 프로젝트(2026-04), 오픈소스 웹 시스템 관리 도구(제품명 비공개)(2026-05), 신한·KB국민·하나은행 등 금융사 37곳(2026-09), 빗썸(2026-10), 대신증권(2026-10), G마켓(2026-10)

| 심각도 | 점검 | 방식 | 근거 사건 | 추가 |
|---|---|---|---|---|
| critical | `authn-authz/auth-flow-server-verification` 인증·본인확인 흐름의 서버 측 검증 | code | 신한·KB국민·하나은행 등 금융사 37곳, 오픈소스 웹 시스템 관리 도구(제품명 비공개), Base44(바이브 코딩 플랫폼), ServiceNow Virtual Agent / Now Assist | 1.0.0 |
| critical | `authn-authz/object-level-authorization` 객체 단위 인가(IDOR/BOLA) | code | 신한·KB국민·하나은행 등 금융사 37곳, G마켓, 대신증권, McDonald's 채용 AI 챗봇(Paradox.ai), Lovable 공개 프로젝트 | 1.0.0 |
| high | `authn-authz/credential-stuffing-defense` 크리덴셜 스터핑 방어 | code | GS리테일(GS25·GS SHOP) | 1.0.0 |
| high | `authn-authz/destructive-admin-action-guard` 파괴적 관리 명령의 다중 승인 | infra | Stryker, 노출된 Langflow 서버 경유 운영 DB | 1.0.0 |
| high | `authn-authz/phishing-resistant-mfa-remote-admin` 원격·관리자 접근의 피싱 내성 MFA | infra | 행정안전부(온나라·GVPN), Odido(네덜란드 통신사), 55개국 FortiGate 장비 600대+, 빗썸, 의료·응급서비스·정부 등 최소 17개 조직, 기술·금융·화학·정부 약 30곳 | 1.0.0 |

## 클라우드·BaaS 설정 오류 (`cloud-baas-config`)

Firebase·Supabase 보안 규칙, 공개 스토리지 버킷, 인증 없는 DB·검색엔진·관리 콘솔 노출, 과도한 IAM 권한처럼 설정 때문에 데이터가 열린 경우.

사건: Lovable로 생성된 앱(2025-05), Tea Dating Advice(2025-07), Moltbook(바이브 코딩 AI 에이전트 SNS)(2026-02), Stryker(2026-03), 공개 접근 가능한 AI 생성 앱 약 38만 개(2026-05), 티빙(2026-06), 노출된 Langflow 서버 경유 운영 DB(2026-07), 유럽 정당·언론·싱크탱크(2026-02), 할리스(2026-10)

| 심각도 | 점검 | 방식 | 근거 사건 | 추가 |
|---|---|---|---|---|
| critical | `cloud-baas-config/firebase-security-rules` Firebase 보안 규칙 | config | Tea Dating Advice | 1.0.0 |
| critical | `cloud-baas-config/supabase-rls` Supabase Row Level Security | config | Lovable로 생성된 앱, Moltbook(바이브 코딩 AI 에이전트 SNS) | 1.0.0 |
| high | `cloud-baas-config/exposed-datastores` 인증 없이 열린 DB·캐시·검색엔진 | config | 노출된 Langflow 서버 경유 운영 DB, 유럽 정당·언론·싱크탱크 | 1.0.0 |
| high | `cloud-baas-config/public-object-storage` 공개된 객체 스토리지와 그 안의 비밀 | config | Tea Dating Advice, 노출된 Langflow 서버 경유 운영 DB, 할리스 | 1.0.0 |
| high | `cloud-baas-config/repo-and-environment-least-privilege` 저장소·개발환경의 최소 권한 | infra | 티빙, GitHub | 1.0.0 |

## 소프트웨어 공급망·CI/CD (`software-supply-chain`)

악성·탈취된 오픈소스 패키지와 자가 전파 웜, 유지관리자 계정 피싱, CI 워크플로 취약 설정, 빌드·배포 파이프라인 변조로 들어온 경우.

사건: Bybit / Safe{Wallet}(2025-02), Amazon Q Developer VS Code 확장(2025-07), Nx npm 패키지 사용자(2025-08), npm chalk·debug 등 18개 패키지(2025-09), 비공식 postmark-mcp 사용자(2025-09), npm 생태계(1차 500+, 2차 약 800 패키지)(2025-09), Cline npm 릴리스 파이프라인(2026-02), npm 개발자·AI 어시스턴트 사용자(2026-02), axios(npm)(2026-03), European Commission(2026-03), LiteLLM(AI 게이트웨이) 사용자(2026-03), Aqua Trivy(하류: LiteLLM, EU 집행위 등)(2026-03), CI 코딩 에이전트(Claude Code Security Review, Gemini CLI Action, Copilot Agent)(2026-04), GitHub(2026-05), TanStack npm(하류: OpenAI 등)(2026-05)

| 심각도 | 점검 | 방식 | 근거 사건 | 추가 |
|---|---|---|---|---|
| critical | `software-supply-chain/gha-untrusted-trigger` GitHub Actions의 신뢰할 수 없는 트리거·입력 | config | Nx npm 패키지 사용자, Aqua Trivy(하류: LiteLLM, EU 집행위 등), TanStack npm(하류: OpenAI 등), npm 생태계(1차 500+, 2차 약 800 패키지) | 1.0.0 |
| high | `software-supply-chain/ci-action-pinning` CI 액션·도구의 커밋 SHA 고정 | config | Aqua Trivy(하류: LiteLLM, EU 집행위 등), LiteLLM(AI 게이트웨이) 사용자, European Commission | 1.0.0 |
| high | `software-supply-chain/ci-token-scope-and-isolation` CI 토큰 권한과 작업 격리 | config | Amazon Q Developer VS Code 확장, TanStack npm(하류: OpenAI 등), Cline npm 릴리스 파이프라인 | 1.0.0 |
| high | `software-supply-chain/dependency-pinning-and-cooldown` 의존성 고정과 신규 버전 유예 | config | npm chalk·debug 등 18개 패키지, axios(npm), TanStack npm(하류: OpenAI 등), npm 생태계(1차 500+, 2차 약 800 패키지) | 1.0.0 |
| high | `software-supply-chain/frontend-asset-integrity` 프런트엔드 정적 자산 무결성 | config | Bybit / Safe{Wallet}, Salesforce Agentforce | 1.0.0 |
| high | `software-supply-chain/ide-extension-and-installer-integrity` IDE 확장·개발 도구 설치본 관리 | process | GitHub, Binance | 1.0.0 |
| high | `software-supply-chain/install-scripts` 패키지 install 스크립트 실행 제한 | config | Nx npm 패키지 사용자, npm 생태계(1차 500+, 2차 약 800 패키지) | 1.0.0 |
| high | `software-supply-chain/package-publishing-hardening` 직접 게시하는 패키지의 계정·게시 보호 | process | npm chalk·debug 등 18개 패키지, axios(npm), LiteLLM(AI 게이트웨이) 사용자 | 1.0.0 |

## 서드파티 SaaS·OAuth 연동 (`saas-oauth-thirdparty`)

CRM·지원도구 등 SaaS에 연결된 서드파티 앱의 OAuth 토큰·API 키가 탈취되거나, 위탁·협력사를 거쳐 고객 데이터가 빠져나간 경우.

사건: 디올·티파니·루이비통 코리아(2025-05), Salesforce 고객사 다수(Google, Qantas, Allianz Life 등)(2025-06), LG유플러스(2025-08), Salesloft Drift 경유 Salesforce 고객 700곳+(2025-08), Gainsight 앱 사용 Salesforce 고객 200+ 인스턴스(2025-11), Mixpanel → OpenAI API 사용자 등(2025-11), Vercel(Context.ai 경유)(2026-04), Klue → 고객사 약 200곳(2026-06), 기술·SaaS 기업과 고객 테넌트, 항공사, 에너지 기업(2026-09), 맑은소프트(LMS 수탁사)와 고객사 20여 곳(2026-09), 대신증권(2026-10), 대한항공·아시아나항공(Amadeus 경유)(2026-10)

| 심각도 | 점검 | 방식 | 근거 사건 | 추가 |
|---|---|---|---|---|
| critical | `saas-oauth-thirdparty/stored-customer-token-protection` 우리 서비스가 보관하는 고객 OAuth 토큰 보호 | code | Salesloft Drift 경유 Salesforce 고객 700곳+, Klue → 고객사 약 200곳, Gainsight 앱 사용 Salesforce 고객 200+ 인스턴스 | 1.0.0 |
| high | `saas-oauth-thirdparty/connected-app-governance` SaaS 연결 앱·OAuth 권한 관리 | process | Salesforce 고객사 다수(Google, Qantas, Allianz Life 등), Salesloft Drift 경유 Salesforce 고객 700곳+, Gainsight 앱 사용 Salesforce 고객 200+ 인스턴스, Klue → 고객사 약 200곳, Vercel(Context.ai 경유), 디올·티파니·루이비통 코리아 | 1.0.0 |
| high | `saas-oauth-thirdparty/vendor-and-subcontractor-access` 협력사·수탁사 접근 관리 | process | LG유플러스, 맑은소프트(LMS 수탁사)와 고객사 20여 곳, 대한항공·아시아나항공(Amadeus 경유), 대신증권, Coinbase | 1.0.0 |

## 사회공학·헬프데스크·내부자 (`social-engineering-identity`)

보이스피싱·헬프데스크 사칭으로 비밀번호·MFA를 재설정하거나, 내부자 매수·퇴사자 권한 잔존으로 접근한 경우. 대부분 조직 절차 점검.

사건: Bybit / Safe{Wallet}(2025-02), Marks & Spencer, Co-op(2025-04), Coinbase(2025-05), 디올·티파니·루이비통 코리아(2025-05), Salesforce 고객사 다수(Google, Qantas, Allianz Life 등)(2025-06), 미 국무장관 사칭 → 외국 외교장관·주지사 등(2025-07), 원격 채용 기술기업(2025-08), Odido(네덜란드 통신사)(2026-02), axios(npm)(2026-03), Drift Protocol(Solana DeFi)(2026-04), Charter Communications(Spectrum)(2026-05), Binance(2026-10)

| 심각도 | 점검 | 방식 | 근거 사건 | 추가 |
|---|---|---|---|---|
| critical | `social-engineering-identity/helpdesk-reset-verification` 헬프데스크의 비밀번호·MFA 재설정 본인확인 | process | Marks & Spencer, Co-op, Salesforce 고객사 다수(Google, Qantas, Allianz Life 등), 디올·티파니·루이비통 코리아, Odido(네덜란드 통신사), Charter Communications(Spectrum) | 1.0.0 |
| high | `social-engineering-identity/developer-targeted-lures` 개발자 대상 가짜 채용·협업 미끼 | process | Binance, axios(npm), Bybit / Safe{Wallet}, 원격 채용 기술기업 | 1.0.0 |
| high | `social-engineering-identity/support-tool-data-exposure` 고객지원·관리 도구의 데이터 노출 범위 | code | Coinbase, Odido(네덜란드 통신사), 디올·티파니·루이비통 코리아 | 1.0.0 |
| medium | `social-engineering-identity/out-of-band-verification` 음성·영상 사칭에 대비한 대역 외 확인 | process | 미 국무장관 사칭 → 외국 외교장관·주지사 등, Drift Protocol(Solana DeFi) | 1.0.0 |

## AI·LLM 애플리케이션 (`ai-app-security`)

프롬프트 인젝션(간접 포함), 과도한 에이전트 권한, 모델 출력의 무검증 실행, RAG·도구 호출을 통한 데이터 유출처럼 서비스에 들어간 AI 구성요소가 공격면이 된 경우.

사건: GitHub MCP 서버 사용자(2025-05), Lovable로 생성된 앱(2025-05), Microsoft 365 Copilot(2025-06), Base44(바이브 코딩 플랫폼)(2025-07), Salesforce Agentforce(2025-09), ServiceNow Virtual Agent / Now Assist(2026-01), Moltbook(바이브 코딩 AI 에이전트 SNS)(2026-02), 공개 접근 가능한 AI 생성 앱 약 38만 개(2026-05), AI 기업 약 30곳의 평가 샌드박스(2026-09)

| 심각도 | 점검 | 방식 | 근거 사건 | 추가 |
|---|---|---|---|---|
| critical | `ai-app-security/untrusted-content-in-agent-context` 에이전트가 읽는 외부 콘텐츠(간접 프롬프트 인젝션) | code | Microsoft 365 Copilot, Salesforce Agentforce, GitHub MCP 서버 사용자, AI 기업 약 30곳의 평가 샌드박스 | 1.0.0 |
| high | `ai-app-security/agent-tool-authorization` 에이전트 도구의 권한과 사용자 단위 인가 | code | ServiceNow Virtual Agent / Now Assist, GitHub MCP 서버 사용자 | 1.0.0 |
| high | `ai-app-security/ai-generated-app-review` AI로 만든 앱의 배포 전 보안 검토 | process | 공개 접근 가능한 AI 생성 앱 약 38만 개, Base44(바이브 코딩 플랫폼), Lovable로 생성된 앱, Moltbook(바이브 코딩 AI 에이전트 SNS) | 1.0.0 |
| high | `ai-app-security/llm-keys-and-sandbox-isolation` LLM 키 노출과 코드 실행 샌드박스 격리 | config | AI 기업 약 30곳의 평가 샌드박스, 기술·SaaS 기업과 고객 테넌트, 항공사, 에너지 기업, 노출된 Langflow 서버 경유 운영 DB | 1.0.0 |
| high | `ai-app-security/llm-output-handling` 모델 출력의 렌더링·실행 | code | Microsoft 365 Copilot, Salesforce Agentforce | 1.0.0 |

## AI 개발 도구·에이전트 환경 (`ai-dev-tooling`)

개발자 PC의 AI 코딩 에이전트·MCP 서버·IDE 확장이 악용되거나, AI가 환각한 패키지명 선점(slopsquatting)·악성 MCP 서버로 비밀과 코드가 빠져나간 경우.

사건: GitHub MCP 서버 사용자(2025-05), Amazon Q Developer VS Code 확장(2025-07), Cursor IDE(2025-08), Nx npm 패키지 사용자(2025-08), 비공식 postmark-mcp 사용자(2025-09), 불특정(일부 국가 배후)(2025-11), OpenClaw(자체 호스팅 에이전트 게이트웨이)(2026-01), OpenClaw ClawHub 스킬 마켓(2026-02), Cline npm 릴리스 파이프라인(2026-02), npm 개발자·AI 어시스턴트 사용자(2026-02), LiteLLM(AI 게이트웨이) 사용자(2026-03), CI 코딩 에이전트(Claude Code Security Review, Gemini CLI Action, Copilot Agent)(2026-04), GitHub(2026-05), Binance(2026-10)

| 심각도 | 점검 | 방식 | 근거 사건 | 추가 |
|---|---|---|---|---|
| critical | `ai-dev-tooling/ci-agents-untrusted-input` CI 안의 AI 에이전트와 외부 입력 | config | Cline npm 릴리스 파이프라인, CI 코딩 에이전트(Claude Code Security Review, Gemini CLI Action, Copilot Agent), Nx npm 패키지 사용자 | 1.0.0 |
| high | `ai-dev-tooling/coding-agent-permissions` 코딩 에이전트 권한 설정과 비밀 접근 | config | Nx npm 패키지 사용자, 불특정(일부 국가 배후) | 1.0.0 |
| high | `ai-dev-tooling/mcp-server-allowlist` MCP 서버 허용 목록과 버전 고정 | config | 비공식 postmark-mcp 사용자, npm 개발자·AI 어시스턴트 사용자, Cursor IDE, GitHub MCP 서버 사용자 | 1.0.0 |
| medium | `ai-dev-tooling/ai-suggested-packages-and-skills` AI가 제안한 패키지·에이전트 스킬·플러그인 검증 | process | OpenClaw ClawHub 스킬 마켓 | 1.0.0 |

## 랜섬웨어 대응력·내부 확산 (`ransomware-resilience`)

침입 이후 내부망 측면 이동, 백업 동시 암호화, 망 분리 미흡으로 피해가 서비스 중단까지 커진 경우. 첫 침입 경로는 다른 카테고리에 함께 분류한다.

사건: SK텔레콤(2025-04), Marks & Spencer, Co-op(2025-04), 예스24(2025-06), SGI서울보증(2025-07), Asahi Group(일본)(2025-09), 노출된 Langflow 서버 경유 운영 DB(2026-07)

| 심각도 | 점검 | 방식 | 근거 사건 | 추가 |
|---|---|---|---|---|
| critical | `ransomware-resilience/isolated-backups-and-restore` 격리 백업과 복구 시험 | infra | 예스24, SGI서울보증, 노출된 Langflow 서버 경유 운영 DB, 유럽 정당·언론·싱크탱크 | 1.0.0 |
| high | `ransomware-resilience/segmentation-and-lateral-movement` 내부망 분리와 수평 이동 차단 | infra | SK텔레콤, Asahi Group(일본), Marks & Spencer, Co-op | 1.0.0 |

## 데이터 최소화·파기 (`data-minimization`)

탈퇴·휴면 계정, 옛 시스템 데이터, 임시 파일, 로그·메모리 덤프, 협업 도구 속 신분증처럼 남겨 둘 필요가 없던 데이터가 유출 규모를 키운 경우. 개인정보보호법 파기 의무와 직결.

사건: Tea Dating Advice(2025-07), Salesloft Drift 경유 Salesforce 고객 700곳+(2025-08), Mixpanel → OpenAI API 사용자 등(2025-11), 넷마블(2025-11), 티빙(2026-06), 행정안전부 정부24(어린이포털)(2026-08), 신한·KB국민·하나은행 등 금융사 37곳(2026-09), 맑은소프트(LMS 수탁사)와 고객사 20여 곳(2026-09), 빗썸(2026-10), 할리스(2026-10)

| 심각도 | 점검 | 방식 | 근거 사건 | 추가 |
|---|---|---|---|---|
| high | `data-minimization/retention-and-disposal` 탈퇴·휴면·옛 시스템 데이터와 임시 파일 파기 | code | 티빙, 넷마블, 맑은소프트(LMS 수탁사)와 고객사 20여 곳, 할리스, Tea Dating Advice | 1.0.0 |
| high | `data-minimization/sensitive-data-in-logs-and-dumps` 로그·메모리 덤프·에러 응답 속 개인정보와 비밀 | code | 행정안전부 정부24(어린이포털), 신한·KB국민·하나은행 등 금융사 37곳 | 1.0.0 |
| medium | `data-minimization/sensitive-data-in-third-parties-and-tools` 분석 SDK·협업 도구로 흘러간 민감 데이터 | code | Mixpanel → OpenAI API 사용자 등, 빗썸, Salesloft Drift 경유 Salesforce 고객 700곳+ | 1.0.0 |

## 탐지·로깅·신고 (`detection-response`)

로그 부재·보존 기간 부족, 이상 징후 미탐지로 수개월 뒤 발견되거나, 법정 신고 기한(정보통신망법 24시간, 개인정보보호법 72시간)을 놓친 경우.

사건: GS리테일(GS25·GS SHOP)(2025-01), SK텔레콤(2025-04), Coinbase(2025-05), 디올·티파니·루이비통 코리아(2025-05), Salesforce 고객사 다수(Google, Qantas, Allianz Life 등)(2025-06), 예스24(2025-06), LG유플러스(2025-08), KT(2025-09), 롯데카드(2025-09), F5(2025-10), 행정안전부(온나라·GVPN)(2025-10), 쿠팡(2025-11), 넷마블(2025-11), Cisco Catalyst SD-WAN 사용 기관(2026-02), Odido(네덜란드 통신사)(2026-02), European Commission(2026-03), Charter Communications(Spectrum)(2026-05), 행정안전부 정부24(어린이포털)(2026-08), 신한·KB국민·하나은행 등 금융사 37곳(2026-09), 대한항공·아시아나항공(Amadeus 경유)(2026-10)

| 심각도 | 점검 | 방식 | 근거 사건 | 추가 |
|---|---|---|---|---|
| high | `detection-response/anomalous-access-alerting` 대량 조회·비정상 접근 탐지와 알림 | infra | 쿠팡, GS리테일(GS25·GS SHOP), Salesforce 고객사 다수(Google, Qantas, Allianz Life 등), Charter Communications(Spectrum), Coinbase, European Commission, Cisco Catalyst SD-WAN 사용 기관, F5, 신한·KB국민·하나은행 등 금융사 37곳 | 1.0.0 |
| high | `detection-response/security-log-coverage-and-retention` 보안 로그 범위와 보존 기간 | config | KT, SK텔레콤, 행정안전부(온나라·GVPN), 대한항공·아시아나항공(Amadeus 경유), 디올·티파니·루이비통 코리아 | 1.0.0 |
| medium | `detection-response/breach-notification-runbook` 침해 신고·통지 런북과 증거 보존 | process | KT, LG유플러스, SK텔레콤, 디올·티파니·루이비통 코리아, 행정안전부 정부24(어린이포털) | 1.0.0 |
