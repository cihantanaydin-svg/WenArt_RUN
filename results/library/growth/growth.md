# Library growth, pod P4

docs/milestone12.md §6.4; user OK of 11 Oct 2026 (four lists).

| source | approved | downloaded / generated | GSO licence kept | converted | catalogued | dropped | keep | fix | removed | pending |
|---|---|---|---|---|---|---|---|---|---|---|
| polyhaven | 88 | 87 |  |  | 87 | 1 | 69 | 1 | 17 | 0 |
| abo | 232 | 232 |  |  | 202 | 30 | 195 | 1 | 6 | 0 |
| gso | 36 | 36 | 36 | 36 | 36 | 0 | 31 | 0 | 5 | 0 |
| infinigen | 30 | 30 |  | 30 | 27 | 0 | 15 | 2 | 10 | 0 |

Infinigen: tag v1.19.0 = commit 01c39c7f7adcf7363ccbcc57c64410c69f4a4e7c; 274 factories listed; jobs {'done': 30}; missing factories: none; setup: {"ok": true, "commit": "01c39c7f7adcf7363ccbcc57c64410c69f4a4e7c", "tag": "v1.19.0", "python": "3.11.16", "bpy": "4.2.0", "uv": "0.12.18", "seconds": 268, "submodules": {"infinigen/infinigen_gpl": {"commit": "10c1d76f5c35003e919be7265185c9c355e3b70c", "licence": "GPL-3.0 (run on the pod only)"}, "infinigen/OcMesher": {"commit": "bb895a01b8f574da10be1df470210df7463a75c7", "licence": "BSD-3-Clause"}}}.

## Dropped (not catalogued)

| source | id | reason |
|---|---|---|
| polyhaven | decorative_book_set_01 | not downloaded: KeyError: 'Poly Haven file table has no gltf/1k (available: [])' |
| abo | abo_B075QBL1TB | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B075QJDGPN | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B075QMGMYP | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B075X2CVQK | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07B4SCPNQ | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07B4W235R | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07B4W5TDF | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07B4YC7LD | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07B4YXRH1 | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07B4ZGB6K | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07B4ZQQPR | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07DVRNRCW | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07GFFQZQ1 | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07H8SMDMT | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07H8T39V6 | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07KSJRMC6 | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07KSRKDXF | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07M7MMYCL | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07M7MMYDR | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07M7MN85B | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07MCBKLXJ | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07MCBKT23 | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07MCCRNLV | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07MCCRP2G | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07MCCRYSR | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07MCCSGS1 | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07MCCSGT9 | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07MJL66BL | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07MQD1ZZD | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |
| abo | abo_B07MQD22K6 | no catalogue type for headboard (downloaded, kept on the volume; headboards wait for a bed-frame type) |

## Steps

| step | rc | seconds |
|---|---|---|
| ingest-gso | 0 | 14 |
| gso-licence | 0 | 12 |
| convert-gso | 0 | 21 |
| ingest-polyhaven | 1 | 113 |
| ingest-abo | 0 | 113 |
| catalogue | 0 | 39 |
| render-a | 0 | 465 |
| infinigen | 0 | 1012 |
| convert-infinigen | 0 | 57 |
| catalogue-b | 0 | 12 |
| render-b | 0 | 135 |
| code | 0 | 7 |
| setup-check | 0 | 1241 |
| ask | 0 | 630 |
| decide | 0 | 1 |
| write | 0 | 0 |
| vision-fields | 0 | 1 |
| pending | 0 | 1 |
| sheets | 0 | 5 |
| gaps | 0 | 0 |
| preview | 0 | 17 |
| report | 0 | 0 |
| gpu-tests | 1 | 20 |
