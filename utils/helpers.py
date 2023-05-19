import numpy as np
import matplotlib.pyplot as plt

class Rounder(object):
    @staticmethod
    def round(arr):
        decimals = 1
        arr = np.power(10, decimals) * np.round(arr, decimals=decimals)
        return arr.astype(int)


def pareto_optimum(row, df):
    mask1 = df['tardiness_proportion'] < row['tardiness_proportion']
    mask2 = df[mask1]['rejection_proportion'] < row['rejection_proportion']
    
    mask3 = df['weighted_tardiness_proportion'] < row['weighted_tardiness_proportion']
    mask4 = df[mask3]['weighted_rejection_proportion'] < row['weighted_rejection_proportion']
    
    mask5 = df['avg_tardiness_amount'] < row['avg_tardiness_amount']
    mask6 = df[mask5]['rejection_proportion'] < row['rejection_proportion']
    
    mask7 = df['weighted_avg_tardiness_amount'] < row['weighted_avg_tardiness_amount']
    mask8 = df[mask7]['weighted_rejection_proportion'] < row['weighted_rejection_proportion']
    
    return mask2.sum() == 0, mask4.sum() == 0, mask6.sum() == 0, mask8.sum() == 0


def plot_frontier(results, type):
    if type == 't_v_r':
        colors = ['r' if x else 'b' for x in results['pareto_opt1']]
        plt.scatter(results['tardiness_proportion'], results['rejection_proportion'], c=colors)

        for _, row in results.iterrows():
            if row['pareto_opt1']:
                plt.text(row['tardiness_proportion'], row['rejection_proportion'], f'({row["dispatching"]}-{row["due_date"]}-{row["due_date_param"]})')

        plt.title('tardiness vs. rejection proportion')
        plt.xlabel('tardiness proportion')
        plt.ylabel('rejection proportion')
        plt.show()
    
    if type == 'wt_v_wr':
        colors = ['r' if x else 'b' for x in results['pareto_opt_weighted1']]
        plt.scatter(results['weighted_tardiness_proportion'], results['weighted_rejection_proportion'], c=colors)

        for _, row in results.iterrows():
            if row['pareto_opt_weighted1']:
                plt.text(row['weighted_tardiness_proportion'], row['weighted_rejection_proportion'], f'({row["dispatching"]}-{row["due_date"]}-{row["due_date_param"]})')

        plt.title('weighted tardiness vs. weighted rejection proportions')
        plt.xlabel('weighted tardiness proportion')
        plt.ylabel('weighted rejection proportion')
        plt.show()

    if type == 'avgt_v_r':
        colors = ['r' if x else 'b' for x in results['pareto_opt2']]
        plt.scatter(results['avg_tardiness_amount'], results['rejection_proportion'], c=colors)

        for _, row in results.iterrows():
            if row['pareto_opt2']:
                plt.text(row['avg_tardiness_amount'], row['rejection_proportion'], f'({row["dispatching"]}-{row["due_date"]}-{row["due_date_param"]})')

        plt.title('avg tardiness amount vs. rejection proportion')
        plt.xlabel('avg tardiness amount')
        plt.ylabel('rejection proportion')
        plt.show()

    if type == 'wavgt_t_wr':
        colors = ['r' if x else 'b' for x in results['pareto_opt_weighted2']]
        plt.scatter(results['weighted_avg_tardiness_amount'], results['weighted_rejection_proportion'], c=colors)

        for _, row in results.iterrows():
            if row['pareto_opt_weighted2']:
                plt.text(row['weighted_avg_tardiness_amount'], row['weighted_rejection_proportion'], f'({row["dispatching"]}-{row["due_date"]}-{row["due_date_param"]})')

        plt.title('weighted avg tardiness amount vs. weighted rejection proportions')
        plt.xlabel('weighted avg tardiness amount')
        plt.ylabel('weighted rejection proportion')
        plt.show()

