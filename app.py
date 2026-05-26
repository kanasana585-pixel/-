import streamlit as st
import pandas as pd
import calendar
import datetime
import json

# ==========================================
# 定数・初期データの設定
# ==========================================
STAFF_LIST = ["鎌田", "藤井", "鰐渕", "下畑", "錦織", "杉田", "牧野", "小木", "大谷", "飯田", "オーブリー", "西田", "三田村", "木村", "高村", "奥田", "寺前"]
SHIFT_LIST = ["夜10", "こす早8", "こす早10", "こす早日", "ゆき早8", "ゆき早10", "ゆき早日", "パ早4", "こす遅10", "こす遅13", "ゆき遅10", "ゆき遅13", "こす遅8", "ゆき遅8", "日10", "日8", "時短6", "有休", "研修", "休"]
DEFAULT_HOLIDAYS_BASE = {"鎌田":10, "藤井":10, "鰐渕":10, "下畑":10, "錦織":10, "杉田":10, "牧野":9, "大谷":10, "西田":9, "三田村":9, "木村":9, "高村":12, "寺前":9}
HOLIDAYS_10H = {1: 14, 2: 12, 3: 13, 4: 13, 5: 14, 6: 13, 7: 13, 8: 14, 9: 13, 10: 14, 11: 13, 12: 14}
DIFF_8H = {1: 1, 2: -1, 3: 0, 4: 0, 5: 1, 6: 0, 7: 0, 8: 1, 9: 0, 10: 1, 11: 0, 12: 1}

# 6月のプリセット条件
JUNE_PRESETS = [
    {"name": "鎌田", "day": "5", "type": "固定", "shift": "夜10"}, {"name": "鎌田", "day": "11", "type": "固定", "shift": "こす遅13"}, {"name": "鎌田", "day": "17", "type": "固定", "shift": "こす早8"},
    {"name": "藤井", "day": "13", "type": "固定", "shift": "夜10"}, {"name": "藤井", "day": "16", "type": "固定", "shift": "ゆき早8"}, {"name": "藤井", "day": "17", "type": "固定", "shift": "ゆき早8"}, {"name": "藤井", "day": "18", "type": "固定", "shift": "研修"}, {"name": "藤井", "day": "19", "type": "固定", "shift": "研修"}, {"name": "藤井", "day": "26", "type": "固定", "shift": "研修"},
    {"name": "鰐渕", "day": "4", "type": "固定", "shift": "夜10"}, {"name": "鰐渕", "day": "17", "type": "固定", "shift": "こす早8"}, {"name": "鰐渕", "day": "19", "type": "固定", "shift": "こす遅13"},
    {"name": "下畑", "day": "11", "type": "固定", "shift": "ゆき遅13"}, {"name": "下畑", "day": "12", "type": "固定", "shift": "夜10"}, {"name": "下畑", "day": "25", "type": "固定", "shift": "夜10"}, {"name": "下畑", "day": "27", "type": "固定", "shift": "有休"},
    {"name": "錦織", "day": "2", "type": "固定", "shift": "こす遅13"}, {"name": "杉田", "day": "10", "type": "固定", "shift": "こす遅13"}, {"name": "牧野", "day": "19", "type": "固定", "shift": "こす早8"},
    {"name": "小木", "day": "3", "type": "固定", "shift": "夜10"}, {"name": "小木", "day": "8", "type": "固定", "shift": "こす遅13"}, {"name": "小木", "day": "10", "type": "固定", "shift": "夜10"}, {"name": "小木", "day": "17", "type": "固定", "shift": "夜10"}, {"name": "小木", "day": "24", "type": "固定", "shift": "夜10"}, {"name": "小木", "day": "28", "type": "固定", "shift": "夜10"},
    {"name": "大谷", "day": "19", "type": "固定", "shift": "有休"}, {"name": "飯田", "day": "2", "type": "固定", "shift": "ゆき早10"},
    {"name": "オーブリー", "day": "10", "type": "固定", "shift": "こす遅10"}, {"name": "オーブリー", "day": "22", "type": "固定", "shift": "夜10"}, {"name": "オーブリー", "day": "28", "type": "固定", "shift": "夜10"}
]

# ==========================================
# 関数定義
# ==========================================
def get_default_holidays(month, days_in_month):
    holidays = {}
    for name in STAFF_LIST:
        if name in ["小木", "飯田", "オーブリー"]:
            holidays[name] = HOLIDAYS_10H[month]
        elif name == "奥田":
            h_count = 0
            for d in range(1, days_in_month + 1):
                # 0:Mon, 1:Tue, 2:Wed, 3:Thu, 4:Fri, 5:Sat, 6:Sun
                # JSの getDay() 0(Sun), 3(Wed), 6(Sat) に対応させる
                weekday = datetime.date(2026, month, d).weekday()
                if weekday in [6, 2, 5]: 
                    h_count += 1
            holidays[name] = h_count
        elif month == 1 and name in ["牧野", "三田村", "木村", "寺前"]:
            holidays[name] = 10
        else:
            holidays[name] = DEFAULT_HOLIDAYS_BASE[name] + DIFF_8H[month]
    return holidays

# ==========================================
# ページ設定 & 初期化
# ==========================================
st.set_page_config(page_title="シフト作成コードジェネレーター", page_icon="📅", layout="wide")

if "conditions_df" not in st.session_state:
    st.session_state.conditions_df = pd.DataFrame(JUNE_PRESETS)
if "current_month" not in st.session_state:
    st.session_state.current_month = 6

st.title("📅 シフト作成コードジェネレーター (V8 - カレンダー条件指定版)")
st.markdown("Streamlit版: 条件を追加し、最後にGoogle Colab用のPythonコードを出力します。早日は「こす早日」「ゆき早日」に完全分離されています。")

# ==========================================
# 月選択
# ==========================================
st.header("1. 対象の月を選択")
month_options = {
    1: "2026年 1月 (31日間 - 10H組は8Hシフト1回)", 2: "2026年 2月 (28日間 - 10H組は8Hシフト0回)",
    3: "2026年 3月 (31日間 - 10H組は8Hシフト2回)", 4: "2026年 4月 (30日間 - 10H組は8Hシフト1回)",
    5: "2026年 5月 (31日間 - 10H組は8Hシフト1回)", 6: "2026年 6月 (30日間 - 10H組は8Hシフト1回)",
    7: "2026年 7月 (31日間 - 10H組は8Hシフト2回)", 8: "2026年 8月 (31日間 - 10H組は8Hシフト1回)",
    9: "2026年 9月 (30日間 - 10H組は8Hシフト1回)", 10: "2026年 10月 (31日間 - 10H組は8Hシフト1回)",
    11: "2026年 11月 (30日間 - 10H組は8Hシフト1回)", 12: "2026年 12月 (31日間 - 10H組は8Hシフト1回)"
}

selected_month = st.selectbox("月を選択", options=list(month_options.keys()), format_func=lambda x: month_options[x], index=5)
days_in_month = calendar.monthrange(2026, selected_month)[1]

# 月が変更されたら条件リストをリセット（必要に応じて）
if st.session_state.current_month != selected_month:
    if selected_month == 6:
        st.session_state.conditions_df = pd.DataFrame(JUNE_PRESETS)
    else:
        st.session_state.conditions_df = pd.DataFrame(columns=["name", "day", "type", "shift"])
    st.session_state.current_month = selected_month

# ==========================================
# 公休数設定
# ==========================================
st.header("2. スタッフ別の公休数設定")
default_holidays = get_default_holidays(selected_month, days_in_month)
holiday_inputs = {}

cols = st.columns(6)
for i, staff in enumerate(STAFF_LIST):
    with cols[i % 6]:
        holiday_inputs[staff] = st.number_input(f"{staff}", min_value=0, max_value=days_in_month, value=default_holidays[staff])

# ==========================================
# 条件設定（追加フォーム & データエディタ）
# ==========================================
st.header("3. シフト条件（固定・禁止）の指定")

with st.expander("➕ 新しい条件を追加する", expanded=True):
    with st.form("add_condition_form"):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            add_name = st.selectbox("スタッフ", STAFF_LIST)
        with col2:
            day_options = ["All"] + [str(d) for d in range(1, days_in_month + 1)]
            add_day = st.selectbox("日付 (All=全日)", day_options)
        with col3:
            add_type = st.selectbox("種類", ["固定", "禁止"])
        with col4:
            add_shift = st.selectbox("シフト", SHIFT_LIST)
        with col5:
            st.write("") # アライメント用
            st.write("")
            submit_btn = st.form_submit_button("追加")

        if submit_btn:
            new_row = {"name": add_name, "day": add_day, "type": add_type, "shift": add_shift}
            st.session_state.conditions_df = pd.concat([st.session_state.conditions_df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("追加しました！下の表に反映されています。")

st.markdown("▼ **現在設定されている条件**（表の右端をクリックして行の削除が可能です）")
st.session_state.conditions_df = st.data_editor(
    st.session_state.conditions_df,
    column_config={
        "name": st.column_config.TextColumn("スタッフ名"),
        "day": st.column_config.TextColumn("日付"),
        "type": st.column_config.TextColumn("条件(固定/禁止)"),
        "shift": st.column_config.TextColumn("シフト")
    },
    num_rows="dynamic",
    use_container_width=True
)

# ==========================================
# コード生成ロジック
# ==========================================
st.header("4. コードの生成")

if st.button("🚀 Google Colab用コードを生成する", type="primary"):
    
    df = st.session_state.conditions_df
    
    target_8h_count = 1 if selected_month in [1, 4, 5, 6, 8, 9, 10, 11, 12] else 2 if selected_month in [3, 7] else 0
    py_first_day = datetime.date(2026, selected_month, 1).weekday() # 0:Mon, 6:Sun
    
    # 有休のカウント
    yukyu_obj = {staff: 0 for staff in STAFF_LIST}
    if not df.empty:
        for _, row in df.iterrows():
            if row["type"] == "固定" and row["shift"] == "有休":
                yukyu_obj[row["name"]] += 1

    # 条件の仕分け
    fixed_lines = []
    forbidden_lines = []
    
    if not df.empty:
        for _, row in df.iterrows():
            r_name = row["name"]
            r_day = row["day"]
            r_type = row["type"]
            r_shift = row["shift"]
            
            if r_type == "固定":
                if r_day == "All": continue
                fixed_lines.append(f'    ("{r_name}", {int(r_day) - 1}, "{r_shift}")')
            else:
                if r_day == "All":
                    forbidden_lines.append(f'    ("{r_name}", "All", "{r_shift}")')
                else:
                    forbidden_lines.append(f'    ("{r_name}", {int(r_day) - 1}, "{r_shift}")')

    py_fixed_list = ",\n".join(fixed_lines)
    py_forbidden_list = ",\n".join(forbidden_lines)

    generated_code = f"""# ===================================================
# 🌟 Google Colab用 シフト自動計算 ＆ 再調整システム V8
# ===================================================
!pip install ortools pandas
import pandas as pd
import os
from ortools.sat.python import cp_model
from google.colab import files

RE_CALCULATE = False
RE_CALCULATE_FILE = "shift_2026年{selected_month}月.csv"

num_days = {days_in_month}
year_month = "2026年{selected_month}月"
start_weekday = {py_first_day}
staff_list = {json.dumps(STAFF_LIST, ensure_ascii=False)}
shifts = {json.dumps(SHIFT_LIST, ensure_ascii=False)}
holidays = {json.dumps(holiday_inputs, ensure_ascii=False)}

fixed_shifts = [
{py_fixed_list}
]

forbidden_shifts = [
{py_forbidden_list}
]

model = cp_model.CpModel()
x = {{}}
for e in staff_list:
    for d in range(num_days):
        for s in shifts:
            x[(e, d, s)] = model.NewBoolVar(f"x_{{e}}_{{d}}_{{s}}")

for e in staff_list:
    for d in range(num_days):
        model.AddExactlyOne(x[(e, d, s)] for s in shifts)
    model.Add(sum(x[(e, d, "休")] for d in range(num_days)) == holidays[e])

yukyu_counts = {json.dumps(yukyu_obj, ensure_ascii=False)}
for e in staff_list:
    model.Add(sum(x[(e, d, "有休")] for d in range(num_days)) == yukyu_counts.get(e, 0))
    kenshu_fixed = sum(1 for (name, d_f, s) in fixed_shifts if name == e and s == "研修")
    model.Add(sum(x[(e, d, "研修")] for d in range(num_days)) == kenshu_fixed)

forced_by_file = {{}}
if RE_CALCULATE and os.path.exists(RE_CALCULATE_FILE):
    print("♻️ 手動修正ファイルを読み込んで再調整用の計算を行います...")
    df_mod = pd.read_csv(RE_CALCULATE_FILE)
    for _, r in df_mod.iterrows():
        name = r["氏名"]
        if name in staff_list:
            for d in range(num_days):
                s_val = str(r[str(d+1)]).strip()
                if s_val in shifts:
                    forced_by_file[(name, d)] = s_val

fixed_dict = {{}}
for e, d, s in fixed_shifts:
    if (e, d) in forced_by_file: continue
    model.Add(x[(e, d, s)] == 1)
    fixed_dict[(e, d)] = s

for e, d, s in forbidden_shifts:
    if d == "All":
        for day_idx in range(num_days):
            model.Add(x[(e, day_idx, s)] == 0)
    else:
        model.Add(x[(e, int(d), s)] == 0)

for (e, d), s in forced_by_file.items():
    model.Add(x[(e, d, s)] == 1)
    fixed_dict[(e, d)] = s

for d in range(num_days):
    if ("奥田", d) in fixed_dict: continue
    weekday = (d + start_weekday) % 7
    if weekday == 0: model.Add(x[("奥田", d, "パ早4")] == 1)
    elif weekday in [1, 3, 4]: model.Add(x[("奥田", d, "パ4")] == 1)
    else: model.Add(x[("奥田", d, "休")] == 1)

for e in staff_list:
    if e != "奥田":
        for d in range(num_days):
            model.Add(x[(e, d, "パ早4")] == 0)
            model.Add(x[(e, d, "パ4")] == 0)

for e in staff_list:
    for d in range(num_days - 1):
        model.AddImplication(x[(e, d, "夜10")], x[(e, d+1, "休")])
    for d in range(num_days - 4):
        model.Add(sum(x[(e, d+i, "休")] + x[(e, d+i, "有休")] for i in range(5)) >= 1)

# 遅出・早日の翌日早出禁止
late_shifts = ["こす遅13", "こす遅10", "ゆき遅13", "ゆき遅10", "こす早日", "ゆき早日"]
early_shifts = ["こす早10", "こす早8", "ゆき早10", "ゆき早8", "パ早4", "こす早日", "ゆき早日"]
for e in staff_list:
    for d in range(num_days - 1):
        for s_late in late_shifts:
            for s_early in early_shifts:
                model.AddImplication(x[(e, d, s_late)], x[(e, d+1, s_early)].Not())

target_8h_count = {target_8h_count}
shifts_8h_for_10h = ["日8", "こす早8", "ゆき早8", "こす遅8", "ゆき遅8"]
for e in ["小木", "飯田", "オーブリー"]:
    modified_count = sum(1 for d in range(num_days) if (e, d) in forced_by_file and forced_by_file[(e, d)] in shifts_8h_for_10h)
    if modified_count == 0:
        model.Add(sum(x[(e, d, s)] for d in range(num_days) for s in shifts_8h_for_10h) == target_8h_count)

allowed_10h_staff_shifts = ["こす遅10", "ゆき遅10", "日10", "こす早10", "ゆき早10", "夜10", "休", "有休", "日8", "こす早8", "ゆき早8", "こす遅8", "ゆき遅8"]
for e in ["小木", "飯田", "オーブリー"]:
    for d in range(num_days):
        if (e, d) in fixed_dict: continue
        for s in shifts:
            if s not in allowed_10h_staff_shifts:
                model.Add(x[(e, d, s)] == 0)

no_10h_staff = ["鎌田", "藤井", "鰐渕", "下畑", "錦織", "杉田", "牧野", "大谷"]
for e in no_10h_staff:
    for d in range(num_days):
        if (e, d) in fixed_dict: continue
        for s in ["こす早10", "ゆき早10", "こす遅10", "ゆき遅10", "日10"]:
            model.Add(x[(e, d, s)] == 0)

for d in range(num_days):
    if ("牧野", d) in fixed_dict: continue
    for s in shifts:
        if s not in ["こす早8", "ゆき早8", "こす遅8", "ゆき遅8", "休", "有休"]:
            model.Add(x[("牧野", d, s)] == 0)

model.Add(sum(x[("高村", d, "こす早8")] for d in range(num_days)) <= 4)
for d in range(num_days):
    if ("高村", d) in fixed_dict: continue
    for s in shifts:
        if s not in ["こす早8", "日8", "休", "有休"]:
            model.Add(x[("高村", d, s)] == 0)

for e in staff_list:
    if e in ["木村", "三田村", "寺前"]:
        for d in range(num_days):
            if (e, d) in fixed_dict: continue
            for s in shifts:
                if s not in ["時短6", "休", "有休"]: model.Add(x[(e, d, s)] == 0)
    else:
        for d in range(num_days):
            model.Add(x[(e, d, "時短6")] == 0)

for d in range(num_days):
    if ("西田", d) in fixed_dict: continue
    for s in shifts:
        if s not in ["日8", "夜10", "ゆき早8", "ゆき遅8", "こす早日", "ゆき早日", "休", "有休"]:
            model.Add(x[("西田", d, s)] == 0)

# 人数枠の死守 ＆ 相殺ロジック (V8アップデート)
for d in range(num_days):
    f_night = sum(1 for (e, d_f, s) in fixed_shifts if d_f == d and s == "夜10")
    f_k_o1 = sum(1 for (e, d_f, s) in fixed_shifts if d_f == d and s in ["こす遅10", "こす遅13"])
    f_y_o1 = sum(1 for (e, d_f, s) in fixed_shifts if d_f == d and s in ["ゆき遅10", "ゆき遅13"])
    f_k_h = sum(1 for (e, d_f, s) in fixed_shifts if d_f == d and s in ["こす早10", "こす早8"])
    f_y_h = sum(1 for (e, d_f, s) in fixed_shifts if d_f == d and s in ["ゆき早10", "ゆき早8", "パ早4"])
    f_k_o2 = sum(1 for (e, d_f, s) in fixed_shifts if d_f == d and s in ["こす遅8", "日10"])
    f_y_o2 = sum(1 for (e, d_f, s) in fixed_shifts if d_f == d and s in ["ゆき遅8", "日10"])
    
    weekday = (d + start_weekday) % 7
    if weekday == 0: f_y_h += 1
    
    model.Add(sum(x[(e, d, "夜10")] for e in staff_list) == max(2, f_night))
    model.Add(sum(x[(e, d, "こす遅10")] + x[(e, d, "こす遅13")] for e in staff_list) == max(1, f_k_o1))
    model.Add(sum(x[(e, d, "ゆき遅10")] + x[(e, d, "ゆき遅13")] for e in staff_list) == max(1, f_y_o1))
    
    # 系統ごとの早日変数を集計
    kosu_hayahi = sum(x[(e, d, "こす早日")] for e in staff_list)
    yuki_hayahi = sum(x[(e, d, "ゆき早日")] for e in staff_list)
    model.Add(kosu_hayahi + yuki_hayahi <= 2) # 全体で最大2名まで
    
    # 早出の集計
    kosu_haya = sum(x[(e, d, "こす早10")] + x[(e, d, "こす早8")] for e in staff_list)
    yuki_haya = sum(x[(e, d, "ゆき早10")] + x[(e, d, "ゆき早8")] + x[(e, d, "パ早4")] for e in staff_list)
    
    # ★ ゆきの方が「ゆき早日」なら、ゆきの方で早出枠を相殺する厳密なロジック
    if f_k_h >= 1:
        model.Add(kosu_haya == f_k_h)
    else:
        model.Add(kosu_haya + kosu_hayahi <= 1)
        
    if f_y_h >= 1:
        model.Add(yuki_haya == f_y_h)
    else:
        model.Add(yuki_haya + yuki_hayahi <= 1)
        
    # 早出全体としての必要人数死守
    model.Add(kosu_haya + yuki_haya + kosu_hayahi + yuki_hayahi == max(2, f_k_h + f_y_h))
    
    # 遅2の偏り防止 ＆ 早日系統別相殺
    kosu_oso2 = sum(x[(e, d, "こす遅8")] + x[(e, d, "日10")] for e in staff_list)
    yuki_oso2 = sum(x[(e, d, "ゆき遅8")] + x[(e, d, "日10")] for e in staff_list)
    
    model.Add(kosu_oso2 + kosu_hayahi >= max(1, f_k_o2))
    model.Add(yuki_oso2 + yuki_hayahi >= max(1, f_y_o2))
    
    total_oso2 = sum(x[(e, d, "こす遅8")] + x[(e, d, "ゆき遅8")] + x[(e, d, "日10")] for e in staff_list)
    model.Add(total_oso2 + kosu_hayahi + yuki_hayahi == max(2, f_k_o2 + f_y_o2))

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 120.0
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print(f"✨ シフトの計算・調整が完了しました！")
    schedule = []
    for e in staff_list:
        row = {{"氏名": e}}
        work_days = 0
        for d in range(num_days):
            for s in shifts:
                if solver.Value(x[(e, d, s)]) == 1:
                    display_shift = "早日" if s in ["こす早日", "ゆき早日"] else s
                    row[str(d+1)] = display_shift
                    if s not in ["休", "有休"]: work_days += 1
        row["休の数"] = holidays[e]
        row["有休"] = sum(1 for d in range(num_days) if solver.Value(x[(e, d, "有休")]) == 1)
        row["業務数"] = work_days
        schedule.append(row)
    
    summary_rows = {{
        "夜勤": ["夜10"], "こす早": ["こす早10", "こす早8"], "ゆき早": ["ゆき早10", "ゆき早8"], "パ早4": ["パ早4"], "こす早日": ["こす早日"], "ゆき早日": ["ゆき早日"], "時短": ["時短6"], "こす遅1": ["こす遅10", "こす遅13"], "ゆき遅1": ["ゆき遅10", "ゆき遅13"], "こす遅2": ["こす遅8", "日10"], "ゆき遅2": ["ゆき遅8", "日10"]
    }}
    for label, target_shifts in summary_rows.items():
        row = {{"氏名": label}}
        for d in range(num_days):
            count = sum(solver.Value(x[(e, d, s)]) for e in staff_list for s in target_shifts)
            row[str(d+1)] = count
        schedule.append(row)
    df = pd.DataFrame(schedule)
    filename = f"shift_{{year_month}}.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    files.download(filename)
    print("✅ ダウンロードが完了しました。")
else:
    print("⚠️ エラー：条件が厳しすぎます。")
"""

    st.success("✅ コードを生成しました！右上のコピーボタンからコピーしてGoogle Colabに貼り付けてください。")
    st.code(generated_code, language="python")
