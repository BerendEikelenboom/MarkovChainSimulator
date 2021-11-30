import streamlit as st
import graphviz as graphviz
import time
import numpy as np
import pandas as pd

st.header("Markov Chain Simulator")

# Upper columns
up_col1, up_col2 = st.columns((1, 3))
with up_col1:
    states = st.number_input("Number of states", step=1, min_value=2, max_value=5, value=3)

counter = [np.zeros(states)]
counter = [counter[0].astype(int)]


def transition(start):
    random = np.random.uniform(0, 1)
    for i in range(states):
        lower = sum(transition_matrix[start][0:i])
        upper = sum(transition_matrix[start][0:i+1])
        if lower < random <= upper:
            counter[0][i] += 1
            return i


# Write transition probability matrix
st.subheader("Transition probability matrix")

# Middle columns
col_list = st.columns((1, 1, 1, 1, 1, 5))

transition_matrix = np.zeros([states, states])

# Create input boxes and values
for state in range(states):
    with col_list[state]:
        for i in range(states):
            if state == 0:
                value = 0.6
            elif state == i + 1:
                value = 0.4
            else:
                value = 0
            if state == 0 and i == states - 1:
                value = 1
            number = st.text_input("", key=f"{state * states + i + 1}", value=f'{value}')
            transition_matrix[i, state] = number if number else 0

# Lower columns
low_col1, low_col2 = st.columns((2, 1))

# Check correct probabilities
nr_correct = 0
for i in range(states):
    if 0.99 < sum(transition_matrix[i][:]) < 1.01:
        nr_correct += 1

if nr_correct == states:
    # Create speed slider
    with low_col2:
        speed = st.number_input("Speed (1-5)", step=1, min_value=1, max_value=5, value=1)

    # Create dynamics checkbox
    with low_col2:
        dynamics_on = st.checkbox("Simulate")

    with col_list[-1]:
        # Create graph viz
        graph = graphviz.Digraph()
        for i in range(states):
            for j in range(states):
                if transition_matrix[i][j] != 0:
                    graph.edge(f'{i}', f'{j}', label=f'{transition_matrix[i][j]}')

        red_node = 0
        graph.attr(nodesep='0.5')
        graph.node(f'{red_node}', style='filled', fillcolor='green')
        dmc = st.graphviz_chart(graph)

    with low_col1:
        # Create dataframe
        df = pd.DataFrame(
            counter,
            columns=([f'state {state}' for state in range(states)]),
            index=(['Visits', 'Visits (%)'])
        )
        metrics_table = st.table(df)

        # Create dynamics
        while dynamics_on:
            time.sleep(1/((speed/1.2)**2))
            new_red_node = transition(red_node)
            graph.node(f'{red_node}', style='')
            dmc.graphviz_chart(graph)
            time.sleep(0.1)
            graph.node(f'{new_red_node}', style='filled', fillcolor='green')
            dmc.graphviz_chart(graph)
            red_node = new_red_node

            df[f'state {new_red_node}'][0] = counter[0][new_red_node]
            df[f'state {new_red_node}'][1] = counter[0][new_red_node] / sum(counter[0]) * 100
            metrics_table.table(df)


else:
    st.write("Wrong probabilities!")
