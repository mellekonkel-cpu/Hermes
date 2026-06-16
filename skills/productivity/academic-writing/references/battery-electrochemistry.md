# Battery Electrochemistry — Full CV/dQ/dV/GITT Reference

## CV Peak Mechanism (Layman's Explanation)

**Analogy**: Delivery service — voltage = accelerator, reactants = ingredients at surface.

1. Voltage crosses threshold → surface fully stocked → current surges
2. Surface reactants consumed, deeper supply hasn't diffused yet → supply-demand imbalance
3. Current peaks at the inflection point, then decay under diffusion control

**Peak = reaction drive pushing supply to exhaustion.**

## CV Key Parameters

| Parameter | What it tells you |
|-----------|-------------------|
| Anodic peak potential | Oxidation voltage of specific material/additive |
| Cathodic peak potential | Reduction voltage |
| ΔEp = Epa − Epc | Reversibility: ~57/n mV (reversible) → larger (irreversible/polarized) |
| ipa/ipc ratio | ~1 = reversible; deviates = side reactions or kinetic asymmetry |
| Multi-cycle peak decay | Film formation quality: decay = stable SEI/CEI |

## dQ/dV Peak Assignment (Li-rich Mn-based Cathode)

| Potential | Process | Notes |
|-----------|---------|-------|
| ~3.7–4.0V (charge) | Ni²⁺→Ni⁴⁺ | Conventional layered capacity |
| ~4.1–4.2V (charge) | Mn³⁺→Mn⁴⁺ | Some systems |
| ~4.5–4.8V (charge, 1st cycle) | Li₂MnO₃ activation | Irreversible; O₂ release; high capacity source |
| ~3.3–3.5V (discharge) | Mn⁴⁺→Mn³⁺ | |
| ~2.8–3.0V (discharge) | Ni⁴⁺→Ni²⁺ | |

## Degradation Indicators from dQ/dV

| Feature | Meaning |
|---------|---------|
| Peak intensity fade | Capacity loss |
| Peak shift (increased polarization) | Impedance growth, film thickening |
| Peak splitting / new peaks | Irreversible phase transition (layered→spinel) |
| Small peaks at ~3.0–3.5V charge | Additive reduction — SEI formation |
| Small peaks at ~4.5V+ charge | Electrolyte oxidation — if suppressed by additive, CEI is working |

## Additive Effect Interpretation Templates

| Observation | Interpretation | Academic Phrase |
|-------------|---------------|-----------------|
| Oxidation peak shifts higher / weakens | CEI suppresses electrolyte decomposition | "添加剂构筑的CEI有效抑制了电解液在高压下的持续氧化分解" |
| New reduction peak appears | Additive preferentially reduces | "添加剂优先于溶剂还原分解，构筑SEI" |
| ΔEp decreases | Lower interfacial polarization | "添加剂降低了界面极化，提升了反应可逆性" |
| Overlap of redox peaks improves | Better reversibility | "氧化还原峰高度重合，表明界面反应动力学显著改善" |

## Dual-Additive Compatibility Reasoning (PFPN + TMSB / LiDFOB + TMSN)

When reviewer asks whether two additives with high reactivity interfere with each other, use this three-layer argument:

### Layer 1: Reactivity Type Separation

| Additive | Reactivity Origin | Reaction Type | Active Site |
|----------|-----------------|---------------|-------------|
| PFPN | P=N bond polarity (P electrophilic) | **Reduction** (LUMO low) | **Anode** — preferential reduction at low potential |
| TMSB | B-O-Si bond cleavage | **Oxidation** (HOMO highest) | **Cathode** — preferential oxidation at high potential |
| LiDFOB | B-O/oxalate decomposition | **Oxidation** (HOMO highest among BLSN) | **Cathode** — constructs borate framework |
| TMSN | Si-N bond HF-scavenging | **Oxidation + chemical** (HOMO second) | **Cathode + solution** — introduces N/Si species |

Key insight: **One reduces at anode (low E), one oxidizes at cathode (high E)** — reaction potential windows do not overlap.

### Layer 2: No Thermodynamic Driving Force for Mutual Reaction

- **Frontier orbital mismatch**: PFPN (low LUMO) wants electrons → finds them at anode surface. TMSB (high HOMO) loses electrons → finds holes at cathode surface. Neither has a reason to react with the other in the bulk electrolyte.
- **Spatial separation**: Reduction happens at the anode/separator interface; oxidation at the cathode interface. The two additives don't "meet" in solution under working conditions.

### Layer 3: Experimental Evidence

If additives consumed each other in bulk electrolyte, you would observe:
- Capacity retention collapse (protective film not formed)
- Flame retardancy loss (PFPN consumed)

Direct experimental counter-evidence:
- FDPT system: 200 cycles at 4.8 V/0.5 C with 91.1% retention **+** passed burn test → both additives functional and coexisting

### Answer Template (Defense-Ready Academic Chinese)

> PFPN 与 TMSB 的活性确实较高，但两者的反应类型完全不同。PFPN 因 P=N 键的高极性而具有较低的 LUMO 能级（-0.68 eV），在低电位下发生还原反应，优先在**负极**成膜；TMSB 的 HOMO 能级最高（-7.81 eV），在高电位下发生氧化反应，优先在**正极**构建 CEI。两者在工况下分别作用于负极和正极，反应电位窗口不重叠，不存在在电解液本体中相互消耗的驱动力。FDPT 体系 200 圈容量保持率 91.1% 且通过阻燃测试，也从实验层面证实了两者能协同工作而非相互干扰。

### Contrast Pair for Reference

- **PFPN + TMP** (both gas-phase flame retardant, both diffuse freely in solution) → possible mutual interference
- **PFPN + TMSB** (reduction vs oxidation, anode vs cathode) → no overlap, no competition

Use this contrast to show you understand when mutual interference IS a concern vs when it isn't.

---

## Reusable Academic Chinese Phrases

### CV Peak Interpretation
- "氧化峰向高电位偏移且峰电流减弱" → additive forms CEI, suppresses electrolyte decomposition
- "还原峰负移且强度降低" → additive preferentially reduces to form SEI, passivates surface
- "氧化还原峰高度重合" → high reversibility, low polarization
- "含添加剂体系峰电位差（ΔEp）缩小" → improved reaction kinetics due to low-impedance interface film
- "添加剂体系的电解液分解峰被有效压制" → CEI/SEI formation success

### GITT
- "GITT测试结果表明，XX体系的Li⁺扩散系数显著高于对比体系"
- Always add: "表明该体系构筑的界面膜具有优良的离子传输特性，有利于减小浓度极化、提升倍率性能并改善电极反应动力学"

### General Writing Rules
1. Always include implications — never state an observation without saying what it means
2. "归因于" (attributed to) is a strong connector for cause-effect
3. "有效" / "显著" are acceptable intensifiers in thesis writing
4. Avoid quotes (") and em-dashes (—) in formal academic text
