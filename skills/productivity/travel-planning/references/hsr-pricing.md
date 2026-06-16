# HSR Pricing Reference (高铁票价参考)

## Standard Pricing Formulae (二等座, G-trains)

G-train 二等座 pricing in China follows a consistent formula:
- **~0.46-0.50 元 per route-km** (varies slightly by line operator)
- Safe estimate: `票价 ≈ 里程 × 0.47` (round to nearest 10元)
- G 一等座 ≈ 1.6× 二等座
- D 动车 二等座 ≈ 0.66× G-train rate (~0.31 元/km)
- K/T 普速 硬座 ≈ 0.12-0.15 元/km

## Station Codes (12306)

| City | Station | Code |
|------|---------|------|
| 天津 | 天津站 | TJP |
| 天津 | 天津西 | TXP |
| 天津 | 天津南 | TIP |
| 天津 | 天津北 | TBP |
| 武汉 | 武汉站 | WHN |
| 武汉 | 汉口站 | HKN |
| 武汉 | 武昌站 | WSN |
| 连云港 | 连云港站 | UIH |
| 徐州 | 徐州东 | EXF |
| 济南 | 济南西 | JGK |
| 郑州 | 郑州东 | ZAF |
| 北京 | 北京南 | VNP |
| 上海 | 上海虹桥 | AOH |
| 南京 | 南京南 | NKH |
| 长沙 | 长沙南 | CWQ |
| 重庆 | 重庆北 | CUW |
| 成都 | 成都东 | ICW |
| 昆明 | 昆明南 | KOM |
| 贵阳 | 贵阳北 | KQW |
| 大理 | 大理 | DAP |
| 丽江 | 丽江 | LJM |

## Sample Route Prices

Based on G-train ~0.47 元/km formula:

| Route | Est. Rail km | Est. 二等座 | Est. 一等座 | Actual Range |
|-------|-------------|-----------|-----------|-------------|
| 天津西→武汉 | ~1,060 | ~500 | ~800 | 488-520 |
| 天津→连云港 | ~520 | ~245 | ~390 | 230-255 |
| 连云港→武汉 | ~700 | ~330 | ~530 | 320-360 |
| 天津→连云港→武汉(合计) | ~1,220 | ~575 | ~920 | 570-600 |
| 北京南→上海虹桥 | ~1,310 | ~615 | ~990 | 553-625 |
| 北京南→南京南 | ~1,020 | ~480 | ~770 | 443-510 |
| 南京南→上海虹桥 | ~300 | ~140 | ~230 | 135-145 |
| 武汉→广州南 | ~1,070 | ~500 | ~800 | 463-540 |
| 郑州东→武汉 | ~530 | ~250 | ~400 | 243-260 |
| 徐州东→连云港 | ~180 | ~85 | ~135 | 84-90 |
| 徐州东→天津西 | ~660 | ~310 | ~500 | 285-315 |

## Historical 12306 API Behavior

- `kyfw.12306.cn/otn/leftTicket/queryZ` returns JSON when accessed with a valid JSESSIONID cookie
- Without session: returns HTML error page ("网络可能存在问题")
- Query params: `leftTicketDTO.train_date=YYYY-MM-DD&leftTicketDTO.from_station=XXX&leftTicketDTO.to_station=YYY&purpose_codes=ADULT`
- Response format: `result` array of pipe-delimited strings; field indices vary by API version
- Known field positions (approximate): [3]=车次, [6]=出发站, [7]=到站, [8]=发时, [9]=到时, [10]=历时, [30]=二等座余票, [31]=一等座余票
- Station code list: `kyfw.12306.cn/otn/resources/js/framework/station_name.js` (comma-separated, pipe-delimited entries)
