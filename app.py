import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import prod
import random

# ---------- Настройки страницы ----------
st.set_page_config(
    page_title="Парадокс дней рождения",
    page_icon="🎂",
    layout="wide",
)

# ---------- Математика ----------
def birthday_probability(n: int, days: int = 365) -> float:
    """Вероятность совпадения дней рождения хотя бы у двух из n человек."""
    if n > days:
        return 1.0
    p_no_match = prod((days - i) / days for i in range(n))
    return 1 - p_no_match


def min_people(threshold: float = 0.5, days: int = 365) -> int:
    p_no_match = 1.0
    n = 0
    while 1 - p_no_match < threshold:
        n += 1
        p_no_match *= (days - (n - 1)) / days
    return n


def simulate(trials: int, n: int, days: int = 365) -> float:
    hits = 0
    for _ in range(trials):
        birthdays = [random.randint(1, days) for _ in range(n)]
        if len(set(birthdays)) < n:
            hits += 1
    return hits / trials


# ---------- Заголовок ----------
st.title("🎂 Парадокс дней рождения")
st.markdown(
    "Сколько человек нужно в группе, чтобы вероятность совпадения "
    "дней рождения хотя бы у двух превысила 50%? Интуиция говорит "
    "«~180», но ответ — **23**."
)

# ---------- Боковая панель ----------
with st.sidebar:
    st.header("Параметры")
    days = st.number_input("Дней в году", min_value=2, max_value=366, value=365, step=1)
    threshold = st.slider(
        "Целевая вероятность", min_value=0.01, max_value=0.999,
        value=0.50, step=0.001, format="%.3f"
    )
    n_current = st.slider("Число людей (n)", min_value=1, max_value=min(days, 200), value=23)
    trials = st.select_slider(
        "Испытаний Монте-Карло",
        options=[1_000, 5_000, 10_000, 50_000, 100_000],
        value=10_000,
    )

# ---------- Метрики ----------
n_required = min_people(threshold, days)
p_curr = birthday_probability(n_current, days)

col1, col2, col3 = st.columns(3)
col1.metric("Минимум людей для порога", f"{n_required}")
col2.metric(f"P при n = {n_current}", f"{p_curr:.2%}")
col3.metric("Число пар при n", f"{n_current * (n_current - 1) // 2}")

st.caption(
    f"Для вероятности ≥ {threshold:.1%} при {days} днях в году нужно "
    f"**{n_required}** человек(а)."
)

# ---------- График ----------
st.subheader("Кривая вероятности")

ns = np.arange(1, min(days, 150) + 1)
ps = np.array([birthday_probability(int(n), days) for n in ns])

fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(ns, ps, linewidth=2, color="#1f77b4", label="P(совпадение)")
ax.axhline(threshold, color="gray", linestyle="--", label=f"порог {threshold:.1%}")
ax.axvline(n_required, color="red", linestyle=":",
           label=f"n = {n_required}")
ax.scatter([n_current], [p_curr], color="orange", s=80, zorder=5,
           label=f"текущее n = {n_current}")
ax.set_xlabel("Число людей (n)")
ax.set_ylabel("Вероятность")
ax.set_ylim(0, 1.02)
ax.grid(alpha=0.3)
ax.legend()
st.pyplot(fig)

# ---------- Таблица ----------
st.subheader("Таблица ключевых значений")
checkpoints = [5, 10, 15, 20, 23, 30, 40, 50, 57, 70, 100]
checkpoints = [n for n in checkpoints if n <= days]
df = pd.DataFrame({
    "n": checkpoints,
    "P(совпадение)": [f"{birthday_probability(n, days):.4f}" for n in checkpoints],
    "P(все разные)": [f"{1 - birthday_probability(n, days):.4f}" for n in checkpoints],
})
st.dataframe(df, use_container_width=True, hide_index=True)

# ---------- Монте-Карло ----------
st.subheader("Эмпирическая проверка (Монте-Карло)")
if st.button("Запустить симуляцию", type="primary"):
    with st.spinner(f"Считаем {trials:,} испытаний..."):
        emp = simulate(trials, n_current, days)
    c1, c2 = st.columns(2)
    c1.metric("Теоретически", f"{p_curr:.4f}")
    c2.metric("Эмпирически", f"{emp:.4f}", delta=f"{emp - p_curr:+.4f}")
    st.progress(min(max(emp, 0.0), 1.0))

# ---------- Пояснение ----------
with st.expander("Почему интуиция ошибается?"):
    st.markdown(
        f"""
        Интуиция отвечает на вопрос *«сколько людей должны иметь тот же день
        рождения, что и я?»* — для 50% нужно ~253 человека.

        Но задача другая: **совпадение любой пары**. Число пар растёт
        квадратично: при n = {n_current} это
        **{n_current * (n_current - 1) // 2}** пар.

        Формула через противоположное событие (все дни разные):

        $$P(\\bar A) = \\prod_{{i=0}}^{{n-1}} \\frac{{365 - i}}{{365}},
        \\quad P(A) = 1 - P(\\bar A)$$
        """
    )

st.caption("Формула верна для равномерного распределения и независимости дней рождения.")