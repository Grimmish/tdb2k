# Various notes
## NRF24 sentences [Arduino <-> ODroid]
| Byte 0 | Domain |
| --- | --- |
| B | Button event |
| I | IR beam event |
| D | Display payload |

| Byte 1 | Sub-domain |
| --- | --- |
| B | Button ID: character |
| I | Transceiver ID: character |
| D | Red or green channel: 'R' or 'G' |

| Bytes 2-31 |Payload |
| --- | --- |
| B | Button state: '1' (depressed) or '0' (release) |
| I | IR beam state: '1' (broken) or '0' (steady) |
| D | 16 bytes - on/off values for 16x8 grid:<br>1. Left-to-right<br>2. Top-to-bottom
