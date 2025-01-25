import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def calculate_tax(asset_value, heirs, spouse_inherits_all):
    # 基礎控除の計算
    base_deduction = 3000 + (600 * heirs)  # 万円単位
    taxable_amount = max(asset_value - base_deduction, 0)

    # 最新の税率表と控除額
    tax_brackets = [
        (1000, 0.10, 0),
        (3000, 0.15, 50),
        (5000, 0.20, 200),
        (10000, 0.30, 700),
        (20000, 0.40, 1700),
        (30000, 0.45, 2700),
        (60000, 0.50, 4200),
        (float('inf'), 0.55, 7200)
    ]

    # 税額計算
    tax = 0
    for limit, rate, deduction in tax_brackets:
        if taxable_amount > limit:
            tax += limit * rate - deduction
            taxable_amount -= limit
        else:
            tax += taxable_amount * rate - deduction
            break

    # 配偶者控除（配偶者が全額相続する場合）
    if spouse_inherits_all:
        spouse_deduction = min(asset_value, 16000)  # 1億6000万円まで控除
        taxable_amount = max(asset_value - spouse_deduction - base_deduction, 0)
        tax = sum(min(taxable_amount, limit) * rate - deduction for limit, rate, deduction in tax_brackets if taxable_amount > 0)
    
    return max(round(tax, 2), 0)

# Streamlit UI
st.title("相続税シミュレーター")

# 資産の入力
st.header("資産情報")
land_value = st.number_input("土地・家屋の評価額（万円）", min_value=0)
insurance_value = st.number_input("生命保険の評価額（万円）", min_value=0)
savings_value = st.number_input("貯蓄の評価額（万円）", min_value=0)
stocks_value = st.number_input("株式の評価額（万円）", min_value=0)

total_assets = land_value + insurance_value + savings_value + stocks_value
st.write(f"総資産額: {total_assets} 万円")

# 相続人の入力
st.header("相続人情報")
num_children = st.number_input("子供の人数", min_value=0, value=1)
spouse_inherits_all = st.checkbox("配偶者がすべて相続する")

# シミュレーション実行
if st.button("相続税を計算"):
    # 一次相続の計算
    primary_tax = calculate_tax(total_assets, num_children + 1, spouse_inherits_all)
    st.subheader("一次相続の結果")
    st.write(f"推定相続税: {primary_tax} 万円")
    
    if spouse_inherits_all:
        # 二次相続の計算（配偶者死亡後）
        secondary_tax = calculate_tax(total_assets, num_children, False)
        st.subheader("二次相続の結果")
        st.write(f"推定相続税（二次相続時）: {secondary_tax} 万円")
        total_tax = primary_tax + secondary_tax
        st.write(f"総相続税（一次＋二次）: {total_tax} 万円")
    else:
        st.write("配偶者がすべて相続しない場合、二次相続は発生しません。")

    # グラフ表示
    labels = ['一次相続税', '二次相続税'] if spouse_inherits_all else ['一次相続税']
    values = [primary_tax] if not spouse_inherits_all else [primary_tax, secondary_tax]
    plt.bar(labels, values)
    plt.title('相続税の比較')
    plt.ylabel('税額 (万円)')
    st.pyplot(plt)
