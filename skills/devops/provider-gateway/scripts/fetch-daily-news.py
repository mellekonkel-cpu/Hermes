#!/usr/bin/env python3
"""
Daily news fetcher for morning briefing.
Searches Tavily across multiple categories and saves to file.
Designed to be run as a cron job.

Usage:
    python3 scripts/fetch-daily-news.py
"""

import json, urllib.request, time, os, re, datetime

TAVILY_KEY = "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"
OUTPUT_DIR = os.environ.get("HERMES_HOME", "/opt/data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "青桑", "每日新闻简报.txt")
ARCHIVE_DIR = os.path.join(OUTPUT_DIR, "青桑", "每日简报存档")

# Chinese and international holidays lookup (month, day) -> (Chinese name, International name)
HOLIDAYS = {
    (1, 1): ("元旦", "New Year's Day"),
    (1, 6): ("", "Epiphany"),
    (1, 7): ("", "Orthodox Christmas"),
    (1, 26): ("", "International Customs Day"),
    (1, 27): ("", "International Holocaust Remembrance Day"),
    (2, 2): ("", "World Wetlands Day"),
    (2, 4): ("", "World Cancer Day"),
    (2, 10): ("", "World Pulses Day"),
    (2, 11): ("", "International Day of Women and Girls in Science"),
    (2, 13): ("", "World Radio Day"),
    (2, 14): ("情人节", "Valentine's Day"),
    (2, 20): ("", "World Day of Social Justice"),
    (2, 21): ("", "International Mother Language Day"),
    (3, 3): ("", "World Wildlife Day"),
    (3, 5): ("学雷锋纪念日", ""),
    (3, 8): ("妇女节", "International Women's Day"),
    (3, 12): ("植树节", ""),
    (3, 14): ("", "White Day"),
    (3, 15): ("消费者权益日", "World Consumer Rights Day"),
    (3, 20): ("", "International Day of Happiness"),
    (3, 21): ("", "World Down Syndrome Day, World Poetry Day"),
    (3, 22): ("", "World Water Day"),
    (3, 23): ("", "World Meteorological Day"),
    (3, 24): ("", "World Tuberculosis Day"),
    (3, 25): ("", "International Day of Remembrance of Slavery Victims"),
    (3, 27): ("", "World Theatre Day"),
    (4, 1): ("", "April Fools' Day"),
    (4, 2): ("", "World Autism Awareness Day"),
    (4, 4): ("清明节", ""),
    (4, 5): ("清明节", ""),
    (4, 7): ("", "World Health Day"),
    (4, 12): ("", "International Day of Human Space Flight"),
    (4, 22): ("世界地球日", "Earth Day"),
    (4, 23): ("", "World Book Day"),
    (4, 24): ("", "International Day of Multilateralism"),
    (4, 25): ("", "World Malaria Day, DNA Day"),
    (4, 26): ("", "World Intellectual Property Day"),
    (4, 28): ("", "World Day for Safety and Health at Work"),
    (4, 29): ("", "International Dance Day"),
    (5, 1): ("劳动节", "International Workers' Day"),
    (5, 2): ("", "World Tuna Day"),
    (5, 3): ("", "World Press Freedom Day"),
    (5, 4): ("青年节", ""),
    (5, 5): ("", "World Hand Hygiene Day"),
    (5, 6): ("", "International No Diet Day"),
    (5, 8): ("世界红十字日", "World Red Cross Day"),
    (5, 9): ("", "Europe Day"),
    (5, 10): ("", "International Day of Argania"),
    (5, 11): ("", "World Migratory Bird Day"),
    (5, 12): ("护士节", "International Nurses Day, World Fibromyalgia Day"),
    (5, 15): ("国际家庭日", "International Day of Families"),
    (5, 16): ("", "International Day of Light"),
    (5, 17): ("", "World Telecommunication Day"),
    (5, 18): ("", "International Museum Day"),
    (5, 20): ("", "World Bee Day, World Metrology Day"),
    (5, 21): ("", "World Day for Cultural Diversity"),
    (5, 22): ("", "International Day for Biological Diversity"),
    (5, 23): ("", "International Day to End Obstetric Fistula"),
    (5, 25): ("大学生心理健康日", "Africa Day"),
    (5, 29): ("", "International Day of UN Peacekeepers"),
    (5, 31): ("世界无烟日", "World No Tobacco Day"),
    (6, 1): ("儿童节", "International Children's Day"),
    (6, 3): ("", "World Bicycle Day"),
    (6, 5): ("世界环境日", "World Environment Day"),
    (6, 6): ("", "UN Russian Language Day"),
    (6, 7): ("", "World Food Safety Day"),
    (6, 8): ("世界海洋日", "World Oceans Day"),
    (6, 12): ("", "World Day Against Child Labour"),
    (6, 14): ("", "World Blood Donor Day"),
    (6, 15): ("", "World Elder Abuse Awareness Day"),
    (6, 16): ("", "International Day of Family Remittances"),
    (6, 17): ("", "World Day to Combat Desertification and Drought"),
    (6, 18): ("", "Sustainable Gastronomy Day"),
    (6, 19): ("", "International Day for the Elimination of Sexual Violence"),
    (6, 20): ("世界难民日", "World Refugee Day"),
    (6, 21): ("", "International Day of Yoga, World Music Day"),
    (6, 23): ("", "International Widows Day, Public Service Day"),
    (6, 25): ("全国土地日", ""),
    (6, 26): ("国际禁毒日", "International Day Against Drug Abuse"),
    (6, 30): ("", "International Asteroid Day"),
    (7, 1): ("建党节", "Canada Day"),
    (7, 4): ("", "Independence Day (US)"),
    (7, 7): ("", "World Chocolate Day"),
    (7, 11): ("", "World Population Day"),
    (7, 14): ("", "Bastille Day (France)"),
    (7, 15): ("", "World Youth Skills Day"),
    (7, 18): ("", "Nelson Mandela International Day"),
    (7, 20): ("", "International Moon Day"),
    (7, 28): ("", "World Hepatitis Day"),
    (7, 30): ("", "International Day of Friendship"),
    (8, 1): ("建军节", ""),
    (8, 9): ("", "International Day of the World's Indigenous Peoples"),
    (8, 12): ("", "International Youth Day"),
    (8, 13): ("", "International Left-Handers Day"),
    (8, 19): ("中国医师节", "World Humanitarian Day, World Photography Day"),
    (8, 21): ("", "International Day of Remembrance of Slave Trade"),
    (8, 23): ("", "International Day for the Remembrance of the Slave Trade"),
    (8, 29): ("", "International Day against Nuclear Tests"),
    (8, 30): ("", "International Day of the Disappeared"),
    (9, 5): ("", "International Day of Charity"),
    (9, 8): ("", "International Literacy Day"),
    (9, 10): ("教师节", "World Suicide Prevention Day"),
    (9, 15): ("", "International Day of Democracy"),
    (9, 16): ("", "International Day for the Preservation of the Ozone Layer"),
    (9, 18): ("九一八事变纪念日", ""),
    (9, 21): ("", "International Day of Peace"),
    (9, 22): ("", "World Car-Free Day"),
    (9, 23): ("", "International Day of Sign Languages"),
    (9, 26): ("", "European Day of Languages"),
    (9, 27): ("", "World Tourism Day"),
    (9, 28): ("", "International Day for Universal Access to Information"),
    (9, 29): ("", "World Heart Day"),
    (9, 30): ("烈士纪念日", "International Translation Day"),
    (10, 1): ("国庆节", "International Day of Older Persons"),
    (10, 2): ("", "International Day of Non-Violence"),
    (10, 4): ("", "World Animal Day"),
    (10, 5): ("", "World Teachers' Day"),
    (10, 9): ("", "World Post Day"),
    (10, 10): ("辛亥革命纪念日", "World Mental Health Day"),
    (10, 11): ("", "International Day of the Girl Child"),
    (10, 13): ("", "International Day for Disaster Risk Reduction"),
    (10, 14): ("", "World Standards Day"),
    (10, 15): ("", "International Day of Rural Women, Global Handwashing Day"),
    (10, 16): ("", "World Food Day"),
    (10, 17): ("", "International Day for the Eradication of Poverty"),
    (10, 20): ("", "World Statistics Day"),
    (10, 24): ("联合国日", "United Nations Day, World Development Information Day"),
    (10, 27): ("", "World Day for Audiovisual Heritage"),
    (10, 31): ("万圣节", "World Cities Day, Halloween"),
    (11, 1): ("", "World Vegan Day"),
    (11, 2): ("", "International Day to End Impunity for Crimes against Journalists"),
    (11, 5): ("", "World Tsunami Awareness Day"),
    (11, 6): ("", "International Day for Preventing the Exploitation of the Environment"),
    (11, 8): ("记者节", ""),
    (11, 9): ("", "World Freedom Day"),
    (11, 10): ("", "World Science Day for Peace and Development"),
    (11, 11): ("光棍节", "Remembrance Day, Veterans Day (US)"),
    (11, 14): ("", "World Diabetes Day"),
    (11, 15): ("", "World Day of Remembrance for Road Traffic Victims"),
    (11, 16): ("", "International Day for Tolerance"),
    (11, 17): ("", "International Students' Day"),
    (11, 19): ("", "World Toilet Day, International Men's Day"),
    (11, 20): ("", "Universal Children's Day, Africa Industrialization Day"),
    (11, 21): ("世界问候日", "World Television Day"),
    (11, 22): ("", "World Philosophy Day"),
    (11, 25): ("", "International Day for the Elimination of Violence against Women"),
    (11, 29): ("", "International Day of Solidarity with the Palestinian People"),
    (11, 30): ("", "Day of Remembrance for all Victims of Chemical Warfare"),
    (12, 1): ("世界艾滋病日", "World AIDS Day"),
    (12, 2): ("", "International Day for the Abolition of Slavery"),
    (12, 3): ("国际残疾人日", "International Day of Persons with Disabilities"),
    (12, 4): ("国家宪法日", ""),
    (12, 5): ("", "International Volunteer Day"),
    (12, 6): ("", "International Civil Aviation Day"),
    (12, 7): ("", "International Civil Aviation Day"),
    (12, 9): ("", "International Anti-Corruption Day"),
    (12, 10): ("", "Human Rights Day"),
    (12, 11): ("", "International Mountain Day"),
    (12, 12): ("西安事变纪念日", ""),
    (12, 13): ("南京大屠杀死难者国家公祭日", ""),
    (12, 14): ("", "International Day of Neutrality"),
    (12, 18): ("", "International Migrants Day"),
    (12, 20): ("澳门回归纪念日", "International Human Solidarity Day"),
    (12, 21): ("", "World Peace Day"),
    (12, 24): ("平安夜", "Christmas Eve"),
    (12, 25): ("圣诞节", "Christmas Day"),
    (12, 26): ("毛泽东诞辰纪念日", ""),
    (12, 31): ("", "New Year's Eve"),
}

WEEKDAY_CN = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


def get_today_info():
    """Get today's date info with holidays."""
    now = datetime.datetime.now()
    month, day = now.month, now.day
    weekday = WEEKDAY_CN[now.weekday()]
    
    # Look up holidays
    holiday = HOLIDAYS.get((month, day), ("", ""))
    cn_name = holiday[0]
    intl_name = holiday[1]
    
    # Also search for Mother's Day, Father's Day etc. (floating dates)
    # Mother's Day: 2nd Sunday of May
    if month == 5:
        # Check if it's Mother's Day (2nd Sunday)
        cal = now.isocalendar()
        # Simple check: if day is 8-14 and weekday is Sunday (6)
        if 8 <= day <= 14 and now.weekday() == 6:
            intl_name = (intl_name + ", Mother's Day" if intl_name else "Mother's Day (母亲节)")
            cn_name = cn_name + "母亲节" if cn_name else "母亲节"
        # Check if it's World Red Cross Day (May 8)
    
    # Father's Day: 3rd Sunday of June
    if month == 6:
        if 15 <= day <= 21 and now.weekday() == 6:
            intl_name = (intl_name + ", Father's Day" if intl_name else "Father's Day (父亲节)")
            cn_name = cn_name + "父亲节" if cn_name else "父亲节"
    
    # Thanksgiving: 4th Thursday of November
    if month == 11:
        if 22 <= day <= 28 and now.weekday() == 3:
            intl_name = (intl_name + ", Thanksgiving Day" if intl_name else "Thanksgiving Day")
    
    return now, month, day, weekday, cn_name, intl_name

CATEGORIES = [
    ("国际经济", "major international economic news markets trade policy today this week"),
    ("前沿科技", "latest technology news AI semiconductor breakthrough innovation this week"),
    ("新能源电池", "battery electrolyte lithium metal solid state battery new energy vehicle news this week"),
    ("新材料", "new materials science research breakthrough graphene polymer composite this week"),
    ("国内产业", "中国新能源电池新材料产业政策 market dynamics lithium battery 2026"),
]

def clean_text(text):
    """Remove markdown/HTML formatting artifacts from Tavily content snippets."""
    if not text:
        return ""
    # Remove markdown headings
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    # Remove image markdown
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove inline links (keep link text)
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Remove common CSS class / JSON remnants
    text = re.sub(r'\s*\{[^}]*\}\s*', ' ', text)
    # Remove lines that are just numbers, bullets, or navigation text
    text = re.sub(r'^[\d\s•·▪▸→●○●]+$', '', text, flags=re.MULTILINE)
    # Collapse multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Collapse multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    # Remove leading/trailing whitespace per line
    text = '\n'.join(line.strip() for line in text.split('\n'))
    # Remove "Join IC", "Join Pro", "COPY LINK", "Copied!" etc.
    text = re.sub(r'\b(Join IC|Join Pro|COPY LINK|Copied!|Share on social media|References)\b', '', text, flags=re.IGNORECASE)
    # Remove standalone social media buttons
    text = re.sub(r'\b(Facebook|X\s*\(formerly Twitter\)|LinkedIn|Gmail|Email)\b', '', text)
    # Collapse multiple spaces again
    text = re.sub(r' {2,}', ' ', text)
    # Remove empty lines at start
    text = text.strip()
    return text

def search_tavily(query, depth="advanced", max_results=6):
    payload = json.dumps({
        "api_key": TAVILY_KEY,
        "query": query,
        "search_depth": depth,
        "max_results": max_results,
        "include_answer": True,
        "include_raw_content": False
    }).encode()
    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read())
        results = data.get("results", [])
        answer = data.get("answer", "")
        latency = round((time.time() - t0) * 1000)
        return results, answer, latency

def main():
    now, month, day, weekday, cn_name, intl_name = get_today_info()
    date_str = now.strftime("%Y-%m-%d")
    
    lines = [f"=== 每日新闻简报 | {date_str} | {weekday} ===", ""]
    
    # Today's special day section
    today_notes = []
    if cn_name:
        today_notes.append(f"🇨🇳 {cn_name}")
    if intl_name:
        today_notes.append(f"🌍 {intl_name}")
    if today_notes:
        lines.append(f"   {'  |  '.join(today_notes)}")
        lines.append("")

    for label, query in CATEGORIES:
        lines.append(f"── {label} ──")
        try:
            results, answer, latency = search_tavily(query)
            # If Tavily generated a summary answer, include it
            if answer:
                lines.append(f"📌 概览：{clean_text(answer)[:500]}")
                lines.append("")
            if results:
                for i, r in enumerate(results[:6]):
                    title = r.get("title", "?").strip()
                    url = r.get("url", "").strip()
                    content = r.get("content", "").strip()
                    # Clean and truncate to 300 chars as summary
                    cleaned = clean_text(content)[:300]
                    lines.append(f"▪ {title}")
                    if url:
                        lines.append(f"  🔗 {url}")
                    if cleaned:
                        lines.append(f"  📝 {cleaned}")
                    lines.append("")
            else:
                lines.append("▪ (暂无结果)")
                lines.append("")
        except Exception as e:
            lines.append(f"▪ (搜索失败: {str(e)[:80]})")
            lines.append("")

    news_count = sum(1 for l in lines if l.startswith("▪"))
    lines.append(f"=== 简报结束 | 共计 {news_count} 条新闻 ===")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    content = "\n".join(lines)
    # Save dated copy (never overwrite) — this is the primary archive
    dated_file = os.path.join(ARCHIVE_DIR, f"每日新闻简报_{date_str}.txt")
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    if not os.path.exists(dated_file):
        with open(dated_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Archived to {dated_file}")
    else:
        print(f"ℹ️  Archive already exists: {dated_file}, skipping dated write")

    print(content)
    print(f"\n✅ Archived to {dated_file}")

if __name__ == "__main__":
    main()
