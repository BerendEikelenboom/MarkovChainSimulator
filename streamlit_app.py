import streamlit as st
import graphviz as graphviz
import time
import numpy as np
import pandas as pd


def DMC():
    st.subheader("Discrete Time Markov Chain Simulator")

    # Upper columns
    up_col1, up_col2 = st.columns((1, 3))
    # Write transition probability matrix
    st.write("Transition probability matrix")
    # Middle columns
    col_list = st.columns((1, 1, 1, 1, 1, 5))
    # Lower columns
    low_col1, low_col2 = st.columns((2, 1))

    with up_col1:
        if 'df' not in st.session_state:
            placeholder = st.empty()
            states = placeholder.number_input("Number of states", step=1, min_value=2, max_value=5, value=3)
            st.session_state['states'] = states
        if 'df' in st.session_state:
            placeholder = False
            states = st.session_state['states']

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
            run = st.button("Simulate")
            if run:
                st.session_state['run'] = True
                if placeholder:
                    placeholder.empty()
            st.button("Pause")
            reset = st.button("Reset")
            if reset:
                if 'run' in st.session_state and st.session_state['run'] is True:
                    st.button("Full reset")
                st.session_state['run'] = False

        if reset and 'df' in st.session_state:
            del st.session_state['df']
            del st.session_state['node']

        with col_list[-1]:
            # Create graph viz
            graph = graphviz.Digraph()
            for i in range(states):
                for j in range(states):
                    if transition_matrix[i][j] != 0:
                        graph.edge(f'{i}', f'{j}', label=f'{transition_matrix[i][j]}')

            red_node = st.session_state['node'] if 'node' in st.session_state else 0
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
            if 'df' in st.session_state:
                df = st.session_state['df']
                counter[0] = list(df.iloc[0])

            metrics_table = st.table(df)

            # Create dynamics
            while run:
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

                st.session_state['df'] = df
                st.session_state['node'] = red_node

    else:
        st.write("Wrong probabilities!")


def CMC():
    st.subheader("Continuous Time Markov Chain Simulator")

    # Upper columns
    up_col1, up_col2 = st.columns((1, 3))
    # Write transition rate matrix
    st.write("Transition rate matrix")
    # Middle columns
    col_list = st.columns((1, 1, 1, 1, 1, 5))
    # Lower columns
    low_col1, low_col2 = st.columns((2, 1))

    with up_col1:
        if 'df' not in st.session_state:
            placeholder = st.empty()
            states = placeholder.number_input("Number of states", step=1, min_value=2, max_value=5, value=3)
            st.session_state['states'] = states
        if 'df' in st.session_state:
            placeholder = False
            states = st.session_state['states']

    counter = [np.zeros(states)]

    def get_probability_matrix(transition_matrix):
        probability_matrix = np.zeros([states, states])
        for i in range(states):
            for j in range(states):
                if i != j:
                    probability_matrix[i][j] = transition_matrix[i][j] / transition_matrix[i][i]
                else:
                    probability_matrix[i][j] = 0
        return probability_matrix

    def get_sojourne(transition_matrix, node):
        lmda = transition_matrix[node][node]
        return np.random.exponential(1/lmda)

    def transition(start):
        random = np.random.uniform(0, 1)
        for i in range(states):
            lower = sum(transition_matrix[start][0:i])
            upper = sum(transition_matrix[start][0:i + 1])
            if lower < random <= upper:
                return i

    transition_rate_matrix = np.zeros([states, states])

    # Create input boxes and values
    for state in range(states):
        with col_list[state]:
            for i in range(states):
                if states == 2:
                    if i == 0 and (state == 0 or state == 1):
                        value = 5
                    elif i == 1 and (state == 0 or state == 1):
                        value = 2
                else:
                    if state == i:
                        value = 5 - i
                    elif state == i + 1:
                        value = 4 - i
                    elif state == i + 2:
                        value = 1
                    elif i == states - 1 and state == 0:
                        value = 4 - i
                    elif i == states - 1 and state == 1:
                        value = 1
                    elif i == states - 2 and state == 0:
                        value = 1
                    else:
                        value = 0
                number = st.text_input("", key=f"{state * states + i + 1}", value=f'{value}')
                transition_rate_matrix[i, state] = number if number else 0

    transition_matrix = get_probability_matrix(transition_rate_matrix)

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
            run = st.button("Simulate")
            if run:
                st.session_state['run'] = True
                if placeholder:
                    placeholder.empty()
            st.button("Pause")
            reset = st.button("Reset")
            if reset:
                if 'run' in st.session_state and st.session_state['run'] is True:
                    st.button("Full reset")
                st.session_state['run'] = False

        if reset and 'df' in st.session_state:
            del st.session_state['df']
            del st.session_state['node']

        with col_list[-1]:
            # Create graph viz
            graph = graphviz.Digraph()
            for i in range(states):
                for j in range(states):
                    if transition_matrix[i][j] != 0:
                        graph.edge(f'{i}', f'{j}', label=f'{round(transition_matrix[i][j], 2)}')

            red_node = st.session_state['node'] if 'node' in st.session_state else 0
            graph.attr(nodesep='0.5')
            graph.node(f'{red_node}', style='filled', fillcolor='green')
            dmc = st.graphviz_chart(graph)

        with low_col1:
            # Create dataframe
            df = pd.DataFrame(
                counter,
                columns=([f'state {state}' for state in range(states)]),
                index=(['Time', 'Time (%)'])
            )

            if 'df' in st.session_state:
                df = st.session_state['df']
                counter[0] = list(df.iloc[0])

            metrics_table = st.table(df.style.format("{:.2f}"))

            # Create dynamics
            while run:
                sojourne_time = get_sojourne(transition_rate_matrix, red_node)
                counter[0][red_node] += round(sojourne_time, 2)
                time.sleep(sojourne_time*3/speed)

                df[f'state {red_node}'][0] = counter[0][red_node]
                df[f'state {red_node}'][1] = round(counter[0][red_node] / sum(counter[0]) * 100, 2)
                metrics_table.table(df.style.format("{:.2f}"))

                st.session_state['df'] = df
                st.session_state['node'] = red_node

                new_red_node = transition(red_node)
                graph.node(f'{red_node}', style='')
                dmc.graphviz_chart(graph)
                time.sleep(0.1)
                graph.node(f'{new_red_node}', style='filled', fillcolor='green')
                dmc.graphviz_chart(graph)
                red_node = new_red_node

    else:
        st.write("Wrong probabilities!")


if __name__ == '__main__':
    st.set_page_config(layout="wide")
    st.header("Simulation")
    choice = st.radio("", ["Discrete Markov Chain", "Continuous Markov Chain"])

    if choice == "Discrete Markov Chain":
        DMC()

    else:
        CMC()
