---
name: travel-planning
description: Multi-city travel itinerary planning with high-speed rail constraints — day-by-day breakdowns, route visualization, accommodation/food tips, and iterative city selection.
version: 1.0.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [travel, itinerary, route-planning, high-speed-rail, china-travel, logistics]
    category: productivity
    requires_toolsets: []
    supersedes: []
---

# Travel Planning Skill

Class-level skill for planning multi-city, multi-leg travel itineraries in China, primarily using high-speed rail (高铁).

## When to Use

- User asks for a travel route between two or more cities
- User wants day-by-day itinerary with transport, sightseeing, accommodations
- User needs to optimize a route with time/distance constraints
- User wants alternative city suggestions after ruling out certain destinations
- **User has an existing itinerary file and wants to add/remove/replace a city** (modify existing plan)
- **User wants a side trip that branches off the main route** (hub-and-spoke)

## Core Workflow

### 1. Gather Constraints First

Before proposing anything, establish the non-negotiables:

| Constraint | Examples |
|------------|----------|
| Travel dates | 6.1 到昆明, 6.10 必须到连云港 |
| Fixed stops | "先去大理丽江" |
| Excluded cities | "长沙南京我都去过了" |
| Travel mode | 高铁 / 飞机 |
| Group composition | 情侣 / 家庭 / 单人 |
| Budget tier | 穷游 / 舒适 / 奢华 |

### 2. Map the High-Speed Rail Network

Key hub cities for cross-country routes (approximate G-train times):

```
丽江→大理(1.5h)→昆明(2h)
昆明→贵阳(2h)
贵阳→长沙(3h)
贵阳→重庆(2h)
贵阳→成都(3h)
长沙→武汉(1.5h)
武汉→郑州(2h)
郑州→徐州(1.5h)
徐州→连云港(1h)
徐州→天津(2.5h)
武汉→济南(4h)
济南→天津(1h)
济南→连云港(2.5h)
长沙→南昌(1.5h)→合肥(2h)→南京(1h)
南京→连云港(2.5h)
```

Natural split points for couples returning to different cities (e.g. 天津 + 连云港):
- **徐州东站** — 她去连云港(1h), 他去天津(2.5h) ← 最优
- **济南西站** — 她去连云港(2.5h), 他去天津(1h)
- **郑州东站** — 她去连云港(3h+), 他去天津(2.5h)

### 3. Output Format

Always structure responses in this order:

**Phase layout:** Split into logical phases (e.g. "云南段" / "返程段")

Each day's entry must include:

| Element | Required? |
|---------|-----------|
| Date + weekday | ✅ Always |
| Morning plan | ✅ |
| Afternoon plan | ✅ |
| Evening plan | ✅ |
| Where to stay | ✅ |
| What to eat (local specialties) | ✅ |
| Transport legs with durations | ✅ |
| ⚠️ Warnings (ticket booking, weather, scams) | ✅ if applicable |

**Visual route diagram** (ASCII-style):
```
昆明(2h)→大理(1.5h)→丽江 → 贵阳(2h) → 武汉(4h) → 徐州(3.5h)
                                                       ↘ 她：连云港(1h)
                                                       ↘ 你：天津(2.5h)
```

### 4. Handling User Corrections

When user says "XX城市我去过了":

1. Immediately acknowledge and remove from consideration
2. Propose 2-3 alternative route options using different hub cities
3. Show each option in a comparison table (days, comfort level, uniqueness)
4. Give a clear recommendation with rationale

### 5. Iterative Refinement

After presenting a full itinerary:

- If user asks "先规划XX段", focus on that phase with detailed daily breakdowns
- Offer flexible durations (e.g. "丽江可住2-4天，看你兴趣")
- Always include the "如果时间紧/时间充裕" variants

### 6. 极化 Extreme Value Optimization (省钱+玩好)

When user says "省钱又能玩好" or asks for a "极化" itinerary along a corridor:

**Concept:** Sacrifice the least-valuable stop to maximize the ratio of experience quality to cost. On high-speed rail corridors where every leg is 30-40min, the marginal cost of stopping is just the hotel + meal (~150元), and the marginal gain can be a world-class sight.

**Decision heuristic:**
1. List all potential stops along the corridor, sorted by "世界遗产 / 国家5A级 / 独特性"
2. Compute 性价比 = 门票价÷体验价值 (low-cost high-value wins)
3. Pick 1-3 stops max — more than that turns into赶路
4. For each stop, estimate the **额外花费** (extra cost beyond direct transit):
   - 高铁短途票差价: ~40-80元 per leg
   - 住宿: ~100-150元 (快捷酒店)
   - 吃饭: ~30-50元
   - 门票: varies
5. Present as "总花费额外约XXX元" to show incremental cost

**Common 极化 corridors:**
- 郑州→天津：安阳（殷墟70元+文字馆免费）→ 保定（直隶总督署30元）→ 白洋淀（船票80元）
- 昆明→丽江：大理（洱海骑行免费）> 香格里拉（松赞林寺+普达措）> 丽江（雪山门票贵）
- See `references/china-hsr-routes.md` for detailed 极化 stop plans

### 7. Modifying Existing Itineraries (Adding/Removing Cities)

When user asks to add a new city to an **existing** itinerary plan (e.g. "加上香格里拉"):

**Workflow:**

1. **Read the existing plan file first** — search for it in the user's documents directory. Common naming patterns include `<地名>行程_<日期范围>.md` or `<地名>行详细计划表_<日期范围>.md`.

2. **Assess geography** — locate the new city relative to the current route. Determine if it's:
   - **Linear extension** (e.g. add a city at the end of the route → just extend)
   - **Inline insertion** (e.g. insert between two existing stops → reshuffle days)
   - **Hub-and-spoke / side trip** (e.g. go from hub → spoke → return to hub → continue)

3. **Identify squeeze points** — with a fixed time budget, something must give. Common squeeze strategies:
   - **Compress leisure/redundant days** (e.g. 2-night stay → 1-night, merge free days)
   - **Trim the least-unique attraction** from an existing city
   - **Rearrange day activities** to arrive/leave earlier/later

4. **Preserve total nights when possible** — try to keep total lodging nights the same by shifting, not adding.

5. **Always verify the return constraint** — if the trip ends with a flight from a specific city, ensure the new addition doesn't strand the user away from their departure airport.

6. **Write back to the same file path** — update in place, don't create a new file. The user's path is canonical.

**Pitfalls:**
- Don't propose extending the trip length unless the user explicitly offers flexibility ("时间自有安排" means they trust you to fit it in, not that you can add days)
- When compressing, be explicit about what was cut and why (show a before/after table)
- Side trips that require returning to the hub add 2× transit time — factor that into the day budget

### 8. Hub-and-Spoke / Side Trip Patterns

When a destination is **not on the main linear route** and requires going out and back:

**Pattern recognition:**
```
Main route:    A → B → C → D
Side trip:     C → X → C (then continue to D)
```

**Key logistics for spoke destinations:**
- **Return cost:** Travel time is 2× (out + back). A "3小时" bus means 6 hours total transit that day
- **Luggage:** Best to leave luggage at the hub city hotel and take only a small bag/overnight pack to the spoke
- **Altitude transitions:** Note when the spoke is significantly higher/lower than the hub (e.g. Lijiang 2400m → Shangri-La 3300m)
- **Return deadline:** The return leg must arrive back at the hub early enough to not jeopardize the next day's departure (especially flights)

**When to recommend a spoke vs. linear reroute:**
- Spoke (out-and-back) is better when: the detour is short (1-2h each way), the spoke city is small and needs only 1 night, the hub city has the flight/transport hub
- Linear reroute (reorder cities) is better when: the spoke is 4+ hours away, you can reorder the route to pass through naturally, the return flight is from the spoke city

**Common spoke pairs (云南):**
| Hub | Spoke | Travel time | Nights needed |
|-----|-------|-------------|---------------|
| 丽江 (2400m) | 香格里拉 (3300m) | 大巴3h | 1-2晚 |
| 大理 | 沙溪古镇 | 大巴2h | 1晚 |
| 昆明 | 抚仙湖 | 大巴1.5h | 1晚 |

## Content Ingredients Per City

| City | Must-include | Food picks |
|------|-------------|------------|
| 昆明 | 斗南花市(晚上去)、翠湖、滇池 | 过桥米线、菌子火锅 |
| 大理 | 洱海骑行(喜洲→双廊)、古城城楼日落 | 烤乳扇、凉鸡米线、酸辣鱼 |
| 丽江 | 玉龙雪山(需抢票/跟团,详见references/yulong-snow-mountain.md)、蓝月谷、古城夜景、束河古镇、白沙古镇 | 腊排骨、土鸡米线、鸡豆凉粉 |
| **香格里拉** (3300m) | **松赞林寺(小布达拉宫,门票~90元)、普达措国家公园(属都湖木栈道1.5h,~138元)、独克宗古城+世界最大转经筒(免费)、纳帕海(草原/湿地,可骑行)** | **酥油茶、牦牛肉火锅、青稞饼、糌粑** |
| 贵阳 | 甲秀楼夜景、黔灵山 | 酸汤鱼、肠旺面、丝娃娃 |
| 武汉 | 东湖骑行、长江轮渡、粮道街过早 | 热干面、鸭脖、小龙虾、豆皮 |
| 重庆 | 洪崖洞、长江索道、南山夜景 | 火锅、小面、江湖菜 |
| 成都 | 大熊猫基地、宽窄巷子、人民公园 | 火锅、串串、兔头 |
| **安阳** | **殷墟(70元,世界遗产)、中国文字博物馆(免费)** | **扁粉菜、道口烧鸡** |
| **保定** | **直隶总督署(30元)、古莲花池(10元)** | **驴肉火烧** |
| **白洋淀** | **游船穿芦苇荡(6月荷花季,船票~80元)** | **全鱼宴** |

## Route Cost Comparison (高铁票价估算)

When user asks which route is cheaper/faster — direct vs. multi-leg (e.g. 天津→武汉 vs 天津→连云港→武汉):

### Pricing Formula

| Seat Class | Price per km | Notes |
|------------|-------------|-------|
| G 二等座 | ~0.46-0.50 元/km | Uniform across most G lines |
| G 一等座 | ~0.74-0.80 元/km | ~1.6x 二等座 |
| D 二等座 | ~0.31-0.37 元/km | 动车, ~30% cheaper than G |
| K/T 硬座 | ~0.12-0.15 元/km | 普速列车 |

Approximate rail distances for common comparisons (can also compute via OSRM driving distance as rough proxy):

| Comparison Scenario | Direct Distance | Via-City Distance Sum |
|--------------------|----------------|----------------------|
| 天津↔武汉 vs 天津→连云港→武汉 | ~1,060 km | ~520+700=1,220 km |
| 北京↔上海 vs 北京→南京→上海 | ~1,300 km | ~1,000+300=1,300 km (接近) |

### Comparison Table Format

Always present a direct-vs-multi-leg comparison in this format:

```
直达：A → B
  里程：~X km | 二等座：~Y 元 | 耗时：~Z h | 换乘：0次

绕道：A → C → B
  ① A→C：~X1 km / ~Y1 元 / ~Z1 h
  ② C→B：~X2 km / ~Y2 元 / ~Z2 h
  合计：~(X1+X2) km / ~(Y1+Y2) 元 / ~(Z1+Z2) h | 换乘：1次

差价对比：
  票价：绕道贵约△元（+~N%）
  时间：绕道多花△h
```

### Price Calculation Procedure

1. Estimate rail distance (use known data or OSRM driving distance as rough proxy)
2. Multiply by rate: `二等座票价 ≈ 里程 × 0.47`
3. Round to nearest 10 元
4. If actual price data is available from 12306 or recent query, prefer that over formula

### 12306 API Notes (read-only queries)

12306's public API (`kyfw.12306.cn/otn/leftTicket/queryZ`) is **not accessible** without a valid session cookie. Attempts return HTML error pages ("网络可能存在问题"). Do NOT rely on raw curl to 12306 — use known pricing data or alternative sources.

**Station codes** (useful for building query URLs if session available):

```
天津 = TJP   天津西 = TXP   天津南 = TIP
武汉 = WHN   武汉站 = WHN   汉口 = HKN   武昌 = WSN
连云港 = UIH  徐州东 = EXF  济南西 = JGK  郑州东 = ZAF
北京南 = VNP  上海虹桥 = AOH  南京南 = NKH
```

## Pitfalls

- **门票提醒：** 玉龙雪山索道票需提前3天晚8点抢，旺季极难。强烈建议推荐纯玩一日团(350-500元含票)，详细攻略见 references/yulong-snow-mountain.md
- **雨季：** 6月开始云南进入雨季，备伞和薄外套
- **住宿选址：** 丽江/大理古城内石板路拖箱子痛苦，建议住古城边/南门附近
- **防晒：** 云南紫外线强，提醒用户
- **海拔跃迁：** 丽江→香格里拉海拔从2400m升至3300m，相差近1000m。务必提醒高反应对：到香格里拉后勿剧烈运动、备氧气罐、注意保暖(6月夜间仅10℃)。雪山上买的氧气罐别扔，带去香格里拉还能用
- **高铁抢票：** 12306提前订，尤其是节假日/周末热门路线
- **不要在第一次方案里假设用户去过所有城市** — 提出方案时先问「去过哪些城市」，或一次性给2-3个选项

## Verification & Persistence

When user confirms a plan (new itinerary), produce a condensed summary AND save the full itinerary as a file. **When modifying an existing plan, update the file in place instead.**

**Step 1 — Condensed summary to display:**
```
总天数：X天
交通：全程高铁，总耗时约X小时
总预算预估：约XXXX元/人（含住宿+门票+餐饮+交通）
分手点：徐州东站（她→连云港1h / 你→天津2.5h）
```

**Step 2 — Save/update full itinerary to file:**
Write the complete day-by-day itinerary to the user's documents directory. For a **new** plan, create a new file. For an **existing** plan being modified, **update the same file in place** (the user's original path is canonical).

- New plan path: `/opt/data/青桑/文档/<地名>行程_<日期范围>.md`
- Existing plan: read the file, overwrite with updated content at the same path
- Include: all days, transport times, accommodation, food recommendations, warnings, and a **"调整说明" (changes summary) section** showing what was changed from the original
- This ensures the user can request the itinerary again in a future session without re-planning
