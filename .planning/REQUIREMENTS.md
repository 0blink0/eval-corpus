# Requirements: 鏂囨。瑙ｆ瀽宸ュ叿鍒嗗潡鎸囨爣瀵规瘮瀹為獙

**Defined:** 2026-04-13  
**Core Value:** 鍚屼竴濂楀垎鍧椾笌璇勬祴鍙ｅ緞涓嬪姣?PaddleOCR銆丟LM-OCR銆丮inerU 鐨勫垎鍧楄川閲忥紝浜у嚭鍙鐜扮殑瀵规瘮琛ㄤ笌鍒嗛」缁撴灉銆?
## v1 Requirements

### 璇枡涓庨厤缃?(CORP)

- [x] **CORP-01**: 瀹為獙鍙€氳繃閰嶇疆锛圕LI 鍙傛暟鎴栫幆澧冨彉閲忥級鎸囧畾璇枡鏍圭洰褰曪紝榛樿鏂囨。涓害瀹氭敮鎸?**鍖楃噧鐑姏瀹ｄ紶鍝侀噰璐綊妗ｈ祫鏂?* 鐨勫疄闄呰矾寰?- [x] **CORP-02**: 鐢熸垚璇枡娓呭崟锛堟枃浠惰矾寰勩€佹牸寮忋€侀〉鏁?澶у皬鍝堝笇鍙€夛級锛岃繍琛屽墠鏍￠獙鍙
- [x] **CORP-03**: 鎻愪緵銆岄粍閲戠粺璁°€嶈緭鍑猴細鍘熸枃瀛楃鏁般€佽〃鏍兼暟閲忥紙鑻ュ彲妫€娴嬶級銆侀〉鏁扮瓑锛屼緵瑕嗙洊瀹屾暣鐜囦笌琛ㄦ牸淇濇寔鐜囧垎姣嶄娇鐢?
### 缁熶竴琛ㄧず涓庡垎鍧?(CHUNK)

- [x] **CHUNK-01**: 瀹氫箟骞跺疄鐜扮粺涓€涓棿琛ㄧず `ParsedBlock`锛堢被鍨嬨€佹枃鏈?琛ㄦ牸搴忓垪鍖栥€侀〉鐮併€佹爣棰樿矾寰勶級
- [x] **CHUNK-02**: 瀹炵幇缁熶竴鍒嗗潡鍣細鐩爣鍧楅暱 300鈥?000 瀛楃銆佽〃鏍间紭鍏堝師瀛愬潡銆佸彞鐣屼紭鍏堝垏鍒嗐€佸彲閰嶇疆閲嶅彔 10鈥?0%锛堥粯璁?15% 浜庢枃鏈潡锛?- [x] **CHUNK-03**: 鍚屼竴鍒嗗潡鍣ㄥ涓夊宸ュ叿褰掍竴鍚庣殑 `ParsedBlock[]` 鎵ц锛屼繚璇佸姣斿叕骞?
### 宸ュ叿閫傞厤 (ADPT)

- [ ] **ADPT-01**: PaddleOCR 閾捐矾锛氫粠璇枡鍒?`ParsedBlock[]` 鐨勫彲杩愯閫傞厤锛堢増鏈笌渚濊禆鍐欏叆 README/lock锛?- [ ] **ADPT-02**: GLM-OCR 閾捐矾锛氬悓涓?- [ ] **ADPT-03**: MinerU 閾捐矾锛氬悓涓?
### 鎸囨爣璁＄畻 (METR)

- [ ] **METR-01**: **瑕嗙洊瀹屾暣鐜?*锛氬垎鍧楄繕鍘熸枃鏈笌鍘熸彁鍙栧叏鏂囬暱搴︽瘮鍙婄己澶辫瘖鏂?- [ ] **METR-02**: **鍧楅暱搴﹁揪鏍囩巼**锛?00鈥?000 瀛楃鍗犳瘮缁熻
- [ ] **METR-03**: **杈圭晫鍑嗙‘鐜?* / 纭垏姣斾緥锛氳竟鐣岃惤鍦ㄥ彞鏈?娈垫湯 vs 纭垏
- [ ] **METR-04**: **琛ㄦ牸淇濇寔鐜?*锛氬畬鏁磋〃鏍煎潡鏁?/ 鍘熻〃鏍兼暟锛堝師琛ㄦ牸鏁版潵鑷綊涓€闃舵鏍囨敞锛?- [ ] **METR-05**: **閲嶅彔鍚堢悊鐜?*锛氱浉閭绘枃鏈潡閲嶅彔姣斾緥钀藉湪 10鈥?0% 鐨勫崰姣?- [ ] **METR-06**: **鍏冩暟鎹畬鏁寸巼**锛歝hunk 鍚屾椂鍏峰椤电爜涓庢爣棰樿矾寰勶紙鎴栧彲瑙ｉ噴缂哄け鍘熷洜锛夌殑鍗犳瘮
- [ ] **METR-07**: **璇箟瀹屾暣鐜?*锛氭寜 PROJECT 绾﹀畾鎵ц锛堣鍒欒繎浼?+ 鍙鐜版娊妫€鑴氭湰锛屾敮鎸佹帴鍏?LLM-as-Judge 鍙€夛級

### 鎶ュ憡涓庝骇鐗?(RPT)

- [ ] **RPT-01**: 鐢熸垚**鎬诲姣旇〃**锛堜笁宸ュ叿 脳 涓冩寚鏍囷紝闄勭洰鏍囬槇鍊煎垪锛?- [ ] **RPT-02**: 鐢熸垚**姣忓伐鍏锋槑缁?*锛堝師濮嬫寚鏍?JSON/CSV + Markdown 鎴?HTML 鎽樿锛?- [ ] **RPT-03**: 鍗曟杩愯鍐欏叆鏃堕棿鎴炽€佸伐鍏风増鏈€丟it commit锛堣嫢鏈夛級锛屼繚璇佸彲杩芥函

### 娴嬭瘯鏁版嵁涓庤妯″寲 (DATA)

- [ ] **DATA-01**: 鎻愪緵鍚堟垚鎴栧皬鏍锋湰鐢熸垚鍣紝鐢ㄤ簬鏃犵湡鏂欐椂鐨勫洖褰掍笌 CI 鐑熸祴
- [ ] **DATA-02**: 鏀寔鎵瑰鐞嗘ā寮忥紙鐩綍閫掑綊锛夛紝渚夸簬浜戜富鏈轰笂鎵╄窇

## v2 Requirements

### 鑷姩鍖栧寮?
- **AUTO-01**: 涓€閿?Docker/Poetry 闀滃儚閿佸畾鍚勮В鏋愪緷璧?- **AUTO-02**: 涓?搂2 妫€绱㈡寚鏍囨墦閫氱殑瀵煎嚭鏍煎紡锛坈hunk 鍏冩暟鎹吋瀹瑰悜閲忓簱锛?
## Out of Scope

| Feature | Reason |
|---------|--------|
| 瀹屾暣瀹℃煡骞冲彴涓氬姟 | 瑙?PROJECT.md锛涙湰瀹為獙浠呬负瑙ｆ瀽+鍒嗗潡璇勬祴 |
| 搂2鈥撀? 鍏ㄩ噺鎸囨爣 | 鏈疆鑱氱劍 搂1锛涘叾浣欏彟绔嬮」 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CORP-01 | Phase 1 | Done |
| CORP-02 | Phase 1 | Done |
| CORP-03 | Phase 1 | Done |
| CHUNK-01 | Phase 2 | Done |
| CHUNK-02 | Phase 2 | Done |
| CHUNK-03 | Phase 2 | Done |
| ADPT-01 | Phase 3 | Pending |
| ADPT-02 | Phase 3 | Pending |
| ADPT-03 | Phase 3 | Pending |
| METR-01 | Phase 4 | Pending |
| METR-02 | Phase 4 | Pending |
| METR-03 | Phase 4 | Pending |
| METR-04 | Phase 4 | Pending |
| METR-05 | Phase 4 | Pending |
| METR-06 | Phase 4 | Pending |
| METR-07 | Phase 4 | Pending |
| RPT-01 | Phase 5 | Pending |
| RPT-02 | Phase 5 | Pending |
| RPT-03 | Phase 5 | Pending |
| DATA-01 | Phase 5 | Pending |
| DATA-02 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0 鉁?
---
*Requirements defined: 2026-04-13*  
*Last updated: 2026-04-13 after initial definition*

