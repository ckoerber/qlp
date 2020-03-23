import matplotlib.pyplot as plt
from qlpdb.data.models import Data as data_Data
import numpy as np
import math
from statsmodels.stats.proportion import proportion_confint

label_params = dict()
label_params["fontsize"] = 7
tick_params = dict()
tick_params["labelsize"] = 7
tick_params["width"] = 0.5
errorbar_params = dict()
errorbar_params["mew"] = 0.5
errorbar_params["markersize"] = 5
red = '#c82506'
green = '#70b741'
blue = '#51a7f9'


def getdata():
    nndata = {
        v: data_Data.objects.filter(
            experiment__graph__tag=f"NN(8)",
            experiment__tag=f"FixEmbedding_NegShiftLinear_-{v}_{v}",
            experiment__settings__annealing_time=400,
            experiment__settings__num_spin_reversal_transforms=10,
        ).to_dataframe()
        for v in [0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]
    }
    return nndata

def gettadata():
    anneal_time =  [1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,200,300,400,500,600,700,800,900,1000,2000]
    if True:
        y = [0.07668, 0.08274, 0.08514, 0.10004, 0.1008, 0.09996, 0.1081, 0.11764, 0.10532, 0.11918, 0.11146, 0.11622, 0.12044, 0.1258, 0.13804, 0.15984, 0.15142, 0.14064, 0.13776, 0.15494, 0.15438, 0.159, 0.17544, 0.18446, 0.15764, 0.16654, 0.17408, 0.1595, 0.16164]
    else:
        nndata = {
            v: data_Data.objects.filter(
                experiment__graph__tag=f"NN(6)",
                experiment__tag=f"FixEmbedding_Constant_-0.05_0.1_v3",
                experiment__settings__annealing_time=v,
                experiment__settings__num_spin_reversal_transforms=0,
            ).to_dataframe()
            for v in anneal_time
        }
        X = list(nndata.keys())
        y = [
            nndata[key].groupby("energy").count()["id"].iloc[0] / nndata[key].count()["id"]
            for key in X
        ]
        print(y)
    y = {key: y[idx] for idx, key in enumerate(anneal_time)}
    return y

def getsrtdata():
    srt = [0,1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100]
    if True:
        y = [0.16442, 0.17682, 0.17596, 0.19654, 0.19372, 0.20508, 0.18886, 0.19086, 0.18424, 0.18096, 0.18428, 0.18888, 0.17866, 0.18366, 0.18718, 0.1747, 0.17612, 0.17486, 0.17378, 0.1687]
    else:
        nndata = {
            v: data_Data.objects.filter(
                experiment__graph__tag=f"NN(6)",
                experiment__tag=f"FixEmbedding_Constant_-0.05_0.1_v3",
                experiment__settings__annealing_time=600,
                experiment__settings__num_spin_reversal_transforms=v,
            ).to_dataframe()
            for v in srt
        }
        X = list(nndata.keys())
        y = [
            nndata[key].groupby("energy").count()["id"].iloc[0] / nndata[key].count()["id"]
            for key in X
        ]
        print(y)
    y = {key: y[idx] for idx, key in enumerate(srt)}
    return y

def plotta(data):
    X = list(data.keys())
    y = [data[key] for key in X]
    nobs = 50000
    yerr = [proportion_confint(yi*nobs, nobs, alpha=0.05, method='normal') for yi in y]
    yerr1 = [yi[0] for yi in yerr]
    yerr2 = [yi[1] for yi in yerr]
    fig = plt.figure("scaling", figsize=(7, 4))
    ax = plt.axes([0.15, 0.15, 0.8, 0.8])
    ax.errorbar(x=X, y=y, marker="o", color=red, **errorbar_params)
    ax.fill_between(x=X, y1=yerr1, y2=yerr2, color=red, alpha=0.5)
    ax.set_xscale("log")
    ax.set_ylabel("MDS probability")
    ax.set_xlabel("anneal time (microseconds)")
    plt.draw()
    plt.savefig("./anneal_time_scaling.pdf", transparent=True)
    plt.show()

def plotsrt(data):
    X = list(data.keys())
    y = [data[key] for key in X]
    nobs = 50000
    yerr = [proportion_confint(yi*nobs, nobs, alpha=0.05, method='normal') for yi in y]
    yerr1 = [yi[0] for yi in yerr]
    yerr2 = [yi[1] for yi in yerr]
    fig = plt.figure("scaling", figsize=(7, 4))
    ax = plt.axes([0.15, 0.15, 0.8, 0.8])
    ax.errorbar(x=X, y=y, marker="o", color=red, **errorbar_params)
    ax.fill_between(x=X, y1=yerr1, y2=yerr2, color=red, alpha=0.5)
    ax.set_xscale("log")
    ax.set_ylabel("MDS probability")
    ax.set_xlabel("num. spin reversal transformations")
    plt.draw()
    plt.savefig("./srt_scaling.pdf", transparent=True)
    plt.show()

def getdata_full(min, rangex):
    if True and (min==-0.05 and rangex==0.1):
        y = dict()
        y['NegBinary']=[0.91412, 0.49042, 0.39314, 0.48902, 0.12068, 0.13554, 0.02416, 0.03152, 0.02964, 0.06066, 0.00276, 0.0004, 0.00982, 0.0004, 0.03406]
        y['Constant']=[0.93954, 0.59944, 0.68282, 0.54476, 0.19078, 0.27118, 0.05238, 0.0445, 0.0443, 0.0748, 0.00598, 0.00118, 0.01212, 0.00108, 0.04166]
        y['Binary']=[0.9609, 0.68384, 0.71634, 0.65542, 0.45214, 0.32984, 0.56138, 0.19348, 0.17938, 0.2841, 0.04538, 0.0101, 0.06574, 0.00946, 0.1465]
    elif True and (min==-0.04 and rangex== 0.08):
        y = dict()
        y['NegBinary']=[0.92398, 0.543, 0.50756, 0.51004, 0.14294, 0.13256, 0.01662, 0.02278, 0.01948, 0.05336, 0.00218,0.00056, 0.00942, 0.00044, 0.03578]
        y['Constant']=[0.93954, 0.59944, 0.68282, 0.54476, 0.19078, 0.27118, 0.05238, 0.0445, 0.0443, 0.0748, 0.00598, 0.00118, 0.01212, 0.00108, 0.04166]
        y['Binary']=[0.95874, 0.6662, 0.72216, 0.61578, 0.45492, 0.29548, 0.55536, 0.15962, 0.13796, 0.1876, 0.0245, 0.00706, 0.06484, 0.00818, 0.12892]
    elif True and (min==-0.03 and rangex==0.06):
        y = dict()
        y['NegBinary']=[0.933, 0.5577, 0.58678, 0.54532, 0.16342, 0.15068, 0.01802, 0.03104, 0.02472, 0.06206, 0.003, 0.00036, 0.00932, 0.00036, 0.04412]
        y['Constant']=[0.93954, 0.59944, 0.68282, 0.54476, 0.19078, 0.27118, 0.05238, 0.0445, 0.0443, 0.0748, 0.00598, 0.00118, 0.01212, 0.00108, 0.04166]
        y['Binary']=[0.95516, 0.65064, 0.7633, 0.6541, 0.4315, 0.31108, 0.43398, 0.1183, 0.1131, 0.2026, 0.0221, 0.0043, 0.06176, 0.00442, 0.10068]
    elif True and (min==-0.02 and rangex==0.04):
        y = dict()
        y['NegBinary']=[0.93184, 0.59092, 0.6471, 0.55094, 0.16332, 0.17006, 0.01964, 0.0398, 0.02808, 0.0661, 0.00428, 0.00068, 0.01074, 0.0005, 0.04578]
        y['Constant']=[0.93954, 0.59944, 0.68282, 0.54476, 0.19078, 0.27118, 0.05238, 0.0445, 0.0443, 0.0748, 0.00598, 0.00118, 0.01212, 0.00108, 0.04166]
        y['Binary']=[0.952, 0.63998, 0.75932, 0.63612, 0.32166, 0.32244, 0.23534, 0.0861, 0.07174, 0.15234, 0.01402, 0.0025, 0.03394, 0.00324, 0.07716]
    elif True and (min==-0.01 and rangex==0.02):
        y = dict()
        y['NegBinary']=[0.93658, 0.58272, 0.65048, 0.51694, 0.15504, 0.20756, 0.03004, 0.03668, 0.03244, 0.05604, 0.00474, 0.0008, 0.009, 0.00044, 0.03458]
        y['Constant']=[0.93954, 0.59944, 0.68282, 0.54476, 0.19078, 0.27118, 0.05238, 0.0445, 0.0443, 0.0748, 0.00598, 0.00118, 0.01212, 0.00108, 0.04166]
        y['Binary']=[0.94522, 0.61414, 0.70294, 0.56562, 0.21784, 0.30222, 0.099, 0.0557, 0.0471, 0.09092, 0.00784, 0.00148, 0.0163, 0.0013, 0.0425]

    else:
        data = {
            offx: {
                int(v): data_Data.objects.filter(
                    experiment__graph__tag=f"NN({v})",
                    experiment__tag=f"FixEmbedding_{offx}_{min}_{rangex}_v3_1",
                    experiment__settings__annealing_time=600,
                    experiment__settings__num_spin_reversal_transforms=5,
                ).to_dataframe()
                for v in range(2, 17)
            }
            for offx in ["NegBinary", "Constant", "Binary"]
        }
        y = dict()
        for offset in data.keys():
            X = list(data[offset].keys())
            y[offset] = []
            for key in X:
                mds = math.ceil(key / 3)
                try:
                    energy_count = (
                        data[offset][key].groupby("energy").count()["id"].loc[mds]
                    )
                except:
                    energy_count = 0
                total_count = data[offset][key].count()["id"]
                y[offset].append(energy_count / total_count)
        print(y)
    return y


def degenfcn(n):
    if n % 3 == 2:
        return n // 3 + 2
    if n % 3 == 1:
        return 2 * (n // 3 + 1)
    if n % 3 == 0:
        return 1


def plot_full(data, save_tag):
    yhmc = np.array(
        [1, 0.738, 0.823, 0.657, 0.271, 0.568, 0.336, 0.1, 0.318, 0.158, 0.029, 0.169]
    )
    Xhmc = np.arange(len(yhmc)) + 2

    fig = plt.figure("scaling", figsize=(7, 4))
    ax = plt.axes([0.15, 0.15, 0.8, 0.8])
    y = data
    for offset in y:
        X = np.arange(len(y[offset])) + 2
        ax.errorbar(x=X, y=y[offset], label=offset)
    ax.errorbar(x=Xhmc, y=yhmc, label="HMC")
    degeneracy = np.array([degenfcn(Xi) for Xi in X])
    rguess = np.array([1 / 2 ** xi for xi in X]) * degeneracy
    ax.errorbar(x=X, y=rguess, label="Random Guess")
    ax.set_yscale("log")
    ax.legend()
    plt.draw()
    plt.savefig(f"./scaling_full_{save_tag}.pdf")

    fig = plt.figure("ratio scaling", figsize=(7, 4))
    ax = plt.axes([0.15, 0.15, 0.8, 0.8])
    ax.errorbar(
        x=X,
        y=np.array(y["NegBinary"]) / np.array(y["Constant"]),
        label="NegBin / Const.",
    )
    ax.errorbar(
        x=X,
        y=np.array(y["Constant"]) / np.array(y["Constant"]),
        label="Const. / Const.",
    )
    ax.errorbar(
        x=X, y=np.array(y["Binary"]) / np.array(y["Constant"]), label="Bin / Const."
    )
    ax.axhline(y=1)
    ax.legend()
    plt.draw()
    plt.savefig(f"./scaling_full_ratio_{save_tag}.pdf")

    fig = plt.figure("ratio scaling random", figsize=(7, 4))
    ax = plt.axes([0.15, 0.15, 0.8, 0.8])
    ax.errorbar(x=X, y=np.array(y["NegBinary"]) / rguess, label="NegBin / Random")
    ax.errorbar(x=X, y=np.array(y["Constant"]) / rguess, label="Const. / Random")
    ax.errorbar(x=X, y=np.array(y["Binary"]) / rguess, label="Bin / Random")
    ax.errorbar(x=Xhmc, y=yhmc / rguess[:len(yhmc)], label="HMC / Random")
    ax.axhline(y=1)
    ax.legend()
    # ax.set_yscale("log")

    plt.draw()
    plt.savefig(f"./scaling_full_ratio_random_{save_tag}.pdf")
    plt.show()


def get_y(data):
    y = dict()
    for offset in data.keys():
        X = list(data[offset].keys())
        y[offset] = []
        for key in X:
            mds = math.ceil(key / 3)
            try:
                energy_count = (
                    data[offset][key].groupby("energy").count()["id"].loc[mds]
                )
            except:
                energy_count = 0
            total_count = data[offset][key].count()["id"]
            y[offset].append(energy_count / total_count)
    return X, y


def plot_compare(data1, data2):
    fig = plt.figure("scaling compare", figsize=(7, 4))
    ax = plt.axes([0.15, 0.15, 0.8, 0.8])
    X1, y1 = get_y(data1)
    X2, y2 = get_y(data2)
    ax.errorbar(
        x=X1,
        y=np.array(y1["NegBinary"]) / np.array(y2["NegBinary"]),
        label="0.1/0.08 NegBin",
    )
    ax.errorbar(
        x=X1,
        y=np.array(y1["Constant"]) / np.array(y2["Constant"]),
        label="0.1/0.08 Const",
    )
    ax.errorbar(
        x=X1, y=np.array(y1["Binary"]) / np.array(y2["Binary"]), label="0.1/0.08 Bin"
    )
    ax.axhline(y=1)
    ax.legend()
    plt.draw()
    plt.savefig("./scaling_comparison_0p1_0p08.pdf")
    plt.show()

def plot_compare_all(data02, data04, data06, data08, data10):
    fig = plt.figure("scaling compare", figsize=(7, 4))
    ax = plt.axes([0.15, 0.15, 0.8, 0.8])
    X = np.arange(len(data10["Constant"]))+2
    ax.errorbar(x=X, y=data10["Binary"], label="Binary 0.10", color=red, **errorbar_params)
    ax.errorbar(x=X, y=data08["Binary"], label="Binary 0.08", color=green, **errorbar_params)
    ax.errorbar(x=X, y=data06["Binary"], label="Binary 0.06", color=blue, **errorbar_params)
    ax.errorbar(x=X, y=data04["Binary"], label="Binary 0.04", color=red, ls='--', **errorbar_params)
    ax.errorbar(x=X, y=data02["Binary"], label="Binary 0.02", color=green, ls='--', **errorbar_params)
    ax.errorbar(x=X, y=data10["Constant"], label="Constant", color=blue, ls='--', **errorbar_params)
    ax.legend()
    ax.set_yscale("log")
    plt.draw()
    plt.savefig("./scaling_comparison_all.pdf")
    plt.show()

if __name__ == "__main__":
    # plot scaling with anneal_time
    # NN(6) constant offset no spin reversal transformation
    #tadata = gettadata()
    #plotta(tadata)

    # plot srt scaling
    # NN(6) constant offset annal time 600
    #srtdata = getsrtdata()
    #plotsrt(srtdata)

    # full scaling plot
    # NN(2) to NN(16)
    # anneal time 600 5 srt
    # offset -0.05 to 0
    data02 = getdata_full(-0.01, 0.02)
    #plot_full(data02, "0p02")
    data04 = getdata_full(-0.02, 0.04)
    #plot_full(data04, "0p02")
    data06 = getdata_full(-0.03, 0.06)
    #plot_full(data06, "0p02")
    data08 = getdata_full(-0.04, 0.08)
    #plot_full(data08, "0p02")
    data10 = getdata_full(-0.05, 0.1)
    #plot_full(data10, "0p10")

    # compare offset plot
    plot_compare_all(data02, data04, data06, data08, data10)