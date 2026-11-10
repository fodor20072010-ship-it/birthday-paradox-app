import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="birthday paradox", page_icon="🎂", layout="wide")


def prob(n, days=365):
    if n > days:
        return 1.0
    q = 1.0 #вероятность, что все дни разные
    for i in range(n):
        q *= (days - i) / days
    return 1 - q


def needed(target_probability, days=365): 
    q = 1.0
    n = 0
    while (1 - q) < target_probability:
        n += 1
        q *= (days - n + 1) / days
    return n


def run_mc(trials, n, days = 365): #trials - сколько эксперементов провели
    c = 0 #cчётчик групп с совпадением
    r = random.Random()
    for t in range(trials):
        bdays = []
        for i in range(n):
            bdays.append(r.randint(1, days))
        uniq = set(bdays)
        if len(uniq) < len(bdays):
            c += 1
    return c / trials #эмпирическая вероятность


st.title("🎂 Парадокс дней рождения")
st.write("Сколько человек нужно, чтобы вероятность совпадения превысила 50%? "
         "Обычно думают ~180, но правильный ответ 23.")

with st.sidebar:
    st.header("Параметры")
    days = st.number_input("Дней в году", 2, 366, 365, 1) #366 с 29 февраля
    threshold = st.slider("Целевая вероятность", 0.01, 0.999, 0.5, 0.001,
                          format="%.3f")
    n_current = st.slider("Число людей (n)", 1, min(days, 200), 23)
    trials = st.select_slider( "Испытаний",
                              [1000, 5000, 10000, 50000, 100000], 10000)

n_required = needed(threshold, days)
p_curr = prob(n_current, days)

c1, c2, c3 = st.columns(3)
c1.metric("Минимум людей для порога" , n_required)
c2.metric(f"P при n = {n_current}", f"{p_curr:.2%}")
c3.metric("Число пар при n", n_current * (n_current - 1) // 2)

st.caption(f"Для вероятности ≥ {threshold:.1%} при {days} днях в году нужно "
           f"**{n_required}** человек(а).")

st.subheader("Кривая вероятности")

xs = list(range(1, min(days, 150) + 1))
ys = []
for x in xs:
    ys.append(prob(x, days))

fig, ax = plt.subplots(figsize = (10, 4.5) )
ax.plot(xs, ys, linewidth =2, color = "#1b87d4", label = "P(совпадение)" )
ax.axhline(threshold, color = "gray", linestyle ="--",
           label=f"порог {threshold:.1%}")
ax.axvline(n_required, color = "red", linestyle = ":", label = f"n = {n_required}" )
ax.scatter([n_current], [p_curr], color="orange", s=80, zorder=5,
           label=f"текущее n = {n_current}")
ax.set_xlabel("Число людей (n)")
ax.set_ylabel("Вероятность")
ax.set_ylim(0, 1.02)
ax.grid(alpha =0.3)
ax.legend()
st.pyplot(fig)

st.subheader("Таблица ключевых значений")
checkpoints = [5, 10, 15, 20, 23, 30, 40, 50, 57, 70, 100]
checkpoints = [k for k in checkpoints if k <= days]

rows = []
for k in checkpoints:
    p = prob(k, days)
    rows.append({"n": k, "P(совпадение)": round(p, 4),
                 "P(все разные)": round(1 - p, 4)})
st.dataframe(pd.DataFrame(rows), use_container_width = True, hide_index = True)

st.subheader("Эмпирическая проверка")

if st.button("Запустить симуляцию", type="primary"):
    with st.spinner(f"Считаем {trials:,} испытаний..."):
        emp = run_mc(trials, n_current, days)
    a, b = st.columns(2)
    a.metric("Теоретически", f"{p_curr:.4f}")
    b.metric("Эмпирически", f"{emp:.4f}", delta=f"{emp - p_curr:+.4f}")
    st.progress(min(max(emp, 0.0), 1.0))

with st.expander("Почему интуиция ошибается?"):
    pairs = n_current * (n_current - 1) // 2
    st.markdown(
        f"Интуиция отвечает на вопрос «сколько людей должны иметь тот же день "
        f"рождения, что и я?» — для 50% нужно около 253 человек.\n\n"
        f"Но здесь задача другая: совпадение любой пары. Число пар растёт "
        f"квадратично: при n = {n_current} это {pairs} пар.\n\n"
        f"Формула через противоположное событие (все дни разные):"
    )
    st.latex(r"P(\bar A) = \prod_{i=0}^{n-1} \frac{365 - i}{365}, \quad "
             r"P(A) = 1 - P(\bar A)")

st.caption("Формула верна для равномерного распределения и независимости "
           "дней рождения.")
