import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_heatmap(df_results: pd.DataFrame,
                 metric_name: str,
                 output_dir: str):
    """根据参数结果绘制热力图"""

    pivot_table = df_results.pivot(index="slow", columns="fast", values=metric_name)
    plt.figure(figsize=(12, 10))

    sns.heatmap(
        pivot_table,
        annot=True,
        cmap="RdYlGn",
        fmt=".4f",
        linewidths=.5,
        cbar_kws={'label':metric_name}
    )
    plt.title(f"{metric_name} 参数热力图")
    plt.xlabel("快线周期(Fast)")
    plt.ylabel("慢线周期(Slow)")

    heatmap_path = os.path.join(output_dir, f'{metric_name}_Heatmap.png')
    plt.savefig(heatmap_path)
    plt.close()
    print(f"-> 热力图已保存到: {heatmap_path}")

    if not df_results.empty:
        best_row = df_results.loc[df_results[metric_name].idxmax()]
        print(f"\n-> 最佳 {metric_name} 参数组合: fast={best_row['fast']}, slow={best_row['slow']}, Value={best_row[metric_name]:.4f}")
    
    return best_row